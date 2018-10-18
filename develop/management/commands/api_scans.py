import logging

from .actions import *
from develop.models import *

logger = logging.getLogger("django")


def development_api_scan():
    # ////
    # Development Planning API
    # https://data-ral.opendata.arcgis.com/datasets/development-plans
    # \\\\

    # Get all development ids
    all_dev_ids_query = ("https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/Development_Plans"
                         "/FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=false&returnIdsOnly=true"
                         "&outSR=4326&f=json")
    all_dev_ids = get_all_ids(all_dev_ids_query)

    # Process the ids in batches of 1000
    for x in batch(all_dev_ids, 1000):
        start_dev_id = x[0]
        end_dev_id = x[-1]

        # Example - where=OBJECTID>=35811 AND OBJECTID<=35816
        dev_range_query = ("https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/Development_Plans"
                           "/FeatureServer/0/query?"
                           "where=OBJECTID>=" + str(start_dev_id) + " AND OBJECTID<=" + str(end_dev_id) +
                           "&outFields=*&returnGeometry=false&returnIdsOnly=false&outSR=4326&f=json")

        batch_of_devs_json = get_dev_range_json(dev_range_query)
        # batch_of_devs_json = get_test_data()

        # Process each dev
        try:
            for features in batch_of_devs_json["features"]:
                dev = features["attributes"]

                # Try to get the development from the DB and check if it needs to be updated.
                try:
                    known_dev = Development.objects.get(devplan_id=dev["devplan_id"])

                    # If the new object is not the same as the one in the DB, update it.
                    if api_object_is_different(known_dev, dev):
                        # print("Object is in the DB and is different. Updating it.")

                        known_dev.OBJECTID = dev["OBJECTID"]
                        known_dev.submitted = dev["submitted"]
                        known_dev.submitted_yr = dev["submitted_yr"]
                        known_dev.approved = dev["approved"]
                        known_dev.daystoapprove = dev["daystoapprove"]
                        known_dev.plan_type = dev["plan_type"]
                        known_dev.status = dev["status"]
                        known_dev.appealperiodends = dev["appealperiodends"]
                        known_dev.updated = dev["updated"]
                        known_dev.sunset_date = dev["sunset_date"]
                        known_dev.acreage = dev["acreage"]
                        known_dev.major_street = dev["major_street"]
                        known_dev.cac = dev["cac"]
                        known_dev.engineer = dev["engineer"]
                        known_dev.engineer_phone = dev["engineer_phone"]
                        known_dev.developer = dev["developer"]
                        known_dev.developer_phone = dev["developer_phone"]
                        known_dev.plan_name = dev["plan_name"]
                        known_dev.planurl = dev["planurl"]
                        known_dev.planurl_approved = dev["planurl_approved"]
                        known_dev.planner = dev["planner"]
                        known_dev.lots_req = dev["lots_req"]
                        known_dev.lots_rec = dev["lots_rec"]
                        known_dev.lots_apprv = dev["lots_apprv"]
                        known_dev.sq_ft_req = dev["sq_ft_req"]
                        known_dev.units_apprv = dev["units_apprv"]
                        known_dev.units_req = dev["units_req"]
                        known_dev.zoning = dev["zoning"]
                        known_dev.plan_number = dev["plan_number"]
                        known_dev.CreationDate = dev["CreationDate"]
                        known_dev.Creator = dev["Creator"]
                        known_dev.EditDate = dev["EditDate"]
                        known_dev.Editor = dev["Editor"]

                        known_dev.save()

                    # Nothing new here.
                    # else:
                        # print("Nothing new from the API. We already know about it.")

                # If we don't know about it, we need to add it
                except Development.DoesNotExist:
                    Development.objects.create(OBJECTID=dev["OBJECTID"],
                                               devplan_id=dev["devplan_id"],
                                               submitted=dev["submitted"],
                                               submitted_yr=dev["submitted_yr"],
                                               approved=dev["approved"],
                                               daystoapprove=dev["daystoapprove"],
                                               plan_type=dev["plan_type"],
                                               status=dev["status"],
                                               appealperiodends=dev["appealperiodends"],
                                               updated=dev["updated"],
                                               sunset_date=dev["sunset_date"],
                                               acreage=dev["acreage"],
                                               major_street=dev["major_street"],
                                               cac=dev["cac"],
                                               engineer=dev["engineer"],
                                               engineer_phone=dev["engineer_phone"],
                                               developer=dev["developer"],
                                               developer_phone=dev["developer_phone"],
                                               plan_name=dev["plan_name"],
                                               planurl=dev["planurl"],
                                               planurl_approved=dev["planurl_approved"],
                                               planner=dev["planner"],
                                               lots_req=dev["lots_req"],
                                               lots_rec=dev["lots_rec"],
                                               lots_apprv=dev["lots_apprv"],
                                               sq_ft_req=dev["sq_ft_req"],
                                               units_apprv=dev["units_apprv"],
                                               units_req=dev["units_req"],
                                               zoning=dev["zoning"],
                                               plan_number=dev["plan_number"],
                                               CreationDate=dev["CreationDate"],
                                               Creator=dev["Creator"],
                                               EditDate=dev["EditDate"],
                                               Editor=dev["Editor"])
                    # print("Does not exist. Creating one.")
        except KeyError:
            n = datetime.now()
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": KeyError: 'features'")
            logger.info("batch_of_devs_json")
            logger.info(batch_of_devs_json)


def zoning_api_scan():
    # ////
    # Zoning API (Rezoning requests)
    # https://data-ral.opendata.arcgis.com/datasets/rezoning-requests
    # \\\\

    # Get all zoning ids
    # all_zon_ids_query = ("https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/Rezoning_Requests/"
    #                      "FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=false&returnIdsOnly=true&"
    #                      "outSR=4326&f=json")
    # all_zon_ids = get_all_ids(all_zon_ids_query)

    zon_query = ("https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/Rezoning_Requests/"
                 "FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json")

    zon_json = get_api_json(zon_query)

    # Process each zoning request
    if zon_json is not None:
        try:
            for features in zon_json["features"]:
                zon = features["attributes"]

                # Try to get the zoning request from the DB and check if it needs to be updated.
                try:
                    known_zon = Zoning.objects.get(zpyear=zon["zpyear"], zpnum=zon["zpnum"])

                    # If the new object is not the same as the one in the DB, update it.
                    if api_object_is_different(known_zon, zon):
                        # print("Object " + str(known_zon) + "is in the DB and is different. Updating it.")

                        known_zon.OBJECTID = zon["OBJECTID"]
                        known_zon.zpyear = zon["zpyear"]
                        known_zon.zpnum = zon["zpnum"]
                        known_zon.submittal_date = zon["submittal_date"]
                        known_zon.petitioner = zon["petitioner"]
                        known_zon.location = zon["location"]
                        known_zon.remarks = zon["remarks"]
                        known_zon.zp_petition_acres = str(zon["zp_petition_acres"])
                        known_zon.planning_commission_action = zon["planning_commission_action"]
                        known_zon.city_council_action = zon["city_council_action"]
                        known_zon.ph_date = zon["ph_date"]
                        known_zon.withdraw_date = zon["withdraw_date"]
                        known_zon.exp_date_120_days = zon["exp_date_120_days"]
                        known_zon.exp_date_2_year = zon["exp_date_2_year"]
                        known_zon.ordinance_number = zon["ordinance_number"]
                        known_zon.received_by = zon["received_by"]
                        known_zon.last_revised = zon["last_revised"]
                        known_zon.drain_basin = zon["drain_basin"]
                        known_zon.cac = zon["cac"]
                        known_zon.comprehensive_plan_districts = zon["comprehensive_plan_districts"]
                        known_zon.GlobalID = zon["GlobalID"]
                        known_zon.CreationDate = zon["CreationDate"]
                        known_zon.EditDate = zon["EditDate"]

                        known_zon.save()

                    # Nothing new here.
                    # else:
                    #     print("Nothing new from the API. We already know about it.")

                # If we don't know about it, we need to add it
                except Zoning.DoesNotExist:
                    Zoning.objects.create(OBJECTID=zon["OBJECTID"],
                                          zpyear=zon["zpyear"],
                                          zpnum=zon["zpnum"],
                                          submittal_date=zon["submittal_date"],
                                          petitioner=zon["petitioner"],
                                          location=zon["location"],
                                          remarks=zon["remarks"],
                                          zp_petition_acres=zon["zp_petition_acres"],
                                          planning_commission_action=zon["planning_commission_action"],
                                          city_council_action=zon["city_council_action"],
                                          ph_date=zon["ph_date"],
                                          withdraw_date=zon["withdraw_date"],
                                          exp_date_120_days=zon["exp_date_120_days"],
                                          exp_date_2_year=zon["exp_date_2_year"],
                                          ordinance_number=zon["ordinance_number"],
                                          received_by=zon["received_by"],
                                          last_revised=zon["last_revised"],
                                          drain_basin=zon["drain_basin"],
                                          cac=zon["cac"],
                                          comprehensive_plan_districts=zon["comprehensive_plan_districts"],
                                          GlobalID=zon["GlobalID"],
                                          CreationDate=zon["CreationDate"],
                                          EditDate=zon["EditDate"])
                    # print("Does not exist. Creating one.")
        except KeyError:
            n = datetime.now()
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": KeyError: 'features'")
            logger.info("zon_json")
            logger.info(zon_json)
    else:
        n = datetime.now()
        logger.info(n.strftime("%H:%M %m-%d-%y") + ": zon_json is None. Zoning API is probably down")