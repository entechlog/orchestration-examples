- [DEMO-01 - Setup Astronomer Airflow](#demo-01---setup-astronomer-airflow)
  - [Airflow Setup](#airflow-setup)
  - [S3 Operator testing](#s3-operator-testing)

# DEMO-01 - Setup Astronomer Airflow

## Airflow Setup

- Download and run [Docker](https://docs.docker.com/docker-for-mac/install/)
- Download the [Astro CLI](https://github.com/astronomer/astro-cli)
- Initialize astro `astro dev init`
- Start astro by running `astro dev start`
  > Set environment `setx DOCKER_BUILDKIT 0` to fix buildkit not supported by daemon Error
- Check containers by running `astro dev ps`
- Stop astro by running `astro dev stop`

## S3 Operator testing

- IAM user and s3 bucket is required for testing
- S3 connection `aws_s3_demo_connection` has to be created manually for now
