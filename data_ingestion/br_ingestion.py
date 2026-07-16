# This script will pull data from minio and append it to postgres (datawarehouse)
# Planning (remove after use)
# create a class to interact with minio
## create a method to create connection to minio
## create a method to make a list of objects available to us, this should be able to filter down to the objects
## of our interest and only list them, by default, it'll list out everything.
## Create a method that will download objects that for which it's paths are given and save it in local disk.
# Create a class to interact with postgres
## Create a method to create connection with postgres, and it'll return it as an object
## Create a method to read the json files, make them into python object or variables and then insert it into postgres
## Create a method to do a quality check on the latest added rows. We'll read the objects that were created by reading
## the JSON files and see if they exist in the current working date. If it does, it returns true, and if any mismatches foudn
## return false
# the main class will be used to orchestrate the above two classes
## It will call on the minio methods and download all the objects under a company name for the current data(by default)
## and then call on the postgres methods to append the values into postgres.
## once uploaded, a quality check will run to see if the rows were added or not, if pass, we'll delete the local files
## and move on to the next company.

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, EndpointConnectionError
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

time_now = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = f"logs/br_ingestion_{time_now}"

logging.basicConfig(
    level=logging.INFO,
    filename=log_filename,
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# Instatiate environment variables
load_dotenv()
MINIO_END_POINT = os.getenv("MINIO_END_POINT")
ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")


class object_storage():
    # Create connection
    # return connection object
    def __init__(self):


        logging.info("Environment variables set.")

        self.s3_conn = boto3.client(
            "s3",
            endpoint_url = MINIO_END_POINT,
            aws_access_key_id = ACCESS_KEY,
            aws_secret_access_key = SECRET_KEY,
            config = boto3.session.Config(signature_version="s3v4"),
            region_name = "us-east-1"
        )
        try:
            response = self.s3_conn.head_bucket(Bucket = BUCKET_NAME)
            logging.info("Connection to object storage successful!!!")
            return None
        except EndpointConnectionError:
            logging.error("Failed to connect to object storage. Is Minio Online?")
            exit(1)
        except NoCredentialsError:
            logging.error("No credentials provided. Explicit credentials are required.")
            exit(1)
        except PartialCredentialsError:
            logging.error("Incomplete credentials provided.")
            exit(1) 
        except Exception as e:
            logging.error(e)
            exit(1)
    
    def list_objects(self, extract_date=datetime.now().strftime("%Y-%m-%d")):
        try:
            paginator = self.s3_conn.get_paginator("list_objects_v2")
            page_iterator = paginator.paginate(Bucket = BUCKET_NAME, Prefix=extract_date+"/")

            self.objects_list = []
            logging.info(f"Reading bucket object names with prefix {extract_date}")
            for page in page_iterator:
                if "Contents" in page:
                    for obj in page['Contents']:
                        self.objects_list.append(obj['Key'])
        except Exception as e:
            logging.error(e)
            exit(1)

        obj_count = len(self.objects_list) 
        if obj_count == 0:
            logging.warning(f"Bucket has no objects with the prefix {extract_date}")
        else:
            logging.info(f"Found {obj_count} object(s) in the bucket")
        return None