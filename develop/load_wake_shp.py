import os
from django.contrib.gis.utils import LayerMapping
from develop.models import WakeCorporate

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

wake_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'Corporate_Limits', 'Corporate_Limits.shp'),
)


def run(verbose=True):
    lm = LayerMapping(WakeCorporate, wake_shp, wakecorporate_mapping, transform=False)
    lm.save(strict=True, verbose=verbose)
