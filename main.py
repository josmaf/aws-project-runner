from apr import iac
from apr import s3
from apr import logger
from apr import creds
from apr import ssm
import argparse


log = logger.get_logger(__name__)


def prepare_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project_folder', required=True, type=str, help='Project folder')
    parser.add_argument('-d', '--data_folder', required=True, type=str, help='Input data folder')
    return parser.parse_args()


if __name__ == "__main__":
    # args = prepare_arguments()
    data_folder = '/home/jose.fernandez/projects/aws-project-runner/test/input'
    project_folder = '/home/jose.fernandez/projects/aws-project-runner/test/project1'
    creds_file_path = '/home/jose.fernandez/Dropbox/amazon/jose_aws_privada_copia.csv'
    
    # Read AWS credentials
    aws_creds = creds.read_credentials(creds_file_path)

    # Clean infrastructure & create from scratch
    iac = iac.Iac(aws_creds)
    iac.clean_previous_infrastructure()
    iac.create_initial_infrastructure()

    # Send project and data to S3
    s3 = s3.S3(aws_creds, iac.get_bucket_name())
    zip_project_file_name = s3.send_project_s3(project_folder, 'projects/')
    zip_data_file_name = s3.send_zipped_folder(data_folder, 'input/')
    
    # Launch instance
    instance_id = iac.launch_runnable_instance()
    iac.configure_instance(instance_id, zip_project_file_name, zip_data_file_name)

    # Run detached orchestrator job.sh  
    _ssm = ssm.Ssm(aws_creds)
    _ssm.run_command("sh /home/ec2-user/projects/job.sh", instance_id)
    log.info("Job launched!")
    
    # Delete infra
    # iac.clean_previous_infrastructure()
    # ssm.run_command("aws ec2 terminate-instances --instance-ids {}".format(instance_id), instance_id)




