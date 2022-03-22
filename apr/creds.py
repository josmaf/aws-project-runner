import pandas as pd


AWS_ACCESS_KEY_ID_COLUMN = 'AWSAccessKeyId'
AWS_SECRET_ACCESS_KEY_COLUMN = 'AWSSecretKey'


def read_credentials(file_path):
    """Read AWS credentials file.

    :param file_path: Credentials file full path
    :return: tuple of (aws access key ID, aws secret access key)
    """
    cred = pd.read_csv(file_path)
    return cred[AWS_ACCESS_KEY_ID_COLUMN][0], cred[AWS_SECRET_ACCESS_KEY_COLUMN][0]
