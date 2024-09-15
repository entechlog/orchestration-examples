import httpx
from prefect import flow, task, get_run_logger
from prefect_utils import generate_task_run_name
from s3_utils import write_to_s3, clean_s3_directory
from date_utils import (
    get_backfill_dates,
    validate_inputs,
    get_batch_cycle_date,
    get_expected_start_date,
)
from prefect_aws.credentials import AwsCredentials
from datetime import datetime, timedelta
import argparse


@task
def generate_time_ranges_for_date(date: str, freq: str):
    """
    Generate time ranges for the given date based on the frequency.
    Returns a list of (start_time, end_time) tuples.
    """
    logger = get_run_logger()
    logger.info(
        f"Inputs for generate_time_ranges_for_date -> date: {date}, frequency: {freq}"
    )

    start_time = datetime.strptime(f"{date}T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    end_of_day = start_time + timedelta(days=1)
    time_ranges = []

    if freq.endswith("m"):
        minutes = int(freq[:-1])
        delta = timedelta(minutes=minutes)
    elif freq.endswith("h"):
        hours = int(freq[:-1])
        delta = timedelta(hours=hours)
    elif freq.endswith("d"):
        days = int(freq[:-1])
        delta = timedelta(days=days)
    else:
        raise ValueError(f"Unsupported frequency: {freq}")

    current_time = start_time
    while current_time < end_of_day:
        next_time = current_time + delta
        if next_time > end_of_day:
            next_time = end_of_day
        time_ranges.append((current_time, next_time - timedelta(seconds=1)))
        current_time = next_time

    logger.info(f"Generated time ranges: {time_ranges}")
    return time_ranges


@task
def fetch_data_from_api(url: str) -> dict:
    """
    Task to fetch data from the API.
    """
    logger = get_run_logger()
    logger.info(f"Fetching data from API with URL: {url}")
    try:
        response = httpx.get(url, timeout=20)
        response.raise_for_status()
        logger.info(f"Successfully fetched data from {url}")
        return response.json()
    except httpx.RequestError as e:
        logger.error(f"Failed to fetch data from API: {e}")
        raise e


@flow(name="get-pair-candles", log_prints=True)
def get_pair_candles(
    base_url: str,
    endpoint: str,
    frequency: str,
    page_size: str,
    s3_bucket: str,
    s3_key_prefix: str,
    run_type: str = "daily",
    batch_cycle_date: str = None,
    backfill_start_date: str = None,
    backfill_end_date: str = None,
    clean_directory_before_write: bool = False,
):
    """
    Prefect flow to fetch pair candles data from an API and store it in S3, supporting both daily and backfill runs.
    """
    logger = get_run_logger()

    # Log inputs to the flow
    logger.info(
        f"Flow inputs -> base_url: {base_url}, endpoint: {endpoint}, frequency: {frequency}, "
        f"page_size: {page_size}, s3_bucket: {s3_bucket}, s3_key_prefix: {s3_key_prefix}, "
        f"run_type: {run_type}, batch_cycle_date: {batch_cycle_date}, backfill_start_date: {backfill_start_date}, "
        f"backfill_end_date: {backfill_end_date}, "
        f"clean_directory_before_write: {clean_directory_before_write}"
    )

    # Load AWS credentials and S3 client
    aws_credentials_block = AwsCredentials.load("aws-credentials")
    s3_client = aws_credentials_block.get_s3_client()

    # Retrieve expected start date
    expected_start_date = get_expected_start_date()
    logger.info(f"Expected start date: {expected_start_date}")

    # Validate the input dates and run type
    validate = validate_inputs(
        run_type=run_type,
        batch_cycle_date=batch_cycle_date,
        backfill_start_date=backfill_start_date,
        backfill_end_date=backfill_end_date,
        expected_start_date=expected_start_date,
        wait_for=[expected_start_date],
    )

    if run_type == "backfill":
        # Use get_backfill_dates from date_utils.py for backfill mode
        dates = get_backfill_dates(
            start_date=backfill_start_date,
            end_date=backfill_end_date,
            wait_for=[validate],
        )
    else:
        # For daily runs, use get_batch_cycle_date to get the date
        dates = [
            get_batch_cycle_date(
                expected_start_date=expected_start_date,
                batch_cycle_date=batch_cycle_date,
                wait_for=[validate],
            )
        ]

    # Loop through each date and generate time ranges based on frequency
    for date in dates:
        logger.info(f"Processing data for date: {date}")

        # time_ranges = generate_time_ranges_for_date(date, frequency, wait_for=[dates])
        time_ranges = generate_time_ranges_for_date.with_options(
            name=generate_task_run_name("generate_time_ranges_for_date", date)
        ).submit(date, frequency, wait_for=[dates])

        for start_time, end_time in time_ranges.result():
            start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

            # Generate URL for API call
            url = f"{base_url}{endpoint}?pairs=*&frequency={frequency}&page_size={page_size}&start_time={start_time_str}&end_time={end_time_str}"

            # Fetch data from API
            data = fetch_data_from_api.with_options(
                name=generate_task_run_name("fetch_data_from_api", date)
            ).submit(url, wait_for=[time_ranges])

            # Generate S3 directory name
            directory_name = f"/event_type={frequency}/year={date[:4]}/month={date[5:7]}/day={date[8:10]}/"

            # Clean S3 directory if needed
            if clean_directory_before_write:
                clean_s3_dir = clean_s3_directory.with_options(
                    name=generate_task_run_name("clean_s3_directory", date)
                ).submit(
                    bucket_name=s3_bucket,
                    prefix=f"{s3_key_prefix}{directory_name}",
                    s3_client=s3_client,
                    wait_for=[data],
                )

            # Format S3 key
            filename = f"{endpoint.strip('/').replace('-', '_')}_{frequency}_{start_time_str}_{end_time_str}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
            s3_key = f"{s3_key_prefix}{directory_name}{filename}"

            # Write data to S3
            write_to_s3.with_options(
                name=generate_task_run_name("write_to_s3", date)
            ).submit(
                bucket=s3_bucket,
                key=s3_key,
                data=data.result(),
                s3_client=s3_client,
                wait_for=[clean_s3_dir.result()],
            )
            logger.info(f"Data written to S3 at {s3_key}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the get_pair_candles flow with runtime parameters."
    )
    parser.add_argument(
        "--base_url", type=str, required=True, help="Base URL of the API."
    )
    parser.add_argument("--endpoint", type=str, required=True, help="API endpoint.")
    parser.add_argument(
        "--frequency", type=str, required=True, help="Frequency for time ranges."
    )
    parser.add_argument(
        "--page_size", type=str, required=True, help="Page size for API calls."
    )
    parser.add_argument(
        "--s3_bucket", type=str, required=True, help="S3 bucket to store data."
    )
    parser.add_argument(
        "--s3_key_prefix", type=str, required=True, help="S3 key prefix."
    )
    parser.add_argument(
        "--run_type",
        type=str,
        required=True,
        choices=["daily", "backfill"],
        help="Type of run (daily or backfill).",
    )
    parser.add_argument(
        "--batch_cycle_date",
        type=str,
        help="Batch cycle date (YYYY-MM-DD). Required for daily runs.",
    )
    parser.add_argument(
        "--backfill_start_date",
        type=str,
        help="Start date for backfill (YYYY-MM-DD). Required for backfill runs.",
    )
    parser.add_argument(
        "--backfill_end_date",
        type=str,
        help="End date for backfill (YYYY-MM-DD). Required for backfill runs.",
    )
    parser.add_argument(
        "--clean_directory_before_write",
        action="store_true",
        help="Clean the S3 directory before writing.",
    )

    args = parser.parse_args()

    get_pair_candles(
        base_url=args.base_url,
        endpoint=args.endpoint,
        frequency=args.frequency,
        page_size=args.page_size,
        s3_bucket=args.s3_bucket,
        s3_key_prefix=args.s3_key_prefix,
        run_type=args.run_type,
        batch_cycle_date=args.batch_cycle_date,
        backfill_start_date=args.backfill_start_date,
        backfill_end_date=args.backfill_end_date,
        clean_directory_before_write=args.clean_directory_before_write,
    )
