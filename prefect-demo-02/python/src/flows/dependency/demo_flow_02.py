from prefect import flow, task

@task
def print_hello():
    print("Hello from Flow 2")

@flow(name="demo-flow-02", log_prints=True)
def flow_2():
    print_hello()

if __name__ == "__main__":
    flow_2()
