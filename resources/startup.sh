#!/bin/bash
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
mkdir /home/ec2-user/project
chown -R ec2-user:ec2-user /home/ec2-user/project
