import os
from django.contrib.gis.utils import LayerMapping
from develop.models import CitizenAdvisoryCouncil

citizenadvisorycouncil_mapping = {
    'objectid': 'OBJECTID',
    'cac': 'CAC',
    'name': 'NAME',
    'cac_code': 'CAC_CODE',
    'shape_leng': 'SHAPE_Leng',
    'shape_area': 'SHAPE_Area',
    'geom': 'MULTIPOLYGON',
}

cac_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'Citizen_Advisory_Council', 'Citizen_Advisory_Council.shp'),
)


def run(verbose=True):
    lm = LayerMapping(CitizenAdvisoryCouncil, cac_shp, citizenadvisorycouncil_mapping, transform=False)
    lm.save(strict=True, verbose=verbose)
