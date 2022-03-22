import shutil
import hashlib
import os
import random
import string
import boto3
from apr import ssm


BUCKET_NAME = "aws-script-runner-017272392845"  # TODO get aws id dynamically
LOCAL_DOCKERFILE_PATH = 'docker/Dockerfile'
LOCAL_DOCKER_ENTRYPOINT_PATH = 'docker/entrypoint.sh'
LOCAL_JOB_SCRIPT_PATH = 'resources/job.sh'
REGION = "eu-west-1"
S3_DATA_FOLDER = '/input'
S3_PROJECT_FOLDER = 'projects/'

class S3:
    '''Class to manage S3-related actions'''

    def __init__(self, aws_creds):
        self.s3_client = boto3.client('s3', aws_access_key_id=aws_creds[0], aws_secret_access_key=aws_creds[1])
 
    def __generate_file_md5(self, rootdir, filename, blocksize=2**20):
        m = hashlib.md5()
        with open( os.path.join(rootdir, filename) , "rb" ) as f:
            while True:
                buf = f.read(blocksize)
                if not buf:
                    break
                m.update( buf )
        return m.hexdigest()

    def __generate_random_string(self, length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def __zip_folder(self, folder_path):
        tmp_file_name = os.path.abspath(self.__generate_random_string(16)) 
        # create zip from input folder
        shutil.make_archive(tmp_file_name, 'zip', folder_path)
        # generate hash and rename
        new_file_name = self.__generate_file_md5('.', tmp_file_name + '.zip')
        os.rename(tmp_file_name + '.zip', new_file_name)
        return new_file_name

    def create_s3_bucket(self, bucket_name):
        """Create a S3 bucket.
        
        :param bucket_name: Bucket name
        :return: None
        """
        response = self.s3_client.create_bucket(
           Bucket = bucket_name,
           CreateBucketConfiguration={'LocationConstraint': REGION})

    def send_zipped_folder(self, local_folder_path, s3_folder):
        """ Zip a local folder and send the file to a S3 folder

        :param local_folder_path: full folder path, everythoing within this folder will be zipped
        :param s3_folder: s3 folder where the zip file will be sent
        return: full pth of zip file  
        """
        zipped_data_file_name = self.__zip_folder(local_folder_path)
        with open(zipped_data_file_name, "rb") as f:
            self.s3_client.upload_fileobj(f, BUCKET_NAME, s3_folder + zipped_data_file_name)
        return zipped_data_file_name

    def download_unzip_to_instance(self, instance_id, s3_folder_name, file_name):
        """Connects to an instance, download zip file from S3, unzip the file.

        :param instance_id: AWS instance id
        :param folder_name: S3 folder name where the zip file will be unzip
        :param file_name: Zip file name
        :return: None 
        """
        download_command = 'aws s3 cp s3://{bn}/{folder}/{fn} /home/ec2-user/{folder}/{fn}'\
            .format(bn=BUCKET_NAME, folder=s3_folder_name, fn=file_name)
        unzip_command = 'unzip /home/ec2-user/{}/{}'.format(s3_folder_name, file_name)
        ssm.run_command(download_command, instance_id) 
        ssm.run_command(unzip_command, instance_id) 


    def send_project_s3(self, local_project_folder, s3_project_folder):
        """Prepare project with auxiliary files, zip it, and send it to S3.

        :param local_project_folder: Full path of local project to be run in the cloud
        :param s3_project_folder: S3 path where project is stored
        :return: Zip file path in S3
        """
        aux_files = (
            shutil.copy(LOCAL_DOCKERFILE_PATH, local_project_folder), 
            shutil.copy(LOCAL_DOCKER_ENTRYPOINT_PATH , local_project_folder),
            shutil.copy(LOCAL_JOB_SCRIPT_PATH, local_project_folder))
        zip_project_file_name = self.send_zipped_folder(local_project_folder, s3_project_folder)
        for aux_f in aux_files:  # TODO  issue if there already exist a dockerfile or entrypoint file
            os.remove(aux_f)
        os.remove(zip_project_file_name)
        return zip_project_file_name
        
    def create_init_setup(self):
        # create s3 bucket: aws-script-runner-<user_id>
        # create s3 folders: input, output, projects, resources
        pass
   

