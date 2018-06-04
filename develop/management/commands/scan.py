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
        # Development Planning API

        # Get total number of developments from the API
        total_dev_count_query = ("https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/Development_Plans"
                                 "/FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=false"
                                 "&outSR=4326&f=json&returnCountOnly=true")
        total_devs = get_total_developments(total_dev_count_query)

        print("Total Devs: " + str(total_devs))

        # Get all development ids
        all_dev_ids_query = ("https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/Development_Plans"
                             "/FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=false&returnIdsOnly=true"
                             "&outSR=4326&f=json")
        all_dev_ids = get_all_dev_ids(all_dev_ids_query)

        # print("Dev ids: ")
        # print(all_dev_ids)

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

            # print(len(batch_of_devs_json))

            # Process each dev
            for dev in batch_of_devs_json:
                # Is the dev new? Do we have it already in the DB?
                # If no, need to add it
                if not known_dev(dev):
                    # create new development object, dev_json_to_django_object()
                    # save()
                    pass
                # If yes, we already know about it
                # Next question. Is there an update?
                else:
                    # create new development object, dev_json_to_django_object()
                    # get existing from DB
                    # If the new object is the same as the one in the DB, do nothing
                    if new_dev == existing_dev:
                        pass
                    # If the new object does differ from the one in the DB, update it
                    else:
                        new_dev.update()

