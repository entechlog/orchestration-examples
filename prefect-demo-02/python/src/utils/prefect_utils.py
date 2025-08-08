from prefect import get_client
from prefect.utilities.asyncutils import sync_compatible
from loguru import logger
from prefect.runtime import flow_run
from datetime import datetime, timezone
from typing import List, Dict

# Helper functions for API requests

@sync_compatible
async def get(route):
    """GET any route with the orchestration client"""
    async with get_client() as client:
        response = await client._client.get(url=route)
    logger.info(f"GET request to {route} returned status: {response.status_code}")
    return response.json()


@sync_compatible
async def post(route, payload=None):
    """POST any route with the orchestration client"""
    async with get_client() as client:
        response = await client._client.post(url=route, json=payload)
    logger.info(f"POST request to {route} with payload: {payload} returned status: {response.status_code}")
    return response.json()


@sync_compatible
async def put(route, payload=None):
    """PUT any route with the orchestration client"""
    async with get_client() as client:
        response = await client._client.put(url=route, json=payload)
    logger.info(f"PUT request to {route} with payload: {payload} returned status: {response.status_code}")
    return response


# Function to generate a flow run name

def generate_flow_run_name():
    """
    Generates a generic, descriptive flow run name in kebab-case.
    Works for all flows:
      - flow name
      - command (if provided)
      - extra args (if provided)
      - boolean flags as key-value pairs
      - UTC timestamp
    """
    flow_name = flow_run.flow_name.replace("_", "-")
    parameters = flow_run.parameters

    command = str(parameters.get("command", "")).strip().replace("_", "-")
    extra_args = [str(arg).replace("_", "-") for arg in parameters.get("extra_command_args", [])]

    # Append boolean flags in a standard format
    # flags = [f"{key}-{value}" for key, value in parameters.items() if isinstance(value, bool)]

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")

    parts = [flow_name, command] + extra_args + [timestamp]
    return "-".join(p for p in parts if p)

# Function to generate a task run name

def generate_task_run_name(base_task_name: str, date: str):
    """
    Generates a task run name by appending the given date to the base task name.
    """
    return f"{base_task_name}_{date.replace('-', '')}"

# Function to fetch the last deployment runs with deployment name

def fetch_last_runs(since_time: datetime, tag_filter: str = None) -> List[Dict]:
    """
    Fetch deployment runs from the Prefect API based on the provided time range and optional tag filter.
    :param since_time: The datetime to filter runs starting from.
    :param tag_filter: Optional tag to filter the runs.
    :return: A list of dictionaries containing deployment run details.
    """
    logger.info(f"Fetching runs since {since_time} with tag filter: {tag_filter}")

    # Correctly format the 'since_time' without microseconds
    formatted_since_time = since_time.replace(microsecond=0).isoformat() + "Z"  # UTC timezone

    # Prefect API URL for flow runs filtering
    prefect_api_url = "/flow_runs/filter"

    # Set up request payload with filters
    payload = {
        "sort": "START_TIME_DESC",  # Sort by most recent runs
        "flow_runs": {
            "start_time": {
                "after_": formatted_since_time  # Fetch runs after the given time
            }
        },
        "limit": 100  # Adjust the limit as needed
    }

    if tag_filter:
        # Add tag filter if specified
        payload["flow_runs"]["tags"] = {"all_": [tag_filter]}  # Use 'all_' for an exact match

    try:
        # Make the POST request using Prefect client
        runs = post(prefect_api_url, payload)

        deployment_runs = []

        # Check if runs is a list or dict and process accordingly
        runs_data = runs.get("data") if isinstance(runs, dict) else runs

        # Loop through flow run results
        for run in runs_data:
            flow_run_name = run.get("name", "Unknown Flow Run")
            deployment_id = run.get("deployment_id")

            # Fetch deployment details if deployment_id exists
            deployment_name = "Unknown Deployment"
            if deployment_id:
                deployment_details = get(f"/deployments/{deployment_id}")
                deployment_name = deployment_details.get("name", "Unknown Deployment")

            last_run_time = run.get("start_time", "Unknown Time")
            status = run.get("state", {}).get("name", "Unknown Status")
            work_pool_name = run.get("work_pool_name", "Unknown Work Pool")
            total_run_time = run.get("total_run_time", "Unknown Duration")

            deployment_runs.append({
                "flow_run_name": flow_run_name,
                "deployment_name": deployment_name,
                "last_run_time": last_run_time,
                "status": status,
                "work_pool_name": work_pool_name,
                "total_run_time": total_run_time
            })

        logger.info(f"Fetched {len(deployment_runs)} runs.")
        return deployment_runs

    except Exception as e:
        logger.error(f"Error fetching deployment runs: {e}")
        raise
