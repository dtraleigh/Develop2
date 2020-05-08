from bs4 import BeautifulSoup

from django.test import SimpleTestCase
from develop.management.commands.scrape import *


class ScrapeTestCase(SimpleTestCase):
    def test_get_page_content(self):
        # quick test to check that the sites we are scraping are returning data
        websites_used = [
            "https://raleighnc.gov/services/zoning-planning-and-development/site-review-cases",
            "https://raleighnc.gov/SupportPages/administrative-alternate-design-cases",
            "https://raleighnc.gov/SupportPages/zoning-cases",
            "https://raleighnc.gov/SupportPages/text-change-cases",
            ]

        for url in websites_used:
            self.assertIsNotNone(get_page_content(url))

    def test_get_rows_in_table(self):
        # get_rows_in_table() takes in an html table and returns
        # a list of the rows. Test that we get back the correct number of rows from the table.

        # Check one random sample from SRs
        sr_table = """<table><thead><tr><td><strong>Case Number</strong></td>
        <td><strong>Project Name/Location/Description</strong></td>
        <td><strong>CAC</strong></td>
        <td><strong>Status*</strong></td>
        <td><strong>Contact</strong></td>
        </tr></thead><tbody><tr><td><a href="https://cityofraleigh0drupal.blob.core.usgovcloudapi.net/drupal-prod/COR15/ASR-0001-2020.pdf">ASR-0001-2020</a></td>
        <td>Brier Creek Apartments/ 3900, 3910, 3920 and 3930 Macaw St/ apartments</td>
        <td>Northwest</td>
        <td>UR</td>
        <td><a href="/directory?action=search&amp;firstName=Michael&amp;lastName=Walters">Walters</a></td>
        </tr><tr><td><a href="https://cityofraleigh0drupal.blob.core.usgovcloudapi.net/drupal-prod/COR15/ASR-0002-2020.pdf">ASR-0002-2020</a></td>
        <td>Iglesia De Dios Pentecostal/ 4508 Old Poole Rd/ church</td>
        <td>Southeast</td>
        <td>UR</td>
        <td><a href="/directory?action=search&amp;firstName=Kasey&amp;lastName=Evans">Evans</a></td>
        </tr><tr><td><a href="https://cityofraleigh0drupal.blob.core.usgovcloudapi.net/drupal-prod/COR15/SR-106-17.pdf">SR-106-17</a></td>
        <td>Wakefield United Methodist/ 11001 Forest Pines Dr/ Place of Worship</td>
        <td>North</td>
        <td>UR</td>
        <td><a href="/directory?action=search&amp;firstName=Michael&amp;lastName=Walters">Walters</a></td>
        </tr></tbody></table>"""
        sr_souped = BeautifulSoup(sr_table, "html.parser")

        self.assertEqual(len(get_rows_in_table(sr_souped, "test")), 3)

    def test_get_case_number_from_row(self):
        # get_case_number_from_row() takes in a a list of all <td> tags that were in that <tr>
        sr_tds1 = """<td><a href="https://cityofraleigh0drupal.blob.core.usgovcloudapi.net/drupal-prod/COR15/SR-106-17.pdf">SR-106-17</a></td>, <td>Wakefield United Methodist/ 11001 Forest Pines Dr/ Place of Worship</td>, <td>North</td>, <td>UR</td>, <td><a href="/directory?action=search&amp;firstName=Michael&amp;lastName=Walters">Walters</a></td>"""
        tds_souped = BeautifulSoup(sr_tds1, "html.parser")
        row_tds = tds_souped.find_all("td")

        self.assertEqual(get_case_number_from_row(row_tds), "SR-106-17")

        sr_tds2 = """<td>SR-106-17</td>, <td>Wakefield United Methodist/ 11001 Forest Pines Dr/ Place of Worship</td>, <td>North</td>, <td>UR</td>, <td><a href="/directory?action=search&amp;firstName=Michael&amp;lastName=Walters">Walters</a></td>"""
        tds_souped = BeautifulSoup(sr_tds1, "html.parser")
        row_tds = tds_souped.find_all("td")

        self.assertEqual(get_case_number_from_row(row_tds), "SR-106-17")

    def test_get_contact(self):
        contact1 = """<td><a href="/directory?action=search&amp;firstName=Michael&amp;lastName=Walters">Walters</a></td>"""
        contact1_souped = BeautifulSoup(contact1, "html.parser")

        self.assertEqual(get_contact(contact1_souped), "Walters")

        contact2 = """<td>Walters</td>"""
        contact2_souped = BeautifulSoup(contact2, "html.parser")

        self.assertEqual(get_contact(contact2_souped), "Walters")

        contact3 = """<td></td>"""
        contact3_souped = BeautifulSoup(contact3, "html.parser")

        self.assertEqual(get_contact(contact3_souped), None)

    def test_get_generic_link(self):
        content1 = """<td><a href="https://cityofraleigh0drupal.blob.core.usgovcloudapi.net/drupal-prod/COR15/SR-106-17.pdf">SR-106-17</a></td>"""
        content1_souped = BeautifulSoup(content1, "html.parser")

        self.assertEqual(get_generic_link(content1_souped), "https://cityofraleigh0drupal.blob.core.usgovcloudapi.net/drupal-prod/COR15/SR-106-17.pdf")

        content2 = """<td><a href="https://cityofraleigh0drupal.blob.core.usgovcloudapi.net/drupal prod/COR15/SR 106 17.pdf">SR-106-17</a></td>"""
        content2_souped = BeautifulSoup(content2, "html.parser")

        self.assertEqual(get_generic_link(content2_souped), "https://cityofraleigh0drupal.blob.core.usgovcloudapi.net/drupal%20prod/COR15/SR%20106%2017.pdf")

        content3 = """<td>SR-106-17</td>"""
        content3_souped = BeautifulSoup(content3, "html.parser")

        self.assertEqual(get_generic_link(content3_souped), None)

    def test_get_contact_url(self):
        content1 = """<td><a href="/directory?action=search&amp;firstName=Jason&amp;lastName=Hardin">Hardin</a></td>"""
        content1_souped = BeautifulSoup(content1, "html.parser")

        self.assertEqual(get_contact_url(content1_souped),
                         "https://raleighnc.gov/directory?action=search&firstName=Jason&lastName=Hardin")

        content2 = """<td><a href="/directory?action=sea rch&amp;firstName = Jason&amp;lastName=Hardin">Hardin</a></td>"""
        content2_souped = BeautifulSoup(content2, "html.parser")

        self.assertEqual(get_contact_url(content2_souped),
                         "https://raleighnc.gov/directory?action=search&firstName=Jason&lastName=Hardin")

        content3 = """<td>Hardin</td>"""
        content3_souped = BeautifulSoup(content3, "html.parser")

        self.assertEqual(get_contact_url(content3_souped), None)

