# ///
# This command is used to query the API, compare the results with the DB and make appropriate changes.
# \\\
import logging, requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
from datetime import datetime

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
        n = datetime.now()
        logger.info(n.strftime("%H:%M %m-%d-%y") + ": Web scrape started.")

        page_link = "https://www.raleighnc.gov/development"

        page_response = requests.get(page_link, timeout=10)

        if page_response.status_code == 200:
            page_content = BeautifulSoup(page_response.content, "html.parser")

            # Site Reviews
            try:
                site_review_title = page_content.find("h3", {"id": "SiteReviewCases(SR)"})
            except:
                logger.info("Couldn't find #SiteReviewCases(SR)")

            # drill down
            try:
                site_review_section = site_review_title.findNext("div")
                sr_table = site_review_section.find("table")
                sr_table_tbody = sr_table.find("tbody")
                sr_rows = sr_table_tbody.findAll("tr")
            except:
                logger.info("Problem getting to the #SiteReviewCases(SR) table trs")
                if site_review_section:
                    logger.info("site_review_section:" + site_review_section)
                if sr_table:
                    logger.info("sr_table: " + sr_table)
                if sr_table_tbody:
                    logger.info("sr_table_tbody: " + sr_table_tbody)
                if sr_rows:
                    logger.info("sr_rows: " + sr_rows)

            # For each row, get the values then check if we already know about this item
            # If we do not, then add it to the DB
            # If we do, check for differences and update if
            for sr_row in sr_rows:
                row_tds = sr_row.findAll("td")

                case_number = row_tds[0].find("a").string
                case_url = page_link + row_tds[0].find("a")["href"]
                project_name = row_tds[1].get_text().strip()
                cac = row_tds[2].get_text().strip()
                status = row_tds[3].get_text().strip()
                contact = row_tds[4].find("a").get_text().strip()
                contact_url = page_link + row_tds[4].find("a")["href"]

                # If any of these variables are None, log it and move on.
                if not case_number or not case_url or not project_name or not cac or not status or not contact or not contact_url:
                    logger.info("********** Problem scraping this row **********")
                    logger.info(str(row_tds))
                    logger.info("case_number scrape: " + str(case_number))
                    logger.info("case_url scrape: " + str(case_url))
                    logger.info("project_name scrape: " + str(project_name))
                    logger.info("cac scrape: " + str(cac))
                    logger.info("status scrape: " + str(status))
                    logger.info("contact scrape: " + str(contact))
                    logger.info("contact_url scrape: " + str(contact_url))

                    continue

                known_sr_cases = SiteReviewCases.objects.all()

                # go through all of them. Criteria of a match:
                # 1. fuzz.ratio(case_number, sr_case.case_number) > 90
                # 2. fuzz.ratio(project_name, sr_case.project_name) > 90
                # 3. fuzz.ratio(cac, sr_case.cac) > 90
                # 2 of 3 need to be true
                known_sr_case = None

                for sr_case in known_sr_cases:
                    total_score = 0
                    case_number_score = fuzz.ratio(case_number, sr_case.case_number)
                    project_name_score = fuzz.ratio(project_name, sr_case.project_name)
                    cac_score = fuzz.ratio(cac, sr_case.cac)

                    if case_number_score >= 90:
                        total_score += 1
                    if project_name_score >= 90:
                        total_score += 1
                    if cac_score >= 90:
                        total_score += 1

                    # sr_case is indeed the same as the scanned info
                    if total_score >= 2 and project_name_score > 50:
                        known_sr_case = sr_case
                        break

                # if known_sr_case was found, check for differences
                # if known_sr_case was not found, then we assume a new one was added
                # need to create
                if known_sr_case:
                    # Check for difference between known_sr_case and the variables
                    # Assume that the sr_case number doesn't change.
                    if (
                        not fields_are_same(known_sr_case.case_url, case_url) or
                        not fields_are_same(known_sr_case.project_name, project_name) or
                        not fields_are_same(known_sr_case.cac, cac) or
                        not fields_are_same(known_sr_case.status, status) or
                        not fields_are_same(known_sr_case.contact, contact) or
                        not fields_are_same(known_sr_case.contact_url, contact_url)
                    ):
                            known_sr_case.case_url = case_url
                            known_sr_case.project_name = project_name
                            known_sr_case.cac = cac
                            known_sr_case.status = status
                            known_sr_case.contact = contact
                            known_sr_case.contact_url = contact_url

                            known_sr_case.save()
                            logger.info("**********************")
                            logger.info("Updating a site case")
                            logger.info("case_number:" + case_number)
                            logger.info("project_name:" + project_name)
                            logger.info("cac: " + cac)
                            logger.info("**********************")

                else:
                    # create a new instance
                    logger.info("**********************")
                    logger.info("Creating new site case")
                    logger.info("case_number:" + case_number)
                    logger.info("project_name:" + project_name)
                    logger.info("cac: " + cac)
                    logger.info("**********************")

                    SiteReviewCases.objects.create(case_number=case_number,
                                                   case_url=case_url,
                                                   project_name=project_name,
                                                   cac=cac,
                                                   status=status,
                                                   contact=contact,
                                                   contact_url=contact_url)
        else:
            # Send email alert saying that we could not reach the development page, did not get 200
            pass

        n = datetime.now()
        logger.info(n.strftime("%H:%M %m-%d-%y") + ": Web scrape finished.")
