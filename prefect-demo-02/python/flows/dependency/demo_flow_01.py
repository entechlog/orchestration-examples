from prefect import flow, task
import time

@task
def print_hello():
    time.sleep(30)
    print("Hello from Flow 1")

@flow(name="demo-flow-01", log_prints=True)
def flow_1():
    print_hello()

if __name__ == "__main__":
    flow_1()
