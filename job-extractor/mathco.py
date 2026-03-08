import requests
import json
from save_file import fileSaver
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

    # fetching job details response and saving the files
    for job in json.loads(job_search_response.text)['data']['data']:
        job_details_payload = {
            "jobUrl": f"{job["_source"]["jobUrl"]}?id={job["_id"]}",
            "externalSource": "CareerSite",
            "campusUrl": "empty",
            "companyId": job["_source"]["companyId"],
            "jobId": job["_id"]
        }
        #print(json.dumps(job_details_payload))
        job_details_response = requests.post(job_details_url, json = job_details_payload, headers = headers)
        file_content = {
            "company_name" : "mathco",
            "job_id" : str(job["_id"]),
            "job_search_response": json.loads(job_search_response.text),
            "job_details": json.loads(job_details_response.text),
        }
        #print(json.dumps(str(file_content)))

        is_file_saved = fileSaver.save_job(extract_date, file_content, "mathco", job['_id'])
        if not is_file_saved:
            print("Failed to save files: ",  job['_id'], job["_source"]["jobUrl"])


    if json.loads(job_search_response.text)['data']['hasMoreData'] == False:
        break
