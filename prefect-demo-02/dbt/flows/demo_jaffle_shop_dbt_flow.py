from prefect import flow, get_run_logger
from prefect_dbt_flow import dbt_flow
from prefect_dbt_flow.dbt import DbtDagOptions, DbtProfile, DbtProject
from utils.dbt_utils import set_dbt_env_variables
from typing import Optional
import os

@flow(name="demo-jaffle-shop-dbt-flow", log_prints=True)
def run_jaffle_shop(batch_cycle_date: Optional[str] = None, 
                    backfill_start_date: Optional[str] = None, 
                    backfill_end_date: Optional[str] = None):
    
    logger = get_run_logger()

    # Set environment variables using the utility task
    set_dbt_env_variables()

    # Log the start of the dbt flow
    logger.info("Starting the dbt flow execution.")

    # Define the dbt flow within the flow
    my_dbt_flow = dbt_flow(
        project=DbtProject(
            name="example_jaffle_shop",
            project_dir=os.environ["DBT_PROJECT_DIR"],  # Use environment variable
            profiles_dir=os.environ["DBT_PROFILES_DIR"]  # Use environment variable
        ),
        profile=DbtProfile(
            target=os.environ["ENV_CODE"],  # Use environment variable
        ),
        dag_options=DbtDagOptions(
            run_test_after_model=True,
        ),
    )

    # Run the dbt flow
    my_dbt_flow()

    # Log completion of the flow
    logger.info("dbt flow execution completed.")

if __name__ == "__main__":
    run_jaffle_shop()
