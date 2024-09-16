variable "prefect_account_id" {
  type        = string
  description = "your Account/Organization ID"
}

variable "prefect_api_key" {
  type        = string
  description = "your prefect API Key"
}

variable "aws_account_id" {
  description = "AWS Account ID"
  type        = string
}

resource "prefect_variable" "aws_account_id" {
  name  = "aws_account_id"
  value = var.aws_account_id

  workspace_id = prefect_workspace.dev.id
}