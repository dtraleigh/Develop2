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

        print(total_devs)
