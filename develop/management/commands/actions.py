import datetime, logging

import requests

from develop.models import *

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


def get_total_developments(url):
    # Example:
    # {
    #   "count":6250
    # }

    json_count = get_api_json(url)

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

    json_of_devs = get_api_json(url)

    return json_of_devs["features"]