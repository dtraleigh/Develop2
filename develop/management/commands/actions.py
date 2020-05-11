import logging
import json
import requests
import pytz

from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta

from develop.models import *
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

from .text_generates import *
from .emails import *

logger = logging.getLogger("django")


def get_api_json(url):
    response = None

    try:
        response = requests.get(url)
    except requests.exceptions.ChunkedEncodingError:
        n = datetime.now()
        logger.info(n.strftime("%H:%M %m-%d-%y") + ": problem hitting the api. (" + url + ")")

    if response.status_code == 200:
        return response.json()

    return response


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


def get_total_developments():
    # Example:
    # {
    #   "count":6250
    # }
    total_dev_count_query = ("https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/Development_Plans"
                             "/FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=false"
                             "&outSR=4326&f=json&returnCountOnly=true")

    json_count = get_api_json(total_dev_count_query)

    return json_count["count"]


def get_all_ids(url):
    # Example:
    # {
    #     "objectIdFieldName": "OBJECTID",
    #     "objectIds": [
    #         35811,
    #         35812,
    #           .....
    #         42081,
    #         42082
    #       ]
    # }

    json_object_ids = get_api_json(url)

    try:
        return json_object_ids["objectIds"]
    except KeyError:
        n = datetime.now()
        message = n.strftime("%H:%M %m-%d-%y") + ": KeyError: 'objectIds'\n"
        message += "actions.get_all_ids: KeyError with variable json_object_ids in get_all_ids()\n"
        message += str(json_object_ids)
        logger.info(message)
        send_email_notice(message, email_admins())
        return None


def get_dev_range_json(url):
    # returns a range of dev json starting at one ID up until another

    return get_api_json(url)


def fields_are_same(object_item, api_or_web_scrape_item):
    try:
        return object_item == api_or_web_scrape_item
    except:
        n = datetime.datetime.now()
        logger.info(n.strftime("%H:%M %m-%d-%y") + ": Error comparing object_item, " + str(object_item) +
                    ", with json_item, " + str(api_or_web_scrape_item))


def get_status_legend_text():
    page_link = "https://www.raleighnc.gov/development"

    page_response = requests.get(page_link, timeout=10)

    if page_response.status_code == 200:
        page_content = BeautifulSoup(page_response.content, "html.parser")

        # Status Abbreviations
        status_abbreviations_title = page_content.find("h3", {"id": "StatusAbbreviations"})

        status_section = status_abbreviations_title.findNext("div")

        status_ul = status_section.find("ul")
        status_legend = ""

        for li in status_ul.findAll('li'):
            status_legend += li.get_text() + "\n"

        return status_legend

    return "Unable to scrape the status legend."


def api_object_is_different(known_object, item_json):
    # Return False unless any of the individual field compare
    # functions return True
    n = datetime.now()

    list_of_Development_fields_to_compare = ["OBJECTID", "submitted_yr", "approved", "daystoapprove",
                                             "plan_type", "status", "appealperiodends", "sunset_date", "acreage",
                                             "major_street", "cac", "engineer", "engineer_phone", "developer",
                                             "developer_phone", "plan_name", "planurl", "planurl_approved",
                                             "planner", "lots_req", "lots_rec", "lots_apprv", "sq_ft_req",
                                             "units_apprv", "units_req", "zoning", "plan_number", "CreationDate",
                                             "Creator", "Editor"]

    if isinstance(known_object, Development):
        for field in list_of_Development_fields_to_compare:
            if not fields_are_same(str(getattr(known_object, field)), str(item_json[field])):
                logger.info(n.strftime("%H:%M %m-%d-%y") + ": Difference found with " + str(field) +
                            " on Development " + str(known_object))
                logger.info("Known_object: " +
                            str(getattr(known_object, field)) +
                            " (" + str(type(getattr(known_object, field))) + ")" +
                            ",  item_json[" + field + "]: " +
                            str(item_json[field]) +
                            " (" + str(type(item_json[field])) + ")"
                            )
                logger.info("\n")
                logger.info("known_object------------->")
                logger.info(known_object)
                logger.info("\nitem_json-------------->")
                logger.info(item_json)
                return True

    list_of_Zoning_fields_to_compare = ["submittal_date", "petitioner", "location", "remarks", "zp_petition_acres",
                                        "planning_commission_action", "city_council_action", "ph_date", "withdraw_date",
                                        "exp_date_120_days", "exp_date_2_year", "ordinance_number", "received_by",
                                        "last_revised", "drain_basin", "advisory_committee_areas",
                                        "comprehensive_plan_districts", "GlobalID", "CreationDate", "EditDate"]

    if isinstance(known_object, Zoning):
        for field in list_of_Zoning_fields_to_compare:
            # special case for CAC as it has a different name
            if field == "advisory_committee_areas":
                if not fields_are_same(str(known_object.cac), str(item_json["advisory_committee_areas"])):
                    logger.info(n.strftime("%H:%M %m-%d-%y") + ": Difference found with " + str(field) +
                                " on zoning case " + str(known_object))
                    return True
            else:
                if not fields_are_same(str(getattr(known_object, field)), str(item_json[field])):
                    logger.info(n.strftime("%H:%M %m-%d-%y") + ": Difference found with " + str(field) +
                                " on zoning case " + str(known_object))
                    return True

    # Returning false here basically means no difference was found
    return False


def create_email_message(items_that_changed):
    # /// Header
    email_header = "=========================\n"
    email_header += "The latest updates from\n"
    email_header += "THE RALEIGH WIRE SERVICE\n"

    if settings.DEVELOP_INSTANCE == "Develop":
        email_header += "[Develop version]\n"
    email_header += "=========================\n\n"

    # \\\\ End Header

    # //// New Devs Section
    # If the dev's created date was in the last hour, we assume it's a new dev
    new_devs = []
    updated_devs = []
    new_zons = []
    updated_zons = []

    for item in items_that_changed:
        if isinstance(item, Development) or isinstance(item, SiteReviewCases):
            if item.created_date > timezone.now() - timedelta(hours=1):
                new_devs.append(item)
            else:
                updated_devs.append(item)
        if isinstance(item, Zoning):
            if item.created_date > timezone.now() - timedelta(hours=1):
                new_zons.append(item)
            else:
                updated_zons.append(item)

    # /// New Devs section

    if new_devs:
        new_devs_message = "--------------New Developments---------------\n\n"
        for new_dev in new_devs:
            new_devs_message += get_new_dev_text(new_dev)
    else:
        new_devs_message = ""


    # \\\ End New Devs Section

    # /// Dev Updates Section

    if updated_devs:
        updated_devs_message = "-------------Existing Dev Updates------------\n\n"
        for updated_dev in updated_devs:
            updated_devs_message += get_updated_dev_text(updated_dev)
    else:
        updated_devs_message = ""

    # \\\ End Dev Updates Section

    # /// New Zons section

    if new_zons:
        new_zons_message = "-----------New Zoning Requests------------\n\n"
        for new_zon in new_zons:
            new_zons_message += get_new_zon_text(new_zon)
    else:
        new_zons_message = ""

    # \\\ End New Devs Section

    # /// Dev Updates Section

    if updated_zons:
        updated_zons_message = "--------Existing Zoning Request Updates-------\n\n"
        for updated_zon in updated_zons:
            updated_zons_message += get_updated_zon_text(updated_zon)
    else:
        updated_zons_message = ""

    # \\\ End Dev Updates Section

    # /// Footer
    email_footer = "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*\n"
    try:
        email_footer += get_status_legend_text() + "\n\n"
    except AttributeError:
        email_footer += "Please see the Current Development Activity website for status abbreviations.\n\n"
    email_footer += "You are subscribed to THE RALEIGH WIRE SERVICE\n"
    email_footer += "This is a service of DTRaleigh.com\n"
    email_footer += "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*\n"

    # \\\ End Footer

    message = email_header + new_devs_message + updated_devs_message + new_zons_message + updated_zons_message + \
              email_footer

    return message


def create_new_discourse_post(subscriber, item):
    headers = {
        'Content-Type': "application/json",
        'Api-Key': subscriber.api_key,
        'Api-Username': subscriber.name,
        'Accept': "*/*",
        'Cache-Control': "no-cache",
        'Host': "community.dtraleigh.com",
        'Accept-Encoding': "gzip, deflate",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
    }

    post_url = "https://community.dtraleigh.com/posts.json"
    get_url = "https://community.dtraleigh.com/t/" + str(subscriber.topic_id) + ".json"

    response = requests.request("GET", get_url, headers=headers)
    r = response.json()

    slug = r["slug"]
    topic_header_url = "https://community.dtraleigh.com/t/" + slug + "/" + str(subscriber.topic_id) + "/1"
    message = ""

    # Create discourse message
    if isinstance(item, Development) or isinstance(item, SiteReviewCases):
        if item.created_date > timezone.now() - timedelta(hours=1):
            message += "--------------New Development---------------\n\n"
            message += get_new_dev_text(item)
        else:
            message = "--------------Existing Dev Update---------------\n\n"
            message += get_updated_dev_text(item)
    if isinstance(item, Zoning):
        if item.created_date > timezone.now() - timedelta(hours=1):
            message = "--------------New Zoning Request---------------\n\n"
            message += get_new_zon_text(item)
        else:
            message = "--------------Existing Zoning Request Update---------------\n\n"
            message += get_updated_zon_text(item)
    if isinstance(item, AdministrativeAlternates):
        if item.created_date > timezone.now() - timedelta(hours=1):
            message = "--------New Administrative Alternate for Design ----------\n\n"
            message += get_new_aad_text(item)
        else:
            message = "--------Existing Administrative Alternate for Design Update ----------\n\n"
            message += get_updated_aad_text(item)
    if isinstance(item, TextChangeCases):
        if item.created_date > timezone.now() - timedelta(hours=1):
            message = "--------New Text Change Case ----------\n\n"
            message += get_new_tc_text(item)
        else:
            message = "--------Existing Text Change Case Update ----------\n\n"
            message += get_updated_tc_text(item)

    message += "\n\nSee status abbreviations and sources at " \
               "<a href=\"" + topic_header_url + "\">the topic's header</a>."
    # End message create

    # POST to Discourse
    post_payload = json.dumps({"topic_id": subscriber.topic_id,
                               "raw": message})

    requests.request("POST", post_url, data=post_payload, headers=headers)
