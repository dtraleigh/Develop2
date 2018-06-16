# ///
# This command is used to query the API, compare the results with the DB and make appropriate changes.
# \\\
import logging
from django.core.management.base import BaseCommand

from develop.management.commands.actions import *
from develop.models import *

logger = logging.getLogger("django")


class Command(BaseCommand):
    def handle(self, *args, **options):
        # ////
        # Development Planning API
        # \\\\

        # Get all development ids
        all_dev_ids_query = ("https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/Development_Plans"
                             "/FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=false&returnIdsOnly=true"
                             "&outSR=4326&f=json")
        all_dev_ids = get_all_dev_ids(all_dev_ids_query)

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
                    print("Does not exist. Creating one.")

        # print("Total Devs: " + str(get_total_developments()))
