resource "prefect_block" "aws_credentials_prefect" {
  name      = "aws-credentials-prefect"
  type_slug = "aws-credentials"

  data = jsonencode({
    "region_name" = "us-east-1"
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