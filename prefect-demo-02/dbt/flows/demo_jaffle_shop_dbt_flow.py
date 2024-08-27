from pathlib import Path
from prefect import task, flow
from prefect_dbt_flow import dbt_flow
from prefect_dbt_flow.dbt import DbtDagOptions, DbtProfile, DbtProject
from prefect_snowflake import SnowflakeCredentials
import os

@task
def set_env_variables():
    snowflake_credentials_block = SnowflakeCredentials.load("snowflake-credentials-dbt")
    os.environ["SNOWSQL_ACCOUNT"] = snowflake_credentials_block.account
    os.environ["SNOWSQL_PWD"] = snowflake_credentials_block.password.get_secret_value()
    os.environ["ENV_CODE"] = os.getenv('ENV_CODE')
    os.environ["PROJ_CODE"] = os.getenv('PROJ_CODE')
    os.environ["DBT_PROFILES_DIR"] = os.getenv('DBT_PROFILES_DIR', os.getcwd())  # Defaults to current working directory if not set
    os.environ["DBT_PROJECT_DIR"] = os.getenv('DBT_PROJECT_DIR', os.getcwd())  # Defaults to current working directory if not set

    if not os.environ["ENV_CODE"] or not os.environ["PROJ_CODE"]:
        raise ValueError("Environment variables ENV_CODE or PROJ_CODE are not set.")

    # Print the environment variables
    print(f"Environment Code (ENV_CODE): {os.environ['ENV_CODE']}")
    print(f"Project Code (PROJ_CODE): {os.environ['PROJ_CODE']}")
    print(f"dbt project dir (DBT_PROJECT_DIR): {os.environ['DBT_PROJECT_DIR']}")
    print(f"dbt profiles dir (DBT_PROFILES_DIR): {os.environ['DBT_PROFILES_DIR']}")

@flow(name="demo-jaffle-shop-dbt-flow", log_prints=True)
def run_jaffle_shop(batch_cycle_date: str = None, backfill_start_date: str = None, backfill_end_date: str = None):
    # Set environment variables
    set_env_variables()

    # Define the dbt flow within the flow
    my_dbt_flow = dbt_flow(
        project=DbtProject(
            name="example_jaffle_shop",
            project_dir=os.environ["DBT_PROJECT_DIR"],  # Use environment variable
            profiles_dir=os.environ["DBT_PROFILES_DIR"]  # Use environment variable
        ),
        profile=DbtProfile(
            target=os.environ["ENV_CODE"],  # Use environment variable
        ),
        dag_options=DbtDagOptions(
            run_test_after_model=True,
        ),
    )

    # Run the dbt flow
    my_dbt_flow()

if __name__ == "__main__":
    run_jaffle_shop()
