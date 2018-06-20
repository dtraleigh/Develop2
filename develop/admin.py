import datetime

from django.contrib import admin

from develop.models import Development, Subscriber

from simple_history.admin import SimpleHistoryAdmin


class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "date_created", "send_emails")


class DevelopmentsAdmin(SimpleHistoryAdmin):
    list_display = ("devplan_id", "updated_date", "submitted_yr", "status", "major_street", "cac", "plan_name", "plan_number")
    history_list_display = ["status"]

    def updated_date(self, obj):
        if obj.updated:
            return datetime.datetime.fromtimestamp(obj.updated / 1000).strftime('%Y-%m-%d %H:%M:%S')
        else:
            return "NA"

    updated_date.short_description = 'Date Updated'
    updated_date.admin_order_field = 'updated'


admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(Development, DevelopmentsAdmin)
