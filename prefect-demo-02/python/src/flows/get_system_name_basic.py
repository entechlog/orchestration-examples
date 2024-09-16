import socket


def get_system_name():
    """
    Function to log the system's hostname.
    """
    # Get the system hostname
    system_name = socket.gethostname()

    # Print the message with the system name
    print(f"Hello from {system_name}!!")


if __name__ == "__main__":
    get_system_name()
