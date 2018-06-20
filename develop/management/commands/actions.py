import logging, json, requests
from datetime import datetime

from develop.models import *
from django.core.mail import send_mail

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


def get_all_dev_ids(url):
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


def fields_are_same(object_item, json_item):
    try:
        return object_item == json_item
    except:
        n = datetime.datetime.now()
        logger.info(n.strftime("%H:%M %m-%d-%y") + ": Error comparing object_item, " + str(object_item) + ", with json_item, " + str(json_item))


def api_object_is_different(known_dev_object, dev_json):
    # Return False unless if any of the individual field compare
    # functions return True, return True

    if not fields_are_same(known_dev_object.OBJECTID, dev_json["OBJECTID"]):
        return True

    if not fields_are_same(known_dev_object.submitted, dev_json["submitted"]):
        return True

    if not fields_are_same(known_dev_object.submitted_yr, dev_json["submitted_yr"]):
        return True

    if not fields_are_same(known_dev_object.approved, dev_json["approved"]):
        return True

    if not fields_are_same(known_dev_object.daystoapprove, dev_json["daystoapprove"]):
        return True

    if not fields_are_same(known_dev_object.plan_type, dev_json["plan_type"]):
        return True

    if not fields_are_same(known_dev_object.status, dev_json["status"]):
        return True

    if not fields_are_same(known_dev_object.appealperiodends, dev_json["appealperiodends"]):
        return True

    if not fields_are_same(known_dev_object.updated, dev_json["updated"]):
        return True

    if not fields_are_same(known_dev_object.sunset_date, dev_json["sunset_date"]):
        return True

    if not fields_are_same(known_dev_object.acreage, str(dev_json["acreage"])):
        return True

    # Need to convert the decimal field to a char
    if not fields_are_same(known_dev_object.major_street, dev_json["major_street"]):
        return True

    if not fields_are_same(known_dev_object.cac, dev_json["cac"]):
        return True

    if not fields_are_same(known_dev_object.engineer, dev_json["engineer"]):
        return True

    if not fields_are_same(known_dev_object.engineer_phone, dev_json["engineer_phone"]):
        return True

    if not fields_are_same(known_dev_object.developer, dev_json["developer"]):
        return True

    if not fields_are_same(known_dev_object.developer_phone, dev_json["developer_phone"]):
        return True

    if not fields_are_same(known_dev_object.plan_name, dev_json["plan_name"]):
        return True

    if not fields_are_same(known_dev_object.planurl, dev_json["planurl"]):
        return True

    if not fields_are_same(known_dev_object.planurl_approved, dev_json["planurl_approved"]):
        return True

    if not fields_are_same(known_dev_object.planner, dev_json["planner"]):
        return True

    if not fields_are_same(known_dev_object.lots_req, dev_json["lots_req"]):
        return True

    if not fields_are_same(known_dev_object.lots_rec, dev_json["lots_rec"]):
        return True

    if not fields_are_same(known_dev_object.lots_apprv, dev_json["lots_apprv"]):
        return True

    if not fields_are_same(known_dev_object.sq_ft_req, dev_json["sq_ft_req"]):
        return True

    if not fields_are_same(known_dev_object.units_apprv, dev_json["units_apprv"]):
        return True

    if not fields_are_same(known_dev_object.units_req, dev_json["units_req"]):
        return True

    if not fields_are_same(known_dev_object.zoning, dev_json["zoning"]):
        return True

    if not fields_are_same(known_dev_object.plan_number, str(dev_json["plan_number"])):
        return True

    if not fields_are_same(known_dev_object.CreationDate, dev_json["CreationDate"]):
        return True

    if not fields_are_same(known_dev_object.Creator, dev_json["Creator"]):
        return True

    if not fields_are_same(known_dev_object.EditDate, dev_json["EditDate"]):
        return True

    if not fields_are_same(known_dev_object.Editor, dev_json["Editor"]):
        return True

    return False


# def send_email():
#     subject = "This is a test from develop2"
#     message = "This is the message from develop2"
#     email_from = "develop2@dtraleigh.com"
#     all_active_subscribers = Subscriber.objects.filter(send_emails=True)
#
#     notification = EmailMessage(
#         subject,
#         message,
#         email_from,
#         [sub.email for sub in all_active_subscribers],
#         reply_to=['leo@dtraleigh.com'],
#     )
#     return [notification]

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