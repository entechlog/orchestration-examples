- [DEMO-01 - Setup Astronomer Airflow](#demo-01---setup-astronomer-airflow)
  - [Airflow Setup](#airflow-setup)

# DEMO-01 - Setup Astronomer Airflow

## Airflow Setup

- Download and run [Docker](https://docs.docker.com/docker-for-mac/install/)
- Download the [Astro CLI](https://github.com/astronomer/astro-cli)
- Initialize astro `astro dev init`
- Start astro by running `astro dev start`
  > Set environment `setx DOCKER_BUILDKIT 0` to fix buildkit not supported by daemon Error
- Check containers by running `astro dev ps`
- Stop astro by running `astro dev stop`
