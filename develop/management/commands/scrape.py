import logging
import requests
import sys
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
from datetime import datetime

from django.core.management.base import BaseCommand

from develop.management.commands.actions import *
from develop.management.commands.location import *
from develop.models import *

logger = logging.getLogger("django")


class Command(BaseCommand):
    def handle(self, *args, **options):
        # ////
        # Development Site Scraper
        # \\\\
        control = Control.objects.get(id=1)
        if control.scrape:
            n = datetime.now()
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": Web scrape started.")

            sr_page_link = "https://raleighnc.gov/services/zoning-planning-and-development/site-review-cases"
            aad_page_link = "https://raleighnc.gov/SupportPages/administrative-alternate-design-cases"
            zon_page_link = "https://raleighnc.gov/SupportPages/zoning-cases"
            tc_page_link = "https://raleighnc.gov/SupportPages/text-change-cases"

            zoning_requests(get_page_content(zon_page_link))
            admin_alternates(get_page_content(aad_page_link))
            text_changes_cases(get_page_content(tc_page_link))
            site_reviews(get_page_content(sr_page_link))

            logger.info(n.strftime("%H:%M %m-%d-%y") + ": Web scrape finished.")


def get_page_content(page_link):
    n = datetime.now()

    try:
        page_response = requests.get(page_link, timeout=10)
    except requests.exceptions.RequestException as e:
        logger.info(n.strftime("%H:%M %m-%d-%y") + ": Connection problem to " + page_link)
        logger.info(e)
        sys.exit(1)

    if page_response.status_code == 200:
        return BeautifulSoup(page_response.content, "html.parser")
    else:
        message = "scrape.get_page_content did not return 200 at " + n.strftime("%H:%M %m-%d-%y")
        send_email_notice(message, email_admins())
        return None


def get_rows_in_table(table, page):
    if table is not None:
        # We don't want the first row as that is the header row
        return table.find_all("tr")[1:]


def get_case_number_from_row(row_tds):
    try:
        # If the case number is a link:
        case_number = row_tds[0].find("a").string
        return case_number
    except:
        # in rare cases the case number is not a link
        return row_tds[0].string


def get_contact(content):
    # content usually is a link but if not we need to account for a non-link piece of text
    contact = content.find("a")

    if contact:
        return contact.get_text().strip()
    else:
        if content.text.strip() != "":
            return content.text.strip()
        return None


def get_generic_link(content):
    # This is used to grab the hyperlink out of a snippet of code
    # This assumes the entire link is in there vs a relative link.
    if len(content.find_all("a")) == 0:
        return None
    elif len(content.find_all("a")) == 1:
        return content.find("a")["href"].strip().replace(" ", "%20")
    else:
        return None


def get_contact_url(content):
    # contact urls are relative
    # Ex: "<td><a href="/directory?action=search&amp;firstName=Jason&amp;lastName=Hardin">Hardin</a></td>"
    if content.find("a"):
        return "https://raleighnc.gov" + content.find("a")["href"].replace(" ", "")
    else:
        return None


def determine_if_known_case(known_cases, case_number, project_name, cac):
    # Go through all of the cases. Criteria of a match:
    # 1. fuzz.ratio(case_number, sr_case.case_number) > 90
    # 2. fuzz.ratio(project_name, sr_case.project_name) > 90
    # 3. fuzz.ratio(cac, sr_case.cac) > 90
    # 2 of 3 need to be true
    for case in known_cases:
        total_score = 0
        case_number_score = fuzz.ratio(case_number, case.case_number)
        project_name_score = fuzz.ratio(project_name, case.project_name)

        # TCs don't use CAC
        if cac:
            cac_score = fuzz.ratio(cac, case.cac)
        else:
            cac_score = 0

        if case_number_score >= 90:
            total_score += 1
        if project_name_score >= 90:
            total_score += 1
        if cac_score >= 90:
            total_score += 1

        if total_score >= 2 and case_number_score == 100:
            return case

    return None


def site_reviews(page_content):
    # Site Review tables
    sr_tables = page_content.find_all("table")

    for sr_table in sr_tables:
        sr_rows = get_rows_in_table(sr_table, "SR")

        # For each row, get the values then check if we already know about this item
        # If we do not, then add it to the DB
        # If we do, check for differences and update it
        for sr_row in sr_rows:
            row_tds = sr_row.find_all("td")

            case_number = get_case_number_from_row(row_tds)
            case_url = get_generic_link(row_tds[0])

            project_name = row_tds[1].get_text().strip()
            cac = row_tds[2].get_text().strip()
            status = row_tds[3].get_text().strip()
            contact = get_contact(row_tds[4])
            contact_url = get_contact_url(row_tds[4])

            # If any of these variables are None, log it and move on.
            if not case_number or not case_url or not project_name or not cac or not status or not contact:
                scraped_info = [["row_tds", row_tds],
                                ["case_number", case_number],
                                ["case_url", case_url],
                                ["project_name", project_name],
                                ["cac", cac],
                                ["status", status],
                                ["contact", contact],
                                ["contact_url", contact_url]]
                message = "scrape.site_reviews: Problem scraping this row"
                message += scraped_info
                logger.info(message)
                send_email_notice(message, email_admins())

                # Reminder: continue will move this to the next loop iteration.
                continue

            known_sr_cases = SiteReviewCases.objects.all()
            known_sr_case = determine_if_known_case(known_sr_cases, case_number, project_name, cac)

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
                    logger.info("Updating a site case (" + str(known_sr_case) + ")")
                    logger.info("scrape case_number:" + case_number)
                    logger.info("scrape project_name:" + project_name)
                    logger.info("scrape cac: " + cac)
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


def admin_alternates(page_content):
    # Administrative Alternate Requests
    aads_tables = page_content.find_all("table")

    for aads_table in aads_tables:
        aads_rows = get_rows_in_table(aads_table, "AAD")

        # For each row, get the values then check if we already know about this item
        # If we do not, then add it to the DB
        # If we do, check for differences and update if
        for aads_row in aads_rows:
            row_tds = aads_row.find_all("td")

            case_number = get_case_number_from_row(row_tds)
            case_url = get_generic_link(row_tds[0])

            project_name = row_tds[1].get_text().strip()
            cac = row_tds[2].get_text().strip()
            status = row_tds[3].get_text().strip()
            contact = get_contact(row_tds[4])
            contact_url = get_contact_url(row_tds[4])

            # If any of these variables are None, log it and move on.
            if not case_number or not case_url or not project_name or not cac or not status or not contact or not \
                    contact_url:
                scraped_info = [["row_tds", row_tds],
                                ["case_number", case_number],
                                ["case_url", case_url],
                                ["project_name", project_name],
                                ["cac", cac],
                                ["status", status],
                                ["contact", contact],
                                ["contact_url", contact_url]]
                message = "scrape.admin_alternates: Problem scraping this row"
                message += scraped_info
                logger.info(message)
                send_email_notice(message, email_admins())

                continue

            known_aad_cases = AdministrativeAlternates.objects.all()
            known_aad_case = determine_if_known_case(known_aad_cases, case_number, project_name, cac)

            # if known_tc_case was found, check for differences
            # if known_tc_case was not found, then we assume a new one was added
            # need to create
            if known_aad_case:
                # Check for difference between known_tc_case and the variables
                # Assume that the aad_case number doesn't change.
                if (
                    not fields_are_same(known_aad_case.case_url, case_url) or
                    not fields_are_same(known_aad_case.project_name, project_name) or
                    not fields_are_same(known_aad_case.cac, cac) or
                    not fields_are_same(known_aad_case.status, status) or
                    not fields_are_same(known_aad_case.contact, contact) or
                    not fields_are_same(known_aad_case.contact_url, contact_url)
                ):
                    known_aad_case.case_url = case_url
                    known_aad_case.project_name = project_name
                    known_aad_case.cac = cac
                    known_aad_case.status = status
                    known_aad_case.contact = contact
                    known_aad_case.contact_url = contact_url

                    known_aad_case.save()
                    logger.info("**********************")
                    logger.info("Updating an AAD case (" + str(known_aad_case) + ")")
                    logger.info("scrape case_number:" + case_number)
                    logger.info("scrape project_name:" + project_name)
                    logger.info("scrape cac: " + cac)
                    logger.info("**********************")

            else:
                # create a new instance
                logger.info("**********************")
                logger.info("Creating new site case")
                logger.info("case_number:" + case_number)
                logger.info("project_name:" + project_name)
                logger.info("cac: " + cac)
                logger.info("**********************")

                AdministrativeAlternates.objects.create(case_number=case_number,
                                                        case_url=case_url,
                                                        project_name=project_name,
                                                        cac=cac,
                                                        status=status,
                                                        contact=contact,
                                                        contact_url=contact_url)
            
            
def text_changes_cases(page_content):
    # Text Change Cases
    tc_tables = page_content.find_all("table")

    for tc_table in tc_tables:
        tc_rows = get_rows_in_table(tc_table, "TCC")

        for tc in tc_rows:
            row_tds = tc.find_all("td")

            case_number = get_case_number_from_row(row_tds)
            case_url = get_generic_link(row_tds[0])

            project_name = row_tds[1].get_text().strip()
            status = row_tds[2].get_text().strip()
            contact = get_contact(row_tds[3])
            contact_url = get_contact_url(row_tds[3])

            # Found a case where the TC name was not a link. We'll set it to something generic in the mean time.
            if not case_url:
                case_url = "NA"

            # If any of these variables are None, log it and move on.
            if not case_number or not case_url or not project_name or not status or not contact or not contact_url:
                scraped_info = [["row_tds", row_tds],
                                ["case_number", case_number],
                                ["case_url", case_url],
                                ["project_name", project_name],
                                ["status", status],
                                ["contact", contact],
                                ["contact_url", contact_url]]
                message = "scrape.text_changes_cases: Problem scraping this row"
                message += scraped_info
                logger.info(message)
                send_email_notice(message, email_admins())

                continue

            known_tc_cases = TextChangeCases.objects.all()
            known_tc_case = determine_if_known_case(known_tc_cases, case_number, project_name, cac=None)

            # if known_tc_case was found, check for differences
            # if known_tc_case was not found, then we assume a new one was added
            # need to create
            if known_tc_case:
                # Check for difference between known_tc_case and the variables
                # Assume that the tc_case number doesn't change.
                if (
                    not fields_are_same(known_tc_case.case_url, case_url) or
                    not fields_are_same(known_tc_case.project_name, project_name) or
                    not fields_are_same(known_tc_case.status, status) or
                    not fields_are_same(known_tc_case.contact, contact) or
                    not fields_are_same(known_tc_case.contact_url, contact_url)
                ):
                    known_tc_case.case_url = case_url
                    known_tc_case.project_name = project_name
                    known_tc_case.status = status
                    known_tc_case.contact = contact
                    known_tc_case.contact_url = contact_url

                    known_tc_case.save()
                    logger.info("**********************")
                    logger.info("Updating a text change case (" + str(known_tc_case) + ")")
                    logger.info("scrape case_number:" + case_number)
                    logger.info("scrape project_name:" + project_name)
                    logger.info("**********************")

            else:
                # create a new instance
                logger.info("**********************")
                logger.info("Creating new site case")
                logger.info("case_number:" + case_number)
                logger.info("project_name:" + project_name)
                logger.info("**********************")

                TextChangeCases.objects.create(case_number=case_number,
                                               case_url=case_url,
                                               project_name=project_name,
                                               status=status,
                                               contact=contact,
                                               contact_url=contact_url)


def zoning_requests(page_content):
    # Zoning Requests
    zoning_tables = page_content.find_all("table")

    for zoning_table in zoning_tables:
        zoning_rows = get_rows_in_table(zoning_table, "Zoning")

        for i in range(0, len(zoning_rows), 2):
            # First row is zoning_rows[i]
            # Second row is zoning_rows[i+1]
            info_row_tds = zoning_rows[i].find_all("td")
            status_row_tds = zoning_rows[i + 1].find_all("td")

            # This gets the zoning case label.
            # Some cases have a master plan case so label ends up like "Z-14-19MP-1-19"
            case_number = info_row_tds[0].get_text().split("\n")[0]
            if "mp" in case_number.lower():
                case_number = case_number.lower().split("mp")[0]

            location = info_row_tds[1].get_text()
            location_url = get_generic_link(info_row_tds[1])
            # cac = info_row_tds[2].get_text() Now changed to council district which we don't want
            contact = get_contact(info_row_tds[3])
            status = status_row_tds[0].get_text()

            zoning_case = case_number.split("\n")[0]
            plan_url = get_generic_link(info_row_tds[0])

            # Break up zoning_case
            scrape_num = zoning_case.split("-")[1]
            scrape_year = "20" + zoning_case.split("-")[2][:2]

            # If any of these variables are None, log it and move on.
            # Remarks come from the API
            # Status is from the web scrape
            if not case_number or not location or not zoning_case or not status:
                scraped_info = [["info_row_tds", info_row_tds],
                                ["status_row_tds", status_row_tds],
                                ["case_number", case_number],
                                ["location", location],
                                ["location_url", location_url],
                                ["contact", contact],
                                ["status", status],
                                ["plan_url", plan_url]]
                message = "scrape.zoning_requests: Problem scraping this row"
                message += scraped_info
                logger.info(message)
                send_email_notice(message, email_admins())

                continue

            # First check if we already have this zoning request
            if Zoning.objects.filter(zpnum=int(scrape_num), zpyear=int(scrape_year)).exists():
                known_zon = Zoning.objects.get(zpyear=scrape_year, zpnum=scrape_num)

                # If the status, plan_url, or location_url have changed, update the zoning request
                if (not fields_are_same(known_zon.status, status) or
                        not fields_are_same(known_zon.plan_url, plan_url) or
                        not fields_are_same(known_zon.location_url, location_url)):
                    # A zoning web scrape only updates status and/or plan_url and/or location_url
                    known_zon.status = status
                    known_zon.plan_url = plan_url
                    known_zon.location_url = location_url

                    # If we don't know the CAC, let's try and "calculate" it using the pin from location_url
                    if not known_zon.cac and known_zon.cac_override:
                        known_zon.cac_override = calculate_cac(location_url)

                    known_zon.save()

                    # Want to log what the difference is
                    difference = "*"
                    if not fields_are_same(known_zon.status, status):
                        difference += "Difference: " + str(known_zon.status) + " changed to " + str(status)
                    if not fields_are_same(known_zon.plan_url, plan_url):
                        difference += "Difference: " + str(known_zon.plan_url) + " changed to " + str(plan_url)
                    if not fields_are_same(known_zon.location_url, location_url):
                        difference += "Difference: " + str(known_zon.location_url) + " changed to " + str(location_url)

                    logger.info("**********************")
                    logger.info("Updating a zoning request")
                    logger.info("known_zon: " + str(known_zon))
                    logger.info(difference)
                    logger.info("**********************")

            else:
                # We don't know about it so create a new zoning request
                logger.info("**********************")
                logger.info("Creating new Zoning Request from web scrape")
                logger.info("case_number:" + zoning_case)
                logger.info("location: " + location)
                logger.info("**********************")

                # Try to calculate CAC
                cac_calc = calculate_cac(location_url)

                Zoning.objects.create(zpyear=scrape_year,
                                      zpnum=scrape_num,
                                      status=status,
                                      cac_override=cac_calc,
                                      location=location,
                                      received_by=contact,
                                      plan_url=plan_url,
                                      location_url=location_url)
