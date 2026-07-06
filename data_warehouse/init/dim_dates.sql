CREATE TABLE IF NOT EXISTS dim_dates (
    dim_dates_key TEXT PRIMARY KEY,
    date DATE,
    month TEXT,
    year INTEGER,
    day_of_week TEXT,
    day_of_week_nm INTEGER
);