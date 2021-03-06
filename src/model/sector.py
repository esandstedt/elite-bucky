import itertools
from scipy.spatial import KDTree
from model.star import Star

# QUERY = """
# SELECT `id`, `name`, `x`, `y`, `z`, `distanceToNeutron`, `distanceToScoopable`
# FROM `system`
# WHERE `sectorX`=%s
#   AND `sectorY`=%s
#   AND `sectorZ`=%s
#   AND (
#        (`distanceToNeutron` IS NOT NULL AND `distanceToNeutron` < 500)
#     OR (`distanceToScoopable` IS NOT NULL AND `distanceToScoopable` < 500)
#   )
# """

QUERY = """
SELECT `id`, `name`, `x`, `y`, `z`, `distanceToNeutron`, `distanceToScoopable`
FROM `system` 
WHERE `sectorX`=%s
  AND `sectorY`=%s
  AND `sectorZ`=%s
  AND `distanceToNeutron` IS NOT NULL AND `distanceToNeutron` < 500
"""


class Tree:
    def __init__(self, stars):
        self._list = stars
        self._tree_array = [[star.x, star.y, star.z] for star in self._list]
        if len(self._tree_array) != 0:
            self._tree = KDTree(self._tree_array)
        else:
            self._tree = None

    def get_neighbors(self, star, dist):
        if self._tree is None:
            return []
        else:
            indexes = self._tree.query_ball_point(
                [star.x, star.y, star.z], dist)
            return [self._list[i] for i in indexes if self._list[i] is not star]

    def __len__(self):
        return len(self._list)


class Sector:
    def __init__(self, db, x, y, z):
        cursor = db.cursor()
        cursor.execute(
            QUERY,
            (x, y, z)
        )
        all_stars = [Star(*row) for row in cursor.fetchall()]
        # all_tree = Tree(all_stars)

        neutron_stars = [
            star for star in all_stars if star.distance_to_neutron is not None
        ]
        # neutron_star_scoopable_neighbors = list(
        #     filter(
        #         lambda star: star.distance_to_scoopable is not None,
        #         itertools.chain.from_iterable(
        #             [all_tree.get_neighbors(star, 15) for star in neutron_stars])
        #     )
        # )

        # stars = list(set(neutron_stars + neutron_star_scoopable_neighbors))
        stars = neutron_stars
        self._tree = Tree(stars)

        # print("Sector: [%3d:%3d:%3d] %d" % (x, y, z, len(self._tree),))

    def get_neighbors(self, star, dist):
        return self._tree.get_neighbors(star, dist)
