# Job Hunter
This project aims to bring all the analytic tools that you might need to decide your next step in career. This tool will help decide what you might want to target next to become the most marketable for a job you like in a company/a section of a company you like to be a part of.

# Why does this tool exist?
I've been on job hunts and they can be a lot of work, especially as someone fresh in the market. But, sometimes, you just want to be part of the next "big thing", but what is the next big thing? How would you know that? And that's what happened with me.
There are websites that do that for you but they just tell the overall industry trend, you can't refine your filters, may be you want to target a certain sector of the industry, but you might not get the right infromation from the website because their data might be skewed by the overall industry trends. So, I wanted to make something that would help me fine tune these filters and have my data set over a generic one.

# Getting started
## Prerequisites
Make sure you have docker or docker compose installed
## Launch Infrastructure

Start the object storage and PostgreSQL services from the root directory:

```bash
# Build custom image and start services
docker compose up -d --build
```
# User manual
## Configure Environment

Ensure you have a `.env` file in the root directory (see **Configuration & Security** above). Default credentials:
* **MinIO Console**: `http://localhost:9001` (admin/password)
* **pgAdmin**: `http://localhost:5050` (admin@admin.com / admin)
* **Postgres**: `localhost:5432` (admin/admin)

### pgAdmin (Pre-configured):
1. Open `http://localhost:5050`.
2. Login with `admin@admin.com` / `admin`.
3. The **Job Hunter DB** server is already added.
4. Double-click it and enter password `admin` to connect.

## Initialize the Warehouse

**Note:** The database schema is automatically initialized on the first `docker compose up`. To manually re-run or update the schema:

```bash
cd data_warehouse/init
python init.py
```