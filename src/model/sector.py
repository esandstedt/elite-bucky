from scipy.spatial import KDTree
from model.star import Star

QUERY = """
SELECT `id`, `name`, `x`, `y`, `z`, `distanceToNeutron`, `distanceToScoopable`
FROM `system` 
WHERE `sectorX`=%s
  AND `sectorY`=%s
  AND `sectorZ`=%s
  AND (
       (`distanceToNeutron` IS NOT NULL AND `distanceToNeutron` < 500)
    OR (`distanceToScoopable` IS NOT NULL AND `distanceToScoopable` < 500)
  )
"""


class Sector:
    def __init__(self, db, x, y, z):

        cursor = db.cursor()
        cursor.execute(
            QUERY,
            (x, y, z)
        )

        self._list = [Star(*row) for row in cursor.fetchall()]
        self._tree_array = [[star.x, star.y, star.z] for star in self._list]
        if len(self._tree_array) != 0:
            self._tree = KDTree(self._tree_array)
        else:
            self._tree = None

        print("Sector: [%3d:%3d:%3d] %d" % (x, y, z, len(self._list),))

    def get_neighbors(self, star, dist):
        if self._tree is None:
            return []
        else:
            indexes = self._tree.query_ball_point(
                [star.x, star.y, star.z], dist)
            return [self._list[i] for i in indexes]
