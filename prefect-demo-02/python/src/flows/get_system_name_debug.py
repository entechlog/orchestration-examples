from prefect import flow
import socket
import time


@flow(log_prints=True)
def get_system_name(loop_counter: int = 0, delay_counter: int = 0):
    """
    Flow to log the system's hostname in a loop with delay.
    """
    # Loop as many times as specified by loop_counter
    for i in range(loop_counter + 1):  # Run at least once if loop_counter is 0
        # Get the system hostname
        system_name = socket.gethostname()

        # Print the message with the system name and loop iteration
        print(f"Iteration {i + 1}: Hello from {system_name}!!")

        # Sleep for the specified delay (in seconds)
        if delay_counter > 0 and i < loop_counter:  # Avoid sleeping after the last iteration
            print(f"Sleeping for {delay_counter} seconds...")
            time.sleep(delay_counter)


if __name__ == "__main__":
    get_system_name()
