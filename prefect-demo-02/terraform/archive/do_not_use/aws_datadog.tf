variable "datadog_api_key" {
  type    = string
  default = ""
}

# Store the Datadog API key in AWS Secrets Manager for Prefect
resource "aws_secretsmanager_secret" "prefect_datadog_api_key" {
  name                    = "prefect-datadog-api-key"
  description             = "Datadog API Key for Prefect integration"
  recovery_window_in_days = 0
}

# Set the secret value for the Datadog API key
resource "aws_secretsmanager_secret_version" "prefect_datadog_api_key_version" {
  secret_id     = aws_secretsmanager_secret.prefect_datadog_api_key.id
  secret_string = var.datadog_api_key
}

# IAM policy to allow Prefect to read the Datadog API key from Secrets Manager
data "aws_iam_policy_document" "prefect_read_datadog_api_key" {
  statement {
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "secretsmanager:GetSecretValue",
      "ssm:GetParameters"
    ]
    resources = [
      aws_secretsmanager_secret.prefect_datadog_api_key.arn
    ]
  }
}

# Attach IAM policy to the Prefect task execution role for reading the Datadog API key
resource "aws_iam_role_policy" "prefect_read_datadog_api_key" {
  name   = "prefect-read-datadog-api-key"
  role   = module.prefect_ecs_cluster.prefect_worker_execution_role_name
  policy = data.aws_iam_policy_document.prefect_read_datadog_api_key.json
}
