from prefect import flow, task, get_run_logger
from prefect.variables import Variable
from datetime import datetime, timedelta

@task(retries=3, retry_delay_seconds=10, log_prints=True)
def set_batch_cycle_date():
    """
    Task to set the batch cycle date to the previous day's date (UTC).
    """
    logger = get_run_logger()
    batch_cycle_date = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
    Variable.set(name="batch_cycle_date", value=batch_cycle_date, overwrite=True)
    logger.info(f"Set batch_cycle_date to {batch_cycle_date}")

@task(retries=3, retry_delay_seconds=10, log_prints=True)
def set_todays_date():
    """
    Task to set today's date (UTC).
    """
    logger = get_run_logger()
    todays_date = datetime.utcnow().strftime('%Y-%m-%d')
    Variable.set(name="todays_date", value=todays_date, overwrite=True)
    logger.info(f"Set todays_date to {todays_date}")

@flow(name="set_batch_cycle_date_flow", log_prints=True)
def set_batch_cycle_date_flow():
    """
    Flow to set both the batch cycle date and today's date as Prefect variables.
    """
    set_batch_cycle_date()
    set_todays_date()

if __name__ == "__main__":
    set_batch_cycle_date_flow()
