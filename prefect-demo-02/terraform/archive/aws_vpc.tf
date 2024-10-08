module "prefect_vpc" {
  source                    = "github.com/entechlog/aws-examples/aws-modules/network"
  env_code                  = var.env_code
  project_code              = var.project_code
  aws_region                = var.aws_region
  availability_zone         = data.aws_availability_zones.available.names
  vpc_cidr_block            = var.vpc_cidr_block
  private_subnet_cidr_block = var.private_subnet_cidr_block
  public_subnet_cidr_block  = var.public_subnet_cidr_block
  remote_cidr_block         = var.remote_cidr_block
}