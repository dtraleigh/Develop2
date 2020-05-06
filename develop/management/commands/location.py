import logging
from datetime import datetime
from geopy.geocoders import Nominatim

from django.contrib.gis.geos import Point
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
                        if cac.name.lower() == item.cac.lower():
                            covered_items.append(item)

            except AttributeError:
                n = datetime.now()
                logger.info(n.strftime("%H:%M %m-%d-%y") + ": AttributeError. cac.name: " + str(cac) +
                            ", item.cac: " + str(item.cac))

    return covered_items


def cac_lookup(address):
    locator = Nominatim(user_agent="myGeocoder")

    try:
        if address:
            address = clean_address(address)
            location = locator.geocode(address)

            cac = get_cac_location(location.latitude, location.longitude)

            return cac.name
        else:
            n = datetime.now()
            logger.info(n.strftime("%H:%M %m-%d-%y") + ": Newly added item does not have an address.")
            return None
    except AttributeError:
        n = datetime.now()
        logger.info(n.strftime("%H:%M %m-%d-%y") + "Unable to acquire position for ", address)

    return None


def clean_address(address):
    """
    We need to clean the addresses a bit.
    Scenario 1: "S West St" needs to be "South West St"
    Scenario 2: "200 S West St" needs to be "200 South west St"
    Scenario 3: Need to add city, state, and country
    """
    address_parts = address.split()

    for i, part in enumerate(address_parts):
        if part.lower() == "s":
            address_parts[i] = "south"
        elif part.lower() == "n":
            address_parts[i] = "north"
        elif part.lower() == "w":
            address_parts[i] = "west"
        elif part.lower() == "e":
            address_parts[i] = "east"

    return " ".join(address_parts) + ", raleigh NC USA"


def get_wake_location(lat, lon):
    """
    Take in a lat and lon and check which muni it is in the wake app
    """
    pnt = Point(lon, lat)
    try:
        return WakeCorporate.objects.get(geom__intersects=pnt)
    except:
        return None


def get_cac_location(lat, lon):
    """
    Take in a lat and lon and check which cac it is in the cac app
    """
    pnt = Point(lon, lat)
    try:
        return CitizenAdvisoryCouncil.objects.get(geom__intersects=pnt)
    except:
        return None