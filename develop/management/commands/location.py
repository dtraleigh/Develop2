import logging
from datetime import datetime

from develop.models import *

logger = logging.getLogger("django")


def get_subscribers_covered_CACs(subscriber):
    # Subscribers have "cover areas"
    # A cover area is a collection of CACs
    # CACs should match the name of the strings coming in from the CAC field
    covered_CACs_total_extend = []
    cover_areas_for_this_user = [a for a in subscriber.cover_areas.all()]

    for area in cover_areas_for_this_user:
        cacs = [b for b in area.CACs.all()]
        covered_CACs_total_extend.extend(cacs)

    return list(set(covered_CACs_total_extend))


def get_subscribers_covered_changed_items(items_that_changed, covered_CACs_total):
    # With a subscriber's covered CACs and a list of changed items,
    # return a subset of the items that are equal to one of these CACs
    # also include CAC of None
    covered_items = []

    for item in items_that_changed:
        cac = ""

        if isinstance(item, TextChangeCases):
            covered_items.append(item)
        else:
            try:
                if item.cac is None and item.cac_override is None:
                    covered_items.append(item)
                elif item.cac_override:
                    for cac in covered_CACs_total:
                        if cac.name.lower() in item.cac_override.lower():
                            covered_items.append(item)
                else:
                    for cac in covered_CACs_total:
                        if cac.name.lower() in item.cac.lower():
                            covered_items.append(item)

            except AttributeError:
                n = datetime.now()
                logger.info(n.strftime("%H:%M %m-%d-%y") + ": AttributeError. cac.name: " + str(cac) +
                            ", item.cac: " + str(item.cac))
