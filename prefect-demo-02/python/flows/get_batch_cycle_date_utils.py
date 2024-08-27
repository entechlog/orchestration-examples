from prefect import flow
from utils.batch_cycle import get_batch_cycle_date, get_backfill_dates
from typing import Optional

@flow(name="get-batch-cycle-date-utils", log_prints=True)
def get_batch_cycle_date_utils(batch_cycle_date: Optional[str] = None, 
                                        backfill_start_date: Optional[str] = None, 
                                        backfill_end_date: Optional[str] = None):
    
    # Determine flow logic based on whether backfill is used
    if backfill_start_date and backfill_end_date:
        dates = get_backfill_dates(backfill_start_date, backfill_end_date)
        for date in dates:
            print(f"Running batch for date: {date.isoformat()}")
    else:
        date = get_batch_cycle_date(batch_cycle_date)
        print(f"Running batch for date: {date.isoformat()}")

if __name__ == "__main__":
    get_batch_cycle_date_utils()
