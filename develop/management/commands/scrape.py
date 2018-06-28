# ///
# This command is used to query the API, compare the results with the DB and make appropriate changes.
# \\\
import logging, requests
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from django.core.mail import send_mail

from develop.management.commands.actions import *
from develop.models import *

logger = logging.getLogger("django")


class Command(BaseCommand):
    def handle(self, *args, **options):
        # ////
        # Development Site Scraper
        # \\\\
        page_link = "https://www.raleighnc.gov/development"

        page_response = requests.get(page_link, timeout=10)

        if page_response.status_code == 200:
            page_content = BeautifulSoup(page_response.content, "html.parser")

            # Site Reviews
            site_review_title = page_content.find("h3", {"id": "SiteReviewCases(SR)"})

            # drill down
            site_review_section = site_review_title.findNext("div")
            sr_table = site_review_section.find("table")
            sr_table_tbody = sr_table.find("tbody")
            sr_rows = sr_table_tbody.findAll("tr")

            # For each row, get the values then check if we already know about this item
            # If we do not, then add it to the DB
            # If we do, check for differences and update if
            for sr_row in sr_rows:
                row_tds = sr_row.findAll("td")

                case_number = row_tds[0].find("a").string
                case_url = page_link + row_tds[0].find("a")["href"]
                project_name = row_tds[1].string
                cac = row_tds[2].string
                status = row_tds[3].string
                contact = row_tds[4].find("a").string
                contact_url = page_link + row_tds[4].find("a")["href"]

                try:
                    
        else:
            # Send email alert saying that we could not reach the development page, did not get 200
            pass
