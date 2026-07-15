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


class object_storage():
    # Create connection
    # return connection object
    def s3_connector(self):

        # Instatiate environment variables
        load_dotenv()
        MINIO_END_POINT = os.getenv("MINIO_END_POINT")
        ACCESS_KEY = os.getenv("ACCESS_KEY")
        SECRET_KEY = os.getenv("SECRET_KEY")
        BUCKET_NAME = os.getenv("BUCKET_NAME")

        logging.info("Environment variables set.")

        s3_conn = boto3.client(
            "s3",
            endpoint_url = MINIO_END_POINT,
            aws_access_key_id = ACCESS_KEY,
            aws_secret_access_key = SECRET_KEY,
            config = boto3.session.Config(signature_version="s3v4"),
            region_name = "us-east-1"
        )
        try:
            response = s3_conn.head_bucket(Bucket = BUCKET_NAME)
            logging.info("Connection to object storage successful!!!")
            return s3_conn
        except EndpointConnectionError:
            logging.error("Failed to connect to object storage. Is Minio Online?")
            return None
        except NoCredentialsError:
            logging.error("No credentials provided. Explicit credentials are required.")
            return None
        except PartialCredentialsError:
            logging.error("Incomplete credentials provided.")
            return None
        except Exception as e:
            logging.error(e)
            return None
