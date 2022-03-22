#!/bin/bash
docker build -t josemfer/aws-script-runner:latest .
docker run josemfer/aws-script-runner:latest
