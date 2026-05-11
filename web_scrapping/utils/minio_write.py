from pathlib import Path

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

import os
import gzip

import json

from datetime import datetime

TMP_LOCATION = "web_scrapping/utils/tmp"
ENDPOINT_URL = "http://localhost:9000"
ACCESS_KEY = "admin"
SECRET_KEY = "password"
BUCKET_NAME = "raw-jobs"

# The below function will generate a file in TMP_LOCATION
# Then Upload the generated file to desired path in bucket
def save_job(company_name:str,  file_content:str, extract_date:str) -> bool:
    current_date_time = datetime.today().strftime('%Y%m%d%H%M%S')
    

    location = f"{TMP_LOCATION}/{extract_date}/{company_name}"
    file_name = f"{company_name}_{current_date_time}.json"

    if not os.path.exists(location):
        try:
            os.makedirs(location)
            print(f"Directory '{location}' created successfully.")
        except PermissionError:
            print(f"Permission denied: Unable to create '{location}'.")
            return False
        except Exception as e:
            print(f"An error occurred while creating directory '{location}': {e}")
            return False
    try:
        gzip_file = f"{location}/{file_name}.gz"
        with gzip.open(gzip_file, "wt", encoding="utf-8") as zipfile:
            zipfile.write(file_content)
    except PermissionError:
            print(f"Permission denied: Unable to create '{location}/{file_name}'.")
            return False
    except Exception as e:
            print(f"An error occurred while saving file '{location}/{file_name}': {e}")
            return False

    upload_file(gzip_file, f"{extract_date}/{company_name}/{file_name}.gz")


def create_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )


def ensure_bucket_exists(s3_client, bucket_name):
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"Bucket already exists: {bucket_name}")
    except ClientError as error:
        status_code = error.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        if status_code == 404:
            s3_client.create_bucket(Bucket=bucket_name)
            print(f"Created bucket: {bucket_name}")
            return

        raise


def upload_file(local_file, bucket_obj):
    s3_client = create_s3_client()

    ensure_bucket_exists(s3_client, BUCKET_NAME)
    s3_client.upload_file(str(local_file), BUCKET_NAME, bucket_obj)

    print(f"Uploaded {local_file} to s3://{BUCKET_NAME}/{bucket_obj}")

