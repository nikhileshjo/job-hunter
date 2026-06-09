import unittest
from unittest.mock import patch, MagicMock
# Replace 'your_scraper' with your actual file name
# from web_scrapping.your_scraper import YourScraper
from web_scrapping.framework.models import JobData

class TestYourScraper(unittest.TestCase):
    
    @patch("requests.get") # or requests.post
    def test_scrape_parsing(self, mock_get):
        """
        TDD: Define how your scraper should parse a mock response 
        BEFORE you write the scraping logic.
        """
        # 1. Setup Mock Response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "jobs": [
                {"id": "123", "title": "Software Engineer", "desc": "We need someone..."}
            ]
        }
        mock_get.return_value = mock_response

        # 2. Instantiate Scraper
        # scraper = YourScraper()
        
        # 3. Verify results
        # results = list(scraper.scrape())
        # self.assertEqual(len(results), 1)
        # self.assertEqual(results[0].job_id, "123")
        pass

if __name__ == "__main__":
    unittest.main()
