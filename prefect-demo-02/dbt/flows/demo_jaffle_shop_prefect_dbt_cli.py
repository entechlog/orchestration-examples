from prefect import flow
from prefect_dbt.cli.commands import trigger_dbt_cli_command
from utils.dbt_utils import set_dbt_env_variables
from typing import Optional
import os

@flow(name="demo-jaffle-shop-prefect-dbt", log_prints=True)
def run_jaffle_shop(batch_cycle_date: Optional[str] = None, 
                    backfill_start_date: Optional[str] = None, 
                    backfill_end_date: Optional[str] = None):
    
    # Set environment variables using the task from utils.dbt_utils
    set_dbt_env_variables()

    # Define the dbt seed task with options
    dbt_seed_task = trigger_dbt_cli_command.with_options(
        name="dbt_seed_task",
        retries=3,
        retry_delay_seconds=300
    )

    # Execute dbt seed
    dbt_seed_result = dbt_seed_task(
        command="dbt seed",
        project_dir=os.environ['DBT_PROJECT_DIR'],
        profiles_dir=os.environ["DBT_PROFILES_DIR"],
        extra_command_args=["--target", os.environ["ENV_CODE"]],
        create_summary_artifact=True,
        summary_artifact_key="dbt-seed-task-summary"
    )

    # Define the dbt run task with options
    dbt_run_task = trigger_dbt_cli_command.with_options(
        name="dbt_run_task",
        retries=3,
        retry_delay_seconds=300
    )

    # Execute dbt run, depending on dbt_seed_result
    dbt_run_result = dbt_run_task(
        command="dbt run",
        project_dir=os.environ['DBT_PROJECT_DIR'],
        profiles_dir=os.environ["DBT_PROFILES_DIR"],
        extra_command_args=["--target", os.environ["ENV_CODE"]],
        create_summary_artifact=True,
        summary_artifact_key="dbt-run-task-summary",
        wait_for=[dbt_seed_result]
    )

    # Define the dbt test task with options
    dbt_test_task = trigger_dbt_cli_command.with_options(
        name="dbt_test_task",
        retries=3,
        retry_delay_seconds=300
    )

    # Execute dbt test, depending on dbt_run_result
    dbt_test_task(
        command="dbt test",
        project_dir=os.environ['DBT_PROJECT_DIR'],
        profiles_dir=os.environ["DBT_PROFILES_DIR"],
        extra_command_args=["--target", os.environ["ENV_CODE"]],
        create_summary_artifact=True,
        summary_artifact_key="dbt-test-task-summary",
        wait_for=[dbt_run_result]
    )

if __name__ == "__main__":
    run_jaffle_shop()
