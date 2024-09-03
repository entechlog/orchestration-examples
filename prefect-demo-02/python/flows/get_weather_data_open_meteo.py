import httpx
from prefect import flow, task, get_run_logger
from utils.date_utils import get_batch_cycle_date, get_backfill_dates, get_expected_start_date, validate_inputs
from typing import Optional

@task(task_run_name="get_weather_data_{date}", retries=3, retry_delay_seconds=300)
def get_weather_data(lat: str, lon: str, date: str) -> dict:
    """
    Task to get weather data for a given date and location from Open Meteo using httpx.
    """
    logger = get_run_logger()
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": date,
        "end_date": date,
        "daily": ["temperature_2m_max", "temperature_2m_min"]
    }
    
    logger.info(f"Calling Open-Meteo API for date: {date}, lat: {lat}, lon: {lon}")
    
    response = httpx.get(url, params=params)
    
    if response.status_code == 200:
        logger.info(f"Received raw weather data response for date: {date}")
        return response.json()
    else:
        logger.error(f"Failed to retrieve weather data: {response.status_code} - {response.text}")
        response.raise_for_status()

@task(task_run_name="get_location_data_{date}", retries=3, retry_delay_seconds=300)
def get_location_data(lat: str, lon: str, date: str) -> dict:
    """
    Task to get location data (e.g., city, country) for a given lat/lon using Nominatim API.
    """
    logger = get_run_logger()
    
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json"
    }
    
    logger.info(f"Calling Nominatim API for lat: {lat}, lon: {lon}")
    
    response = httpx.get(url, params=params)
    
    if response.status_code == 200:
        logger.info(f"Received location data for lat: {lat}, lon: {lon}")
        return response.json()
    else:
        logger.error(f"Failed to retrieve location data: {response.status_code} - {response.text}")
        response.raise_for_status()

@flow(name="get-weather-data-open-meteo", log_prints=True)
def get_weather_data_open_meteo(batch_cycle_date: Optional[str] = None, 
                                backfill_start_date: Optional[str] = None, 
                                backfill_end_date: Optional[str] = None,
                                lat: Optional[str] = None,
                                lon: Optional[str] = None,
                                run_type: str = None):
    
    # Set default run type
    if not run_type:
        run_type = "daily"

    # Initiate logger
    logger = get_run_logger()

    # Retrieve expected start date
    expected_start_date = get_expected_start_date()

    # Validate inputs using the centralized validation function
    validate_inputs(run_type=run_type, batch_cycle_date=batch_cycle_date, 
                    backfill_start_date=backfill_start_date, backfill_end_date=backfill_end_date,
                    expected_start_date=expected_start_date)

    # Determine flow logic based on whether backfill is used
    if run_type == "backfill":
        dates = get_backfill_dates(start_date=backfill_start_date, end_date=backfill_end_date)
    else:
        dates = [get_batch_cycle_date(expected_start_date=expected_start_date, batch_cycle_date=batch_cycle_date)]

    for date in dates:
        logger.info(f"Running batch for date: {date}")
        if lat and lon:
            weather_data = get_weather_data(lat=lat, lon=lon, date=date)
            location_data = get_location_data(lat=lat, lon=lon, date=date, wait_for=[weather_data])
            logger.info(f"Weather data for {date}:\n{weather_data}")
            logger.info(f"Location data for lat: {lat}, lon: {lon}:\n{location_data}")

if __name__ == "__main__":
    get_weather_data_open_meteo()
