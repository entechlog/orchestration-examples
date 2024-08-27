resource "prefect_work_pool" "local-dkr-01" {
  name         = "local-dkr-01"
  type         = "docker"
  workspace_id = prefect_workspace.dev.id
}