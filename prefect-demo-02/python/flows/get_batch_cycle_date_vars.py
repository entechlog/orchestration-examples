from prefect import flow, task
from prefect.variables import Variable
from datetime import datetime, timedelta
from typing import Optional, List

@task
def print_date(date: datetime):
    print(f"Batch Cycle Date: {date.isoformat()}")

@flow(name="get-batch-cycle-date-vars", log_prints=True)
def get_batch_cycle_date_vars(batch_cycle_date: Optional[str] = None, 
                          backfill_start_date: Optional[str] = None, 
                          backfill_end_date: Optional[str] = None):
    
    if not batch_cycle_date:
        # Retrieve the batch_cycle_date from Prefect variables
        batch_cycle_date = Variable.get("batch_cycle_date").value
    
    # Convert the batch_cycle_date string to a datetime object
    batch_cycle_date = datetime.strptime(batch_cycle_date, "%Y-%m-%d")
    
    if backfill_start_date and backfill_end_date:
        # If backfill dates are provided, run in backfill mode
        start_date = datetime.strptime(backfill_start_date, "%Y-%m-%d")
        end_date = datetime.strptime(backfill_end_date, "%Y-%m-%d")
        current_date = start_date

        while current_date <= end_date:
            print_date(current_date)
            current_date += timedelta(days=1)
    else:
        # Regular run
        print_date(batch_cycle_date)

if __name__ == "__main__":
    get_batch_cycle_date_vars()
