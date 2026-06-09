import unittest
from unittest.mock import MagicMock, patch
from web_scrapping.framework.base_scraper import BaseScraper
from web_scrapping.framework.models import JobData

class MockScraper(BaseScraper):
    """A scraper for testing the framework logic."""
    def scrape(self):
        yield JobData(
            job_id="test-1",
            company_name=self.company_name,
            url="http://test.com/1",
            title="Test Job 1",
            description="Description 1"
        )
        yield JobData(
            job_id="test-2",
            company_name=self.company_name,
            url="http://test.com/2",
            title="Test Job 2",
            description="Description 2"
        )

class TestFramework(unittest.TestCase):
    @patch("web_scrapping.framework.base_scraper.save_job")
    def test_scraper_run_flow(self, mock_save):
        mock_save.return_value = True
        
        scraper = MockScraper("TestCo")
        scraper.run()
        
        # Verify save_job was called twice (once per yielded job)
        self.assertEqual(mock_save.call_count, 2)
        
        # Verify the first call content
        args, _ = mock_save.call_args_list[0]
        self.assertEqual(args[0], "TestCo")
        content = json.loads(args[1])
        self.assertEqual(content["job_id"], "test-1")

if __name__ == "__main__":
    import json
    unittest.main()
