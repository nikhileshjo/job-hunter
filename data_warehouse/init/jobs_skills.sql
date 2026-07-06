CREATE TABLE IF NOT EXISTS jobs_skills (
    dim_jobs_key TEXT REFERENCES dim_jobs(dim_jobs_key),
    dim_skills_key TEXT REFERENCES dim_skills(dim_skills_key)
);