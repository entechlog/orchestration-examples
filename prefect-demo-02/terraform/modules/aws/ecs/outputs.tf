output "prefect_worker_service_id" {
  value = aws_ecs_service.prefect_worker_service.id
}

output "prefect_worker_execution_role_arn" {
  value = aws_iam_role.prefect_worker_execution_role.arn
}

output "prefect_worker_execution_role_id" {
  value = aws_iam_role.prefect_worker_execution_role.id
}

output "prefect_worker_execution_role_name" {
  value = aws_iam_role.prefect_worker_execution_role.name
}

output "prefect_worker_task_role_arn" {
  value = var.worker_task_role_arn == null ? aws_iam_role.prefect_worker_task_role[0].arn : var.worker_task_role_arn
}

output "prefect_worker_security_group" {
  value = aws_security_group.prefect_worker.id
}

output "prefect_worker_cluster_name" {
  value = aws_ecs_cluster.prefect_worker_cluster.name
}

output "prefect_worker_cluster_arn" {
  value = aws_ecs_cluster.prefect_worker_cluster.arn
}

output "datadog_api_key_arn" {
  value       = var.enable_datadog ? aws_secretsmanager_secret.prefect_datadog_api_key[0].arn : null
  description = "The ARN of the Datadog API key secret"
}
