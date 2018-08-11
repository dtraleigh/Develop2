# ///
# This command is used to query the APIs, compare the results with the DB and make appropriate changes.
# \\\
import logging

from django.core.management.base import BaseCommand

from develop.management.commands.api_scans import *

logger = logging.getLogger("django")


class Command(BaseCommand):
    def handle(self, *args, **options):
        development_api_scan()
        zoning_api_scan()
