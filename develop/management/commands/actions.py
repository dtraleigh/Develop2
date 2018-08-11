import logging, json, requests, pytz
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta

from develop.models import *
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

from .text_generates import *

logger = logging.getLogger("django")


def get_api_json(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()

    return None


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

    return json_object_ids["objectIds"]


def get_dev_range_json(url):
    # returns a range of dev json starting at one ID up until another

    return get_api_json(url)


def get_test_data():
    single_object_json = """{"objectIdFieldName":"OBJECTID","globalIdFieldName":"","geometryType":"esriGeometryPoint","spatialReference":{"wkid":4326,"latestWkid":4326},"fields":[{"name":"OBJECTID","type":"esriFieldTypeOID","alias":"OBJECTID","sqlType":"sqlTypeOther","domain":null,"defaultValue":null},{"name":"devplan_id","type":"esriFieldTypeInteger","alias":"Development Plan ID","sqlType":"sqlTypeOther","domain":null,"defaultValue":null},{"name":"submitted","type":"esriFieldTypeDate","alias":"Date Submitted","sqlType":"sqlTypeOther","length":8,"domain":null,"defaultValue":null},{"name":"submitted_yr","type":"esriFieldTypeInteger","alias":"Year Submitted","sqlType":"sqlTypeOther","domain":null,"defaultValue":null},{"name":"approved","type":"esriFieldTypeDate","alias":"Date Approved","sqlType":"sqlTypeOther","length":8,"domain":null,"defaultValue":null},{"name":"daystoapprove","type":"esriFieldTypeInteger","alias":"Days To Approve","sqlType":"sqlTypeOther","domain":null,"defaultValue":null},{"name":"plan_type","type":"esriFieldTypeString","alias":"Plan Type","sqlType":"sqlTypeOther","length":50,"domain":null,"defaultValue":null},{"name":"status","type":"esriFieldTypeString","alias":"Status","sqlType":"sqlTypeOther","length":30,"domain":null,"defaultValue":null},{"name":"appealperiodends","type":"esriFieldTypeDate","alias":"Appeal Period Ends On","sqlType":"sqlTypeOther","length":8,"domain":null,"defaultValue":null},{"name":"updated","type":"esriFieldTypeDate","alias":"Date Updated","sqlType":"sqlTypeOther","length":8,"domain":null,"defaultValue":null},{"name":"sunset_date","type":"esriFieldTypeDate","alias":"Sunset Date","sqlType":"sqlTypeOther","length":8,"domain":null,"defaultValue":null},{"name":"acreage","type":"esriFieldTypeDouble","alias":"Acreage","sqlType":"sqlTypeOther","domain":null,"defaultValue":null},{"name":"major_street","type":"esriFieldTypeString","alias":"Major Street","sqlType":"sqlTypeOther","length":100,"domain":null,"defaultValue":null},{"name":"cac","type":"esriFieldTypeString","alias":"CAC Area","sqlType":"sqlTypeOther","length":30,"domain":null,"defaultValue":null},{"name":"engineer","type":"esriFieldTypeString","alias":"Engineer","sqlType":"sqlTypeOther","length":100,"domain":null,"defaultValue":null},{"name":"engineer_phone","type":"esriFieldTypeString","alias":"Engineer Phone","sqlType":"sqlTypeOther","length":20,"domain":null,"defaultValue":null},{"name":"developer","type":"esriFieldTypeString","alias":"Developer","sqlType":"sqlTypeOther","length":100,"domain":null,"defaultValue":null},{"name":"developer_phone","type":"esriFieldTypeString","alias":"Developer Phone","sqlType":"sqlTypeOther","length":20,"domain":null,"defaultValue":null},{"name":"plan_name","type":"esriFieldTypeString","alias":"Plan Name","sqlType":"sqlTypeOther","length":200,"domain":null,"defaultValue":null},{"name":"planurl","type":"esriFieldTypeString","alias":"Plan URL","sqlType":"sqlTypeOther","length":255,"domain":null,"defaultValue":null},{"name":"planurl_approved","type":"esriFieldTypeString","alias":"Approved Plan URL","sqlType":"sqlTypeOther","length":255,"domain":null,"defaultValue":null},{"name":"planner","type":"esriFieldTypeString","alias":"Planner","sqlType":"sqlTypeOther","length":50,"domain":null,"defaultValue":null},{"name":"lots_req","type":"esriFieldTypeInteger","alias":"Lots Requested","sqlType":"sqlTypeOther","domain":null,"defaultValue":null},{"name":"lots_rec","type":"esriFieldTypeInteger","alias":"Lots Received","sqlType":"sqlTypeOther","domain":null,"defaultValue":null},{"name":"lots_apprv","type":"esriFieldTypeInteger","alias":"Lots Approved","sqlType":"sqlTypeOther","domain":null,"defaultValue":null},{"name":"sq_ft_req","type":"esriFieldTypeInteger","alias":"Square Footage Requested","sqlType":"sqlTypeOther","domain":null,"defaultValue":null},{"name":"units_apprv","type":"esriFieldTypeInteger","alias":"Units Approved","sqlType":"sqlTypeOther","domain":null,"defaultValue":null},{"name":"units_req","type":"esriFieldTypeInteger","alias":"Units Requested","sqlType":"sqlTypeOther","domain":null,"defaultValue":null},{"name":"zoning","type":"esriFieldTypeString","alias":"Zoning","sqlType":"sqlTypeOther","length":50,"domain":null,"defaultValue":null},{"name":"plan_number","type":"esriFieldTypeString","alias":"Plan Number","sqlType":"sqlTypeOther","length":20,"domain":null,"defaultValue":null},{"name":"CreationDate","type":"esriFieldTypeDate","alias":"CreationDate","sqlType":"sqlTypeOther","length":8,"domain":null,"defaultValue":null},{"name":"Creator","type":"esriFieldTypeString","alias":"Creator","sqlType":"sqlTypeOther","length":50,"domain":null,"defaultValue":null},{"name":"EditDate","type":"esriFieldTypeDate","alias":"EditDate","sqlType":"sqlTypeOther","length":8,"domain":null,"defaultValue":null},{"name":"Editor","type":"esriFieldTypeString","alias":"Editor","sqlType":"sqlTypeOther","length":50,"domain":null,"defaultValue":null}],"features":[{"attributes":{"OBJECTID":35811,"devplan_id":7816,"submitted":1071118800012,"submitted_yr":2003,"approved":1106715600000,"daystoapprove":412,"plan_type":"SUBDIVISION","status":"NIMBY","appealperiodends":1109307600000,"updated":1109170860000,"sunset_date":1201323600000,"acreage":2.47,"major_street":" HOLLY LAKE TRL ","cac":"NORTHEAST","engineer":"JOYNER SURVEYING, INC","engineer_phone":"9192661798","developer":"FIELDS, JR","developer_phone":"9192661704","plan_name":"HOLLY ACRES SUBD.","planurl":null,"planurl_approved":null,"planner":"BARBOURS","lots_req":2,"lots_rec":0,"lots_apprv":0,"sq_ft_req":0,"units_apprv":0,"units_req":0,"zoning":"R-4","plan_number":"S-133-2003","CreationDate":1519319915292,"Creator":"OpenData_ral","EditDate":1519319915292,"Editor":"OpenData_ral"}}]}"""

    return json.loads(single_object_json)


def fields_are_same(object_item, api_or_web_scrape_item):
    try:
        return object_item == api_or_web_scrape_item
    except:
        n = datetime.datetime.now()
        logger.info(n.strftime("%H:%M %m-%d-%y") + ": Error comparing object_item, " + str(object_item) + ", with json_item, " + str(api_or_web_scrape_item))


def get_status_legend():
    page_link = "https://www.raleighnc.gov/development"

    page_response = requests.get(page_link, timeout=10)

    if page_response.status_code == 200:
        page_content = BeautifulSoup(page_response.content, "html.parser")

        # Status Abbreviations
        status_abbreviations_title = page_content.find("h3", {"id": "*StatusAbbreviations"})

        status_section = status_abbreviations_title.findNext("div")

        status_ul = status_section.find("ul")
        status_legend = ""

        for li in status_ul.findAll('li'):
            status_legend += li.get_text() + "\n"

        return status_legend

    return "Unable to scrape the status legend."


def api_object_is_different(known_object, item_json):
    # Return False unless if any of the individual field compare
    # functions return True, return True
    n = datetime.now()

    if isinstance(known_object, Development):
        if not fields_are_same(known_object.OBJECTID, item_json["OBJECTID"]):
            return True

        if not fields_are_same(known_object.submitted, item_json["submitted"]):
            return True

        if not fields_are_same(known_object.submitted_yr, item_json["submitted_yr"]):
            return True

        if not fields_are_same(known_object.approved, item_json["approved"]):
            return True

        if not fields_are_same(known_object.daystoapprove, item_json["daystoapprove"]):
            return True

        if not fields_are_same(known_object.plan_type, item_json["plan_type"]):
            return True

        if not fields_are_same(known_object.status, item_json["status"]):
            return True

        if not fields_are_same(known_object.appealperiodends, item_json["appealperiodends"]):
            return True

        # Ignoring updated for now.
        # if not fields_are_same(known_object.updated, item_json["updated"]):
        #     return True

        if not fields_are_same(known_object.sunset_date, item_json["sunset_date"]):
            return True

        if not fields_are_same(known_object.acreage, str(item_json["acreage"])):
            return True

        # Need to convert the decimal field to a char
        if not fields_are_same(known_object.major_street, item_json["major_street"]):
            return True

        if not fields_are_same(known_object.cac, item_json["cac"]):
            return True

        if not fields_are_same(known_object.engineer, item_json["engineer"]):
            return True

        if not fields_are_same(known_object.engineer_phone, item_json["engineer_phone"]):
            return True

        if not fields_are_same(known_object.developer, item_json["developer"]):
            return True

        if not fields_are_same(known_object.developer_phone, item_json["developer_phone"]):
            return True

        if not fields_are_same(known_object.plan_name, item_json["plan_name"]):
            return True

        if not fields_are_same(known_object.planurl, item_json["planurl"]):
            return True

        if not fields_are_same(known_object.planurl_approved, item_json["planurl_approved"]):
            return True

        if not fields_are_same(known_object.planner, item_json["planner"]):
            return True

        if not fields_are_same(known_object.lots_req, item_json["lots_req"]):
            return True

        if not fields_are_same(known_object.lots_rec, item_json["lots_rec"]):
            return True

        if not fields_are_same(known_object.lots_apprv, item_json["lots_apprv"]):
            return True

        if not fields_are_same(known_object.sq_ft_req, item_json["sq_ft_req"]):
            return True

        if not fields_are_same(known_object.units_apprv, item_json["units_apprv"]):
            return True

        if not fields_are_same(known_object.units_req, item_json["units_req"]):
            return True

        if not fields_are_same(known_object.zoning, item_json["zoning"]):
            return True

        if not fields_are_same(known_object.plan_number, str(item_json["plan_number"])):
            return True

        if not fields_are_same(known_object.CreationDate, item_json["CreationDate"]):
            return True

        if not fields_are_same(known_object.Creator, item_json["Creator"]):
            return True

        # Ignoring EditDate for now as some changes come in with EditDate being the only change
        # if not fields_are_same(known_object.EditDate, item_json["EditDate"]):
        #     return True

        if not fields_are_same(known_object.Editor, item_json["Editor"]):
            return True

    if isinstance(known_object, Zoning):
        if not fields_are_same(known_object.submittal_date, item_json["submittal_date"]):
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": Difference found with submittal_date")
            return True

        if not fields_are_same(known_object.petitioner, item_json["petitioner"]):
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": Difference found with petitioner")
            return True

        if not fields_are_same(known_object.location, item_json["location"]):
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": Difference found with location")
            return True

        if not fields_are_same(known_object.remarks, item_json["remarks"]):
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": Difference found with remarks")
            return True

        if not fields_are_same(known_object.zp_petition_acres, str(item_json["zp_petition_acres"])):
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": Difference found with zp_petition_acres")
            return True

        if not fields_are_same(known_object.planning_commission_action, item_json["planning_commission_action"]):
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": Difference found with planning_commission_action")
            return True

        if not fields_are_same(known_object.city_council_action, item_json["city_council_action"]):
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": Difference found with city_council_action")
            return True

        if not fields_are_same(known_object.ph_date, item_json["ph_date"]):
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": Difference found with ph_date")
            return True

        if not fields_are_same(known_object.withdraw_date, item_json["withdraw_date"]):
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": Difference found with withdraw_date")
            return True

        if not fields_are_same(known_object.exp_date_120_days, item_json["exp_date_120_days"]):
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": Difference found with exp_date_120_days")
            return True

        if not fields_are_same(known_object.exp_date_2_year, item_json["exp_date_2_year"]):
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": Difference found with exp_date_2_year")
            return True

        if not fields_are_same(known_object.ordinance_number, item_json["ordinance_number"]):
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": Difference found with ordinance_number")
            return True

        if not fields_are_same(known_object.received_by, item_json["received_by"]):
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": Difference found with received_by")
            return True

        if not fields_are_same(known_object.last_revised, item_json["last_revised"]):
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": Difference found with last_revised")
            return True

        if not fields_are_same(known_object.drain_basin, item_json["drain_basin"]):
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": Difference found with drain_basin")
            return True

        if not fields_are_same(known_object.advisory_committee_areas, item_json["advisory_committee_areas"]):
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": Difference found with advisory_committee_areas")
            return True

        if not fields_are_same(known_object.comprehensive_plan_districts, item_json["comprehensive_plan_districts"]):
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": Difference found with comprehensive_plan_districts")
            return True

        if not fields_are_same(known_object.GlobalID, item_json["GlobalID"]):
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": Difference found with GlobalID")
            return True

        if not fields_are_same(known_object.CreationDate, item_json["CreationDate"]):
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": Difference found with CreationDate")
            return True

        if not fields_are_same(known_object.EditDate, item_json["EditDate"]):
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": Difference found with EditDate")
            return True

    return False


def send_email_test():
    subject = "This is a test from develop2"
    message = "This is the message from develop2"
    email_from = "develop@dtraleigh.com"
    all_active_subscribers = Subscriber.objects.filter(send_emails=True)

    try:
        send_mail(
            subject,
            message,
            email_from,
            [sub.email for sub in all_active_subscribers],
            fail_silently=False,
        )
        n = datetime.now()
        logger.info("Email sent at " + n.strftime("%H:%M %m-%d-%y"))
    except:
        n = datetime.now()
        logger.info("Problem sending email at " + n.strftime("%H:%M %m-%d-%y"))


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

    for item in items_that_changed:
        if isinstance(item, Development):
            if item.created_date > timezone.now() - timedelta(hours=1):
                new_devs.append(item)
            else:
                updated_devs.append(item)
    if new_devs:
        new_devs_message = "--------------New Developments---------------\n\n"
        new_devs_message += get_new_dev_text(new_devs)
    else:
        new_devs_message = ""


    # \\\ End New Devs Section

    # /// Dev Updates Section

    if updated_devs:
        updated_devs_message = "-------------Existing Dev Updates------------\n\n"
        updated_devs_message += get_updated_dev_text(updated_devs)
    else:
        updated_devs_message = ""

    # \\\ End Dev Updates Section

    # /// Footer
    email_footer = "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*\n"
    email_footer += get_status_legend() + "\n\n"
    email_footer += "You are subscribed to THE RALEIGH WIRE SERVICE\n"
    email_footer += "This is a service of DTRaleigh.com\n"
    email_footer += "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*\n"

    # \\\ End Footer

    message = email_header + new_devs_message + updated_devs_message + email_footer

    return message
