# ///
# This command is used to notify subscribers of changes in the last hour
# \\\
import logging, pytz
from datetime import datetime
from datetime import timedelta

from django.utils import timezone
from django.core.management.base import BaseCommand
from django.core.mail import send_mail

from develop.management.commands.actions import *
from develop.models import *

logger = logging.getLogger("django")


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Get developments that have changed in the last hour
        devs_that_changed = Development.objects.filter(modified_date__range=[timezone.now() - timedelta(hours=1), timezone.now()])

        if devs_that_changed:
            subject = "Update on Development Tracker"
            message = create_email_message(devs_that_changed)
            email_from = "develop@dtraleigh.com"
            all_active_subscribers = Subscriber.objects.filter(send_emails=True)

            try:
                send_mail(
                    subject,
                    message,
                    email_from,
                    [sub.email for sub in all_active_subscribers],
                    fail_silently=False,
                )
                n = datetime.now()
                logger.info("Email sent at " + n.strftime("%H:%M %m-%d-%y"))
            except:
                n = datetime.now()
                logger.info("Problem sending email at " + n.strftime("%H:%M %m-%d-%y"))
