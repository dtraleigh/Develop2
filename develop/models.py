from django.db import models

from simple_history.models import HistoricalRecords


class Subscriber(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date Subscribed")
    name = models.CharField(max_length=254)
    email = models.EmailField(unique=True)
    send_emails = models.BooleanField(default=True)

    def __str__(self):
        return u"%s (%s)" % (self.name, self.email)


class Development(models.Model):
    OBJECTID = models.IntegerField(verbose_name="Object ID")
    devplan_id = models.IntegerField(verbose_name="Development Plan ID")
    submitted = models.BigIntegerField(blank=True, null=True, verbose_name="Submitted")
    submitted_yr = models.SmallIntegerField(blank=True, null=True, verbose_name="Year Submitted")
    approved = models.BigIntegerField(blank=True, null=True, verbose_name="Approved")
    daystoapprove = models.IntegerField(blank=True, null=True, verbose_name="Days to Approve")
    plan_type = models.CharField(blank=True, max_length=100, null=True, verbose_name="Plan Type")
    status = models.CharField(blank=True, max_length=100, null=True, verbose_name="Status")
    appealperiodends = models.BigIntegerField(blank=True, null=True, verbose_name="Appeal Period Ends")
    updated = models.BigIntegerField(blank=True, null=True, verbose_name="Updated")
    sunset_date = models.BigIntegerField(blank=True, null=True, verbose_name="Sunset Date")
    acreage = models.CharField(blank=True, max_length=100, null=True, verbose_name="Acreage") #Need to convert from decimal to char
    major_street = models.CharField(blank=True, max_length=100, null=True, verbose_name="Major Street")
    cac = models.CharField(blank=True, max_length=100, null=True, verbose_name="CAC")
    engineer = models.CharField(blank=True, max_length=100, null=True, verbose_name="Engineer")
    engineer_phone = models.CharField(blank=True, max_length=100, null=True, verbose_name="Engineer Phone")
    developer = models.CharField(blank=True, max_length=100, null=True, verbose_name="Developer")
    developer_phone = models.CharField(blank=True, max_length=100, null=True, verbose_name="Developer Phone")
    plan_name = models.CharField(blank=True, max_length=100, null=True, verbose_name="Plan Name")
    planurl = models.TextField(blank=True, null=True, verbose_name="Plan URL")
    planurl_approved = models.TextField(blank=True, null=True, verbose_name="Plan URL Approved")
    planner = models.CharField(blank=True, max_length=100, null=True, verbose_name="Planner")
    lots_req = models.IntegerField(blank=True, null=True, verbose_name="Lots Req")
    lots_rec = models.IntegerField(blank=True, null=True, verbose_name="Lots Rec")
    lots_apprv = models.IntegerField(blank=True, null=True, verbose_name="Lots Approved")
    sq_ft_req = models.IntegerField(blank=True, null=True, verbose_name="Square Feet Req")
    units_apprv = models.IntegerField(blank=True, null=True, verbose_name="Units Approved")
    units_req = models.IntegerField(blank=True, null=True, verbose_name="Units Req")
    zoning = models.CharField(blank=True, max_length=100, null=True, verbose_name="Zoning")
    plan_number = models.CharField(blank=True, max_length=100, null=True, verbose_name="Plan Number")
    CreationDate = models.BigIntegerField(blank=True, null=True, verbose_name="Creation Date")
    Creator = models.CharField(blank=True, max_length=100, null=True, verbose_name="Creator")
    EditDate = models.BigIntegerField(blank=True, null=True, verbose_name="Edit Date")
    Editor = models.CharField(blank=True, max_length=100, null=True, verbose_name="Editor")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Development"

    def __str__(self):
        return u"%s - %s (%s)" % (self.plan_name, self.devplan_id, self.submitted_yr)
