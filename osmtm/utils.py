import os
import ConfigParser
from shapely.geometry import Polygon, MultiPolygon
from shapely.prepared import prep
from math import floor, ceil


# Maximum resolution
MAXRESOLUTION = 156543.0339

# X/Y axis limit
max = MAXRESOLUTION * 256 / 2


class TileBuilder(object):

    def __init__(self, parameter):
        self.a = parameter

    def create_square(self, i, j):
        xmin = i * self.a - max
        ymin = j * self.a - max
        xmax = (i + 1) * self.a - max
        ymax = (j + 1) * self.a - max
        return MultiPolygon([Polygon([(xmin, ymin), (xmax, ymin),
                                      (xmax, ymax), (xmin, ymax)])])


# This method finds the tiles that intersect the given geometry for the given
# zoom
def get_tiles_in_geom(geom, z):
    xmin = geom.bounds[0]
    ymin = geom.bounds[1]
    xmax = geom.bounds[2]
    ymax = geom.bounds[3]

    # tile size (in meters) at the required zoom level
    step = max / (2 ** (z - 1))

    xminstep = int(floor((xmin + max) / step))
    xmaxstep = int(ceil((xmax + max) / step))
    yminstep = int(floor((ymin + max) / step))
    ymaxstep = int(ceil((ymax + max) / step))

    tb = TileBuilder(step)
    tiles = []
    prepared_geom = prep(geom)
    for i in range(xminstep, xmaxstep + 1):
        for j in range(yminstep, ymaxstep + 1):
            tile = tb.create_square(i, j)
            if prepared_geom.intersects(tile):
                tiles.append((i, j, tile))
    return tiles


def load_local_settings(settings):
    local_settings_path = os.environ.get('LOCAL_SETTINGS_PATH',
                                         settings['local_settings_path'])
    if os.path.exists(local_settings_path):
        config = ConfigParser.ConfigParser()
        config.read(local_settings_path)
        settings.update(config.items('app:main'))
