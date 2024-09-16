from prefect import flow

from demo_flow_01 import flow_1
from demo_flow_02 import flow_2
from demo_flow_03 import flow_3
from demo_flow_04 import flow_4
from demo_flow_05 import flow_5

@flow(name="demo-master-run-all", log_prints=True)
def run_all_flows():
    flow_1()
    flow_2()
    flow_3()
    flow_4()
    
    # Ensure Flow 5 runs only after Flows 1 to 4 have completed
    flow_5()
    
    print("All flows completed!")

if __name__ == "__main__":
    run_all_flows()
