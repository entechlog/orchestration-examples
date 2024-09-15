from prefect import flow, task, get_run_logger
from prefect.variables import Variable
from datetime import datetime, timedelta
from typing import Optional, List


@task(log_prints=True)
def process_data(date: datetime):
    """
    Dummy task to simulate processing for a given date.
    """
    logger = get_run_logger()
    formatted_date = date.strftime("%Y-%m-%d")
    logger.info(f"Processing data for Batch Cycle Date: {formatted_date}")


@flow(name="get-batch-cycle-date-vars", log_prints=True)
def get_batch_cycle_date_vars(
    batch_cycle_date: Optional[str] = None,
    backfill_start_date: Optional[str] = None,
    backfill_end_date: Optional[str] = None,
):
    """
    Flow to handle batch cycle date processing, optionally in backfill mode.
    """

    # Initiate logger
    logger = get_run_logger()

    # Handle batch_cycle_date
    if not batch_cycle_date:
        # Retrieve the batch_cycle_date from Prefect variables
        batch_cycle_date = Variable.get("batch_cycle_date").value
        logger.info(
            f"Retrieved batch_cycle_date from Prefect variables: {batch_cycle_date}"
        )

    # Convert the batch_cycle_date string to a datetime object
    batch_cycle_date = datetime.strptime(batch_cycle_date, "%Y-%m-%d")

    if backfill_start_date and backfill_end_date:
        # If backfill dates are provided, run in backfill mode
        logger.info(
            f"Running in backfill mode from {backfill_start_date} to {backfill_end_date}."
        )
        start_date = datetime.strptime(backfill_start_date, "%Y-%m-%d")
        end_date = datetime.strptime(backfill_end_date, "%Y-%m-%d")
        current_date = start_date

        while current_date <= end_date:
            process_data(current_date)
            current_date += timedelta(days=1)
    else:
        # Regular run with the provided or retrieved batch_cycle_date
        process_data(batch_cycle_date)


if __name__ == "__main__":
    get_batch_cycle_date_vars()
