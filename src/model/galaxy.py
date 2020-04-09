import itertools
import math
from model.sector import Sector
from model.star import Star


QUERY = """
SELECT `id`, `name`, `x`, `y`, `z`, `distanceToNeutron`, `distanceToScoopable`
FROM `system` 
WHERE `name`=%s
"""


class Galaxy:
    def __init__(self, db):
        self._db = db
        self._sectors = {}

    def get_by_name(self, name):
        cursor = self._db.cursor()
        cursor.execute(
            QUERY,
            (name,)
        )
        return [Star(*row) for row in cursor.fetchall()][0]

    def get_neighbors(self, star, dist):
        sectors = self._get_sectors(star, dist)
        neighbors = [sector.get_neighbors(star, dist) for sector in sectors]
        return list(itertools.chain.from_iterable(neighbors))

    def _get_sectors(self, star, dist):
        def c(v): return math.floor(v/1000)

        points = list(itertools.product(
            range(c(star.x-dist), c(star.x+dist)+1),
            range(c(star.y-dist), c(star.y+dist)+1),
            range(c(star.z-dist), c(star.z+dist)+1)
        ))

        sectors = []
        for point in points:
            if point not in self._sectors:
                self._sectors[point] = Sector(self._db, *point)
            sectors.append(self._sectors[point])

        return sectors
