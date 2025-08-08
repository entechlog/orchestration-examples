import argparse
from typing import List
from prefect import flow, task, get_run_logger

# local imports
from prefect_utils import generate_flow_run_name, generate_task_run_name  # Make sure this import exists
from hubspot_utils import (
    get_hubspot_keys,
    generate_customer_id,
    fetch_companies_without_customer_id,
    update_company_customer_id
)


@task(cache_policy=None)  # Remove the task_run_name from here
def process_companies_batch(
    companies: List[dict],
    hubspot_config: dict,
    base_url: str,
    batch_number: int,
    is_dryrun: bool
):
    """
    Process a batch of companies to generate and optionally update customer IDs
    """
    logger = get_run_logger()
    results = {"processed": 0, "successful": 0, "failed": 0, "errors": []}

    logger.info(f"Processing batch {batch_number} with {len(companies)} companies (dryrun={is_dryrun})")

    for company in companies:
        try:
            company_id = company["id"]
            company_name = company["properties"].get("name", "")

            if not company_name:
                logger.warning(f"Company {company_id} has no name, skipping")
                continue

            customer_id = generate_customer_id(company_name)
            logger.info(f"Generated {customer_id} for {company_name}")

            if is_dryrun:
                logger.info(f"Dry run: Skipping update for {company_id}")
                success = True
            else:
                success = update_company_customer_id(company_id, customer_id, hubspot_config, base_url)

            results["processed"] += 1
            if success:
                results["successful"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(f"Failed to update company {company_id}")

        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"Error processing company {company_id}: {str(e)}")
            logger.error(f"Error processing company {company_id}: {e}")

    logger.info(f"Batch {batch_number} completed: {results['successful']} successful, {results['failed']} failed")
    return results


@flow(name="hubspot-customer-id-generation", flow_run_name=generate_flow_run_name, log_prints=True)
def generate_hubspot_customer_ids(
    base_url: str = "https://api.hubapi.com/crm/v3/objects/companies",
    is_dryrun: bool = True
):
    """
    Flow to generate customer IDs for HubSpot companies
    """
    logger = get_run_logger()
    logger.info(f"Starting HubSpot Customer ID generation flow (dryrun={is_dryrun})")

    try:
        hubspot_config = get_hubspot_keys()
        companies = fetch_companies_without_customer_id(hubspot_config, base_url, limit=100)

        if not companies:
            logger.info("No companies found without customer IDs")
            return {"message": "No companies to process"}

        batch_size = 10
        all_results = {"total_processed": 0, "total_successful": 0, "total_failed": 0, "all_errors": []}
        task_futures = []

        for i in range(0, len(companies), batch_size):
            batch = companies[i:i + batch_size]
            batch_number = i // batch_size + 1

            # Use .with_options() to set the task name dynamically
            future = process_companies_batch.with_options(
                name=generate_task_run_name("process_companies_batch", f"_{batch_number}")
            ).submit(
                companies=batch,
                hubspot_config=hubspot_config,
                base_url=base_url,
                batch_number=batch_number,
                is_dryrun=is_dryrun
            )
            task_futures.append(future)

        for future in task_futures:
            batch_results = future.result()
            all_results["total_processed"] += batch_results["processed"]
            all_results["total_successful"] += batch_results["successful"]
            all_results["total_failed"] += batch_results["failed"]
            all_results["all_errors"].extend(batch_results["errors"])

        logger.info(
            f"Flow completed. Processed: {all_results['total_processed']}, "
            f"Successful: {all_results['total_successful']}, "
            f"Failed: {all_results['total_failed']}"
        )

        if all_results["all_errors"]:
            logger.warning(f"Errors encountered: {all_results['all_errors']}")

        return all_results

    except Exception as e:
        logger.error(f"Flow failed with error: {e}")
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate HubSpot Customer IDs.")
    parser.add_argument(
        "--base_url",
        type=str,
        default="https://api.hubapi.com/crm/v3/objects/companies",
        help="Base URL of the HubSpot API."
    )
    parser.add_argument(
        "--realrun",
        action="store_true",
        help="Run in real mode (perform updates). Default is dry run."
    )

    args = parser.parse_args()

    generate_hubspot_customer_ids(
        base_url=args.base_url,
        is_dryrun=not args.realrun  # default True, flips to False if --realrun is passed
    )