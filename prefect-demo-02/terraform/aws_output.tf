# Network

output "prefect_vpc_vpc_id" {
  value = module.prefect_vpc.vpc_id
}

output "prefect_vpc_private_subnets" {
  value = module.prefect_vpc.private_subnet_id
}

output "prefect_vpc_public_subnets" {
  value = module.prefect_vpc.public_subnet_id
}

output "prefect_vpc_ssh_security_group_id" {
  value = module.prefect_vpc.ssh_security_group_id
}