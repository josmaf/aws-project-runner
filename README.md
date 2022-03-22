# Intro (start here)

Project to launch Python projects in AWS.

It uploads your data & code to AWS and run it on the infrastructure you desire.

Almost no AWS setup required, no risk of leaving costly AWS resources behind after use.


# More in-depth

## Problem

1. Scenario: we have a piece of local Python code that: 
	- Reads data
	- Process data 
	- Generate an output
2. In order to do its job, that code needs: ardware & more code (environment, dependencies...)
3. Sometimes we need to change both quickly: try with more/less CPU cores, GPUs, memory, add/edit dependencies, etc.


## Exploration

Multiple Cloud vendors offer multiple tools to run things in their environments, but:

- Overkill solutions 
- Steep learning curve
- Changing APIs, docs...
- Costs can be hard to forecast
- Costs even when not being used

## Solution

### **What**:

Custom library/Decorator/App (to be decided) to automate data managing and code execution in AWS (by now):

0. Clean & create infrastructure
1. Send all-what-is-needed to S3: input data, code, auxiliary files 
2. Launch EC2 instance 
3. Build Docker image in EC2
4. Send Docker image to ECR
5. Run image as a container in EC2 or ECS (currently exploring...). The container must be able to:              
	a. Download data from S3 to the container file system
	b. Run code
	c. Send results from the container file system to S3, and a http link to the S3 console to the user
6. Destroy all the infrastructure used except the S3 bucket and the ECR repository


### **How**:

Tech stack:
- Python
- Docker
- Shell scripting
- AWS IAM: https://aws.amazon.com/es/iam/
- AWS EC2: https://aws.amazon.com/es/ec2/
- AWS ECS: possible
- AWS SSM: https://aws.amazon.com/es/systems-manager/
- AWS ECR: https://aws.amazon.com/es/ecr/


### Problems found

Changing AWS APIs and doc
Non-deterministic behaviours  (network variability, AWS internal time to apply changes -roles, permissions...)


# Project-to-be-run requirements

The project to be run must meet the following requirements:

1. The script and all the imported modules must be packaged within a parent folder
2. The parent folder must have a requirements.txt file
3. Script must include two mandatory arguments: "-i" (input folder full path) and "-o" (output folder full path) 


# Improvements (Technical debt & functional scope)

## Functional (what)
Allow more than one execution per AWS account (currently: names & permission conflicts)
Allow to use GPUs instances
Fine-grained detail of infrastructure to be kept/destroyed after running
Allow to check job status
Cost calculator (before execution: cost estimation. After execution: how much did it cost?)
Send email when job is finished
Allow using EC2 spot instances (cheaper)

## Technical (how)
Check file already exists before sending objects to S3 to minimize network traffic
Implement exponential back-off in SSM calls
Use non-admin account internally to minimize security leaks
Use EC2 Image Builder?



