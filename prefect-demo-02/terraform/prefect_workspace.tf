resource "prefect_workspace" "dev" {
  name   = "${var.env_code} environment"
  handle = var.env_code
}