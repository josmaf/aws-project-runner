from apr import iac
from apr import s3
from apr import logger
from apr import creds
import os
import shutil
import argparse


log = logger.get_logger(__name__)


S3_DATA_FOLDER = '/input'
S3_PROJECT_FOLDER = 'projects/'


def prepare_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project_folder', required=True, type=str, help='Input folder')
    parser.add_argument('-d', '--data_folder', required=True, type=str, help='Output folder')
    return parser.parse_args()


if __name__ == "__main__":
    # args = prepare_arguments()
    data_folder = '/home/jose.fernandez/projects/aws-project-runner/test/input'
    project_folder = '/home/jose.fernandez/projects/aws-project-runner/test/project1'
    creds_file_path = '/home/jose.fernandez/Dropbox/amazon/jose_aws_privada_copia.csv'
    
    # Read AWS credentials
    aws_creds = creds.read_credentials(creds_file_path)

    # Send zipped project and data to S3
    s3 = s3.S3(aws_creds)
    zip_project_file_name = s3.send_project_s3(project_folder, 'projects/')
    zip_data_file_name = s3.send_zipped_folder(data_folder, 'input/')
    
    # Launch instance
    iac = iac.Iac(aws_creds)
    instance_id = iac.launch_runnable_instance()
    iac.configure_instance(instance_id, s3, zip_project_file_name, zip_data_file_name)

    # Run detached orchestrator job.sh  
    # Unzip /input 
    # Unzip /projects
    # cd /home/ec2-user/projects
    # build image -t <...>/<project_name>:latest 
    # docker run --rm <...>/<project_name>:latest -v /home/ec2-user/input:/input -v /home/ec2-user/output:/output
    # zipear /home/ec2-user/output y mandar a S3 con timestamp
    # Delete infra
    # aws ec2 terminate-instances --instance-ids <instance_id>



