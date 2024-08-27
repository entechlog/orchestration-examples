resource "docker_container" "prefect_worker" {
  image = "prefecthq/prefect:2-python3.9"
  name  = "prefect-worker" # This is the Docker container name, can be anything

  command = [
    "sh", "-c",
    "pip install -U prefect-docker && prefect worker start --pool local-dkr-01 --type docker"
  ]

  env = [
    "PREFECT_API_KEY=${var.prefect_api_key}",
    "PREFECT_API_URL=https://api.prefect.cloud/api/accounts/${var.prefect_account_id}/workspaces/${prefect_workspace.dev.id}"
  ]

  volumes {
    host_path      = "/var/run/docker.sock"
    container_path = "/var/run/docker.sock"
  }
}
