from apr import s3


if __name__ == "__main__":
    input_data_folder = '/home/jose.fernandez/projects/aws-script-runner/test/input'
    project_folder = '/home/jose.fernandez/projects/aws-script-runner/project'
    s3.send_input_data(input_data_folder, 'input/')
    s3.send_input_data(project_folder, 'projects/')
    print("OK")

