# Prefect Cloud Quick Start Guide

This guide provides basic instructions on how to set up and manage Prefect flows using a command-line interface. Below, you'll find steps to create a Prefect configuration file, log in to Prefect Cloud, run a flow, and create a deployment.

## Prerequisites

Ensure you have Prefect installed. If not, you can install it using pip:
```bash
pip install prefect
```

## Configuration
### Creating a prefect.yaml Template File
To create a basic prefect.yaml template file, use the following command:

```bash
prefect init
```

This command will generate a prefect.yaml file in your working directory, which you can modify according to your project's needs.

## Authentication
## Logging into Prefect Cloud
To log in to Prefect Cloud, you need an API key. Once you have your key, you can log in using the following command:
```bash
prefect cloud login -k YOUR_API_KEY
```

Replace YOUR_API_KEY with your actual Prefect Cloud API key.


## Managing Flows
### Running a Flow
To execute a flow, navigate to the directory containing your flow script and run:
```bash
python example-flow-04.py
```

Ensure that example-flow-04.py is the Python file where your flow is defined.

### Creating a Deployment
To deploy your flow to Prefect Cloud or server, use the following command:
```bash
prefect deploy --name example_deployment_02
```

Here example_deployment_02 is the name specified in your prefect.yaml for the deployment. This command will deploy your flow according to the configurations set in the prefect.yaml file.

### Running a Deployment
To run a deployment, use the following command:

```bash
prefect deployment run 'demo-flow/example_deployment_02'
```

### AWS SSO
```bash
# sso login
aws configure sso
# export sso creds to env
eval "$(aws configure export-credentials --profile <profile-name> --format env)"

# install docker
sudo apt install docker.io

# login into ecr
aws ecr get-login-password --region us-east-2 --profile <profile-name> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-2.amazonaws.com
```

### Debug locally
```bash
# Pull the Docker image
docker pull <account-id>.dkr.ecr.us-east-2.amazonaws.com/<image-name>:<tag-name>

# Run the container with an interactive shell
docker run -it <account-id>.dkr.ecr.us-east-2.amazonaws.com/<image-name>:<tag-name> /bin/bash
```

# Reference
- https://github.com/PrefectHQ/prefect-recipes/tree/main/devops/infrastructure-as-code/aws/tf-prefect2-ecs-worker
