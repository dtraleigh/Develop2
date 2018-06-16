from django.contrib import admin

from develop.models import Development, Subscriber

from simple_history.admin import SimpleHistoryAdmin


class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "date_created", "send_emails")


class DevelopmentsAdmin(SimpleHistoryAdmin):
    list_display = ("devplan_id", "submitted_yr", "status", "major_street", "cac", "plan_name", "plan_number")
    history_list_display = ["status"]


admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(Development, DevelopmentsAdmin)
