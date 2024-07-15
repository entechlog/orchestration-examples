from prefect import flow, get_run_logger
import socket

@flow
def get_system_name():
    # Get the system hostname
    system_name = socket.gethostname()

    logger = get_run_logger()
    # Log the message with the system name
    logger.info(f"Hello from {system_name} !!")

if __name__ == "__main__":
    get_system_name()