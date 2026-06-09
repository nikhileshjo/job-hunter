import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Generator
from .models import JobData
from ..utils.minio_write import save_job

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class BaseScraper(ABC):
    def __init__(self, company_name: str):
        self.company_name = company_name
        self.logger = logging.getLogger(f"Scraper-{company_name}")
        self.extract_date = datetime.now().strftime("%Y-%m-%d")

    @abstractmethod
    def scrape(self) -> Generator[JobData, None, None]:
        """
        Site-specific scraping logic. 
        Should yield JobData objects.
        """
        pass

    def save(self, job: JobData) -> bool:
        """Saves standardized job data using the existing utility."""
        try:
            content = json.dumps(job.to_json())
            return save_job(self.company_name, content, self.extract_date)
        except Exception as e:
            self.logger.error(f"Failed to save job {job.job_id}: {e}")
            return False

    def run(self):
        """Main orchestration loop."""
        self.logger.info(f"Starting scrape for {self.company_name}")
        count = 0
        success = 0
        
        try:
            for job in self.scrape():
                count += 1
                if self.save(job):
                    success += 1
                
            self.logger.info(f"Finished. Processed: {count}, Saved: {success}")
        except Exception as e:
            self.logger.error(f"Critical error during scrape: {e}")
