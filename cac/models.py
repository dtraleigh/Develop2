# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models


class CitizenAdvisoryCouncil(models.Model):
    objectid = models.IntegerField()
    cac = models.CharField(max_length=17)
    name = models.CharField(max_length=17)
    cac_code = models.CharField(max_length=1)
    shape_leng = models.FloatField()
    shape_area = models.FloatField()
    geom = models.MultiPolygonField(srid=4326)

    def __str__(self):
        return self.name


# Auto-generated `LayerMapping` dictionary for CitizenAdvisoryCouncil model
citizenadvisorycouncil_mapping = {
    'objectid': 'OBJECTID',
    'cac': 'CAC',
    'name': 'NAME',
    'cac_code': 'CAC_CODE',
    'shape_leng': 'SHAPE_Leng',
    'shape_area': 'SHAPE_Area',
    'geom': 'MULTIPOLYGON',
}
