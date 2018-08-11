from develop.models import *

from datetime import datetime
import logging

logger = logging.getLogger("django")


def string_output_unix_datetime(unix_datetime):
    if unix_datetime:
        return datetime.fromtimestamp(unix_datetime / 1000).strftime('%Y-%m-%d %H:%M:%S')
    return str("None")


def difference_email_output(dev):
    output = ""

    # Get the most recent version of the dev and the one previously
    dev_most_recent = dev.history.first()
    dev_previous = dev_most_recent.prev_record

    # Get all the dev fields
    fields = dev._meta.get_fields()

    # Loop through each field, except created_date, modified_date, and id.
    # If the fields are not equal, add it to output.
    for field in fields:
        if field.name != "created_date" and field.name != "modified_date" and field.name != "id" and field.name != "EditDate":
            dev_most_recent_field = getattr(dev_most_recent, field.name)
            dev_old_field = getattr(dev_previous, field.name)

            # If there is a difference...
            if dev_most_recent_field != dev_old_field:
                # If it's a date field, we need to convert it to a human readable string
                # Let's ignore EditDate
                if field.get_internal_type() == "BigIntegerField" and field.name != "EditDate":
                    try:
                        before_date_hr = datetime.fromtimestamp(dev_old_field / 1000).strftime('%Y-%m-%d %H:%M:%S')
                        after_date_hr = datetime.fromtimestamp(dev_most_recent_field / 1000).strftime('%Y-%m-%d %H:%M:%S')

                        output += "    " + field.verbose_name + " changed from \"" + before_date_hr + "\" to \"" + \
                                  after_date_hr + "\"\n"
                    except:
                        logger.info("Problem calculating the datetime")
                        logger.info("field is " + str(field))
                        if dev_old_field:
                            logger.info("dev_old_field: " + str(dev_old_field))
                        else:
                            logger.info("dev_old_field: None")

                        if dev_old_field:
                            logger.info("dev_most_recent_field: " + str(dev_old_field))
                        else:
                            logger.info("dev_most_recent_field: None")


                else:
                    output += "    " + field.verbose_name + " changed from \"" + str(dev_old_field) + "\" to \"" + \
                              str(dev_most_recent_field) + "\"\n"

    return output


def get_new_dev_text(new_devs):
    for new_dev in new_devs:
        if isinstance(new_dev, Development):
            new_devs_message = "***" + str(new_dev.plan_name) + ", " + str(new_dev.plan_number) + "***\n"
            new_devs_message += "    Submitted year: " + str(new_dev.submitted_yr) + "\n"
            new_devs_message += "    Plan type: " + str(new_dev.plan_type) + "\n"
            new_devs_message += "    Status: " + str(new_dev.status) + "\n"
            new_devs_message += "    Major Street: " + str(new_dev.major_street) + "\n"
            new_devs_message += "    CAC: " + str(new_dev.cac) + "\n"
            new_devs_message += "    URL: " + str(new_dev.planurl) + "\n\n"
        if isinstance(new_dev, SiteReviewCases):
            new_devs_message += "***" + str(new_dev.project_name) + ", " + str(new_dev.case_number) + "***\n"
            new_devs_message += "    Status: " + str(new_dev.status) + "\n"
            new_devs_message += "    CAC: " + str(new_dev.cac) + "\n"
            new_devs_message += "    URL: " + str(new_dev.case_url) + "\n\n"

    return new_devs_message


def get_updated_dev_text(updated_devs):
    for updated_dev in updated_devs:
        # Need to look at the history and compare the most recent update with the one before it.
        if isinstance(updated_dev, Development):
            updated_devs_message = "***" + str(updated_dev.plan_name) + ", " + str(updated_dev.plan_number) + "***\n"
            updated_devs_message += "    Updated: " + string_output_unix_datetime(updated_dev.updated) + "\n"
            updated_devs_message += "    Status: " + str(updated_dev.status) + "\n"
            updated_devs_message += "    CAC: " + str(updated_dev.cac) + "\n"
            updated_devs_message += "    URL: " + str(updated_dev.planurl) + "\n\n"
            updated_devs_message += "  *UPDATES*\n"
            updated_devs_message += difference_email_output(updated_dev)
        if isinstance(updated_dev, SiteReviewCases):
            updated_devs_message += "***" + str(updated_dev.project_name) + ", " + str(updated_dev.case_number) + "***\n"
            updated_devs_message += "    Updated: " + updated_dev.modified_date.strftime("%m-%d-%y %H:%M") + "\n"
            updated_devs_message += "    Status: " + str(updated_dev.status) + "\n"
            updated_devs_message += "    CAC: " + str(updated_dev.cac) + "\n"
            updated_devs_message += "    URL: " + str(updated_dev.case_url) + "\n\n"
            updated_devs_message += "  *UPDATES*\n"
            updated_devs_message += difference_email_output(updated_dev)

        updated_devs_message += "\n"

    return updated_devs_message