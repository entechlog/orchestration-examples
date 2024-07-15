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

# ECS

output "prefect_worker_service_id" {
  value = module.prefect_ecs_cluster.prefect_worker_service_id
}

output "prefect_worker_execution_role_arn" {
  value = module.prefect_ecs_cluster.prefect_worker_execution_role_arn
}

output "prefect_worker_task_role_arn" {
  value = module.prefect_ecs_cluster.prefect_worker_task_role_arn
}

output "prefect_worker_security_group" {
  value = module.prefect_ecs_cluster.prefect_worker_security_group
}

output "prefect_worker_cluster_name" {
  value = module.prefect_ecs_cluster.prefect_worker_cluster_name
}

output "prefect_worker_cluster_arn" {
  value = module.prefect_ecs_cluster.prefect_worker_cluster_arn
}