resource "prefect_block" "aws_dat_prefect" {
  name      = "aws-dat-prefect"
  type_slug = "aws-credentials"

  data = jsonencode({
    "region_name" = "us-east-1"
  })

  workspace_id = prefect_workspace.dev.id
}