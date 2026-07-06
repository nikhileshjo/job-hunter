CREATE TABLE IF NOT EXISTS jobs_locations (
    dim_jobs_key TEXT REFERENCES dim_jobs(dim_jobs_key),
    dim_locations_key TEXT REFERENCES dim_locations(dim_locations_key)
);