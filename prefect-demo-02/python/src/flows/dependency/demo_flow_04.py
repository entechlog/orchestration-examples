from prefect import flow, task
import time

@task
def print_hello():
    time.sleep(60)
    print("Hello from Flow 4")

@flow(name="demo-flow-04", log_prints=True)
def flow_4():
    print_hello()

if __name__ == "__main__":
    flow_4()
