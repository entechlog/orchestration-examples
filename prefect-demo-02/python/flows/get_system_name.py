from prefect import flow, get_run_logger
import socket

@flow(name="system-get-name", log_prints=True)
def get_system_name():
    """
    Flow to log the system's hostname.
    """
    # Get the system hostname
    system_name = socket.gethostname()

    # Initialize logger
    logger = get_run_logger()

    # Log the message with the system name
    logger.info(f"Hello from {system_name}!!")

if __name__ == "__main__":
    get_system_name()
