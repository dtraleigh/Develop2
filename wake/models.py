# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models


class WakeCorporate(models.Model):
    objectid = models.IntegerField()
    short_name = models.CharField(max_length=3)
    long_name = models.CharField(max_length=13)
    ordinance_field = models.CharField(max_length=18)
    effective_field = models.CharField(max_length=24)
    shapearea = models.FloatField()
    shapelen = models.FloatField()
    geom = models.MultiPolygonField(srid=4326)

    def __str__(self):
        return self.long_name


# Auto-generated `LayerMapping` dictionary for WakeCorporate model
wakecorporate_mapping = {
    'objectid': 'OBJECTID',
    'short_name': 'SHORT_NAME',
    'long_name': 'LONG_NAME',
    'ordinance_field': 'ORDINANCE_',
    'effective_field': 'EFFECTIVE_',
    'shapearea': 'SHAPEAREA',
    'shapelen': 'SHAPELEN',
    'geom': 'MULTIPOLYGON',
}
