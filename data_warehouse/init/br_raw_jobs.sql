-- File: data_warehouse/init/br_raw_jobs.sql

CREATE TABLE IF NOT EXISTS br_raw_jobs (
    company_name TEXT,
    job_id TEXT,
    job_url TEXT,,
    job_title TEXT,
    job_description TEXT,
    job_location TEXT,
    job_posting_date TEXT,
    meta_data TEXT, -- Stored as text for zero-loss ingestion
    extract_date DATE DEFAULT CURRENT_DATE
);
