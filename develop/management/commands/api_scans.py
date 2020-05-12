import logging

from .actions import *
from .location import *
from develop.models import *

logger = logging.getLogger("django")


def is_current_dev(item_year):
    cutoff_year = 2000

    if item_year is None:
        return False

    if item_year > cutoff_year:
        return True
    return False


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
    if all_dev_ids:
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
                    dev_info_from_json = features["attributes"]

                    # Let's not even do anything to devs before the cutoff year
                    if is_current_dev(dev_info_from_json["submitted_yr"]):

                        # Try to get the development from the DB and check if it needs to be updated.
                        try:
                            if dev_info_from_json["OBJECTID"]:
                                known_dev_object = Development.objects.get(OBJECTID=dev_info_from_json["OBJECTID"])
                            else:
                                logger.info("No OBJECTID on this item")
                                logger.info(dev_info_from_json)

                            # If the new object is not the same as the one in the DB, update it.
                            # Need to also not include old  developments
                            if api_object_is_different(known_dev_object, dev_info_from_json) and \
                                    known_dev_object.submitted_yr > 2000:
                                # Object is in the DB, is current, and is different. Updating it.

                                known_dev_object.OBJECTID = dev_info_from_json["OBJECTID"]
                                known_dev_object.submitted = dev_info_from_json["submitted"]
                                known_dev_object.submitted_yr = dev_info_from_json["submitted_yr"]
                                known_dev_object.approved = dev_info_from_json["approved"]
                                known_dev_object.daystoapprove = dev_info_from_json["daystoapprove"]
                                known_dev_object.plan_type = dev_info_from_json["plan_type"]
                                known_dev_object.status = dev_info_from_json["status"]
                                known_dev_object.appealperiodends = dev_info_from_json["appealperiodends"]
                                known_dev_object.updated = dev_info_from_json["updated"]
                                known_dev_object.sunset_date = dev_info_from_json["sunset_date"]
                                known_dev_object.acreage = dev_info_from_json["acreage"]
                                known_dev_object.major_street = dev_info_from_json["major_street"]
                                known_dev_object.cac = dev_info_from_json["cac"]
                                known_dev_object.engineer = dev_info_from_json["engineer"]
                                known_dev_object.engineer_phone = dev_info_from_json["engineer_phone"]
                                known_dev_object.developer = dev_info_from_json["developer"]
                                known_dev_object.developer_phone = dev_info_from_json["developer_phone"]
                                known_dev_object.plan_name = dev_info_from_json["plan_name"]
                                known_dev_object.planurl = dev_info_from_json["planurl"]
                                known_dev_object.planurl_approved = dev_info_from_json["planurl_approved"]
                                known_dev_object.planner = dev_info_from_json["planner"]
                                known_dev_object.lots_req = dev_info_from_json["lots_req"]
                                known_dev_object.lots_rec = dev_info_from_json["lots_rec"]
                                known_dev_object.lots_apprv = dev_info_from_json["lots_apprv"]
                                known_dev_object.sq_ft_req = dev_info_from_json["sq_ft_req"]
                                known_dev_object.units_apprv = dev_info_from_json["units_apprv"]
                                known_dev_object.units_req = dev_info_from_json["units_req"]
                                known_dev_object.zoning = dev_info_from_json["zoning"]
                                known_dev_object.plan_number = dev_info_from_json["plan_number"]
                                known_dev_object.CreationDate = dev_info_from_json["CreationDate"]
                                known_dev_object.Creator = dev_info_from_json["Creator"]
                                known_dev_object.EditDate = dev_info_from_json["EditDate"]
                                known_dev_object.Editor = dev_info_from_json["Editor"]

                                # If cac and cac_override are None, let's try to calculate it.
                                if not known_dev_object.cac and not known_dev_object.cac_override:
                                    known_dev_object.cac_override = cac_lookup(dev_info_from_json["major_street"])

                                known_dev_object.save()

                            # Nothing new here.
                            # else:
                                # print("Nothing new from the API. We already know about it.")

                        # If we don't know about it, we need to add it
                        except Development.DoesNotExist:
                            # cac might be None so let's try and figure it out
                            if not dev_info_from_json["cac"]:
                                cac_override = cac_lookup(dev_info_from_json["major_street"])
                            else:
                                cac_override = None

                            Development.objects.create(OBJECTID=dev_info_from_json["OBJECTID"],
                                                       devplan_id=dev_info_from_json["devplan_id"],
                                                       submitted=dev_info_from_json["submitted"],
                                                       submitted_yr=dev_info_from_json["submitted_yr"],
                                                       approved=dev_info_from_json["approved"],
                                                       daystoapprove=dev_info_from_json["daystoapprove"],
                                                       plan_type=dev_info_from_json["plan_type"],
                                                       status=dev_info_from_json["status"],
                                                       appealperiodends=dev_info_from_json["appealperiodends"],
                                                       updated=dev_info_from_json["updated"],
                                                       sunset_date=dev_info_from_json["sunset_date"],
                                                       acreage=dev_info_from_json["acreage"],
                                                       major_street=dev_info_from_json["major_street"],
                                                       cac=dev_info_from_json["cac"],
                                                       cac_override=cac_override,
                                                       engineer=dev_info_from_json["engineer"],
                                                       engineer_phone=dev_info_from_json["engineer_phone"],
                                                       developer=dev_info_from_json["developer"],
                                                       developer_phone=dev_info_from_json["developer_phone"],
                                                       plan_name=dev_info_from_json["plan_name"],
                                                       planurl=dev_info_from_json["planurl"],
                                                       planurl_approved=dev_info_from_json["planurl_approved"],
                                                       planner=dev_info_from_json["planner"],
                                                       lots_req=dev_info_from_json["lots_req"],
                                                       lots_rec=dev_info_from_json["lots_rec"],
                                                       lots_apprv=dev_info_from_json["lots_apprv"],
                                                       sq_ft_req=dev_info_from_json["sq_ft_req"],
                                                       units_apprv=dev_info_from_json["units_apprv"],
                                                       units_req=dev_info_from_json["units_req"],
                                                       zoning=dev_info_from_json["zoning"],
                                                       plan_number=dev_info_from_json["plan_number"],
                                                       CreationDate=dev_info_from_json["CreationDate"],
                                                       Creator=dev_info_from_json["Creator"],
                                                       EditDate=dev_info_from_json["EditDate"],
                                                       Editor=dev_info_from_json["Editor"])

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
                        known_zon.cac = zon["advisory_committee_areas"]
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
                    # cac might be None so let's try and figure it out
                    if not zon["advisory_committee_areas"]:
                        cac_override = cac_lookup(zon["location"])
                    else:
                        cac_override = None

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
                                          cac=zon["advisory_committee_areas"],
                                          cac_override=cac_override,
                                          comprehensive_plan_districts=zon["comprehensive_plan_districts"],
                                          GlobalID=zon["GlobalID"],
                                          CreationDate=zon["CreationDate"],
                                          EditDate=zon["EditDate"])
                    # print("Does not exist. Creating one.")
        except KeyError:
            n = datetime.now()
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": KeyError: 'features'")
            logger.info("zon")
            logger.info(zon)
    else:
        n = datetime.now()
        logger.info(n.strftime("%H:%M %m-%d-%y") + ": zon_json is None. Zoning API is probably down")