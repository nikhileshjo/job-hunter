from web_scrapping.framework.base_scraper import BaseScraper
from web_scrapping.framework.models import JobData
import requests
from bs4 import BeautifulSoup


job_search_url = "https://boards-api.greenhouse.io/v1/boards/postman/jobs"
headers = {
    "User-Agent": "Mozilla/5.0"
}


class TemplateScraper(BaseScraper):
    def __init__(self):
        super().__init__(company_name="Postman")

    def scrape(self):
        job_search_response = requests.get(job_search_url, headers=headers)
        jobs = job_search_response.json()["jobs"]
        for job in jobs:
            job_url = job["absolute_url"]
            job_id = job["id"]
            job_title = job["title"]
            job_location = job["location"]["name"]
            job_update = job["updated_at"]

            job_details_payload = requests.get(job_url, headers=headers)
            job_html_page = BeautifulSoup(job_details_payload.text, "html.parser")
            job_html_content = job_html_page.find(class_="job__description")
            job_intro = str(job_html_content.div)
            job_desc = str(job_html_content.div.next_sibling)
            yield JobData(
                job_id = job['id'],
                company_name = self.company_name,
                url = job_url,
                title = job['title'],
                description = job_intro + job_desc,
                location = job_location,
                posted_at = job_update
            )


if __name__ == "__main__":
    scraper = TemplateScraper()
    scraper.run()
