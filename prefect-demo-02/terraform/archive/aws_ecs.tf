module "prefect_ecs_cluster" {
  source = "./modules/aws/ecs"

  worker_subnets        = module.prefect_vpc.private_subnet_id
  name                  = "ecs-01"
  prefect_account_id    = var.prefect_account_id
  prefect_api_key       = var.prefect_api_key
  prefect_workspace_id  = prefect_workspace.dev.id
  worker_work_pool_name = "aws-ecs-01"
  vpc_id                = module.prefect_vpc.vpc_id
}

# ECS Output

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