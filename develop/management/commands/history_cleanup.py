from django.core.management.base import BaseCommand
from develop.models import *

class Command(BaseCommand):
    def handle(self, *args, **options):
        # self.scan_for_lots_of_history()
        zon_case_1816 = Zoning.objects.get(id=1816)
        all_records = zon_case_1816.history.all()

        n = 0
        while(n < len(all_records) - 1):
            new_record = all_records[n]
            old_record = all_records[n+1]

            delta = new_record.diff_against(old_record)
            changed_fields = []
            for change in delta.changes:
                # print("{} changed from {} to {}".format(change.field, change.old, change.new))
                changed_fields.append(change.field)

            print(changed_fields)

            n += 1

        print("# Records: " + str(len(all_records)))

        # for record in zon_case_1816.history.all():
        #     print(record.modified_date)

    def scan_for_lots_of_history(self):
        all_devs = Development.objects.all()
        all_SiteReviewCases = SiteReviewCases.objects.all()
        all_zoning = Zoning.objects.all()
        all_aas = AdministrativeAlternates.objects.all()
        all_tcs = TextChangeCases.objects.all()

        print("Development")

        for dev in all_devs:
            dev_history = dev.history.all()
            if len(dev_history) > 9:
                print(str(len(dev_history)) + " records, " + str(dev) + " - " + str(dev.id))

        print("\nSiteReviewCases")

        for sr in all_SiteReviewCases:
            sr_history = sr.history.all()
            if len(sr_history) > 9:
                print(str(len(sr_history)) + " records, " + str(sr) + " - " + str(sr.id))

        print("\nZoning")

        for zon in all_zoning:
            zon_history = zon.history.all()
            if len(zon_history) > 9:
                print(str(len(zon_history)) + " records, " + str(zon) + " - " + str(zon.id))

        print("\nAdministrativeAlternates")

        for aa in all_aas:
            aa_history = aa.history.all()
            if len(aa_history) > 9:
                print(str(len(aa_history)) + " records, " + str(aa) + " - " + str(aa.id))

        print("\nTextChangeCases")

        for tc in all_tcs:
            tc_history = tc.history.all()
            if len(tc_history) > 9:
                print(str(len(tc_history)) + " records, " + str(tc) + " - " + str(tc.id))



