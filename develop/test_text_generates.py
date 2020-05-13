from django.test import SimpleTestCase
from develop.management.commands.text_generates import *

from django.conf import settings


class ScrapeTestCase(SimpleTestCase):
    def test_get_instance_text(self):
        if settings.DEVELOP_INSTANCE == "Develop":
            self.assertEqual(get_instance_text("DEV"),
                             "[Develop - DEV]\n")
            self.assertEqual(get_instance_text(""),
                             "[Develop - ]\n")
        else:
            self.assertEqual(get_instance_text("DEV"),
                             "")
            self.assertEqual(get_instance_text(""),
                             "")
