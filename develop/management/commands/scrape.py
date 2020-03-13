# ///
# This command is used to query the API, compare the results with the DB and make appropriate changes.
# \\\
import logging, requests, sys
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
        # Future: Send email alert saying that we could not reach the development page, did not get 200
        return None


def get_correct_url(list_of_a_tags, label):
    list_of_urls = []

    for tag in list_of_a_tags:
        list_of_urls.append(tag["href"])

    zoning_case_from_label = label.split('\n')[0]

    best_match_url = ["", 0]

    for url in list_of_urls:
        pdf_file = url.split('/')[-1]
        zoning_case_from_url = pdf_file.split('.')[0]

        score = fuzz.ratio(zoning_case_from_label.lower(), zoning_case_from_url.lower())

        if score > best_match_url[1]:
            best_match_url = [url, score]

    return best_match_url[0]


def get_rows_in_table(table, page):
    try:
        table_tbody = table.find("tbody")
        table_rows = table_tbody.findAll("tr")
        return table_rows
    except:
        logger.info("Problem getting to a table trs on page, " + page)
        if table:
            logger.info("table: " + table)
        if table_tbody:
            logger.info("table_tbody: " + table_tbody)
        if table_rows:
            logger.info("rows: " + table_rows)


def get_case_number_from_row(row_tds):
    try:
        # If the case number is a link:
        case_number = row_tds[0].find("a").string
        return case_number
    except:
        # in rare cases the case number is not a link
        return row_tds[0].string


def get_case_url_from_row(row_tds):
    try:
        # If the case number is a link:
        case_url = row_tds[0].find("a")["href"].strip().replace(" ", "%20")
        return case_url
    except:
        # in rare cases the case number is not a link
        return ""


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
        if cac:
            cac_score = fuzz.ratio(cac, case.cac)

        if case_number_score >= 90:
            total_score += 1
        if project_name_score >= 90:
            total_score += 1
        if cac_score >= 90:
            total_score += 1

        # if total_score >= 2 and project_name_score > 50:
        if total_score >= 2 and case_number_score == 100:
            return case

    return None


def site_reviews(page_content):
    # Site Review tables
    sr_tables = page_content.findAll("table")

    for sr_table in sr_tables:
        sr_rows = get_rows_in_table(sr_table, "SR")

        # For each row, get the values then check if we already know about this item
        # If we do not, then add it to the DB
        # If we do, check for differences and update if
        for sr_row in sr_rows:
            row_tds = sr_row.findAll("td")

            case_number = get_case_number_from_row(row_tds)
            case_url = get_case_url_from_row(row_tds)

            project_name = row_tds[1].get_text().strip()
            cac = row_tds[2].get_text().strip()
            status = row_tds[3].get_text().strip()
            contact = row_tds[4].find("a").get_text().strip()
            contact_url = "https://raleighnc.gov" + row_tds[4].find("a")["href"].replace(" ", "")

            # Caught an instance where the site review had an empty CAC so if that is the case, let's set it to 'Unspecified'
            if not cac:
                cac = "Unspecified"

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
    aads_tables = page_content.findAll("table")

    for aads_table in aads_tables:
        aads_rows = get_rows_in_table(aads_table, "AAD")

        # For each row, get the values then check if we already know about this item
        # If we do not, then add it to the DB
        # If we do, check for differences and update if
        for aads_row in aads_rows:
            row_tds = aads_row.findAll("td")

            case_number = get_case_number_from_row(row_tds)
            case_url = get_case_url_from_row(row_tds)

            project_name = row_tds[1].get_text().strip()
            cac = row_tds[2].get_text().strip()
            status = row_tds[3].get_text().strip()
            contact = row_tds[4].find("a").get_text().strip()
            contact_url = row_tds[4].find("a")["href"].replace(" ", "")

            # If any of these variables are None, log it and move on.
            if not case_number or not case_url or not project_name or not cac or not status or not contact or not \
                    contact_url:
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
    tc_tables = page_content.findAll("table")

    for tc_table in tc_tables:
        tc_rows = get_rows_in_table(tc_table, "TCC")

        # For each row, get the values then check if we already know about this item
        # If we do not, then add it to the DB
        # If we do, check for differences and update if
        for tc in tc_rows:
            row_tds = tc.findAll("td")

            case_number = get_case_number_from_row(row_tds)
            case_url = get_case_url_from_row(row_tds)

            project_name = row_tds[1].get_text().strip()
            status = row_tds[2].get_text().strip()
            contact = row_tds[3].find("a").get_text().strip()
            contact_url = row_tds[3].find("a")["href"].replace(" ", "")

            # Found a case where the TC name was not a link. We'll set it to something generic in the mean time.
            if not case_url:
                case_url = "NA"

            # If any of these variables are None, log it and move on.
            if not case_number or not case_url or not project_name or not status or not contact or not contact_url:
                logger.info("********** Problem scraping this row **********")
                logger.info(str(row_tds))
                logger.info("case_number scrape: " + str(case_number))
                logger.info("case_url scrape: " + str(case_url))
                logger.info("project_name scrape: " + str(project_name))
                logger.info("status scrape: " + str(status))
                logger.info("contact scrape: " + str(contact))
                logger.info("contact_url scrape: " + str(contact_url))

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
    zoning_tables = page_content.findAll("table")

    for zoning_table in zoning_tables:
        zoning_tbody = zoning_table.find("tbody")
        zoning_rows = zoning_tbody.findAll("tr")

        for i in range(0, len(zoning_rows), 2):
            # First row is zoning_rows[i]
            # Second row is zoning_rows[i+1]
            info_row_tds = zoning_rows[i].findAll("td")
            status_row_tds = zoning_rows[i + 1].findAll("td")

            # This gets the zoning case label.
            # Some cases have a master plan case so label ends up like "Z-14-19MP-1-19"
            label = info_row_tds[0].get_text().split("\n")[0]
            if "mp" in label.lower():
                label = label.lower().split("mp")[0]

            location = info_row_tds[1].get_text()
            cac = info_row_tds[2].get_text()
            contact = info_row_tds[3].get_text()
            status = status_row_tds[0].get_text()

            zoning_case = label.split("\n")[0]

            # If the label is not a hyperlink
            if len(info_row_tds[0].find_all("a")) == 0:
                zoning_case_url = "https://raleighnc.gov/business/content/PlanDev/Articles/DevServ/CurrentDevelopmentActivity.html"
            # If there is only one link for the label
            elif len(info_row_tds[0].find_all("a")) == 1:
                zoning_case_url = info_row_tds[0].find("a")["href"].strip().replace(" ", "%20")
            # If the label has multiple hyperlinks (mistake on the website)
            elif len(info_row_tds[0].find_all("a")) > 1:
                zoning_case_url = get_correct_url(info_row_tds[0].find_all('a'), label).strip().replace(" ", "%20")

            # If any of these variables are None, log it and move on.
            # Remarks come from the API
            # Status is from the web scrape
            if not label or not location or not zoning_case or not cac or not status or not contact:
                logger.info("********** Problem scraping this row **********")
                logger.info(str(info_row_tds))
                logger.info(str(status_row_tds))
                logger.info("label scrape: " + str(label))
                logger.info("location scrape: " + str(location))
                logger.info("cac scrape: " + str(cac))
                logger.info("contact scrape: " + str(contact))
                logger.info("status scrape: " + str(status))
                logger.info("url scrape: " + str(zoning_case_url))
                logger.info("url_text scrape: " + str(zoning_case))

                continue

            # Break up zoning_case
            scrape_num = zoning_case.split("-")[1]
            scrape_year = "20" + zoning_case.split("-")[2]

            # First check if we already have this zoning request
            if Zoning.objects.filter(zpnum=int(scrape_num), zpyear=int(scrape_year)).exists():
                known_zon = Zoning.objects.get(zpyear=scrape_year, zpnum=scrape_num)

                # If the status or plan_url have changed, update the zoning request
                if (not fields_are_same(known_zon.status, status) or
                        not fields_are_same(known_zon.plan_url, zoning_case_url)):
                    # A zoning web scrape only updates status and/or plan_url
                    known_zon.status = status
                    known_zon.plan_url = zoning_case_url

                    known_zon.save()

                    # Want to log what the difference is
                    difference = "*"
                    if not fields_are_same(known_zon.status, status):
                        difference += "Difference: " + str(known_zon.status) + " changed to " + str(status)
                    if not fields_are_same(known_zon.plan_url, zoning_case_url):
                        difference += "Difference: " + str(known_zon.plan_url) + " changed to " + str(zoning_case_url)

                    logger.info("**********************")
                    logger.info("Updating a zoning request")
                    logger.info("known_zon: " + str(known_zon))
                    logger.info(difference)
                    logger.info("**********************")

                    # print("Updating a zoning request")

            else:
                # We don't know about it so create a new zoning request
                # create a new instance
                logger.info("**********************")
                logger.info("Creating new Zoning Request from web scrape")
                logger.info("case_number:" + zoning_case)
                logger.info("cac: " + cac)
                logger.info("**********************")

                plan_url = zoning_case_url

                Zoning.objects.create(zpyear=scrape_year,
                                      zpnum=scrape_num,
                                      cac=cac,
                                      status=status,
                                      location=location,
                                      received_by=contact,
                                      plan_url=plan_url)

                # print("Creating new zoning request")
