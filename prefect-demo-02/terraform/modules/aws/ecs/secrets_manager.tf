resource "aws_secretsmanager_secret" "prefect_api_key" {
  name                    = "prefect-api-key-${var.name}"
  recovery_window_in_days = var.secrets_manager_recovery_in_days

  # lifecycle {
  #   prevent_destroy = true
  # }

}

resource "aws_secretsmanager_secret_version" "prefect_api_key_version" {
  secret_id     = aws_secretsmanager_secret.prefect_api_key.id
  secret_string = var.prefect_api_key

  # lifecycle {
  #   prevent_destroy = true
  # }

}
