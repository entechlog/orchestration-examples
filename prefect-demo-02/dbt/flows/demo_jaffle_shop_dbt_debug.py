from prefect import flow, task, get_run_logger
from prefect_dbt.cli import DbtCoreOperation
from utils.dbt_utils import set_dbt_env_variables
from typing import Optional
import os

@task(retries=3, retry_delay_seconds=300)
def should_continue_loop(current_iteration: int, loop_counter: int) -> bool:
    return current_iteration < loop_counter

@task(retries=3, retry_delay_seconds=300)
def execute_dbt_debug():
    dbt_debug = DbtCoreOperation(
        commands=["dbt debug"],
        project_dir=os.environ['DBT_PROJECT_DIR'],
        profiles_dir=os.environ["DBT_PROFILES_DIR"]
    )
    dbt_debug.run()

@flow(name="demo-jaffle-shop-dbt-debug", log_prints=True)
def run_jaffle_shop(batch_cycle_date: Optional[str] = None, 
                    backfill_start_date: Optional[str] = None, 
                    backfill_end_date: Optional[str] = None,
                    loop_counter: int = 1):
    # Set environment variables
    set_dbt_env_variables()

    logger = get_run_logger()
    current_iteration = 0

    while True:
        # Check the loop condition
        continue_loop = should_continue_loop(current_iteration, loop_counter)

        if not continue_loop:
            break

        # Log the current iteration
        logger.info(f"Executing dbt debug, iteration {current_iteration + 1}/{loop_counter}")

        # Execute dbt debug
        execute_dbt_debug()

        # Increment the iteration counter
        current_iteration += 1

    # Log completion
    logger.info(f"Completed {current_iteration} iterations of dbt debug")

if __name__ == "__main__":
    run_jaffle_shop()
