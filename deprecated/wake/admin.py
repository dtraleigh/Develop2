from django.contrib.gis import admin
from .models import WakeCorporate

admin.site.register(WakeCorporate, admin.GeoModelAdmin)
