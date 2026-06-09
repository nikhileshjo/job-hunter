from web_scrapping.framework.base_scraper import BaseScraper
from web_scrapping.framework.models import JobData
import requests

class TemplateScraper(BaseScraper):
    def __init__(self):
        super().__init__(company_name="template_company")

    def scrape(self):
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
        pass

if __name__ == "__main__":
    scraper = TemplateScraper()
    scraper.run()
