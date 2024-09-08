# Prefect Cloud Quick Start Guide

This guide provides basic instructions on how to set up and manage Prefect flows using a command-line interface. Below, you'll find steps to create a Prefect configuration file, log in to Prefect Cloud, run a flow, and create a deployment.

## Prerequisites

Ensure you have Prefect installed. If not, you can install it using pip:
```bash
pip install prefect
```

## Logging into Prefect Cloud
To log in to Prefect Cloud, you need an API key. Once you have your key, you can log in using the following command:
```bash
export PREFECT_API_KEY=YOUR_API_KEY
OR
prefect cloud login -k YOUR_API_KEY
```

Replace YOUR_API_KEY with your actual Prefect Cloud API key.

## Configuration
To create a basic prefect.yaml template file, use the following command:

```bash
prefect init
```

This command will generate a prefect.yaml file in your working directory, which you can modify according to your project's needs.

## Managing Flows
### Running a Flow
To execute a flow, navigate to the directory containing your flow script and run:
```bash
python get_system_name.py
```

Ensure that get_system_name.py is the Python file where your flow is defined.

### Create image
Create the docker image by running `./build_docker_image_dkr.sh`

### Creating a Deployment
To deploy your flow to Prefect Cloud or server, use the following command:
```bash
prefect --no-prompt deploy --all
prefect --no-prompt deploy --all --prefect-file prefect_local.yaml
prefect --no-prompt deploy --all --prefect-file prefect_ecs.yaml
prefect --no-prompt deploy --all --prefect-file prefect_dbt_shell.yaml
prefect --no-prompt deploy --name get-system-name-dkr --prefect-file prefect_local.yaml
```

Here get-system-name-dkr is the name specified in your prefect.yaml for the deployment. This command will deploy your flow according to the configurations set in the prefect.yaml file.

### Running a Deployment
To run a deployment, use the following command:

```bash
prefect deployment run 'demo-flow/get-system-name-dkr'
```

### AWS SSO
This is required when using ECR

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
docker run -it prefect-local-dbt:latest bash
```

## Naming Standards 

| **Item**        | **Naming Format**                         | **Example**                                          |
| --------------- | ----------------------------------------- | ---------------------------------------------------- |
| **Flows**       | `<project>-<detail>-<action>`             | `system-get-name`                                    |
| **Deployments** | `<project>-<detail>-<action>`             | `system-get-name`                                    |
| **Workpools**   | `<cloudCode>-<infraCode>-<number2Digits>` | `aws-ecs-01`, `local-dkr-01`                         |
| **Blocks**      | `<platform>-<block_type>-<detail>`        | `aws-credential-prefect`, `snowflake-credential-dbt` |


## Known issues and solutions
| **Issue**                                               | **Solution**                      |
| ------------------------------------------------------- | --------------------------------- |
| /bin/bash^M: bad interpreter: No such file or directory | sed -i -e 's/\r$//' scriptname.sh |

# Reference
- https://github.com/PrefectHQ/prefect-recipes/tree/main/devops/infrastructure-as-code/aws/tf-prefect2-ecs-worker
- https://github.com/PrefectHQ/pacc-2024-v4
- https://stackoverflow.com/questions/78483683/accessing-the-scheduled-time-from-within-a-prefect-flow-run
- https://github.com/public-apis/public-apis
