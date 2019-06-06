from develop.models import *
from django.conf import settings

from datetime import datetime
import logging, requests, re
from bs4 import BeautifulSoup

logger = logging.getLogger("django")


def string_output_unix_datetime(unix_datetime):
    if unix_datetime:
        return datetime.fromtimestamp(unix_datetime / 1000).strftime('%Y-%m-%d %H:%M:%S')
    return str("None")


def get_status_legend_dict():
    page_link = "https://www.raleighnc.gov/development"

    page_response = requests.get(page_link, timeout=10)

    if page_response.status_code == 200:
        page_content = BeautifulSoup(page_response.content, "html.parser")

        # Status Abbreviations
        status_abbreviations_title = page_content.find("h3", {"id": "StatusAbbreviations"})

        status_section = status_abbreviations_title.findNext("div")

        status_ul = status_section.find("ul")
        status_dict = {}

        for li in status_ul.findAll('li'):
            status_dict[re.search('\(([^)]+)', li.get_text()).group(1)] = li.get_text()

        return status_dict

    # It doesn't change much so if we can't get to the page for the legend, we'll use this static version.
    return {'CC': 'City Council (CC)',
            'EDI': 'City Council Economic Development and Innovation Committee (EDI)',
            'GNR': 'City Council Growth and Natural Resources Committee (GNR)',
            'HN': 'City Council Healthy Neighborhoods Committee (HN)',
            'TTC': 'City Council Transportation and Transit Committee (TTC)',
            'PC': 'Planning Commission (PC)',
            'COW': 'Planning Commission Committee of the Whole (COW)',
            'SPC': 'Planning Commission Strategic Planning Committee (SPC)',
            'TCC': 'Planning Commission Text Change Committee (TCC)',
            'UR': 'Under Review (UR)',
            'PH': 'Public Hearing (PH)',
            'APA': 'Approved Pending Appeal (APA)',
            'CAPA': 'Approved with Conditions Pending Appeal (CAPA)',
            'AP': 'Appealed (AP)',
            'DPA': 'Denied Pending Appeal (DPA)',
            'EPA': 'Expired Pending Appeal (EPA)',
            'EFF': 'Effective Date (EFF)',
            'BS': 'Boundary Survey (BS)',
            'EX': 'Exemption (EX)',
            'MI': 'Miscellaneous (MI)',
            'R': 'Recombination (R)',
            'RW': 'Right-of-Way (RW)',
            'S': 'Subdivision (S)',
            'SP': 'Site Plan (SP)',
            'SR': 'Site Review (SR)'}


def get_status_text(status):
    # This will take in certain status abbreviations and return the whole text
    # This only applies to web scraped items
    status_dict = get_status_legend_dict()

    if 'CAPA' in status:
        status = status.replace('CAPA', status_dict['CAPA'])

    return status


def get_cac_text(item):
    if item.cac_override:
        return str(item.cac_override)
    return str(item.cac)


def get_field_value(tracked_item, model_field):
    try:
        # If a date, convert to human readable
        if model_field.get_internal_type() == "BigIntegerField":
            return string_output_unix_datetime(getattr(tracked_item, model_field.name))
        # everything else, return as is
        else:
            return getattr(tracked_item, model_field.name)
    except AttributeError:
        n = datetime.now()
        logger.info(n.strftime("%H:%M %m-%d-%y") + ": AttributeError - field is " + str(model_field.name) +
                    " and item_most_recent = " + str(tracked_item))


def difference_email_output(item):
    output = ""

    # Get the most recent version of the item and the one previously
    item_most_recent = item.history.first()
    item_previous = item_most_recent.prev_record

    # Get all the item fields
    fields = item._meta.get_fields()

    ignore_fields = ["created_date", "modified_date", "id", "EditDate", "updated"]

    # Loop through each field, except created_date, modified_date, and id.
    # If the fields are not equal, add it to output.
    for field in fields:
        if field.name not in ignore_fields:
            item_most_recent_field_value = get_field_value(item_most_recent, field)
            item_old_field_value = get_field_value(item_previous, field)

            # If there is a difference...
            if item_most_recent_field_value != item_old_field_value:
                # If a date field
                if field.get_internal_type() == "BigIntegerField":
                    output += "    " + field.verbose_name + " changed from \"" + item_most_recent_field_value + \
                              "\" to \"" + item_old_field_value + "\"\n"
                # Everything else
                else:
                    if isinstance(item, SiteReviewCases) and field.verbose_name == "Status":
                        output += "    Status changed from \"" + get_status_text(item_old_field_value) + \
                                  "\" to \"" + get_status_text(item_most_recent_field_value) + "\"\n"
                    else:
                        output += "    " + field.verbose_name + " changed from \"" + str(item_old_field_value) + \
                                  "\" to \"" + str(item_most_recent_field_value) + "\"\n"

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
        new_devs_message += "    CAC: " + get_cac_text(new_dev) + "\n"
        new_devs_message += "    URL: " + str(new_dev.planurl) + "\n\n"
    if isinstance(new_dev, SiteReviewCases):
        new_devs_message = "***" + str(new_dev.project_name) + ", " + str(new_dev.case_number) + "***\n"
        if settings.DEVELOP_INSTANCE == "Develop":
            new_devs_message += "[Develop - Web scrape]\n"
        if discourse:
            new_devs_message += "    Status: " + get_status_text(new_dev.status) + "\n"
        else:
            new_devs_message += "    Status: " + str(new_dev.status) + str(discourse) + "\n"
        new_devs_message += "    CAC: " + get_cac_text(new_dev) + "\n"
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
        updated_devs_message += "    CAC: " + get_cac_text(updated_dev) + "\n"
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
        updated_devs_message += "    CAC: " + get_cac_text(updated_dev) + "\n"
        updated_devs_message += "    URL: " + str(updated_dev.case_url) + "\n\n"
        updated_devs_message += "  *UPDATES*\n"
        updated_devs_message += difference_email_output(updated_dev)

    updated_devs_message += "\n"

    return updated_devs_message


def get_new_zon_text(new_zon, discourse):
    new_zon_message = "***" + str(new_zon.zpyear) + "-" + str(new_zon.zpnum) + "***\n"
    new_zon_message += "    Location: " + str(new_zon.location) + "\n"
    new_zon_message += "    Remarks: " + str(new_zon.remarks).strip() + "\n"
    new_zon_message += "    Status: " + str(new_zon.status) + "\n"

    if new_zon.plan_url:
        new_zon_message += "    Plan URL: " + str(new_zon.plan_url) + "\n"
    else:
        new_zon_message += "    Plan URL: NA\n"

    new_zon_message += "    CAC: " + get_cac_text(new_zon) + "\n\n"

    return new_zon_message


def get_updated_zon_text(updated_zon, discourse):
    updated_zon_message = "***" + str(updated_zon.zpyear) + "-" + str(updated_zon.zpnum) + "***\n"
    updated_zon_message += "    Location: " + str(updated_zon.location) + "\n"
    updated_zon_message += "    Remarks: " + str(updated_zon.remarks).strip() + "\n"
    updated_zon_message += "    Status: " + str(updated_zon.status) + "\n"

    if updated_zon.plan_url:
        updated_zon_message += "    Plan URL: " + str(updated_zon.plan_url) + "\n"
    else:
        updated_zon_message += "    Plan URL: NA\n"

    updated_zon_message += "    CAC: " + get_cac_text(updated_zon) + "\n\n"
    updated_zon_message += "  *UPDATES*\n"
    updated_zon_message += difference_email_output(updated_zon)

    updated_zon_message += "\n"

    return updated_zon_message


def get_new_aad_text(new_aad, discourse):
    new_aad_message = "***" + str(new_aad.project_name) + ", " + str(new_aad.case_number) + "***\n"
    if settings.DEVELOP_INSTANCE == "Develop":
        new_aad_message += "[AAD - Web scrape]\n"
    if discourse:
        new_aad_message += "    Status: " + get_status_text(new_aad.status) + "\n"
    else:
        new_aad_message += "    Status: " + str(new_aad.status) + str(discourse) + "\n"
    new_aad_message += "    CAC: " + get_cac_text(new_aad) + "\n"
    new_aad_message += "    URL: " + str(new_aad.case_url) + "\n\n"

    return new_aad_message


def get_updated_aad_text(updated_aad, discourse):
    updated_aad_message = "***" + str(updated_aad.project_name) + ", " + str(updated_aad.case_number) + "***\n"
    if settings.DEVELOP_INSTANCE == "Develop":
        updated_aad_message += "[Develop - Web scrape]\n"
    updated_aad_message += "    Updated: " + updated_aad.modified_date.strftime("%m-%d-%y %H:%M") + "\n"
    if discourse:
        updated_aad_message += "    Status: " + get_status_text(updated_aad.status) + "\n"
    else:
        updated_aad_message += "    Status: " + str(updated_aad.status) + str(discourse) + "\n"
    updated_aad_message += "    CAC: " + get_cac_text(updated_aad) + "\n"
    updated_aad_message += "    URL: " + str(updated_aad.case_url) + "\n\n"
    updated_aad_message += "  *UPDATES*\n"
    updated_aad_message += difference_email_output(updated_aad)

    updated_aad_message += "\n"

    return updated_aad_message
