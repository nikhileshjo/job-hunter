CREATE TABLE IF NOT EXISTS dim_generic_job_titles(
    dim_generic_job_titles_key TEXT PRIMARY KEY,
    generic_titles TEXT[],
    generic_description TEXT
);