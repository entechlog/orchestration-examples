resource "aws_cloudwatch_log_group" "prefect_worker_log_group" {
  name              = "/aws/prefect/worker-log-group-${var.name}"
  retention_in_days = var.worker_log_retention_in_days
}