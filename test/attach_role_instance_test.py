# tests.py
from apr import iac
import unittest


role_name = 'aws-project-runner-sms-role'
instance_id = '<INSTANCE_ID>'


class RoleTest(unittest.TestCase):

    def test1_create_iam_role():
        iac.create_iam_role(role_name)

    def test2_attach_role_to_instance(self):
        iac.attach_role_to_instance(role_name, instance_id)


if __name__ == '__main__':
    unittest.main()
