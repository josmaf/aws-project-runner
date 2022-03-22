import boto3
import json
import time
from apr import ssm
from apr import logger
from botocore.exceptions import ClientError


log = logger.get_logger(__name__)


# CONSTANTS
REGION = "eu-west-1"
ROLE_NAME = 'aws-script-runner-sms-role'
INSTANCE_PROFILE_NAME = 'aws-script-runner-instance-profile'
CUSTOM_EC2_POLICY_NAME = "aws-script-runner-ec2-policy"
SSM_COMMAND_WAITING_TIME = 10
INSTANCE_STATE_POLLING_DELAY = 90
TRUST_REL_POLICY_FILE_PATH = 'resources/trust_relationship_policy.json'


class Iac:
    """Class to manage Infrastructure-as-code"""

    def __init__(self, aws_creds):
        self.aws_creds = aws_creds
        self.iam_client = boto3.client('iam', aws_access_key_id=aws_creds[0], aws_secret_access_key=aws_creds[1])
        self.ec2_client = boto3.client('ec2', aws_access_key_id=aws_creds[0], aws_secret_access_key=aws_creds[1])
        self.sts_client = boto3.client('sts', aws_access_key_id=aws_creds[0], aws_secret_access_key=aws_creds[1])
        self.ACCOUNT_ID = self.sts_client.get_caller_identity().get('Account')
        self.CUSTOM_EC2_POLICY_ARN = 'arn:aws:iam::{}:policy/aws-script-runner-ec2-policy'.format(self.ACCOUNT_ID)

    def __wait_until_runnable(self, instance_id):
        wait_for_status = True
        _ssm = ssm.Ssm(self.aws_creds)
        while wait_for_status:
            try:
                command = 'aws sts get-caller-identity >> /home/ec2-user/startup_test.log 2>&1'                
                _ssm.run_command(command, instance_id)
                wait_for_status = False
            except ClientError as exc:
                if exc.response['Error']['Code'] == 'InvalidInstanceId' and 'not in a valid state' in exc.response['Message']:
                    log.info("Instance not ready. Waiting...")
                    time.sleep(INSTANCE_STATE_POLLING_DELAY)
                else:
                    log.error("Unexpected error: %s" % exc)
        log.info("Instance ready to execute actions")

    def __clean_previous_infrastructure(self):
        log.info("Cleaning infrastructure...")
        session = boto3.Session(
            aws_access_key_id=self.aws_creds[0],
            aws_secret_access_key=self.aws_creds[1])
        IAM_RESOURCE = session.resource('iam')

        try:  # Remove roles from instance profile
            instance_profile = IAM_RESOURCE.InstanceProfile(INSTANCE_PROFILE_NAME)
            for attached_role in instance_profile.roles_attribute:
                instance_profile.remove_role(RoleName=attached_role['RoleName'])
        except Exception as exc:
            pass
        try:  # Delete instance profile
            instance_profile.delete()
        except Exception as exc:
            pass
        try:  # Detach policies from role, if attached
            for policy in self.iam_client.list_attached_role_policies(
                    RoleName=ROLE_NAME)['AttachedPolicies']:
                self.iam_client.detach_role_policy(
                    PolicyArn=policy['PolicyArn'], RoleName=ROLE_NAME)
            self.iam_client.delete_role(RoleName=ROLE_NAME)
        except Exception as exc:
            pass

        try:  # Delete policy
            self.iam_client.delete_policy(PolicyArn=self.CUSTOM_EC2_POLICY_ARN)
        except Exception as exc:
            pass
        log.info("Infrastructure cleaned")

    def __create_custom_policy(self):
        log.info("Creating custom policy...")
        try:
            with open('resources/policy.json') as json_file:
                policy_json = json.load(json_file)
                response = self.iam_client.create_policy(
                    PolicyName=CUSTOM_EC2_POLICY_NAME,
                    PolicyDocument=json.dumps(policy_json))
                log.info("Custom policy created")
        except Exception as exc:
            log.error(exc)

    def __create_iam_role(self, role_name):
        """" Create SSM role for EC2 instance"
    
        :param role_name: Name of role to be assigned to the EC2 instance
        """
        log.info("Creating role...")
        try:
            with open(TRUST_REL_POLICY_FILE_PATH, 'r') as json_file:
                trust_relationship_policy = json.load(json_file)
            self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_relationship_policy),
                Description='Role for aws-script-runner app')
            time.sleep(SSM_COMMAND_WAITING_TIME)
            self.iam_client.attach_role_policy(
                RoleName=role_name, PolicyArn=self.CUSTOM_EC2_POLICY_ARN)
            log.info("Role created")
        except ClientError as exc:
            if exc.response['Error']['Code'] == 'EntityAlreadyExists':
                log.error("Role already exists")
            else:
                log.error("Unexpected error: %s" % exc)

    def attach_role_to_instance(self, role_name, instance_id):
        log.info("Attaching SSM role to instance...")
        try:
            # First, create a instancce profile
            self.iam_client.create_instance_profile(
            InstanceProfileName=INSTANCE_PROFILE_NAME)
            time.sleep(SSM_COMMAND_WAITING_TIME)
        except ClientError as exc:
            if exc.response['Error']['Code'] == 'EntityAlreadyExists':
                log.error("Instance profile already exists")
            else:
                log.error("Unexpected error: %s" % exc)
        try:
            self.iam_client.add_role_to_instance_profile(
                InstanceProfileName=INSTANCE_PROFILE_NAME,
                RoleName=role_name)
        except ClientError as exc:
            log.info("Role has not been attached to instance profile")
        time.sleep(SSM_COMMAND_WAITING_TIME)
        response = self.ec2_client.associate_iam_instance_profile(
            IamInstanceProfile={'Name': INSTANCE_PROFILE_NAME},
            InstanceId=instance_id)
        log.info("SSM Role attached to instance")

    def __create_instance(self):
        user_data = '''#!/bin/bash
        yum install awscli -y
        echo export AWS_ACCESS_KEY_ID={aak} >> /etc/environment
        echo export AWS_SECRET_ACCESS_KEY={asa} >> /etc/environment
        echo export AWS_DEFAULT_REGION={adr} >> /etc/environment
        source /etc/environment
        aws configure set aws aws_access_key_id {aak}
        aws configure set aws aws_secret_access_key {asa}
        aws configure set region {adr}
        mkdir /home/ec2-user/input
        chown -R ec2-user:ec2-user /home/ec2-user/input
        mkdir /home/ec2-user/input
        chown -R ec2-user:ec2-user /home/ec2-user/output
        mkdir /home/ec2-user/projects
        chown -R ec2-user:ec2-user /home/ec2-user/projects
        mkdir /home/ec2-user/resources
        chown -R ec2-user:ec2-user /home/ec2-user/resources
        yum install unzip -y
        '''.format(aak=self.aws_creds[0], asa=self.aws_creds[1], adr=REGION)

        # Launch instance
        instances = self.ec2_client.run_instances(
           ImageId="ami-034153729211d5d49",
           MinCount=1,
           MaxCount=1,
           InstanceType="t2.micro",
           KeyName="ireland_keys",
           UserData=user_data)
        instance_id = instances['Instances'][0]['InstanceId']
        log.info("Launching EC2 instance {}...".format(instance_id))
        self.ec2_client.get_waiter('instance_running').wait(InstanceIds=[instance_id])
        log.info("Instance is running, but not fully operational yet")
        return instance_id

    def launch_runnable_instance(self):
        """Launch an EC2 instance ready to execute actions"""
        self.__clean_previous_infrastructure()
        self.__create_custom_policy()
        self.__create_iam_role(ROLE_NAME)
        instance_id = self.__create_instance()
        # Attach role so that the instance has permissions to do things
        self.attach_role_to_instance(ROLE_NAME, instance_id)
        self.__wait_until_runnable(instance_id)  # It takes some time to take effect
        return instance_id

    def configure_instance(self, instance_id, s3, project_folder, data_folder):
        log.info("Configuring instance...")
        s3.download_unzip_to_instance(instance_id, 'input/', data_folder)
        s3.download_unzip_to_instance(instance_id, 'projects/', project_folder)
        log.info("Instance configured")