from prefect import flow, get_run_logger
from utils.date_utils import (
    get_batch_cycle_date,
    get_backfill_dates,
    get_expected_start_date,
)
from typing import Optional, List


@flow(name="get-batch-cycle-date-utils", log_prints=True)
def get_batch_cycle_date_utils(
    batch_cycle_date: Optional[str] = None,
    backfill_start_date: Optional[str] = None,
    backfill_end_date: Optional[str] = None,
):
    """
    Flow to process batch cycle dates or backfill dates.
    """
    # Initiate logger
    logger = get_run_logger()

    # Retrieve the expected start date using the utility function
    expected_start_date = get_expected_start_date()

    # Determine flow logic based on whether backfill is used
    if backfill_start_date and backfill_end_date:
        dates = get_backfill_dates(
            start_date=backfill_start_date, end_date=backfill_end_date
        )
        logger.info(
            f"Running batch for backfill dates from {backfill_start_date} to {backfill_end_date}."
        )
    else:
        dates = [
            get_batch_cycle_date(
                expected_start_date=expected_start_date,
                batch_cycle_date=batch_cycle_date,
            )
        ]
        logger.info(f"Running batch for date: {dates[0]}")

    # Dummy task to process data
    for date in dates:
        process_data(date)


def process_data(date: str):
    """
    Dummy task to simulate data processing for a given date.
    """
    logger = get_run_logger()
    logger.info(f"Processing data for date: {date}")


if __name__ == "__main__":
    get_batch_cycle_date_utils()
