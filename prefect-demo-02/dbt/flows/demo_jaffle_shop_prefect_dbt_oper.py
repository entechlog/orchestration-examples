from prefect import flow, task, get_run_logger
from prefect_dbt.cli import DbtCoreOperation
from utils.dbt_utils import set_dbt_env_variables
from typing import Optional
import os

@task(retries=3, retry_delay_seconds=300)
def execute_dbt_seed():
    logger = get_run_logger()
    logger.info("Executing dbt seed.")

    # Execute dbt seed command
    dbt_seed = DbtCoreOperation(
        commands=["dbt seed"],
        project_dir=os.environ['DBT_PROJECT_DIR'],
        profiles_dir=os.environ["DBT_PROFILES_DIR"]
    )
    dbt_seed.run()

    logger.info("dbt seed completed successfully.")

@task(retries=3, retry_delay_seconds=300)
def execute_dbt_run():
    logger = get_run_logger()
    logger.info("Executing dbt run.")

    # Execute dbt run command
    dbt_run = DbtCoreOperation(
        commands=["dbt run"],
        project_dir=os.environ['DBT_PROJECT_DIR'],
        profiles_dir=os.environ["DBT_PROFILES_DIR"]
    )
    dbt_run.run()

    logger.info("dbt run completed successfully.")

@task(retries=3, retry_delay_seconds=300)
def execute_dbt_test():
    logger = get_run_logger()
    logger.info("Executing dbt test.")

    # Execute dbt test command
    dbt_test = DbtCoreOperation(
        commands=["dbt test"],
        project_dir=os.environ['DBT_PROJECT_DIR'],
        profiles_dir=os.environ["DBT_PROFILES_DIR"]
    )
    dbt_test.run()

    logger.info("dbt test completed successfully.")

@flow(name="demo-jaffle-shop-prefect-dbt", log_prints=True)
def run_jaffle_shop(batch_cycle_date: Optional[str] = None, 
                    backfill_start_date: Optional[str] = None, 
                    backfill_end_date: Optional[str] = None):
    
    logger = get_run_logger()

    # Set environment variables using the utility function
    set_dbt_env_variables()

    logger.info("Starting dbt operations.")

    # Execute dbt seed
    dbt_seed_result = execute_dbt_seed()

    # Execute dbt run, waiting for dbt seed to complete
    dbt_run_result = execute_dbt_run(wait_for=[dbt_seed_result])

    # Execute dbt test, waiting for dbt run to complete
    execute_dbt_test(wait_for=[dbt_run_result])

    logger.info("All dbt operations completed successfully.")

if __name__ == "__main__":
    run_jaffle_shop()
