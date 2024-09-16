# Base image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements.txt to the container
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code from the python directory
COPY . .

# Set PYTHONPATH environment variable
ENV PYTHONPATH "$PYTHONPATH:/app/src/utils"

# Set the default entry point or command if needed
ENTRYPOINT [""]
