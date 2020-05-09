from django.test import SimpleTestCase
from develop.management.commands.location import *


class ScrapeTestCase(SimpleTestCase):
    def test_clean_address(self):
        address1 = "S West Street"
        self.assertEqual(clean_address(address1), "south West Street, raleigh NC USA")

        address2 = "E LENOIR ST"
        self.assertEqual(clean_address(address2), "east LENOIR ST, raleigh NC USA")

        address3 = "T W ALEXANDER  DR"
        self.assertEqual(clean_address(address3), "T W ALEXANDER DR, raleigh NC USA")

        address4 = "M E Valentine Dr"
        self.assertEqual(clean_address(address4), "M E Valentine Dr, raleigh NC USA")

        address5 = "US HWY 70"
        self.assertEqual(clean_address(address5), "US HWY 70, raleigh NC USA")

    def test_get_parcel_by_pin(self):
        pin1 = "1763323847"
        parcel = get_parcel_by_pin(pin1)

        self.assertEqual(parcel["PIN_NUM"], pin1)
