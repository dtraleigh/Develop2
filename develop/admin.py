import datetime

from django.contrib import admin
from django.contrib.gis import admin

from develop.models import *

from simple_history.admin import SimpleHistoryAdmin
from django.contrib.admin import ModelAdmin, SimpleListFilter


class CACStatusFilter(SimpleListFilter):
    title = 'CAC status'
    parameter_name = 'items'

    def lookups(self, request, model_admin):
        return [
            ('has_cac', 'CAC Assigned'),
            ('no_cac', 'No CAC Assigned'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'has_cac':
            return Development.objects.filter(cac=None, cac_override=None)
        if self.value():
            return Development.objects.filter(cac=None, cac_override=None)


class ControlAdmin(admin.ModelAdmin):
    list_display = ("scrape", "scan", "notify")


class CitizenAdvisoryCouncilAdmin(admin.ModelAdmin):
    list_display = ("name",)


class coverAreaAdmin(admin.ModelAdmin):
    list_display = ("name",)


class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_date", "modified_date", "send_emails", "is_bot", "topic_id")


class DevelopmentsAdmin(SimpleHistoryAdmin):
    list_display = ("OBJECTID", "plan_type", "updated_date", "submitted_yr", "status", "major_street", "cac", "cac_override",
                    "plan_name", "plan_number", "modified_date", "created_date")
    history_list_display = ["status"]
    list_filter = (CACStatusFilter,)

    def updated_date(self, obj):
        if obj.updated:
            return datetime.datetime.fromtimestamp(obj.updated / 1000).strftime('%Y-%m-%d %H:%M:%S')
        else:
            return "NA"

    updated_date.short_description = 'Date Updated'
    updated_date.admin_order_field = 'updated'


class SiteReviewCasesAdmin(SimpleHistoryAdmin):
    list_display = ("case_number", "project_name", "cac", "cac_override", "status", "contact", "modified_date",
                    "created_date")
    history_list_display = ["status"]


class ZoningAdmin(SimpleHistoryAdmin):
    list_display = ("zpyear", "zpnum", "submitted_date", "location", "remarks", "cac", "cac_override", "modified_date",
                    "created_date")
    # history_list_display = ["status"]

    def submitted_date(self, obj):
        if obj.submittal_date:
            return datetime.datetime.fromtimestamp(obj.submittal_date / 1000).strftime('%Y-%m-%d %H:%M:%S')
        else:
            return "NA"

    submitted_date.short_description = 'Date Submitted'
    # submitted_date.admin_order_field = 'updated'


class AADAdmin(SimpleHistoryAdmin):
    list_display = ("case_number", "project_name", "cac", "cac_override", "status", "contact", "modified_date",
                    "created_date")
    history_list_display = ["status"]


class TCAdmin(SimpleHistoryAdmin):
    list_display= ("case_number", "project_name", "status", "contact", "modified_date", "created_date")
    history_list_display = ["status"]


admin.site.register(Control, ControlAdmin)
admin.site.register(CitizenAdvisoryCouncil, CitizenAdvisoryCouncilAdmin)
admin.site.register(coverArea, coverAreaAdmin)
admin.site.register(SiteReviewCases, SiteReviewCasesAdmin)
admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(Development, DevelopmentsAdmin)
admin.site.register(Zoning, ZoningAdmin)
admin.site.register(AdministrativeAlternates, AADAdmin)
admin.site.register(TextChangeCases, TCAdmin)
admin.site.register(WakeCorporate, admin.GeoModelAdmin)
