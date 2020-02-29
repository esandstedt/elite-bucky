import heapq
import math
import mysql.connector
import time
from collections import defaultdict
from model.star import Star
from model.galaxy import Galaxy
from model.ship import Ship


ship = Ship("DSV Phoenix", 578, 4, 64, "6A", 8, 2902, 10.5)


class OpenQueue:
    def __init__(self):
        self._heap = []

    def add(self, ctx, weight):
        heapq.heappush(self._heap, [weight, ctx])

    def any(self):
        return len(self._heap) != 0

    def pop(self):
        return heapq.heappop(self._heap)

    def __len__(self):
        return len(self._heap)


class OpenContext:
    def __init__(self, star, fuel):
        self.star = star
        self.fuel = fuel


def run(db):
    time_start = time.time()

    galaxy = Galaxy(db)
    base_jump_range = ship.get_max_jump_range()
    print(base_jump_range)

    start = Star(-1, "Sol", 0, 0, 0, None, None)

    # Omega Mining Operation
    goal = Star(-1, "Omega Sector VE-Q b5-15", -
                1444.3125, -85.8125, 5319.9375, None, None)
    #goal = Star(-1, "Colonia", -9530.5, -910.28125, 19808.125, None, None)

    lowest_dist_to_goal = start.dist(goal)

    def h(star): return star.dist(goal)/(4*base_jump_range)

    # came_from[n] is the node immediately preceding it on the cheapest path currently known
    came_from = {}

    def reconstruct_path(star):
        path = [star.name, goal.name]
        id = star.id
        while id in came_from:
            star = came_from[id]
            path.insert(0, star.name)
            id = star.id
        return path

    # g[n] is the cost of the cheapest path from start to n currently known
    g = defaultdict(lambda: 1000000)
    g[start.id] = 0

    # f[n] is g[n]+h(n)
    f = defaultdict(lambda: 1000000)
    f[start.id] = h(start)

    open_queue = OpenQueue()
    open_queue.add(OpenContext(start, -1), f[start.id])

    while open_queue.any():
        [f_score, ctx] = open_queue.pop()
        current = ctx.star

        # a better route has been found already
        if f[current.id] < f_score:
            continue

        dist = current.dist(goal)
        lowest_dist_to_goal = min(lowest_dist_to_goal, dist)
        print("%7d %4.3f %5d %5d" %
              (len(open_queue), f[current.id], lowest_dist_to_goal, dist))

        jump_range = base_jump_range
        if current.distance_to_neutron is not None:
            jump_range = 4 * base_jump_range

        if dist < 500:
            print()
            for line in reconstruct_path(current):
                print(line)
            break

        neighbors = galaxy.get_neighbors(current, 500)
        for neighbor in neighbors:

            dist = current.dist(neighbor)
            g_score = g[current.id]

            if current.distance_to_neutron is not None:
                g_score += max(1, math.ceil(dist / base_jump_range) - 3)
            else:
                g_score += math.ceil(dist / base_jump_range)

            if g_score < g[neighbor.id]:
                came_from[neighbor.id] = current
                g[neighbor.id] = g_score
                f[neighbor.id] = g_score + h(neighbor)
                open_queue.add(OpenContext(neighbor, -1), f[neighbor.id])

    time_end = time.time()

    print()
    print("time: " + str(time_end - time_start))


if __name__ == "__main__":
    db = mysql.connector.connect(
        host="localhost",
        user="elite",
        passwd="elite",
        database="elite"
    )
    run(db)
