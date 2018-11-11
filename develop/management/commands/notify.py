# ///
# This command is used to notify subscribers of changes in the last hour
# \\\
import logging, pytz
from datetime import datetime
from datetime import timedelta

from django.utils import timezone
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

from .actions import create_email_message
from develop.models import *

logger = logging.getLogger("django")


class Command(BaseCommand):
    def handle(self, *args, **options):
        control = Control.objects.get(id=1)
        if control.notify:
            # Get everything that have changed in the last hour
            devs_that_changed = Development.objects.filter(modified_date__range=[timezone.now() - timedelta(hours=1),
                                                                                 timezone.now()])
            SRs_that_changed = SiteReviewCases.objects.filter(modified_date__range=[timezone.now() - timedelta(hours=1),
                                                                                    timezone.now()])
            zons_that_changed = Zoning.objects.filter(modified_date__range=[timezone.now() - timedelta(hours=1),
                                                                            timezone.now()])

            everything_that_changed = []

            for dev in devs_that_changed:
                everything_that_changed.append(dev)
            for SR in SRs_that_changed:
                everything_that_changed.append(SR)
            for zon in zons_that_changed:
                # Not interested in some fields for zoning including OBJECTID, GlobalID, CreationDate
                # (city seems to change these) so let's remove these items from zons_that_changed
                # Need to first find all fields that have changed in this zon
                # If the changes contain something else than OBJECTID, GlobalID, CreationDate, add to
                # everything_that_changed.
                # Else do not.
                zon_most_recent = zon.history.first()
                zon_previous = zon_most_recent.prev_record

                # Get all the zoning fields
                zon_fields = zon._meta.get_fields()

                zon_fields_that_changed = []
                zon_fields_we_dont_want = [Zoning._meta.get_field('OBJECTID'),
                                           Zoning._meta.get_field('GlobalID'),
                                           Zoning._meta.get_field('CreationDate')]

                # Loop through each field, except created_date, modified_date, and id.
                # If the fields are not equal, add it to output.
                for field in zon_fields:
                    if field.name != "created_date" and field.name != "modified_date" and field.name != "id" and field.name != "EditDate":
                        # If its a web scrape, it won't have a lot fields and therefore, we can "skip" this.
                        try:
                            item_most_recent_field = getattr(zon_most_recent, field.name)
                            item_old_field = getattr(zon_previous, field.name)

                            # If there is a difference...
                            if item_most_recent_field != item_old_field:
                                zon_fields_that_changed.append(field)
                        except AttributeError:
                            # Just catch this for now and move on. Should be ok for the objects that are missing data.
                            zon_fields_that_changed.append(field)

                # check if zon_fields_that_changed contains any elements of zon_fields_we_dont_want but
                # still may contain other fields we need to track.
                if any(elem in zon_fields_that_changed for elem in zon_fields_we_dont_want):
                    # If there are fields in zon_fields_that_changed that are NOT in zon_fields_we_dont_want
                    for field in zon_fields_that_changed:
                        if field not in zon_fields_we_dont_want:
                            everything_that_changed.append(zon)
                            break
                else:
                    everything_that_changed.append(zon)

            if everything_that_changed:
                if settings.DEVELOP_INSTANCE == "Develop":
                    subject = "Update on Development Tracker [Develop]"
                else:
                    subject = "Update on Development Tracker"

                # We need to filter everything_that_changed for only the cover areas that each user is subscribed to.
                # We also need to include None. Rather than pass literally everything_that_changed let's filter it
                # for each user and then send them an email.
                all_active_subscribers = Subscriber.objects.filter(send_emails=True)

                for subscriber in all_active_subscribers:
                    # Get list of CACs we need to worry about
                    covered_cacs_total_extend = []
                    cover_areas_for_this_user = [a for a in subscriber.cover_areas.all()]
                    for area in cover_areas_for_this_user:
                        cacs = [b for b in area.CACs.all()]
                        covered_cacs_total_extend.extend(cacs)

                    covered_cacs_total = list(set(covered_cacs_total_extend))

                    covered_items = []
                    for item in everything_that_changed:
                        # append to covered_items things from only cacs that the user is covering plus None
                        try:
                            for cac in covered_cacs_total:
                                if cac.name.lower() in item.cac.lower():
                                    covered_items.append(item)
                            if item.cac == None:
                                covered_items.append(item)
                        except AttributeError:
                            n = datetime.now()
                            logger.info(n.strftime("%H:%M %m-%d-%y") + ": AttributeError. cac.name: " + cac.name + ", item.cac: " + item.cac)


                    if covered_items:
                        message = create_email_message(covered_items)
                        email_from = "develop@dtraleigh.com"

                        try:
                            send_mail(
                                subject,
                                message,
                                email_from,
                                [subscriber.email],
                                fail_silently=False,
                            )
                            n = datetime.now()
                            logger.info("Email sent at " + n.strftime("%H:%M %m-%d-%y"))
                        except:
                            n = datetime.now()
                            logger.info("Problem sending email at " + n.strftime("%H:%M %m-%d-%y"))
