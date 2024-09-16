resource "aws_secretsmanager_secret" "prefect_api_key" {
  name                    = "prefect-api-key-${var.name}"
  recovery_window_in_days = var.secrets_manager_recovery_in_days
}

resource "aws_secretsmanager_secret_version" "prefect_api_key_version" {
  secret_id     = aws_secretsmanager_secret.prefect_api_key.id
  secret_string = var.prefect_api_key
}

resource "aws_secretsmanager_secret" "prefect_datadog_api_key" {
  count = var.enable_datadog ? 1 : 0

  name                    = "prefect-datadog-api-key-${var.name}"
  description             = "Datadog API Key for Prefect integration"
  recovery_window_in_days = var.secrets_manager_recovery_in_days
}

resource "aws_secretsmanager_secret_version" "prefect_datadog_api_key_version" {
  count = var.enable_datadog ? 1 : 0

  secret_id     = aws_secretsmanager_secret.prefect_datadog_api_key[0].id
  secret_string = var.datadog_api_key
}
