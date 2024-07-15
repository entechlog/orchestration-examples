terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
    prefect = {
      source = "prefecthq/prefect"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = "terraform"
}

provider "prefect" {
  account_id = var.prefect_account_id
  api_key    = var.prefect_api_key
}