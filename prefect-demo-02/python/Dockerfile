# Base image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements.txt from the flows directory to the container
COPY flows/requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code from the python directory
COPY . .

ENTRYPOINT [""]
