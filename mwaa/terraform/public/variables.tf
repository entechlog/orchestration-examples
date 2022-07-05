# MWAA input variables

variable "aws_region" {
  type        = string
  description = "AWS region where resources will be deployed."
  default     = "us-east-1"
}

variable "env_code" {
  type        = string
  description = "Environment code to identify the target environment(dev,stg,prd)"
  default     = "dev"
}

variable "project_code" {
  type        = string
  description = "Project code which will be used as prefix when naming resources"
  default     = "entechlog"
}

variable "vpc_cidr" {
  type        = string
  description = "VPC CIDR block"
  default     = "172.32.0.0/16"
}

variable "public_subnet_cidrs" {
  type        = list(string)
  description = "Public subnet CIDR blocks"
  default     = ["172.32.12.0/22"]
}

variable "private_subnet_cidrs" {
  type        = list(string)
  description = "Private subnet CIDR blocks"
  default     = ["172.32.0.0/22", "172.32.4.0/22", "172.32.8.0/22"]
}

variable "mwaa_max_workers" {
  type        = number
  description = "Maximum number of MWAA workers"
  default     = 3
}
