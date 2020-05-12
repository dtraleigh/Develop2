# ///
# This command is used to query the APIs, compare the results with the DB and make appropriate changes.
# \\\
import logging
from bs4 import BeautifulSoup
import requests, sys
from datetime import datetime
from prettytable import PrettyTable

from django.core.management.base import BaseCommand
from develop.models import *
from datetime import datetime

from .api_scans import development_api_scan, zoning_api_scan
from .emails import *
logger = logging.getLogger("django")


def get_page_content(page_link):
    n = datetime.now()

    try:
        page_response = requests.get(page_link, timeout=10)
    except requests.exceptions.RequestException as e:
        print(n.strftime("%H:%M %m-%d-%y") + ": Connection problem to " + page_link)
        sys.exit(1)

    if page_response.status_code == 200:
        return BeautifulSoup(page_response.content, "html.parser")
    else:
        return None


class Command(BaseCommand):
    def handle(self, *args, **options):
        sr_page_link = "https://raleighnc.gov/services/zoning-planning-and-development/site-review-cases"
        aad_page_link = "https://raleighnc.gov/SupportPages/administrative-alternate-design-cases"
        zon_page_link = "https://raleighnc.gov/SupportPages/zoning-cases"
        tc_page_link = "https://raleighnc.gov/SupportPages/text-change-cases"
        message = ""

        # scrape the target websites and verify that the table headers are what we expect.

        # Site Review tables
        sr_expected = ['Case Number', 'Project Name/Location/Description', 'CAC', 'Status*', 'Contact']
        sr_tables = get_page_content(sr_page_link).find_all("table")
        for sr_table in sr_tables:
            x = PrettyTable()
            sr_actual = []
            table_thead = sr_table.find("thead")
            thead_row = table_thead.find_all("td")

            for header in thead_row:
                sr_actual.append(header.get_text().strip())

            if sr_actual == sr_expected:
                pass
            else:
                message = "SR Table has changed.\n"
                x.add_row(sr_actual)
                x.add_row(sr_expected)
                message += str(x)

        # AAD tables
        aad_expected = ['Case Number', 'Project Name/Location/Description', 'CAC', 'Status*', 'Contact']
        aad_tables = get_page_content(aad_page_link).find_all("table")
        for aad_table in aad_tables:
            x = PrettyTable()
            aad_actual = []
            table_thead = aad_table.find("thead")
            thead_row = table_thead.find_all("td")

            for header in thead_row:
                aad_actual.append(header.get_text().strip())

            if aad_actual == aad_expected:
                pass
            else:
                message = "AAD Table has changed.\n"
                x.add_row(aad_actual)
                x.add_row(aad_expected)
                message += x

        # TCC tables
        tcc_expected = ['Case Number', 'Project Name/Location/Description', 'Status*', 'Contact']
        tcc_tables = get_page_content(tc_page_link).find_all("table")
        for tcc_table in tcc_tables:
            x = PrettyTable()
            tcc_actual = []
            table_thead = tcc_table.find("thead")
            thead_row = table_thead.find_all("td")

            for header in thead_row:
                tcc_actual.append(header.get_text().strip())

            if tcc_actual == tcc_expected:
                pass
            else:
                message = "TCC Table has changed.\n"
                x.add_row(tcc_actual)
                x.add_row(tcc_expected)
                message += x

        # Zoning tables
        zon_expected = ['Case NumberMaster Plan Number			(Date uploaded)', 'Location/Status',
                        'Council District', 'Contact']
        zon_tables = get_page_content(zon_page_link).find_all("table")
        for zon_table in zon_tables:
            x = PrettyTable()
            zon_actual = []
            table_thead = zon_table.find("thead")
            thead_row = table_thead.find_all("td")

            for header in thead_row:
                zon_actual.append(header.get_text().strip().replace('\n', ''))

            if zon_actual == zon_expected:
                pass
            else:
                message = "Zon Table has changed.\n"
                x.add_row(zon_actual)
                x.add_row(zon_expected)
                message += x

        if message:
            send_email_notice(message, email_admins())
