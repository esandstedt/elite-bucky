import math


class Star:
    def __init__(self, id, name, x, y, z, distance_to_neutron, distance_to_scoopable):
        self.id = id
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.distance_to_neutron = distance_to_neutron
        self.distance_to_scoopable = distance_to_scoopable

    def dist(self, other):
        return math.sqrt(self.dist_squared(other))

    def dist_squared(self, other):
        return (self.x-other.x)**2 + (self.y-other.y)**2 + (self.z-other.z)**2

    def __lt__(self, other):
        return self.id < other.id
