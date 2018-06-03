import datetime, logging

import requests

from develop.models import *

logger = logging.getLogger("django")


def get_api_json(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()

    return None


def get_total_developments(url):
    # Example:
    # {
    #   "count":6250
    # }

    json_count = get_api_json(url)

    return json_count["count"]
