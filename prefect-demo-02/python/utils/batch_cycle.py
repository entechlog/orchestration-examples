from prefect import task
from prefect.variables import Variable
from datetime import datetime, timedelta
from typing import Optional, List

@task
def get_batch_cycle_date(batch_cycle_date: Optional[str] = None) -> datetime:
    """
    Retrieves the batch cycle date from Prefect variables if not provided.
    Converts the date string to a datetime object.
    """
    if not batch_cycle_date:
        # Retrieve the batch_cycle_date from Prefect variables
        batch_cycle_date = Variable.get("batch_cycle_date").value
    return datetime.strptime(batch_cycle_date, "%Y-%m-%d")

@task
def get_backfill_dates(start_date: str, end_date: str) -> List[datetime]:
    """
    Generates a list of dates between start_date and end_date for backfill.
    """
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    
    return dates
