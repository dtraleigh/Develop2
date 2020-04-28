from django.contrib.gis import admin
from .models import CitizenAdvisoryCouncil

admin.site.register(CitizenAdvisoryCouncil, admin.GeoModelAdmin)
