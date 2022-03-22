from apr import logger
import boto3
import time


# CONSTANTS
REGION = "eu-west-1"
SSM_COMMAND_WAITING_TIME = 10


log = logger.get_logger(__name__)


class Ssm:
    """Class to control AWS Systems Manager agent"""
        
    def __init__(self, aws_creds):
        self.ssm_client = boto3.client('ssm', aws_access_key_id=aws_creds[0], aws_secret_access_key=aws_creds[1])
 
    def run_command(self, command, instance_id):
        """Execute command in a remote EC2 instance

        :param command: Shell command to be executed
        :param instance_id: ID of EC2 instance
        :return: None        
        """
        command = command + ' >> /home/ec2-user/command.log 2>&1'
        response = self.ssm_client.send_command(
                InstanceIds=[instance_id],
                DocumentName="AWS-RunShellScript",
                Parameters={'commands': [command]})    
        command_id = response['Command']['CommandId']
        time.sleep(SSM_COMMAND_WAITING_TIME)
        output = self.ssm_client.get_command_invocation(CommandId=command_id,InstanceId=instance_id)
        time.sleep(SSM_COMMAND_WAITING_TIME) 
