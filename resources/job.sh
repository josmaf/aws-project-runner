#!/bin/bash
cd /home/ec2-user/projects
docker build -t josemfer/aws-project-runner:latest .
docker run -d --rm -v /home/ec2-user/input:/input -v /home/ec2-user/output:/output josemfer/aws-project-runner:latest
cd /home/ec2-user/
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
BUCKET_NAME='aws-project-runner-108785321365'
zip -r output_$TIMESTAMP.zip output/
aws s3 cp output_$TIMESTAMP.zip s3://$BUCKET_NAME/output/

