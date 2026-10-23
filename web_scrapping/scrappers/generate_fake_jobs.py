import json
import random
from datetime import datetime
from faker import Faker
from utils.minio_write import save_job

fake = Faker()

COMPANIES = ["TechFlow", "DataViz", "CloudScale", "ByteBound", "LogicLink"]
TECH_STACKS = ["Python", "SQL", "AWS", "Docker", "Kubernetes", "PostgreSQL", "React", "Node.js", "Java", "Spark"]

def generate_fake_job():
    company = random.choice(COMPANIES)
    job_id = fake.uuid4()
    
    # Simulate structured metadata
    meta_data = {
        "experience_required": f"{random.randint(1, 10)}+ years",
        "remote": random.choice([True, False]),
        "employment_type": random.choice(["Full-time", "Contract", "Part-time"]),
        "languages": random.sample(TECH_STACKS, k=random.randint(2, 5)),
        "salary_range": f"${random.randint(80, 150)}k - ${random.randint(160, 250)}k"
    }

    job_data = {
        "company_name": company,
        "job_id": job_id,
        "url": f"https://{company.lower()}.jobs/{job_id}",
        "job_description": fake.text(max_nb_chars=2000),
        "meta_data": meta_data
    }
    
    return job_data

def main(count=10):
    extract_date = datetime.now().strftime("%Y-%m-%d")
    print(f"Generating {count} fake jobs for {extract_date}...")
    
    for _ in range(count):
        job = generate_fake_job()
        # save_job expects (company_name, file_content, extract_date)
        # file_content should be string
        is_saved = save_job(job["company_name"], json.dumps(job), extract_date)
        if is_saved:
            print(f"Saved: {job['company_name']} - {job['job_id']}")
        else:
            # save_job prints its own errors but returns None/False on failure
            pass

if __name__ == "__main__":
    main(20)
