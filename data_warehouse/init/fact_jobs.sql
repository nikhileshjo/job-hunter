CREATE TABLE IF NOT EXISTS fact_jobs (
    fact_jobs_key TEXT PRIMARY KEY,
    dim_company_key TEXT REFERENCES dim_company(dim_company_key),
    dim_jobs_key TEXT REFERENCES dim_jobs(dim_jobs_key),
    is_active BOOLEAN,
    extract_date DATE DEFAULT CURRENT_DATE
);