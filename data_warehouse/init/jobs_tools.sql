CREATE TABLE IF NOT EXISTS jobs_tools (
    dim_jobs_key TEXT REFERENCES dim_jobs(dim_jobs_key),
    dim_tools_key TEXT REFERENCES dim_tools(dim_tools_key)
);