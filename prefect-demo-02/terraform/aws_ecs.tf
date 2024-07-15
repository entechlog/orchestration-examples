module "prefect_ecs_cluster" {
  source = "./modules/aws/ecs"

  worker_subnets        = module.prefect_vpc.private_subnet_id
  name                  = "${local.resource_name_prefix}-ecs"
  prefect_account_id    = var.prefect_account_id
  prefect_api_key       = var.prefect_api_key
  prefect_workspace_id  = prefect_workspace.dev.id
  worker_work_pool_name = "${local.resource_name_prefix}-ecs"
  vpc_id                = module.prefect_vpc.vpc_id
}