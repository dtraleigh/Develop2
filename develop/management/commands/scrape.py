# ///
# This command is used to query the API, compare the results with the DB and make appropriate changes.
# \\\
import logging, requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

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
                    known_sr_cases = SiteReviewCases.objects.all()

                    # go through all of them. Criteria of a match:
                    # 1. fuzz.ratio(case_number, sr_case.case_number) > 90
                    # 2. fuzz.ratio(project_name, sr_case.project_name) > 90
                    # 3. fuzz.ratio(cac, sr_case.cac) > 90
                    # 2 of 3 need to be true
                    for sr_case in known_sr_cases:
                        case_number_score = fuzz.ratio(case_number, sr_case.case_number) > 90
                        project_name_score = fuzz.ratio(project_name, sr_case.project_name) > 90
                        cac_score = fuzz.ratio(cac, sr_case.cac) > 90

                        total_score = 0

                        if case_number_score >= 90:
                            total_score += 1
                        if project_name_score >= 90:
                            total_score += 1
                        if cac_score >= 90:
                            total_score += 1

                        # sr_case is indeed the same as the scanned info
                        if total_score >= 2:
                            known_sr_case = sr_case
                            break

                    # if known_sr_case was found, check for differences
                    # if known_sr_case was not found, then we assume a new one was added
                    # need to create
                    if known_sr_case:
                        # check for difference between known_sr_case and the variables
                    else:
                        # create a new instance


        else:
            # Send email alert saying that we could not reach the development page, did not get 200
            pass
