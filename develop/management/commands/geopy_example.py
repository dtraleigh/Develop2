from geopy.geocoders import Nominatim
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from develop.models import Development
from wake.models import WakeCorporate
from cac.models import CitizenAdvisoryCouncil


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


class Command(BaseCommand):
    def handle(self, *args, **options):
        locator = Nominatim(user_agent="myGeocoder")
        devs = Development.objects.all()

        for dev in devs:
            if dev.submitted_yr > 2017 and not dev.cac and not dev.cac_override:
                try:
                    if dev.major_street:
                        address = clean_address(dev.major_street)
                        location = locator.geocode(address)

                        corp = get_wake_location(location.latitude, location.longitude)
                        cac = get_cac_location(location.latitude, location.longitude)

                        # print(str((location.latitude, location.longitude)) + str(corp.long_name) + str(cac.name))
                        print(dev.id, corp.long_name, cac.name)
                    else:
                        print("!!!! - " + str(dev.id) + " has no major street.")
                except AttributeError:
                    print("Unable to acquire position for " + str(dev.id), address)
                    #print(corp)
                    #print(location)
