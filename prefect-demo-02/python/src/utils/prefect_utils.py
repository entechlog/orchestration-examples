from prefect.runtime import flow_run, task_run
from datetime import datetime, timezone


def generate_flow_run_name():
    """
    Generates a unique flow run name based on the command and parameters.
    """
    flow_name = flow_run.flow_name
    parameters = flow_run.parameters
    command = parameters["command"]
    extra_command_args = parameters["extra_command_args"]

    timestamp = datetime.now(timezone.utc)

    # Generate the flow run name with command and timestamp
    return f"{command} {' '.join(extra_command_args)} {timestamp.strftime('%Y-%m-%d-%H:%M:%S')}"


def generate_task_run_name(base_task_name: str, date: str):
    """
    Generates a task run name by appending the given date to the base task name.
    """
    return f"{base_task_name}_{date.replace('-', '')}"
