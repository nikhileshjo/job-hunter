import os
import gzip
import json
import boto3
import psycopg2
from botocore.client import Config
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
ENDPOINT_URL = os.getenv("MINIO_ENDPOINT_URL", "http://localhost:9000")
ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "password")
BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "raw-jobs")

PG_DBNAME = os.getenv("PG_DBNAME", "jobs")
PG_USER = os.getenv("PG_USER", "admin")
PG_PASSWORD = os.getenv("PG_PASSWORD", "admin")
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")

PG_CONN_STR = f"dbname={PG_DBNAME} user={PG_USER} password={PG_PASSWORD} host={PG_HOST} port={PG_PORT}"

def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )

def ingest_to_bronze():
    s3 = get_s3_client()
    
    try:
        conn = psycopg2.connect(PG_CONN_STR)
        cur = conn.cursor()
    except Exception as e:
        print(f"Error connecting to Postgres: {e}")
        return

    print(f"Scanning bucket: {BUCKET_NAME}")
    
    # List all objects in the bucket
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=BUCKET_NAME)

    for page in pages:
        if 'Contents' not in page:
            continue
            
        for obj in page['Contents']:
            key = obj['Key']
            if not key.endswith('.json.gz'):
                continue
                
            print(f"Processing: {key}")
            
            # Extract date from path (format: YYYY-MM-DD/company/file.json.gz)
            path_parts = key.split('/')
            file_extract_date = path_parts[0] if len(path_parts) > 1 else datetime.now().strftime("%Y-%m-%d")

            # Download and decompress
            response = s3.get_object(Bucket=BUCKET_NAME, Key=key)
            gzipped_content = response['Body'].read()
            
            try:
                content = gzip.decompress(gzipped_content).decode('utf-8')
                job_data = json.loads(content)
                
                # Insert into Postgres
                insert_query = """
                INSERT INTO br_raw_jobs (company_name, job_id, url, job_description, meta_data, extract_date)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                # meta_data is stored as TEXT in br_raw_jobs as per plan
                meta_data_str = json.dumps(job_data.get("meta_data", {}))
                
                cur.execute(insert_query, (
                    job_data.get("company_name"),
                    job_data.get("job_id"),
                    job_data.get("url"),
                    job_data.get("job_description"),
                    meta_data_str,
                    file_extract_date
                ))
                
            except Exception as e:
                print(f"Error processing {key}: {e}")
                continue
    
    conn.commit()
    cur.close()
    conn.close()
    print("Ingestion complete.")

if __name__ == "__main__":
    ingest_to_bronze()
