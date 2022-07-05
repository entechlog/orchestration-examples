# Input variables

variable "aws_region" {
  type        = string
  description = "AWS region where resources will be deployed."
}

variable "mwaa_name" {
  type        = string
  description = "name for your mwaa instance"
}

variable "vpc_cidr" {
  type        = string
  description = "VPC CIDR block."
}

variable "public_subnet_cidrs" {
  type        = list(string)
  description = "Public subnets' CIDR blocks."
}

variable "private_subnet_cidrs" {
  type        = list(string)
  description = "Private subnets' CIDR blocks."
}

variable "mwaa_max_workers" {
  type        = number
  description = "Maximum number of MWAA workers."
  default     = 2
}

variable "client_vpn_cidr_block" {
  type        = string
  description = "Client CIDR block for MWAA client VPN."
}

variable "vpn_acm_validity_period_in_days" {
  type        = number
  description = "Amount of days after which TLS certificates used for MWAA client VPN should expire."
  default     = 1095 # 3 years
}

variable "mwaa_webserver_access_mode" {
  type        = string
  description = "Airflow web server access mode"
  default     = "PRIVATE_ONLY"
}
