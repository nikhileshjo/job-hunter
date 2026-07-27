import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, EndpointConnectionError
import os
import shutil
from dotenv import load_dotenv
import logging
from datetime import datetime

import json
import gzip

from sqlalchemy import create_engine, text

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
TEMP_PATH = os.getenv("TEMP_PATH")
COLUMN_MAP = os.getenv("COLUMN_MAP")

PG_DBNAME= os.getenv("PG_DBNAME")
PG_USER= os.getenv("PG_USER")
PG_PASSWORD= os.getenv("PG_PASSWORD")
PG_HOST= os.getenv("PG_HOST")
PG_PORT= os.getenv("PG_PORT")
PG_DRIVER= os.getenv("PG_DRIVER")
BR_TABLE= os.getenv("BR_TABLE")

class object_storage():
    # Create connection
    # return connection object
    def __init__(self):

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

    def download_objects(self):
        logging.info("starting file download from bucket to local...")
        try:
            for obj in self.objects_list:
                object_dir = "/".join(obj.split("/")[:-1])
                local_dir = TEMP_PATH+'/'+ object_dir
                # Check path
                if not os.path.exists(local_dir):
                    os.makedirs(local_dir)
                    logging.warning(f"Path not found: {local_dir}")
                    logging.info(f"Path created: {local_dir}")
                # create file
                local_file = local_dir + "/" + obj.split("/")[-1] 
                with open(local_file, "w") as f:
                    f.write("")
                    logging.info(f"file created: {local_file}")
                logging.info(f"Downloading to {local_file}")
                self.s3_conn.download_file(BUCKET_NAME, obj, local_file)
                logging.info(f"file {obj} downloaded to {local_file}")
        except Exception as e:
            logging.error(e)
            exit(1)

class datawarehouse():
    def __init__(self):
    
    
        # create connection to postgres
        self.engine = create_engine(f"{PG_DRIVER}://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DBNAME}")
        try:
            with self.engine.connect() as test_conn:
                test_conn.execute(text("SELECT 'testing connection'"))
                logging.info("connection to datawarehouse established")
        except Exception as e:
            logging.error(f"error establishing connection {e}")
            exit(1)

    def read_files(self, extract_date=datetime.now().strftime("%Y-%m-%d")):
        # list files in tmp location
        extract_date_tmp_location = TEMP_PATH + "/" + extract_date
        self.json_objs = []
        logging.info("listing temp files...")
        file_cnt = 0
        for root, dirs, files in os.walk(extract_date_tmp_location):
            for file in files:
                tmp_file = os.path.join(root, file)
                logging.info(f"found file {tmp_file}")
                file_cnt += 1
                try:
                    with gzip.open(tmp_file, "rb") as f:
                        file_content = f.read()
                        data_dict = {}
                        for key, val in json.loads(file_content).items():
                            data_dict[key] = json.dumps(val)
                        self.json_objs.append(data_dict)
                        logging.info(f"file read {tmp_file}")
                except Exception as e:
                    logging.error(e)
                    exit(1)
        if file_cnt == 0:
            logging.warning(f"No files found under {extract_date_tmp_location}")

    def append_rows(self, extract_date=datetime.now().strftime("%Y-%m-%d")):
        # get column map
        logging.info(f"reading column map {COLUMN_MAP}")
        with open(COLUMN_MAP, "r") as f:
            file_content = f.read()
            col_map = json.loads(file_content)
            logging.info(f"read column map: {col_map}")

        # create inserting data list
        data = []
        for j in self.json_objs:
            d = {}
            for tb_col, json_key in col_map.items():
                if tb_col == "partition_column":
                    d[json_key] = extract_date
                else:
                    d[tb_col] = j[json_key]
            data.append(d)

        if len(data) > 0:
            # prep column list for query
            col_lst = []
            for tb_col, json_key in col_map.items():
                if tb_col == "partition_column":
                    col_lst.append(json_key)
                else:
                    col_lst.append(tb_col)
            col_str = ",".join(col_lst)
            val_str = ",".join([f":{x}" for x in col_lst])
            # truncate and insert values
            try:
                with self.engine.connect() as conn:
                    conn.execute(text(
                        f"DELETE FROM {BR_TABLE} WHERE {col_map["partition_column"]}=:{col_map["partition_column"]}"),
                        [{col_map["partition_column"]: extract_date}]
                        )
                    logging.info(f"deleted any existing rows of {col_map["partition_column"]}={extract_date}")
                    conn.execute(text(f"INSERT INTO {BR_TABLE} ({col_str}) VALUES ({val_str})"), data,)
                    logging.info(f"inserted rows in {BR_TABLE}")
                    conn.commit()
            except Exception as e:
                logging.error(e)
                exit(1)
        else:
            logging.warning("no data to insert")
        

class quality_checks(object_storage, datawarehouse):
    def __init__(self):
        logging.info("establishing connections for data quality checks...")
        object_storage.__init__(self)
        datawarehouse.__init__(self)

    def compare_data(self, extract_date=datetime.now().strftime("%Y-%m-%d")):
        logging.info(f"starting quality checks for date {extract_date}")
        # getting file count from object storage
        super().list_objects(extract_date)
        self.object_count = len(self.objects_list)

        # getting row count from warehouse
        with open(COLUMN_MAP, "r") as f:
            file_content = f.read()
            col_map = json.loads(file_content)
            logging.info(f"read column map: {col_map}")
        PARTITION_COLUMN = col_map["partition_column"]
        try:
            with self.engine.connect() as conn:
                query_result = conn.execute(text(
                                        f"SELECT COUNT(*) FROM {BR_TABLE} WHERE {PARTITION_COLUMN}=:{PARTITION_COLUMN}"),
                                        [{PARTITION_COLUMN: extract_date}]
                                        )
            self.row_count = query_result.all()[0][0]
        except Exception as e:
            logging.error(f"unexpected result format: {e}")

        if self.row_count != self.object_count:
            logging.error("row count does not match object count")
            logging.info(f"object count: {self.object_count}")
            logging.info(f"row count: {self.row_count}")
            exit(1)
        else:
            logging.info("row count matched object count")

def clean_tmp(extract_date=datetime.now().strftime("%Y-%m-%d")):
    # cleans temp location
    target_location = TEMP_PATH + "/" + extract_date
    logging.info(f"starting to clean temp location: {target_location}")
    try:
        if os.path.exists(target_location):
            shutil.rmtree(target_location)
            logging.info("temp location removed")
        else:
            logging.warning(f"no such path found: {target_location}")
    except Exception as e:
        logging.error(f"failed to delete path: {e}")


if __name__ == "__main__":
    pass