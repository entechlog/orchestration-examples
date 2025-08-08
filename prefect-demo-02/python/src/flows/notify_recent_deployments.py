import argparse
from prefect import flow, task
from prefect.artifacts import create_markdown_artifact
from loguru import logger
from datetime import datetime, timedelta
from prefect_utils import fetch_last_runs

# Task to fetch recent runs
@task
def get_recent_runs(hours: int, tag_filter: str = None):
    since_time = datetime.utcnow() - timedelta(hours=hours)
    return fetch_last_runs(since_time, tag_filter)

# Task to filter out runs with 'Unknown Deployment' based on a flag
@task
def filter_runs(runs, exclude_unknown_deployment: bool):
    if exclude_unknown_deployment:
        filtered_runs = [run for run in runs if run['deployment_name'] != 'Unknown Deployment']
    else:
        filtered_runs = runs
    return filtered_runs

# Task to format the message as a markdown table
@task
def format_message(runs):
    if not runs:
        return "No deployments found in the given time frame."

    markdown_body = (
        "| Deployment Name | Flow Run Name | Last Run | Status | Work Pool Name | Total Run Time (seconds) |\n"
        "|-----------------|---------------|----------|--------|----------------|--------------------------|\n"
    )

    for run in runs:
        # Ensure total_run_time is formatted as seconds
        total_run_time = run['total_run_time']
        if isinstance(total_run_time, (int, float)):
            total_run_time_str = f"{total_run_time:.2f}"
        else:
            total_run_time_str = total_run_time  # Keep as is if not a number

        markdown_body += (
            f"| {run['deployment_name']} | {run['flow_run_name']} | {run['last_run_time']} | "
            f"{run['status']} | {run['work_pool_name']} | {total_run_time_str} |\n"
        )

    return markdown_body

# Task to create the markdown artifact
@task
def create_deployment_summary_artifact(markdown_body: str):
    # Create the markdown artifact
    artifact_id = create_markdown_artifact(markdown_body)

    # Log the artifact creation
    logger.info(f"Markdown artifact created with ID: {artifact_id}")

    return artifact_id

# Main flow
@flow
def notify_deployment_runs(hours: int, tag_filter: str = None, exclude_unknown_deployment: bool = True):
    # Get recent runs based on hours and optional tag filter
    recent_runs = get_recent_runs(hours=hours, tag_filter=tag_filter)

    # Filter out runs with 'Unknown Deployment' based on the flag
    filtered_runs = filter_runs(recent_runs, exclude_unknown_deployment=exclude_unknown_deployment)

    # Format the message as markdown
    markdown_body = format_message(filtered_runs)

    # Create the artifact
    artifact_id = create_deployment_summary_artifact(markdown_body)

    # Log the artifact creation using loguru
    logger.info(f"Artifact created successfully with ID: {artifact_id}")

if __name__ == "__main__":
    # Argument parser to get the parameters from the command line
    parser = argparse.ArgumentParser(
        description="Run the deployment run notifier flow with runtime parameters."
    )
    parser.add_argument(
        "--hours",
        type=int,
        required=True,
        help="Look for deployment runs in the last N hours."
    )
    parser.add_argument(
        "--tag_filter",
        type=str,
        required=False,
        help="Optional tag filter to limit the runs to a specific tag."
    )
    parser.add_argument(
        "--exclude_unknown_deployment",
        type=bool,
        default=True,
        nargs='?',
        const=True,
        help="Exclude runs with 'Unknown Deployment' (default: True). Set to False to include them."
    )

    args = parser.parse_args()

    # Run the flow with parsed arguments
    notify_deployment_runs(
        hours=args.hours,
        tag_filter=args.tag_filter,
        exclude_unknown_deployment=args.exclude_unknown_deployment
    )
