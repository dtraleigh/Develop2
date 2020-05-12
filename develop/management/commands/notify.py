# ///
# This command is used to notify subscribers of changes in the last hour
# \\\
import logging
from datetime import datetime
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from develop.models import *
from .location import *
from .actions import create_email_message, create_new_discourse_post
from .emails import *

logger = logging.getLogger("django")


def get_everything_that_changed():
    # Get everything that has changed in the last hour
    everything_that_changed = []

    # Let's exclude Development changes for now as we need to review the API content due to possible changes.
    # devs_that_changed = Development.objects.filter(modified_date__range=[timezone.now() - timedelta(hours=1),
    #                                                                      timezone.now()])
    SRs_that_changed = SiteReviewCases.objects.filter(modified_date__range=[timezone.now() - timedelta(hours=1),
                                                                            timezone.now()])
    zons_that_changed = Zoning.objects.filter(modified_date__range=[timezone.now() - timedelta(hours=1),
                                                                    timezone.now()])
    AADs_that_changed = AdministrativeAlternates.objects.filter(modified_date__range=[timezone.now() -
                                                                                      timedelta(hours=1),
                                                                                      timezone.now()])
    TCs_that_changed = TextChangeCases.objects.filter(modified_date__range=[timezone.now() -
                                                                            timedelta(hours=1),
                                                                            timezone.now()])

    # for dev in devs_that_changed:
    #     everything_that_changed.append(dev)
    for SR in SRs_that_changed:
        everything_that_changed.append(SR)
    for AAD in AADs_that_changed:
        everything_that_changed.append(AAD)
    for TC in TCs_that_changed:
        everything_that_changed.append(TC)
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

    return everything_that_changed


class Command(BaseCommand):
    def handle(self, *args, **options):
        control = Control.objects.get(id=1)
        if control.notify:

            everything_that_changed = get_everything_that_changed()

            if everything_that_changed:
                if settings.DEVELOP_INSTANCE == "Develop":
                    subject = "Update on Development Tracker [Develop]"
                else:
                    subject = "Update on Development Tracker"

                # We need to filter everything_that_changed for only the cover areas that each user is subscribed to.
                # We also need to include None. Rather than pass literally everything_that_changed let's filter it
                # for each user and then send them an email.
                # Text Changes don't have a CAC so include them all which is ok since there are so few
                all_active_subscribers = Subscriber.objects.filter(send_emails=True)

                for subscriber in all_active_subscribers:
                    # Get list of CACs we need to worry about for this subscriber
                    covered_CACs_total = get_subscribers_covered_CACs(subscriber)

                    # For this subscriber and the list everything_that_changed, get items that changed that
                    # this subscriber is covering
                    covered_items = get_subscribers_covered_changed_items(everything_that_changed, covered_CACs_total)
                    #print(covered_items)

                    # Post to discourse community
                    if covered_items and subscriber.is_bot:
                        for item in covered_items:
                            create_new_discourse_post(subscriber, item)
                            # Alert admin if CAC is None
                            if not isinstance(item, TextChangeCases):
                                if not item.cac and not item.cac_override:
                                    message = "notify: Need to add a CAC to " + str(item)
                                    send_email_notice(message, email_admins())

                    # Send emails if the subscriber is not a bot
                    if covered_items and not subscriber.is_bot:
                        message = create_email_message(covered_items)
                        email_to = [subscriber.email]
                        send_email_notice(message, email_to)

                        n = datetime.now()
                        logger.info("Email sent at " + n.strftime("%H:%M %m-%d-%y"))
