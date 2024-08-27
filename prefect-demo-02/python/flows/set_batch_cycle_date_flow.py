from prefect import flow, task
from prefect.variables import Variable
from datetime import datetime, timedelta
from prefect.tasks import task_input_hash
from datetime import timedelta

@task(retries=3, retry_delay_seconds=10)
def set_batch_cycle_date():
    batch_cycle_date = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
    Variable.set(name="batch_cycle_date", value=batch_cycle_date, overwrite=True)
    print(f"Set batch_cycle_date to {batch_cycle_date}")

@task(retries=3, retry_delay_seconds=10)
def set_todays_date():
    todays_date = datetime.utcnow().strftime('%Y-%m-%d')
    Variable.set(name="todays_date", value=todays_date, overwrite=True)
    print(f"Set todays_date to {todays_date}")

@flow(name="set_batch_cycle_date_flow", log_prints=True)
def set_batch_cycle_date_flow():
    set_batch_cycle_date()
    set_todays_date()

if __name__ == "__main__":
    set_batch_cycle_date_flow()
