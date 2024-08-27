resource "prefect_work_pool" "aws_ecs_01" {
  name         = "aws-ecs-01"
  type         = "ecs"
  workspace_id = prefect_workspace.dev.id
  paused       = false
  base_job_template = templatefile("./config/base_job_template.config", {
    cpu                = 512,
    memory             = 1024,
    image              = "prefecthq/prefect:2-python3.10"
    vpc_id             = module.prefect_vpc.vpc_id,
    task_role_arn      = module.prefect_ecs_cluster.prefect_worker_task_role_arn,
    execution_role_arn = module.prefect_ecs_cluster.prefect_worker_execution_role_arn,
    cluster            = module.prefect_ecs_cluster.prefect_worker_cluster_name,
    network_configuration = jsonencode({
      "subnets" : module.prefect_vpc.private_subnet_id,
      "securityGroups" : [module.prefect_ecs_cluster.prefect_worker_security_group],
      "assignPublicIp" : "DISABLED"
    }),
    prefect_aws_credentials_block = prefect_block.aws_credentials_prefect.id
  })
}
