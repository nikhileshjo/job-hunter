-- File: data_warehouse/init/br_raw_jobs.sql

CREATE TABLE IF NOT EXISTS br_raw_jobs (
    company_name TEXT,
    job_id TEXT,
    url TEXT,
    job_description TEXT,
    meta_data TEXT, -- Stored as text for zero-loss ingestion
    extract_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
