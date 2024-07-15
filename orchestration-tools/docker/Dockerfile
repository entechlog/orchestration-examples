FROM python:3.9-slim-buster

# Install Java
COPY --from=openjdk:8-jre-slim /usr/local/openjdk-8 /usr/local/openjdk-8
ENV JAVA_HOME /usr/local/openjdk-8
RUN update-alternatives --install /usr/bin/java java /usr/local/openjdk-8/bin/java 1

WORKDIR /usr/app

# Install Linux Packages
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    wget \
    git \
    curl \
    sshpass \
    openssh-server \
    sudo \
    nmap \
    gnupg \
    lsb-release \
    alien \
    apt-transport-https \
    python-dev \
    libpq-dev \
    ca-certificates \
    build-essential \
    docker.io \
    unzip && \
    apt-get purge -y --auto-remove && \
    rm -rf /var/lib/apt/lists/*

# Install AWS CLI v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip aws

# Install Python packages
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Terraform
RUN wget -q -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor > /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" > /etc/apt/sources.list.d/hashicorp.list && \
    apt-get update && \
    apt-get install -y terraform && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Prefect and Prefect-Docker
RUN pip install prefect prefect-docker

# Create ubuntu user and add to docker group
RUN useradd -rm -d /home/ubuntu -s /bin/bash -g root -G sudo,docker -u 1001 ubuntu && \
    echo 'ubuntu ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER ubuntu
WORKDIR /home/ubuntu
