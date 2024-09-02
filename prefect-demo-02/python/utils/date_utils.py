from datetime import datetime, timedelta
from typing import Optional, List
from prefect import task, runtime, get_run_logger
from prefect.client import get_client
from prefect.variables import Variable
from pydantic import BaseModel, ValidationError, validator
from typing import Literal

class RunInputValidation(BaseModel):
    run_type: Literal["daily", "backfill"]
    batch_cycle_date: Optional[str] = None
    backfill_start_date: Optional[str] = None
    backfill_end_date: Optional[str] = None

    @validator("batch_cycle_date", "backfill_start_date", "backfill_end_date")
    def validate_date_format(cls, value):
        if value:
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"Date {value} is not in YYYY-MM-DD format")
        return value

    @validator("backfill_start_date", "backfill_end_date")
    def validate_backfill_dates(cls, value, values):
        run_type = values.get("run_type")
        if run_type == "backfill":
            if not values.get("backfill_start_date") or not values.get("backfill_end_date"):
                raise ValueError("Both backfill_start_date and backfill_end_date must be provided when run_type is 'backfill'")
        elif run_type == "daily":
            if values.get("backfill_start_date") or values.get("backfill_end_date"):
                raise ValueError("backfill_start_date and backfill_end_date should not be provided when run_type is 'daily'")
        return value

@task
async def get_expected_start_date() -> datetime:
    """
    Retrieve the flow run's expected start time using the Prefect client and 
    log the expected and current timestamps. Returns the expected start date.
    """
    logger = get_run_logger()
    
    async with get_client() as client:
        flow_run_id = runtime.flow_run.id
        flow_run = await client.read_flow_run(flow_run_id)
        expected_start_time = flow_run.expected_start_time
    
    expected_start_date = expected_start_time.date()
    current_time = datetime.utcnow()
    current_date = current_time.date()

    logger.info(f"Expected Start Time: {expected_start_time.isoformat()}")
    logger.debug(f"Expected Start Date: {expected_start_date.isoformat()}")
    logger.info(f"Current Time: {current_time.isoformat()}")
    logger.debug(f"Current Date: {current_date.isoformat()}")

    return expected_start_date

@task
def validate_inputs(run_type: str, batch_cycle_date: Optional[str], 
                    backfill_start_date: Optional[str], backfill_end_date: Optional[str],
                    expected_start_date: Optional[datetime] = None):
    """
    Task to validate the flow inputs using pydantic.
    If batch_cycle_date is not provided and run_type is daily, set it to the default.
    """
    # If batch_cycle_date is not provided and run_type is daily, set it to the expected default
    if run_type == "daily" and not batch_cycle_date:
        if expected_start_date:
            batch_cycle_date = (expected_start_date - timedelta(days=1)).strftime("%Y-%m-%d")
    
    try:
        RunInputValidation(run_type=run_type, batch_cycle_date=batch_cycle_date, 
                           backfill_start_date=backfill_start_date, backfill_end_date=backfill_end_date)
    except ValidationError as e:
        raise ValueError(f"Input validation failed: {e}")

@task
def get_batch_cycle_date(expected_start_date: Optional[datetime] = None, 
                         batch_cycle_date: Optional[str] = None) -> str:
    """
    Retrieves the batch cycle date. Defaults to expected_start_date - 1 day if not provided.
    Converts the date string to a string in "YYYY-MM-DD" format.
    """
    if not batch_cycle_date:
        # If no batch_cycle_date provided, use expected_start_date - 1 day
        if expected_start_date:
            date = expected_start_date - timedelta(days=1)
            return date.strftime("%Y-%m-%d")
        # Otherwise, retrieve the batch_cycle_date from Prefect variables
        batch_cycle_date = Variable.get("batch_cycle_date").value
    
    return datetime.strptime(batch_cycle_date, "%Y-%m-%d").strftime("%Y-%m-%d")

@task
def get_backfill_dates(start_date: str, end_date: str) -> List[str]:
    """
    Generates a list of dates between start_date and end_date for backfill.
    Returns dates as strings in "YYYY-MM-DD" format.
    """
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    
    return dates
