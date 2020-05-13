import logging
import re
import requests
from datetime import datetime

from bs4 import BeautifulSoup
from django.conf import settings

from develop.models import *

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
        status_abbreviations_title = page_content.find("h2", text="Status Abbreviations")
        status_ul = status_abbreviations_title.findNext("ul")
        status_dict = {}

        for li in status_ul.findAll('li'):
            status_dict[re.search("\(([^)]+)", li.get_text()).group(1)] = li.get_text()

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

    try:
        if 'CAPA' in status:
            status = status.replace('CAPA', status_dict['CAPA'])

        elif 'GNR' in status:
            status = status.replace('GNR', status_dict['GNR'])

        elif 'TCC' in status:
            status = status.replace('TCC', status_dict['TCC'])

        elif 'CC' in status:
            status = status.replace('CC', status_dict['CC'])

        elif 'PC' in status:
            status = status.replace('PC', status_dict['PC'])

        elif 'PH' in status:
            status = status.replace('PH', status_dict['PH'])
    except TypeError:
        n = datetime.now()
        logger.info(n.strftime("%H:%M %m-%d-%y") + ": status is none")
        return "Error Retrieving Status"

    return status


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
                              "\" to \"" + str(item_old_field_value) + "\"\n"
                # Everything else
                else:
                    if isinstance(item, SiteReviewCases) and field.verbose_name == "Status":
                        output += "    Status changed from \"" + get_status_text(item_old_field_value) + \
                                  "\" to \"" + get_status_text(item_most_recent_field_value) + "\"\n"
                    else:
                        output += "    " + field.verbose_name + " changed from \"" + str(item_old_field_value) + \
                                  "\" to \"" + str(item_most_recent_field_value) + "\"\n"

    return output


def get_instance_text(model):
    if settings.DEVELOP_INSTANCE == "Develop":
        return "[Develop - " + model + "]\n"
    else:
        return ""


def add_debug_text(item):
    # Additional text to help with debugging. Only add this if the instance is Develop
    if settings.DEVELOP_INSTANCE == "Develop":
        text = "    [DEBUG] CAC: " + item.cac + "\n"
        text += "    [DEBUG] CAC Override: " + item.cac_override + "\n"
        return text
    else:
        return ""


def get_new_dev_text(new_dev):
    if isinstance(new_dev, Development):
        new_devs_message = "***" + str(new_dev.plan_name) + ", " + str(new_dev.plan_number) + "***\n"
        new_devs_message += get_instance_text("DEV")
        new_devs_message += "    Submitted year: " + str(new_dev.submitted_yr) + "\n"
        new_devs_message += "    Plan type: " + str(new_dev.plan_type) + "\n"
        new_devs_message += "    Status: " + str(new_dev.status) + "\n"
        new_devs_message += "    Major Street: " + str(new_dev.major_street) + "\n"
        new_devs_message += "    URL: " + str(new_dev.planurl) + "\n\n"
        new_devs_message += add_debug_text(new_dev)
    if isinstance(new_dev, SiteReviewCases):
        new_devs_message = "***" + str(new_dev.project_name) + ", " + str(new_dev.case_number) + "***\n"
        new_devs_message += get_instance_text("SR")
        new_devs_message += "    Status: " + str(new_dev.status) + "\n"
        new_devs_message += "    URL: " + str(new_dev.case_url) + "\n\n"
        new_devs_message += add_debug_text(new_dev)

    return new_devs_message


def get_updated_dev_text(updated_dev):
    # Need to look at the history and compare the most recent update with the one before it.
    if isinstance(updated_dev, Development):
        updated_devs_message = "***" + str(updated_dev.plan_name) + ", " + str(updated_dev.plan_number) + "***\n"
        updated_devs_message += get_instance_text("DEV")
        updated_devs_message += "    Updated: " + string_output_unix_datetime(updated_dev.updated) + "\n"
        updated_devs_message += "    Status: " + str(updated_dev.status) + "\n"
        updated_devs_message += "    URL: " + str(updated_dev.planurl) + "\n\n"
        updated_devs_message += add_debug_text(updated_dev)
        updated_devs_message += "  *UPDATES*\n"
        updated_devs_message += difference_email_output(updated_dev)
    if isinstance(updated_dev, SiteReviewCases):
        updated_devs_message = "***" + str(updated_dev.project_name) + ", " + str(updated_dev.case_number) + "***\n"
        updated_devs_message += get_instance_text("SR")
        updated_devs_message += "    Updated: " + updated_dev.modified_date.strftime("%m-%d-%y %H:%M") + "\n"
        updated_devs_message += "    Status: " + str(updated_dev.status) + "\n"
        updated_devs_message += "    URL: " + str(updated_dev.case_url) + "\n\n"
        updated_devs_message += add_debug_text(updated_dev)
        updated_devs_message += "  *UPDATES*\n"
        updated_devs_message += difference_email_output(updated_dev)

    updated_devs_message += "\n"

    return updated_devs_message


def get_new_zon_text(new_zon):
    new_zon_message = "***" + str(new_zon.zpyear) + "-" + str(new_zon.zpnum) + "***\n"
    new_zon_message += get_instance_text("ZON")
    new_zon_message += "    Location: " + str(new_zon.location) + "\n"
    new_zon_message += "    Remarks: " + str(new_zon.remarks).strip() + "\n"
    new_zon_message += "    Status: " + str(new_zon.status) + "\n"
    new_zon_message += add_debug_text(new_zon)

    if new_zon.plan_url:
        new_zon_message += "    Plan URL: " + str(new_zon.plan_url) + "\n"
    else:
        new_zon_message += "    Plan URL: NA\n"

    return new_zon_message


def get_updated_zon_text(updated_zon):
    updated_zon_message = "***" + str(updated_zon.zpyear) + "-" + str(updated_zon.zpnum) + "***\n"
    updated_zon_message += get_instance_text("ZON")
    updated_zon_message += "    Location: " + str(updated_zon.location) + "\n"
    updated_zon_message += "    Remarks: " + str(updated_zon.remarks).strip() + "\n"
    updated_zon_message += "    Status: " + str(updated_zon.status) + "\n"
    updated_zon_message += add_debug_text(updated_zon)

    if updated_zon.plan_url:
        updated_zon_message += "    Plan URL: " + str(updated_zon.plan_url) + "\n"
    else:
        updated_zon_message += "    Plan URL: NA\n"

    updated_zon_message += "  *UPDATES*\n"
    updated_zon_message += difference_email_output(updated_zon)

    updated_zon_message += "\n"

    return updated_zon_message


def get_new_aad_text(new_aad):
    new_aad_message = "***" + str(new_aad.project_name) + ", " + str(new_aad.case_number) + "***\n"
    new_aad_message += get_instance_text("AAD")
    new_aad_message += "    Status: " + str(new_aad.status) + "\n"
    new_aad_message += "    URL: " + str(new_aad.case_url) + "\n\n"
    new_aad_message += add_debug_text(new_aad)

    return new_aad_message


def get_updated_aad_text(updated_aad):
    updated_aad_message = "***" + str(updated_aad.project_name) + ", " + str(updated_aad.case_number) + "***\n"
    updated_aad_message += get_instance_text("AAD")
    updated_aad_message += "    Updated: " + updated_aad.modified_date.strftime("%m-%d-%y %H:%M") + "\n"
    updated_aad_message += "    Status: " + str(updated_aad.status) + "\n"
    updated_aad_message += "    URL: " + str(updated_aad.case_url) + "\n\n"
    updated_aad_message += add_debug_text(updated_aad)
    updated_aad_message += "  *UPDATES*\n"
    updated_aad_message += difference_email_output(updated_aad)

    updated_aad_message += "\n"

    return updated_aad_message


def get_new_tc_text(new_tc):
    new_tc_message = "***" + str(new_tc.project_name) + ", " + str(new_tc.case_number) + "***\n"
    new_tc_message += get_instance_text("TCC")
    new_tc_message += "    Status: " + str(new_tc.status) + "\n"
    new_tc_message += "    URL: " + str(new_tc.case_url) + "\n\n"

    return new_tc_message


def get_updated_tc_text(updated_tc):
    updated_tc_message = "***" + str(updated_tc.project_name) + ", " + str(updated_tc.case_number) + "***\n"
    updated_tc_message += get_instance_text("TCC")
    updated_tc_message += "    Updated: " + updated_tc.modified_date.strftime("%m-%d-%y %H:%M") + "\n"
    updated_tc_message += "    Status: " + str(updated_tc.status) + "\n"
    updated_tc_message += "    URL: " + str(updated_tc.case_url) + "\n\n"
    updated_tc_message += "  *UPDATES*\n"
    updated_tc_message += difference_email_output(updated_tc)

    updated_tc_message += "\n"

    return updated_tc_message
