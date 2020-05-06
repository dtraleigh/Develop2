from django.test import SimpleTestCase
from develop.management.commands.scrape import *


class ScrapeTestCase(SimpleTestCase):
    def test_get_page_content_200(self):
        # quick test to check that the sites we are scraping are returning data
        websites_used = [
            "https://raleighnc.gov/services/zoning-planning-and-development/site-review-cases",
            "https://raleighnc.gov/SupportPages/administrative-alternate-design-cases",
            "https://raleighnc.gov/SupportPages/zoning-cases",
            "https://raleighnc.gov/SupportPages/text-change-cases",
            ]

        for url in websites_used:
            self.assertIsNotNone(get_page_content(url))