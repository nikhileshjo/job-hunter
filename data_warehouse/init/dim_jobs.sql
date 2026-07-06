CREATE TABLE IF NOT EXISTS dim_jobs (
    dim_jobs_key TEXT PRIMARY KEY,
    dim_company_key TEXT REFERENCES dim_company(dim_company_key),
    job_id TEXT,
    job_title TEXT,
    job_url TEXT,
    job_posting_date TEXT REFERENCES dim_dates(dim_dates_key),
    experience_in_years DECIMAL,
    dim_generic_job_titles_key TEXT REFERENCES dim_generic_job_titles(dim_generic_job_titles_key)
);