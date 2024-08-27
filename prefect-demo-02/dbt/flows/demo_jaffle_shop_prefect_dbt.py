from prefect import flow, task
from prefect_dbt.cli import DbtCoreOperation
from prefect_snowflake import SnowflakeCredentials
from typing import Optional
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

@flow(name="demo-jaffle-shop-prefect-dbt", log_prints=True)
def run_jaffle_shop(batch_cycle_date: Optional[str] = None, 
                                        backfill_start_date: Optional[str] = None, 
                                        backfill_end_date: Optional[str] = None):
    # Set environment variables
    set_env_variables()

    # Execute dbt seed
    dbt_seed = DbtCoreOperation(
        commands=["dbt seed"],
        project_dir=os.environ['DBT_PROFILES_DIR'],  # Assuming the dbt project is in the current working directory
        profiles_dir=os.environ["DBT_PROFILES_DIR"]
    )
    seed_result = dbt_seed.run()

    # Execute dbt run
    dbt_run = DbtCoreOperation(
        commands=["dbt run"],
        project_dir=os.environ['DBT_PROFILES_DIR'],
        profiles_dir=os.environ["DBT_PROFILES_DIR"]
    )
    run_result = dbt_run.run()

    # Execute dbt test
    dbt_test = DbtCoreOperation(
        commands=["dbt test"],
        project_dir=os.environ['DBT_PROFILES_DIR'],
        profiles_dir=os.environ["DBT_PROFILES_DIR"]
    )
    test_result = dbt_test.run()

    return test_result

if __name__ == "__main__":
    run_jaffle_shop()
