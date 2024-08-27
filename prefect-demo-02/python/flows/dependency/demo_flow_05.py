from prefect import flow, task

@task
def print_hello():
    print("Hello from Flow 5")

@flow(name="demo-flow-05", log_prints=True)
def flow_5():
    print_hello()

if __name__ == "__main__":
    flow_5()
