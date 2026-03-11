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
    jobs = json.loads(job_search_response.text)['data']['data']
    # fetching job details response and saving the files
    for job_index in range(len(jobs)):
        job_details_payload = {
            "jobUrl": f"{jobs[job_index]["_source"]["jobUrl"]}?id={jobs[job_index]["_id"]}",
            "externalSource": "CareerSite",
            "campusUrl": "empty",
            "companyId": jobs[job_index]["_source"]["companyId"],
            "jobId": jobs[job_index]["_id"]
        }
        #print(json.dumps(job_details_payload))
        job_details_response = requests.post(job_details_url, json = job_details_payload, headers = headers)
        file_content = {
            "company_name" : "mathco",
            "job_id" : str(jobs[job_index]["_id"]),
            "job_search_response": jobs[job_index],
            "job_details": json.loads(job_details_response.text),
        }
        #print(json.dumps(str(file_content)))

        is_file_saved = fileSaver.save_job(extract_date, file_content, "mathco", jobs[job_index]["_id"])
        if not is_file_saved:
            print("Failed to save files: ",  jobs[job_index]['_id'], jobs[job_index]["_source"]["jobUrl"])


    if json.loads(job_search_response.text)['data']['hasMoreData'] == False:
        break
