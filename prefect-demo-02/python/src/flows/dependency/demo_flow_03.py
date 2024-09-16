from prefect import flow, task

@task
def print_hello():
    print("Hello from Flow 3")

@flow(name="demo-flow-03", log_prints=True)
def flow_3():
    print_hello()

if __name__ == "__main__":
    flow_3()
