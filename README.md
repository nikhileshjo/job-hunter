# 🎯 Job Hunter

Job Hunter is an open-source, multi-layered job-scraping and analytics data pipeline. It extracts job postings and metadata from target careers sites, stores raw data in a local MinIO object storage (S3-compatible data lake), and processes/ingests it into a PostgreSQL data warehouse for analysis (e.g., tracking tool and technology trends).

---

## 🏗️ Architecture & Data Flow

The project follows a modern data engineering pipeline architecture:

```mermaid
graph TD
    A[Target Careers API / Website] -->|Scraper script| B[Python Scraper Engine]
    B -->|Save & Gzip Compress| C[(Local / S3 Data Lake: MinIO)]
    C -->|Extract & Transform| D[Ingestion / ETL Layer]
    D -->|Load to Database| E[(PostgreSQL Warehouse)]
    E -->|Bronze Layer: br_mathco| F[Silver Layer: sl_jobs]
    F -->|Gold Layer: gd_tool_trends| G[Analytics / Visualization]
```

### 📂 Directory Structure

* **`web_scrapping/`**: Houses the Python scraping scripts, target schemas, and object storage writers.
  * [mathco.py](file:///C:/Users/joshi/OneDrive/เอกสาร/projects/job-hunter/web_scrapping/mathco.py): Target scraper for The Math Company job board.
  * [utils/minio_write.py](file:///C:/Users/joshi/OneDrive/เอกสาร/projects/job-hunter/web_scrapping/utils/minio_write.py): Utility module to compress and upload JSON feeds to MinIO.
* **`data_warehouse/`**: Contains resources for the analytical warehouse database.
  * [init/](file:///C:/Users/joshi/OneDrive/เอกสาร/projects/job-hunter/data_warehouse/init/): PostgreSQL initial setup schema files (`br_*`, `sl_*`, `gd_*` tables) and the connection initializer `init.py`.
  * [data_ingestion/](file:///C:/Users/joshi/OneDrive/เอกสาร/projects/job-hunter/data_warehouse/data_ingestion/): Target ETL and loader scripts.
* **[docker-compose.yaml](file:///C:/Users/joshi/OneDrive/เอกสาร/projects/job-hunter/docker-compose.yaml)**: Unified launch configuration for MinIO and PostgreSQL (with PL/Python3 support).

---

## 🔒 Configuration & Security

This project uses a `.env` file to manage sensitive credentials for MinIO and PostgreSQL.

### How to Access or Update Credentials
1.  **Locate the File:** The `.env` file is located in the project root.
2.  **Edit Values:** You can update keys such as `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, and `PG_PASSWORD`.
3.  **Default Passwords:** For local development and portfolio review, the default password `admin` (it is `password` for minio) is used across all services (MinIO, Postgres).

### Security Note
For this portfolio project, `.env` demonstrates environment-based configuration. In a production environment, this file should be excluded from version control (via `.gitignore`) and managed through a secure secret management service.

---

## 🛠️ Getting Started

### Prerequisites

Make sure you have the following installed:
* Python 3.10+
* Docker & Docker Compose
* Required Python packages: `boto3`, `requests`, `sqlalchemy`, `psycopg2-binary`

### 1. Launch Infrastructure

Start the object storage and PostgreSQL services from the root directory:

```bash
# Build custom image and start services
docker compose up -d --build
```

### 2. Configure Environment

Ensure you have a `.env` file in the root directory (see **Configuration & Security** above). Default credentials:
* **MinIO Console**: `http://localhost:9001` (admin/password)
* **pgAdmin**: `http://localhost:5050` (admin@admin.com / admin)
* **Postgres**: `localhost:5432` (admin/admin)

#### pgAdmin (Pre-configured):
1. Open `http://localhost:5050`.
2. Login with `admin@admin.com` / `admin`.
3. The **Job Hunter DB** server is already added.
4. Double-click it and enter password `admin` to connect.

### 3. Initialize the Warehouse

**Note:** The database schema is automatically initialized on the first `docker compose up`. To manually re-run or update the schema:

```bash
cd data_warehouse/init
python init.py
```

### 4. Run the Scraper

Execute the scraper script to collect postings and store them in MinIO:

```bash
python web_scrapping/mathco.py
```

---

## 📊 Data Lakehouse Schema

Below is the ER Diagram of the Silver layer

```mermaid
erDiagram
  fact_jobs {
    fact_jobs_key TEXT PK
    dim_company_key TEXT FK
    dim_jobs_key TEXT FK
    is_active BOOLEAN
    extract_date DATE
  }

  dim_company {
    dim_company_key TEXT PK
    company_name TEXT
  }
  dim_dates {
    dim_dates_key TEXT PK
    date DATE
    month TEXT
    year INTEGER
    day_of_week TEXT
    day_of_week_nm INTEGER
    }
  dim_generic_job_titles{
    dim_generic_job_titles_key TEXT PK
    generic_titles TEXT[]
    generic_description TEXT
  }
  dim_jobs {
    dim_jobs_key TEXT PK
    dim_company_key TEXT FK
    job_id TEXT
    job_title TEXT
    job_url TEXT
    job_posting_date TEXT FK
    experience_in_years DECIMAL
    dim_generic_job_titles_key TEXT FK
    }
  dim_locations {
    dim_locations_key TEXT PK
    country TEXT
    state TEXT
    city TEXT
    }
  dim_skills {
    dim_skills_key TEXT PK
    skill TEXT
    }
  dim_tools {
    dim_tools_key TEXT PK
    tool TEXT
    }
  jobs_locations {
    dim_jobs_key TEXT FK
    dim_locations_key TEXT FK
    }
  jobs_skills {
    dim_jobs_key TEXT FK
    dim_skills_key TEXT FK
    }
  jobs_tools {
    dim_jobs_key TEXT FK
    dim_tools_key TEXT FK
    }
  
  fact_jobs ||--|| dim_jobs : references
  fact_jobs ||--|| dim_company : references

  dim_jobs ||--o{ jobs_locations : has
  dim_jobs ||--o{ jobs_skills : requires
  dim_jobs ||--o{ jobs_tools : uses
  dim_jobs ||--|| dim_company : employed

  jobs_locations }o--|| dim_locations : location
  jobs_skills }o--|| dim_skills : skill
  jobs_tools }o--|| dim_tools : tool

  dim_jobs }o--|| dim_dates : posted_on
  dim_jobs }o--|| dim_generic_job_titles : categorized_as

```

---

## 🤝 Contributing

Contributions to support new scraping sources, improve transformation logic, or enhance analytical metrics are welcome! Feel free to open a Pull Request.

## Errors
1. If you face error while using sqlalchemy, you might see the error: `ModuleNotFoundError: No module named 'psycopg2'` which will not get fixed by a simple `pip install psycopg2`. Try using `pip install psycopg2-binary` instead.