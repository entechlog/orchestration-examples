
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

Replace `YOUR_API_KEY` with your actual Prefect Cloud API key.

## Configuration

To create a basic `prefect.yaml` template file, use the following command:

```bash
prefect init
```

This command will generate a `prefect.yaml` file in your working directory, which you can modify according to your project's needs.

## Managing Flows

### Running a Flow

To execute a flow, navigate to the directory containing your flow script and run:

```bash
python get_system_name.py
```

Ensure that `get_system_name.py` is the Python file where your flow is defined.

### Create Docker Image

Create the Docker image by running:

```bash
./build_docker_image_dkr.sh
```

### Creating a Deployment

To deploy your flow to Prefect Cloud or server, use the following command:

```bash
prefect --no-prompt deploy --all
prefect --no-prompt deploy --all --prefect-file prefect_local.yaml
prefect --no-prompt deploy --all --prefect-file prefect_ecs.yaml
prefect --no-prompt deploy --all --prefect-file prefect_dbt_shell.yaml
prefect --no-prompt deploy --name get-system-name-dkr --prefect-file prefect_local.yaml
```

Here `get-system-name-dkr` is the name specified in your `prefect.yaml` for the deployment. This command will deploy your flow according to the configurations set in the `prefect.yaml` file.

### Running a Deployment

To run a deployment, use the following command:

```bash
prefect deployment run 'demo-flow/get-system-name-dkr'
```

### Using the .env File

To manage environment variables, ensure your `.env` file is properly set up. You can define your environment variables in `.env` and they will be automatically loaded by Docker Compose:

```bash
# Example .env
MY_ENV_VAR=value_from_env_file
```

### Starting the Docker Environment

To build and run the Docker environment locally, use Docker Compose:

```bash
docker-compose up --build
OR
docker-compose up -d --build
```

### SSH into the Running Docker Container

After starting the container, you can SSH into it for testing or debugging purposes:

```bash
docker exec -it prefect-local-python /bin/bash
```

### Formatting Python Code with Ruff

To ensure consistent code formatting, use Ruff. Ruff is a fast Python linter and formatter.

To format the Python code, run:

```bash
ruff check --fix src/
```

This will automatically format the code in the `src/` directory according to your project's coding standards.

### AWS SSO (For ECR)

This is required when using ECR:

```bash
# SSO login
aws configure sso
# Export SSO creds to env
eval "$(aws configure export-credentials --profile <profile-name> --format env)"

# Install Docker
sudo apt install docker.io

# Login into ECR
aws ecr get-login-password --region us-east-2 --profile <profile-name> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-2.amazonaws.com
```

### Debug Locally

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

## Known Issues and Solutions

| **Issue**                                               | **Solution**                      |
| ------------------------------------------------------- | --------------------------------- |
| /bin/bash^M: bad interpreter: No such file or directory | sed -i -e 's/$//' scriptname.sh |

# Reference

- https://github.com/PrefectHQ/prefect-recipes/tree/main/devops/infrastructure-as-code/aws/tf-prefect2-ecs-worker
- https://github.com/PrefectHQ/pacc-2024-v4
- https://stackoverflow.com/questions/78483683/accessing-the-scheduled-time-from-within-a-prefect-flow-run
- https://github.com/public-apis/public-apis

# Test cases 
## Daily run with batch cycle date
```bash
python get_pair_candles.py --base_url "https://community-api.coinmetrics.io/v4/timeseries" --endpoint "/pair-candles" --frequency "1d" --page_size "1500" --s3_bucket "dev-entechlog-landing-zone" --s3_key_prefix "source=coinmetrics/event_name=pair-candles" --run_type "daily" --batch_cycle_date "2024-04-20" --clean_directory_before_write
```

## Backfill run with backfill dates (5 days in the past)
```bash
python get_pair_candles.py --base_url "https://community-api.coinmetrics.io/v4/timeseries" --endpoint "/pair-candles" --frequency "1d" --page_size "1500" --s3_bucket "dev-entechlog-landing-zone" --s3_key_prefix "source=coinmetrics/event_name=pair-candles" --run_type "backfill" --backfill_start_date "2024-04-15" --backfill_end_date "2024-04-19" --clean_directory_before_write
```

## Run without batch_cycle_date, backfill_start_date, and backfill_end_date
```bash
python get_pair_candles.py --base_url "https://community-api.coinmetrics.io/v4/timeseries" --endpoint "/pair-candles" --frequency "1d" --page_size "1500" --s3_bucket "dev-entechlog-landing-zone" --s3_key_prefix "source=coinmetrics/event_name=pair-candles" --run_type "daily" --clean_directory_before_write

python get_pair_candles.py --base_url "https://community-api.coinmetrics.io/v4/timeseries" --endpoint "/pair-candles" --frequency "1d" --page_size "1500" --s3_bucket "dev-entechlog-landing-zone" --s3_key_prefix "source=coinmetrics/event_name=pair-candles" --run_type "backfill" --clean_directory_before_write
```

## Same as scenario 3, but without clean_directory_before_write
```bash
python get_pair_candles.py --base_url "https://community-api.coinmetrics.io/v4/timeseries" --endpoint "/pair-candles" --frequency "1d" --page_size "1500" --s3_bucket "dev-entechlog-landing-zone" --s3_key_prefix "source=coinmetrics/event_name=pair-candles" --run_type "daily"
```