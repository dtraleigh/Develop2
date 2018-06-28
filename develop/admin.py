import datetime

from django.contrib import admin

from develop.models import *

from simple_history.admin import SimpleHistoryAdmin


class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_date", "modified_date", "send_emails")


class DevelopmentsAdmin(SimpleHistoryAdmin):
    list_display = ("devplan_id", "updated_date", "submitted_yr", "status", "major_street", "cac", "plan_name", "plan_number", "modified_date", "created_date")
    history_list_display = ["status"]

    def updated_date(self, obj):
        if obj.updated:
            return datetime.datetime.fromtimestamp(obj.updated / 1000).strftime('%Y-%m-%d %H:%M:%S')
        else:
            return "NA"

    updated_date.short_description = 'Date Updated'
    updated_date.admin_order_field = 'updated'


class SiteReviewCasesAdmin(SimpleHistoryAdmin):
    list_display = ("case_number", "project_name", "cac", "status", "contact", "modified_date", "created_date")
    history_list_display = ["status"]


admin.site.register(SiteReviewCases, SiteReviewCasesAdmin)
admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(Development, DevelopmentsAdmin)
