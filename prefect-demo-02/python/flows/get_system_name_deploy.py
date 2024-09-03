from prefect import flow, task
import socket

@task
def get_system_name_task():
    """
    Task to get the system's hostname.
    """
    return socket.gethostname()

@flow(log_prints=True)
def get_system_name():
    """
    Flow to log the system's hostname.
    """
    # Get the system hostname
    system_name = get_system_name_task()

    # Print the message with the system name
    print(f"Hello from {system_name}!!")

if __name__ == "__main__":
    get_system_name.serve(name="get-system-name-task-dkr")
