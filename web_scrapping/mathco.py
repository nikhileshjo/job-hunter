import requests
import json
from .framework.base_scraper import BaseScraper
from .framework.models import JobData

# extract_date = str(datetime.now().strftime("%Y-%m-%d"))

job_search_url = "https://public.zwayam.com/jobs/search"
job_details_url = "https://public.zwayam.com/jobs-service/v1/jobs/careersite"

headers = {
    "User-Agent": "Mozilla/5.0"
}


class MathCoScraper(BaseScraper):
    def __init__(self):
        super().__init__(company_name="MathCo")

    def scrape(self):
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
                job_absolute_url = "https://careers.mathco.com/mathco/jobview/" + jobs[job_index]['_source']['jobUrl']
                job_details_payload = {
                    "jobUrl": job_url,
                    "externalSource": "CareerSite",
                    "campusUrl": "empty",
                    "companyId": jobs[job_index]["_source"]["companyId"],
                    "jobId": job_id
                }
                
                job_details_response = requests.post(job_details_url, json=job_details_payload, headers=headers)
                details = json.loads(job_details_response.text)
                
                yield JobData(
                    job_id=job_id,
                    company_name=self.company_name,
                    url= job_absolute_url,
                    title=jobs[job_index]['_source']['jobTitle'],
                    description=details.get("data", {}).get("jobDescription", ""),
                    location= details["location"],
                    posted_at= details["createDate"],
                    meta_data= details
                    )

            if json.loads(job_search_response.text)['data']['hasMoreData'] == False:
                break
        """
        Implementation logic goes here.
        1. Fetch data (JSON/HTML)
        2. Parse data
        3. Yield JobData objects
        """
        # Example:
        # response = requests.get("https://api.example.com/jobs")
        # jobs = response.json()
        # for job in jobs:
        #     yield JobData(
        #         job_id=job['id'],
        #         company_name=self.company_name,
        #         url=f"https://example.com/jobs/{job['id']}",
        #         title=job['title'],
        #         description=job['body']
        #     )
        # pass

if __name__ == "__main__":
    scraper = MathCoScraper()
    scraper.run()
