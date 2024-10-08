resource "prefect_block" "aws_credentials_prefect" {
  name      = "aws-credentials-prefect"
  type_slug = "aws-credentials"

  data = jsonencode({
    "region_name" = "us-east-1"
  })

  workspace_id = prefect_workspace.dev.id
}

variable "aws_access_key_id" {
  type = string
}

variable "secret_access_key" {
  type = string
}

resource "prefect_block" "aws_credentials" {
  name      = "aws-credentials"
  type_slug = "aws-credentials"

  data = jsonencode({
    "access_key_id"     = var.aws_access_key_id
    "secret_access_key" = var.secret_access_key
    "region_name"       = "us-east-1"
  })

  workspace_id = prefect_workspace.dev.id
}

variable "snowflake_account_dbt" {
  type = string
}

variable "snowflake_user_dbt" {
  type = string
}

variable "snowflake_password_dbt" {
  type      = string
  sensitive = true
}

resource "prefect_block" "snowflake_credentials_dbt" {
  name      = "snowflake-credentials-dbt"
  type_slug = "snowflake-credentials"

  data = jsonencode({
    "account"  = "${var.snowflake_account_dbt}",
    "user"     = "${var.snowflake_user_dbt}",
    "password" = "${var.snowflake_password_dbt}"
  })

  workspace_id = prefect_workspace.dev.id
}

variable "pagerduty_api_key" {
  type        = string
  description = "API Key for PagerDuty integration"
}

variable "pagerduty_integration_key" {
  type        = string
  description = "Integration Key for PagerDuty"
}

resource "prefect_block" "pagerduty_credentials" {
  name      = "pagerduty-credentials"
  type_slug = "pager-duty-webhook"

  data = jsonencode({
    "api_key"         = var.pagerduty_api_key,
    "integration_key" = var.pagerduty_integration_key,
    "source"          = prefect_workspace.dev.name
    "notify_type"     = "failure",
    "region"          = "us",
    "include_image"   = false
  })

  workspace_id = prefect_workspace.dev.id
}
