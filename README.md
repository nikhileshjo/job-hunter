# Job Hunter
Job hunter is an open-source job finding engine.

## Minio - Raw data storage
- When we find jobs by scrapping from the internet, the files that we extract(JSON) will be stored in this place.
- This storage is complient with S3 bucket and hence, if we were to scale this to AWS, our code won't have to change a lot.