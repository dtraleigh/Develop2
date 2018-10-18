from django.db import models

from simple_history.models import HistoricalRecords


class Control(models.Model):
    scrape = models.BooleanField(default=True)
    scan = models.BooleanField(default=True)
    notify = models.BooleanField(default=True)


class CAC(models.Model):
    name = models.CharField(blank=True, max_length=300, null=True, verbose_name="Name")

    class Meta:
        verbose_name = "Citizen Advisory Council"

    def __str__(self):
        return u"%s" % self.name


class coverArea(models.Model):
    name = models.CharField(blank=True, max_length=300, null=True, verbose_name="Name")
    CACs = models.ManyToManyField(CAC)

    class Meta:
        verbose_name = "Cover Area"

    def __str__(self):
        return u"%s" % self.name


class Subscriber(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date Subscribed")
    name = models.CharField(max_length=254)
    email = models.EmailField(unique=True)
    send_emails = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    cover_areas = models.ManyToManyField(coverArea)

    def __str__(self):
        return u"%s (%s)" % (self.name, self.email)


class Development(models.Model):
    # Development is an item produced by the Development API
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
    plan_name = models.CharField(blank=True, max_length=300, null=True, verbose_name="Plan Name")
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
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Development"

    def __str__(self):
        return u"%s - %s (%s)" % (self.plan_name, self.devplan_id, self.submitted_yr)


class SiteReviewCases(models.Model):
    # A Site Review Case is an item on the Development Activity page - Site Review Cases (SR) section
    case_number = models.CharField(blank=True, max_length=100, null=True, verbose_name="Case Number")
    case_url = models.TextField(blank=True, null=True, verbose_name="Plan URL")
    project_name = models.CharField(blank=True, max_length=300, null=True, verbose_name="Plan Name")
    cac = models.CharField(blank=True, max_length=100, null=True, verbose_name="CAC")
    status = models.CharField(blank=True, max_length=100, null=True, verbose_name="Status")
    contact = models.CharField(blank=True, max_length=100, null=True, verbose_name="Contact")
    contact_url = models.CharField(blank=True, max_length=300, null=True, verbose_name="Contact URL")
    history = HistoricalRecords()
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Review Case"

    def __str__(self):
        return u"%s - %s (%s)" % (self.case_number, self.project_name, self.cac)


class Zoning(models.Model):
    # Zoning is an item produced by the Zoning API
    OBJECTID = models.IntegerField(blank=True, null=True, verbose_name="Object ID")
    zpyear = models.SmallIntegerField(blank=True, null=True, verbose_name="Year Submitted")
    zpnum = models.SmallIntegerField(blank=True, null=True, verbose_name="Zoning Number")
    submittal_date = models.BigIntegerField(blank=True, null=True, verbose_name="Submitted")
    petitioner = models.CharField(blank=True, max_length=300, null=True, verbose_name="Petitioner")
    location = models.CharField(blank=True, max_length=300, null=True, verbose_name="Location")
    remarks = models.CharField(blank=True, max_length=300, null=True, verbose_name="Remarks") # API field
    zp_petition_acres = models.CharField(blank=True, max_length=100, null=True, verbose_name="Acreage") # Need to convert from decimal to char
    planning_commission_action = models.CharField(blank=True, max_length=300, null=True, verbose_name="PC Action")
    city_council_action = models.CharField(blank=True, max_length=300, null=True, verbose_name="CC Action")
    ph_date = models.BigIntegerField(blank=True, null=True, verbose_name="PH Date")
    withdraw_date = models.BigIntegerField(blank=True, null=True, verbose_name="Withdraw Date")
    exp_date_120_days = models.BigIntegerField(blank=True, null=True, verbose_name="Exp Date 120 Days")
    exp_date_2_year = models.BigIntegerField(blank=True, null=True, verbose_name="Exp Date 2 Year")
    ordinance_number = models.CharField(blank=True, max_length=300, null=True, verbose_name="Ordinance Number")
    received_by = models.CharField(blank=True, max_length=300, null=True, verbose_name="Received By")
    last_revised = models.CharField(blank=True, max_length=300, null=True, verbose_name="Last Revised")
    drain_basin = models.CharField(blank=True, max_length=300, null=True, verbose_name="Drain Basin")
    cac = models.CharField(blank=True, max_length=300, null=True, verbose_name="CAC")
    comprehensive_plan_districts = models.CharField(blank=True, max_length=300, null=True, verbose_name="Comprehensive Plan Districts")
    GlobalID = models.CharField(blank=True, max_length=300, null=True, verbose_name="Global ID")
    CreationDate = models.BigIntegerField(blank=True, null=True, verbose_name="Creation Date")
    EditDate = models.BigIntegerField(blank=True, null=True, verbose_name="Edit Date")
    history = HistoricalRecords()
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    status = models.CharField(blank=True, max_length=300, null=True, verbose_name="Status") # Web scrape field
    plan_url = models.TextField(blank=True, null=True, verbose_name="Plan URL")

    class Meta:
        verbose_name = "Zoning Request"

    def __str__(self):
        return u"%s (%s)" % (self.zpnum, self.zpyear)


