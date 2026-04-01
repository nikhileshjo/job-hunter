from sqlalchemy import create_engine

# Creating temperory DB
engine = create_engine("postgresql+psycopg2://scott:tiger@localhost/", echo=True)


payload_vals = []
for job in jobs:
    job_params = {
        "job_id" : job["jobId"],
        "job_title" : job["jobTitle"]                       
    }
    payload_vals.append(job_params)
# Open connection
# This will commit automatically at the end if no errors
with engine.begin() as conn:
    conn.execute(
        text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        [{"x": 1, "y": 1}, {"x": 2, "y": 4}],
    )