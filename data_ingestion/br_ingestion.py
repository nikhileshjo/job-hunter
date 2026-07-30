import boto3
from botocore.exceptions import (NoCredentialsError,
                                 PartialCredentialsError,
                                 EndpointConnectionError,
                                 DataNotFoundError,
                                 ConnectTimeoutError,
                                 ReadTimeoutError,
                                 ClientError)

import os
import shutil
from dotenv import load_dotenv
import logging
from datetime import datetime

import json
import gzip

from sqlalchemy import create_engine, text
from sqlalchemy.exc import (
    ArgumentError,
    NoSuchModuleError,
    OperationalError,
    TimeoutError,
    InterfaceError,
)

from sqlalchemy.exc import (
    OperationalError,
    IntegrityError,
    ProgrammingError,
    DataError,
    SQLAlchemyError,
)

import argparse
from pathlib import Path




# Instatiate environment variables
class EnvConfig():

    def __init__(self):


        
        load_dotenv()
        self.MINIO_END_POINT = os.getenv("MINIO_END_POINT")
        self.ACCESS_KEY = os.getenv("ACCESS_KEY")
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.BUCKET_NAME = os.getenv("BUCKET_NAME")
        self.TEMP_PATH = os.getenv("TEMP_PATH")
        self.COLUMN_MAP = os.getenv("COLUMN_MAP")

        self.PG_DBNAME= os.getenv("PG_DBNAME")
        self.PG_USER= os.getenv("PG_USER")
        self.PG_PASSWORD= os.getenv("PG_PASSWORD")
        self.PG_HOST= os.getenv("PG_HOST")
        self.PG_PORT= os.getenv("PG_PORT")
        self.PG_DRIVER= os.getenv("PG_DRIVER")
        self.BR_TABLE= os.getenv("BR_TABLE")

        self.ROWS_ON_MEMORY = int(os.getenv("ROWS_ON_MEMORY"))


        # get column map
        logging.info(f"reading column map {self.COLUMN_MAP}")
        with open(self.COLUMN_MAP, "r") as f:
            file_content = f.read()
            self.col_map = json.loads(file_content)
            logging.info(f"read column map: {self.col_map}")
        self.PARTITION_COLUMN = self.col_map["partition_column"]

class ObjectStorage():
    # Create connection
    # return connection object
    def __init__(self, config : EnvConfig):
        self.config = config
        self.s3_conn = boto3.client(
            "s3",
            endpoint_url = self.config.MINIO_END_POINT,
            aws_access_key_id = self.config.ACCESS_KEY,
            aws_secret_access_key = self.config.SECRET_KEY,
            config = boto3.session.Config(signature_version="s3v4"),
            region_name = "us-east-1"
        )
        try:
            response = self.s3_conn.head_bucket(Bucket = self.config.BUCKET_NAME)
            logging.info("Connection to object storage successful!!!")
        except EndpointConnectionError:
            logging.error("Failed to connect to object storage. Is Minio Online?")
            raise
        except NoCredentialsError:
            logging.error("No credentials provided. Explicit credentials are required.")
            raise
        except PartialCredentialsError:
            logging.error("Incomplete credentials provided.")
            raise
        except Exception as e:
            logging.exception("Unexpected error while connecting to MinIO.")
            raise
    
    def list_objects(self, extract_date=datetime.now().strftime("%Y-%m-%d")):
        try:
            paginator = self.s3_conn.get_paginator("list_objects_v2")
            page_iterator = paginator.paginate(Bucket = self.config.BUCKET_NAME, Prefix=extract_date+"/")

            self.objects_list = []
            logging.info(f"Reading bucket object names with prefix {extract_date}")
            for page in page_iterator:
                if "Contents" in page:
                    for obj in page['Contents']:
                        self.objects_list.append(obj['Key'])
        except EndpointConnectionError as e:
            logging.error("Cannot reach S3 endpoint: %s", e)
            raise

        except (ConnectTimeoutError, ReadTimeoutError) as e:
            logging.error("Connection timed out: %s", e)
            raise

        except (NoCredentialsError, PartialCredentialsError) as e:
            logging.error("Credential error: %s", e)
            raise

        except ClientError as e:
            code = e.response["Error"]["Code"]
            logging.error("S3 returned %s: %s", code, e)
            raise

        except Exception:
            logging.exception("Unexpected error while listing objects")
            raise

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
                local_dir = Path(self.config.TEMP_PATH, object_dir)
                # Check path
                if not os.path.exists(local_dir):
                    logging.warning(f"Path not found: {local_dir}")
                    os.makedirs(local_dir)
                    logging.info(f"Path created: {local_dir}")
                # create file
                local_file = Path(local_dir , obj.split("/")[-1])
                # with open(local_file, "w") as f:
                #     f.write("")
                #     logging.info(f"file created: {local_file}")
                logging.info(f"Downloading to {local_file}")
                self.s3_conn.download_file(self.config.BUCKET_NAME, obj, local_file)
                logging.info(f"file {obj} downloaded to {local_file}")
        except (EndpointConnectionError,
                ConnectTimeoutError,
                ReadTimeoutError):
            logging.error("Network error")
            raise

        except ClientError as e:
            logging.error("S3 error: %s", e.response["Error"]["Code"])
            raise

        except OSError:
            logging.exception("Local filesystem error")
            raise

class DataWarehouse():
    def __init__(self, config : EnvConfig):
    
        self.config = config
        # create connection to postgres
        connection_string = f"{self.config.PG_DRIVER}://{self.config.PG_USER}:{self.config.PG_PASSWORD}@{self.config.PG_HOST}:{self.config.PG_PORT}/{self.config.PG_DBNAME}"
        self.engine = create_engine(connection_string)
        try:
            with self.engine.connect() as test_conn:
                test_conn.execute(text("SELECT 'testing connection'"))
                logging.info("connection to datawarehouse established")
        except NoSuchModuleError:
            logging.error("driver error. Driver missing or miss spelt")
            raise
        except ArgumentError:
            logging.error(f"wrong connection string: {connection_string}")
            raise
        except OperationalError:
            logging.error(f"Network error")
            raise
        except TimeoutError:
            logging.error("Connection timed out")
            raise
        except InterfaceError:
            logging.error("Driver error")
            raise
        except Exception as e:
            logging.exception(f"error establishing connection {e}")
            raise

    def __append_rows(self, rows, extract_date=datetime.now().strftime("%Y-%m-%d")):
        if len(rows) > 0:
            # prep column list for query
            col_lst = []
            for tb_col, json_key in self.config.col_map.items():
                col_lst.append(json_key)
            col_str = ",".join(col_lst)
            val_str = ",".join([f":{x}" for x in col_lst])
            # truncate and insert values
            try:
                with self.engine.connect() as conn:
                    conn.execute(text(
                        f"DELETE FROM {self.config.BR_TABLE} WHERE {self.config.col_map["partition_column"]}=:{self.config.col_map["partition_column"]}"),
                        [{self.config.col_map["partition_column"]: extract_date}]
                        )
                    logging.info(f"deleted any existing rows of {self.config.col_map["partition_column"]}={extract_date}")
                    conn.execute(text(f"INSERT INTO {self.config.BR_TABLE} ({col_str}) VALUES ({val_str})"), rows)
                    logging.info(f"inserted rows in {self.config.BR_TABLE}")
                    conn.commit()
            except IntegrityError as e:
                logging.error("Constraint violation: %s", e)
                raise
            except OperationalError as e:
                logging.error("Database unavailable: %s", e)
                raise
            except SQLAlchemyError as e:
                logging.error("Database error: %s", e)
                raise
            except Exception as e:
                logging.exception("Unexpected error while appending rows to datawarehouse.")
                raise
        else:
            logging.warning("no data to insert")



    def append_rows(self, extract_date=datetime.now().strftime("%Y-%m-%d")):
        # list files in tmp location
        extract_date_tmp_location = Path(self.config.TEMP_PATH, extract_date)
        json_objs = []
        data = []
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
                            data_dict[self.config.col_map[key]] = json.dumps(val)
                        data_dict[self.config.PARTITION_COLUMN] = extract_date
                        data.append(data_dict)
                        logging.info(f"file read {tmp_file}")
                        if len(data) >= self.config.ROWS_ON_MEMORY:
                            self.__append_rows(rows=data, extract_date=extract_date)
                            data = []
                        
                
                except FileNotFoundError:
                    logging.error(f"{tmp_file} not found")
                    raise

                except gzip.BadGzipFile:
                    logging.error(f"{tmp_file} is not a valid gzip file")
                    raise

                except json.JSONDecodeError:
                    logging.error(f"{tmp_file} contains invalid JSON")
                    raise

                except OSError as e:
                    logging.error(f"I/O error reading {tmp_file}: {e}")
                    raise
                except Exception as e:
                    logging.exception(f"Unexpected error while reading {tmp_file}")
                    raise
        if len(data) > 0:
            self.__append_rows(rows=data, extract_date=extract_date)


class QualityChecks():
    def __init__(self, config : EnvConfig):
        self.config = config
        logging.info("establishing connections for data quality checks...")

        self.obj_strg = ObjectStorage(config)

        self.dw = DataWarehouse(config)


    def compare_data(self, extract_date=datetime.now().strftime("%Y-%m-%d")):
        logging.info(f"starting quality checks for date {extract_date}")
        # getting file count from object storage
        self.obj_strg.list_objects(extract_date)
        self.object_count = len(self.obj_strg.objects_list)
        
        try:
            with self.dw.engine.connect() as conn:
                query_result = conn.execute(text(
                                        f"SELECT COUNT(*) FROM {self.config.BR_TABLE} WHERE {self.config.PARTITION_COLUMN}=:{self.config.PARTITION_COLUMN}"),
                                        [{self.config.PARTITION_COLUMN: extract_date}]
                                        )
            self.row_count = query_result.all()[0][0]
        except SQLAlchemyError as e:
            logging.error("Database error: %s", e)
            raise
        except Exception as e:
            logging.error(f"unexpected result format: {e}")
            raise

        if self.row_count != self.object_count:
            logging.error("row count does not match object count")
            logging.info(f"object count: {self.object_count}")
            logging.info(f"row count: {self.row_count}")
            raise
        else:
            logging.info("row count matched object count")

def clean_tmp(config: EnvConfig, extract_date=datetime.now().strftime("%Y-%m-%d")):
    # cleans temp location
    target_location = Path(config.TEMP_PATH ,extract_date)
    logging.info(f"starting to clean temp location: {target_location}")
    try:
        if os.path.exists(target_location):
            shutil.rmtree(target_location)
            logging.info("temp location removed")
        else:
            logging.warning(f"no such path found: {target_location}")
    except FileNotFoundError:
        logging.warning("no such path found: %s", target_location)
        raise
    except PermissionError as e:
        logging.error("permission denied removing %s: %s", target_location, e)
        raise
    except OSError as e:
        logging.error("failed to remove %s: %s", target_location, e)
        raise
    except Exception as e:
        logging.exception(f"Unexpected errors while deleting temp files")
        raise


if __name__ == "__main__":
    time_now = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = Path("logs", f"br_ingestion_{time_now}")
    if not os.path.exists("logs"):
        os.makedirs("logs")
    logging.basicConfig(
        level=logging.INFO,
        filename=log_filename,
        filemode="w",
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info("instantiating environment variables...")
    ev = EnvConfig()
    logging.info("starting ingestion script...")
    parser = argparse.ArgumentParser(
                    prog='br_ingestion',
                    description='Ingest files from object storage into bronze layer of datawarehouse',
                    )
    parser.add_argument('-d', '--date')
    args = parser.parse_args()
    extract_date = args.date
    if extract_date is None:
        extract_date=datetime.now().strftime("%Y-%m-%d")

    
    obj_stg = ObjectStorage(ev)
    obj_stg.list_objects(extract_date)
    obj_stg.download_objects()

    dw = DataWarehouse(ev)
    #dw.read_files(extract_date)
    dw.append_rows(extract_date)

    dq = QualityChecks(ev)
    dq.compare_data(extract_date)

    clean_tmp(ev, extract_date)

    logging.info("script execution completed successfully!!")
    exit(0)
