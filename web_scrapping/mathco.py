import requests
import json
from utils.minio_write import save_job
from datetime import datetime

extract_date = str(datetime.now().strftime("%Y-%m-%d"))

job_search_url = "https://public.zwayam.com/jobs/search"
job_details_url = "https://public.zwayam.com/jobs-service/v1/jobs/careersite"

headers = {
    "User-Agent": "Mozilla/5.0"
}

for ind in range(0, 50, 10):
    # fetching job search response
    job_search_payload = {
        "filterCri": json.dumps({
            "paginationStartNo": ind,
            "selectedCall": "sort",
            "sortCriteria": {
                "name": "modifiedDate",
                "isAscending": False
            },
            "anyOfTheseWords": ""
        }),
        "domain": "careers.mathco.com",
        "companyId": "MTUyMTU="
    }

    job_search_response = requests.post(job_search_url, data=job_search_payload, headers=headers)
    jobs = json.loads(job_search_response.text)['data']['data']
    # fetching job details response and saving the files
    for job_index in range(len(jobs)):
        job_id = str(jobs[job_index]["_id"])
        job_url = f"{jobs[job_index]['_source']['jobUrl']}?id={job_id}"
        
        job_details_payload = {
            "jobUrl": job_url,
            "externalSource": "CareerSite",
            "campusUrl": "empty",
            "companyId": jobs[job_index]["_source"]["companyId"],
            "jobId": job_id
        }
        
        job_details_response = requests.post(job_details_url, json=job_details_payload, headers=headers)
        details = json.loads(job_details_response.text)
        
        # Standardized schema
        file_content = {
            "company_name": "mathco",
            "job_id": job_id,
            "url": job_url,
            "job_description": details.get("data", {}).get("jobDescription", ""),
            "meta_data": {
                "job_search_data": jobs[job_index],
                "job_details_raw": details
            }
        }

        is_file_saved = save_job("mathco", json.dumps(file_content), extract_date)
        if not is_file_saved:
            print(f"Failed to save job: {job_id}")
        else:
            print(f"Saved job: {job_id}")


    if json.loads(job_search_response.text)['data']['hasMoreData'] == False:
        break
