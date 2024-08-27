#!/bin/bash

# Variables
IMAGE_NAME="prefect-local-python"
IMAGE_TAG="latest"

# Build the Docker image locally
docker build -t $IMAGE_NAME:$IMAGE_TAG .

# (Optional) Run the Docker image locally to test
# docker run -it $IMAGE_NAME:$IMAGE_TAG bash
# docker run -it prefect-local-python:latest bash
