import hashlib
import re
import json
import requests
from typing import List, Dict, Any
from prefect import get_run_logger
from prefect.blocks.system import Secret


def get_hubspot_keys() -> dict:
    """
    Utility function to get HubSpot Private App credentials
    
    :return: HubSpot API config with access token
    """
    
    hubspot_secret_block = Secret.load("dat-hubspot-secret-keys", _sync=True)
    hubspot_secret_block_json = hubspot_secret_block.get()
    hubspot_json_dumps = json.dumps(hubspot_secret_block_json)
    hubspot_creds = json.loads(hubspot_json_dumps)
    
    hubspot_keys = {
        "access_token": hubspot_creds['HUBSPOT_ACCESS_TOKEN']
    }
    
    return hubspot_keys


def generate_customer_id(company_name: str) -> str:
    """
    Generate customer ID using the standardized logic
    
    company_name: Name of the company
    
    :return: Generated customer ID
    """
    
    # Get first 3 letters of company name (uppercase) while ignoring special characters
    # This ensures we get 3 alphanumeric characters even when there are special chars
    alpha_numeric_name = re.sub(r'[^a-zA-Z0-9]', '', company_name).upper()
    company_prefix = alpha_numeric_name[:3]
    
    # Pad with 'X' if name is shorter than 3 characters
    if len(company_prefix) < 3:
        company_prefix = company_prefix.ljust(3, 'X')
    
    # Create a name-based hash
    # 1. Remove spaces and special characters
    normalized_name = re.sub(r'[^a-zA-Z0-9]', '', company_name).upper()
    
    # 2. If normalized name is too short, add some padding
    hash_input = normalized_name
    if len(normalized_name) < 5:
        hash_input = normalized_name + 'COMPANY'
    
    # 3. Create a hash from the name (reduced to 6 characters)
    hash_value = hashlib.md5(hash_input.encode()).hexdigest()[:6].upper()
    
    # Combine to create the customer ID
    customer_id = f"CUS-{company_prefix}-{hash_value}"
    
    return customer_id


def fetch_companies_without_customer_id(hubspot_config: dict, base_url: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Fetch all companies that have names but no customer IDs, with pagination.
    """
    logger = get_run_logger()

    params = {
        "properties": ["name", "customer_id", "hs_object_id"],
        "limit": limit,
        "filterGroups": [
            {
                "filters": [
                    {"propertyName": "name", "operator": "HAS_PROPERTY"},
                    {"propertyName": "customer_id", "operator": "NOT_HAS_PROPERTY"}
                ]
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {hubspot_config['access_token']}",
        "Content-Type": "application/json"
    }

    search_url = f"{base_url}/search"
    all_companies = []
    after = None

    try:
        while True:
            payload = dict(params)
            if after:
                payload["after"] = after

            logger.info(f"Requesting companies from HubSpot (after={after})")
            response = requests.post(search_url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])
            all_companies.extend(results)

            paging = data.get("paging", {})
            next_link = paging.get("next", {})
            after = next_link.get("after")

            if not after:
                break  # no more pages

        logger.info(f"Found total {len(all_companies)} companies without customer IDs")
        return all_companies

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching companies: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
        raise

def update_company_customer_id(company_id: str, customer_id: str, hubspot_config: dict, base_url: str) -> bool:
    """
    Update a company's customer ID in HubSpot
    
    company_id: HubSpot company ID
    customer_id: Generated customer ID
    hubspot_config: HubSpot API configuration
    base_url: HubSpot API base URL
    
    :return: Success status
    """
    logger = get_run_logger()
    
    headers = {
        "Authorization": f"Bearer {hubspot_config['access_token']}",
        "Content-Type": "application/json"
    }
    
    data = {
        "properties": {
            "customer_id": customer_id
        }
    }
    
    try:
        url = f"{base_url}/{company_id}"
        response = requests.patch(url, json=data, headers=headers)
        response.raise_for_status()
        
        logger.info(f"Updated company {company_id} with customer ID: {customer_id}")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error updating company {company_id}: {e}")
        return False