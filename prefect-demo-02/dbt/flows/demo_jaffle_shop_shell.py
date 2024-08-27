from prefect import flow, task
from prefect_shell import shell_run_command
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

@task
def run_dbt_seed():
    result = shell_run_command("dbt seed")
    return result

@task
def run_dbt_run():
    result = shell_run_command("dbt run")
    return result

@task
def run_dbt_test():
    result = shell_run_command("dbt test")
    return result

@flow(name="demo-jaffle-shop-shell", log_prints=True)
def run_jaffle_shop(batch_cycle_date: Optional[str] = None, 
                                        backfill_start_date: Optional[str] = None, 
                                        backfill_end_date: Optional[str] = None):
    set_env_variables()
    run_dbt_seed()
    run_dbt_run()
    run_dbt_test()

if __name__ == "__main__":
    run_jaffle_shop()
