from prefect import task, get_run_logger
from prefect_snowflake import SnowflakeCredentials
import os

@task(retries=3, retry_delay_seconds=10)
def set_dbt_env_variables():
    """
    Task to set dbt environment variables using Snowflake credentials and other environment settings.
    """
    # Load Snowflake credentials block
    snowflake_credentials_block = SnowflakeCredentials.load("snowflake-credentials-dbt")

    # Set environment variables
    os.environ["SNOWSQL_ACCOUNT"] = snowflake_credentials_block.account
    os.environ["SNOWSQL_PWD"] = snowflake_credentials_block.password.get_secret_value()
    os.environ["ENV_CODE"] = os.getenv('ENV_CODE')
    os.environ["PROJ_CODE"] = os.getenv('PROJ_CODE')
    os.environ["DBT_PROFILES_DIR"] = os.getenv('DBT_PROFILES_DIR', os.getcwd())  # Defaults to current working directory if not set
    os.environ["DBT_PROJECT_DIR"] = os.getenv('DBT_PROJECT_DIR', os.getcwd())  # Defaults to current working directory if not set

    # Validate critical environment variables
    if not os.environ["ENV_CODE"] or not os.environ["PROJ_CODE"]:
        raise ValueError("Environment variables ENV_CODE or PROJ_CODE are not set.")

    # Initialize logger
    logger = get_run_logger()

    # Log the environment variables
    logger.info(f"Environment Code (ENV_CODE): {os.environ['ENV_CODE']}")
    logger.info(f"Project Code (PROJ_CODE): {os.environ['PROJ_CODE']}")
    logger.info(f"dbt Project Directory (DBT_PROJECT_DIR): {os.environ['DBT_PROJECT_DIR']}")
    logger.info(f"dbt Profiles Directory (DBT_PROFILES_DIR): {os.environ['DBT_PROFILES_DIR']}")

