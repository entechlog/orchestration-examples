from prefect import flow, task, get_run_logger
from prefect_shell import shell_run_command
from utils.dbt_utils import set_dbt_env_variables
from typing import Optional

@task(retries=3, retry_delay_seconds=300)
def run_dbt_seed():
    logger = get_run_logger()
    logger.info("Running dbt seed.")
    result = shell_run_command("dbt seed")
    logger.info("dbt seed completed successfully.")
    return result

@task(retries=3, retry_delay_seconds=300)
def run_dbt_run():
    logger = get_run_logger()
    logger.info("Running dbt run.")
    result = shell_run_command("dbt run")
    logger.info("dbt run completed successfully.")
    return result

@task(retries=3, retry_delay_seconds=300)
def run_dbt_test():
    logger = get_run_logger()
    logger.info("Running dbt test.")
    result = shell_run_command("dbt test")
    logger.info("dbt test completed successfully.")
    return result

@flow(name="demo-jaffle-shop-shell", log_prints=True)
def run_jaffle_shop(batch_cycle_date: Optional[str] = None, 
                    backfill_start_date: Optional[str] = None, 
                    backfill_end_date: Optional[str] = None):
    logger = get_run_logger()

    # Set environment variables using the utility function
    set_dbt_env_variables()

    logger.info("Starting dbt operations.")

    # Execute dbt seed
    dbt_seed_result = run_dbt_seed()

    # Execute dbt run, waiting for dbt seed to complete
    dbt_run_result = run_dbt_run(wait_for=[dbt_seed_result])

    # Execute dbt test, waiting for dbt run to complete
    run_dbt_test(wait_for=[dbt_run_result])

    logger.info("All dbt operations completed successfully.")

if __name__ == "__main__":
    run_jaffle_shop()
