from web_scrapping.framework.base_scraper import BaseScraper
from web_scrapping.framework.models import JobData
import requests
import json

job_search_url = "https://fractal.wd1.myworkdayjobs.com/wday/cxs/fractal/Careers/jobs"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:152.0) Gecko/20100101 Firefox/152.0",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Referer": "https://fractal.wd1.myworkdayjobs.com/en-US/Careers/jobs",
    "Origin": "https://fractal.wd1.myworkdayjobs.com"
}

class TemplateScraper(BaseScraper):
    def __init__(self):
        super().__init__(company_name="fractal")

    def scrape(self):
        """
        Implementation logic goes here.
        1. Fetch data (JSON/HTML)
        2. Parse data
        3. Yield JobData objects
        """
        for ind in range(0, 41, 20):
            # fetching job search response
            job_search_payload = {
                        "appliedFacets": {},
                        "limit": 20,
                        "offset": ind,
                        "searchText": ""
                    }
            
            job_search_response = requests.post(
                                    job_search_url, 
                                    json=job_search_payload, 
                                    headers=headers
                                )
            jobs = json.loads(job_search_response.text)["jobPostings"]
            for job in jobs:
                job_id = job["bulletFields"][0]
                job_rel_url = job["externalPath"]
                job_absolute_url = job_search_url[:-5] + job_rel_url

                job_details_response = requests.get(job_absolute_url, headers=headers)
                details = json.loads(job_details_response.text)

                yield JobData(
                    job_id=job_id,
                    company_name=self.company_name,
                    url= "https://fractal.wd1.myworkdayjobs.com/en-US/Careers"+ job_rel_url,
                    title=details["jobPostingInfo"]["title"],
                    description=details["jobPostingInfo"]["jobDescription"],
                    location= details["jobPostingInfo"]["location"],
                    posted_at= details["jobPostingInfo"]["startDate"],
                    meta_data= details
                    )

        
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
    scraper = TemplateScraper()
    scraper.run()
