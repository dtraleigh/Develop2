from develop.models import *
from django.conf import settings

from datetime import datetime
import logging, requests
from bs4 import BeautifulSoup

logger = logging.getLogger("django")


def string_output_unix_datetime(unix_datetime):
    if unix_datetime:
        return datetime.fromtimestamp(unix_datetime / 1000).strftime('%Y-%m-%d %H:%M:%S')
    return str("None")


def get_status_legend_list():
    page_link = "https://www.raleighnc.gov/development"

    page_response = requests.get(page_link, timeout=10)

    if page_response.status_code == 200:
        page_content = BeautifulSoup(page_response.content, "html.parser")

        # Status Abbreviations
        status_abbreviations_title = page_content.find("h3", {"id": "StatusAbbreviations"})

        status_section = status_abbreviations_title.findNext("div")

        status_ul = status_section.find("ul")
        status_list = []

        for li in status_ul.findAll('li'):
            status_list.append(li.get_text())

        return status_list

    # It doesn't change much so if we can't get to the page for the legend, we'll use this static version.
    return ['City Council (CC)', 'City Council Economic Development and Innovation Committee (EDI)',
            'City Council Growth and Natural Resources Committee (GNR)',
            'City Council Healthy Neighborhoods Committee (HN)',
            'City Council Transportation and Transit Committee (TTC)',
            'Planning Commission (PC)', 'Planning Commission Committee of the Whole (COW)',
            'Planning Commission Strategic Planning Committee (SPC)',
            'Planning Commission Text Change Committee (TCC)', 'Under Review (UR)', 'Public Hearing (PH)',
            'Approved Pending Appeal (APA)', 'Approved with Conditions Pending Appeal (CAPA)', 'Appealed (AP)',
            'Denied Pending Appeal (DPA)', 'Expired Pending Appeal (EPA)', 'Effective Date (EFF)',
            'Boundary Survey (BS)', 'Exemption (EX)', 'Miscellaneous (MI)', 'Recombination (R)', 'Right-of-Way (RW)',
            'Subdivision (S)', 'Site Plan (SP)', 'Site Review (SR)']


def get_status_text(status):
    # This will take in the status abbreviation and return the whole text
    # This only applies to SiteReviewCases
    status_list = get_status_legend_list()

    for s in status_list:
        abbreviation = "(" + status + ")"
        if abbreviation in s:
            return s

    return status


def difference_email_output(item):
    output = ""

    # Get the most recent version of the item and the one previously
    item_most_recent = item.history.first()
    item_previous = item_most_recent.prev_record

    # Get all the item fields
    fields = item._meta.get_fields()

    # Loop through each field, except created_date, modified_date, and id.
    # If the fields are not equal, add it to output.
    for field in fields:
        if field.name != "created_date" and field.name != "modified_date" and field.name != "id" and field.name != "EditDate":
            try:
                item_most_recent_field = getattr(item_most_recent, field.name)
                item_old_field = getattr(item_previous, field.name)
            except AttributeError:
                n = datetime.now()
                logger.info(n.strftime("%H:%M %m-%d-%y") + ": AttributeError - field is " + field + " and item_most_recent = " + item_most_recent)
                continue

            # If there is a difference...
            if item_most_recent_field != item_old_field:
                # If it's a date field, we need to convert it to a human readable string
                # Let's ignore EditDate
                if field.get_internal_type() == "BigIntegerField" and field.name != "EditDate" and all([item_most_recent_field, item_old_field]):
                    try:
                        before_date_hr = datetime.fromtimestamp(item_old_field / 1000).strftime('%Y-%m-%d %H:%M:%S')
                        after_date_hr = datetime.fromtimestamp(item_most_recent_field / 1000).strftime('%Y-%m-%d %H:%M:%S')

                        output += "    " + field.verbose_name + " changed from \"" + before_date_hr + "\" to \"" + \
                                  after_date_hr + "\"\n"
                    except:
                        n = datetime.now()
                        logger.info(n.strftime("%H:%M %m-%d-%y") + ": Problem calculating the datetime")
                        logger.info("field is " + str(field))
                        if item_old_field:
                            logger.info("item_old_field: " + str(item_old_field))
                        else:
                            logger.info("item_old_field: None")

                        if item_old_field:
                            logger.info("item_most_recent_field: " + str(item_old_field))
                        else:
                            logger.info("item_most_recent_field: None")

                else:
                    if isinstance(item, SiteReviewCases) and field.verbose_name == "Status":
                        output += "    Status changed from \"" + get_status_text(item_old_field) + "\" to \"" + \
                                  get_status_text(item_most_recent_field) + "\"\n"
                    else:
                        output += "    " + field.verbose_name + " changed from \"" + str(item_old_field) + "\" to \"" + \
                                  str(item_most_recent_field) + "\"\n"

    return output


def get_new_dev_text(new_dev, discourse):
    if isinstance(new_dev, Development):
        new_devs_message = "***" + str(new_dev.plan_name) + ", " + str(new_dev.plan_number) + "***\n"
        if settings.DEVELOP_INSTANCE == "Develop":
            new_devs_message += "[Develop - API]\n"
        new_devs_message += "    Submitted year: " + str(new_dev.submitted_yr) + "\n"
        new_devs_message += "    Plan type: " + str(new_dev.plan_type) + "\n"
        new_devs_message += "    Status: " + str(new_dev.status) + "\n"
        new_devs_message += "    Major Street: " + str(new_dev.major_street) + "\n"
        new_devs_message += "    CAC: " + str(new_dev.cac) + "\n"
        new_devs_message += "    URL: " + str(new_dev.planurl) + "\n\n"
    if isinstance(new_dev, SiteReviewCases):
        new_devs_message = "***" + str(new_dev.project_name) + ", " + str(new_dev.case_number) + "***\n"
        if settings.DEVELOP_INSTANCE == "Develop":
            new_devs_message += "[Develop - Web scrape]\n"
        if discourse:
            new_devs_message += "    Status: " + get_status_text(new_dev.status) + "\n"
        else:
            new_devs_message += "    Status: " + str(new_dev.status) + str(discourse) + "\n"
        new_devs_message += "    CAC: " + str(new_dev.cac) + "\n"
        new_devs_message += "    URL: " + str(new_dev.case_url) + "\n\n"

    return new_devs_message


def get_updated_dev_text(updated_dev, discourse):
    # Need to look at the history and compare the most recent update with the one before it.
    if isinstance(updated_dev, Development):
        updated_devs_message = "***" + str(updated_dev.plan_name) + ", " + str(updated_dev.plan_number) + "***\n"
        if settings.DEVELOP_INSTANCE == "Develop":
            updated_devs_message += "[Develop - API]\n"
        updated_devs_message += "    Updated: " + string_output_unix_datetime(updated_dev.updated) + "\n"
        updated_devs_message += "    Status: " + str(updated_dev.status) + "\n"
        updated_devs_message += "    CAC: " + str(updated_dev.cac) + "\n"
        updated_devs_message += "    URL: " + str(updated_dev.planurl) + "\n\n"
        updated_devs_message += "  *UPDATES*\n"
        updated_devs_message += difference_email_output(updated_dev)
    if isinstance(updated_dev, SiteReviewCases):
        updated_devs_message = "***" + str(updated_dev.project_name) + ", " + str(updated_dev.case_number) + "***\n"
        if settings.DEVELOP_INSTANCE == "Develop":
            updated_devs_message += "[Develop - Web scrape]\n"
        updated_devs_message += "    Updated: " + updated_dev.modified_date.strftime("%m-%d-%y %H:%M") + "\n"
        if discourse:
            updated_devs_message += "    Status: " + get_status_text(updated_dev.status) + "\n"
        else:
            updated_devs_message += "    Status: " + str(updated_dev.status) + str(discourse) + "\n"
        updated_devs_message += "    CAC: " + str(updated_dev.cac) + "\n"
        updated_devs_message += "    URL: " + str(updated_dev.case_url) + "\n\n"
        updated_devs_message += "  *UPDATES*\n"
        updated_devs_message += difference_email_output(updated_dev)

    updated_devs_message += "\n"

    return updated_devs_message


def get_new_zon_text(new_zon, discourse):
    new_zon_message = "***" + str(new_zon.zpyear) + "-" + str(new_zon.zpnum) + "***\n"
    new_zon_message += "    Location: " + str(new_zon.location) + "\n"
    new_zon_message += "    Remarks: " + str(new_zon.remarks) + "\n"
    new_zon_message += "    Status: " + str(new_zon.status) + "\n"

    if new_zon.plan_url:
        new_zon_message += "    Plan URL: " + str(new_zon.plan_url) + "\n"
    else:
        new_zon_message += "    Plan URL: NA\n"

    new_zon_message += "    CAC: " + str(new_zon.cac) + "\n\n"

    return new_zon_message


def get_updated_zon_text(updated_zon, discourse):
    updated_zon_message = "***" + str(updated_zon.zpyear) + "-" + str(updated_zon.zpnum) + "***\n"
    updated_zon_message += "    Location: " + str(updated_zon.location) + "\n"
    updated_zon_message += "    Remarks: " + str(updated_zon.remarks) + "\n"
    updated_zon_message += "    Status: " + str(updated_zon.status) + "\n"

    if updated_zon.plan_url:
        updated_zon_message += "    Plan URL: " + str(updated_zon.plan_url) + "\n"
    else:
        updated_zon_message += "    Plan URL: NA\n"

    updated_zon_message += "    CAC: " + str(updated_zon.cac) + "\n\n"
    updated_zon_message += "  *UPDATES*\n"
    updated_zon_message += difference_email_output(updated_zon)

    updated_zon_message += "\n"

    return updated_zon_message
