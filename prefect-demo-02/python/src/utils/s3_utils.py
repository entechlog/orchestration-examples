import json
import time
from prefect import task, get_run_logger
from prefect_aws.credentials import AwsCredentials


@task
def write_to_s3(bucket: str, key: str, data: dict, s3_client):
    """
    Task to write data to S3 using a provided S3 client.
    """
    logger = get_run_logger()
    try:
        logger.info(f"Writing data to S3 at {bucket}/{key}")
        s3_client.put_object(Bucket=bucket, Key=key, Body=json.dumps(data))
        logger.info(f"Successfully wrote data to S3 at {bucket}/{key}")
    except Exception as e:
        logger.error(f"Failed to write data to S3: {e}")
        raise e


@task
def clean_s3_directory(bucket_name: str, prefix: str, s3_client):
    """
    Task to delete all objects under a given S3 prefix.
    """
    logger = get_run_logger()
    paginator = s3_client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

    delete_us = []
    for page in pages:
        if "Contents" in page:
            for obj in page["Contents"]:
                delete_us.append({"Key": obj["Key"]})
            if delete_us:
                logger.info(f"Deleting {len(delete_us)} objects from {prefix}")
                s3_client.delete_objects(
                    Bucket=bucket_name, Delete={"Objects": delete_us}
                )
                delete_us.clear()

    if not delete_us:
        logger.info(f"No objects to delete in {prefix}")
    logger.info(
        f"Successfully emptied the directory {prefix} in S3 bucket {bucket_name}."
    )
