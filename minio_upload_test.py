from pathlib import Path

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError


ENDPOINT_URL = "http://localhost:9000"
ACCESS_KEY = "admin"
SECRET_KEY = "password"
BUCKET_NAME = "test-bucket"
OBJECT_NAME = "test-file.txt"
TEST_FILE_PATH = Path("test-file.txt")


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


def main():
    s3_client = create_s3_client()

    TEST_FILE_PATH.write_text(
        "Hello from boto3. This file was uploaded to MinIO.\n",
        encoding="utf-8",
    )

    ensure_bucket_exists(s3_client, BUCKET_NAME)
    s3_client.upload_file(str(TEST_FILE_PATH), BUCKET_NAME, OBJECT_NAME)

    print(f"Uploaded {TEST_FILE_PATH} to s3://{BUCKET_NAME}/{OBJECT_NAME}")


if __name__ == "__main__":
    main()
