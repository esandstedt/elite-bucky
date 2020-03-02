import heapq
import math
import mysql.connector
import time
from collections import defaultdict
from model.star import Star
from model.galaxy import Galaxy
from model.ship import Ship


ship = Ship("DSV Phoenix", 578, 4, 64, "6A", 8, 2902, 10.5, 1.245)


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

    def __lt__(self, other):
        return self.star.id < other.star.id


class CameFromContext:
    def __init__(self, star, refuel):
        self.star = star
        self.refuel = refuel


def reconstruct_path(came_from, star):
    path = [star.name]
    id = star.id
    while id in came_from:
        ctx = came_from[id]
        star = ctx.star
        refuel = ctx.refuel

        types = []
        if star.distance_to_neutron is not None:
            types.append("NS")
        if refuel:
            types.append("SC")

        path.insert(0, "%s [%.2f,%.2f,%.2f;%s]" %
                    (star.name, star.x, star.y, star.z, ",".join(types)))

        id = ctx.star.id
    return path


def handle_neighbors(came_from, g, f, h, open_queue, ctx, neighbors, refuel):
    current = ctx.star
    fuel = ctx.fuel if not refuel else ship.fuel_capacity
    jump_range = ship.get_max_jump_range(fuel)

    if jump_range == 0:
        return

    if current.distance_to_neutron is not None:
        jump_range = 4*jump_range

    for neighbor in neighbors:
        dist = current.dist(neighbor)

        remaining_jump_range = ship.get_max_jump_range()
        remaining_dist = max(0, dist - jump_range)
        num_of_jumps = 1 + math.ceil(remaining_dist / remaining_jump_range)

        refuel_penalty = 0
        if refuel or num_of_jumps > 1:
            refuel_penalty = 1.5

        g_score = g[current.id] + num_of_jumps + refuel_penalty

        if g_score < g[neighbor.id]:
            came_from[neighbor.id] = CameFromContext(current, refuel)
            g[neighbor.id] = g_score
            f_score = g_score + h(neighbor)
            f[neighbor.id] = f_score

            new_fuel = 0
            if num_of_jumps > 1:
                new_fuel = ship.fuel_capacity - ship.max_fuel_per_jump
            else:
                fuel_cost = 0
                if current.distance_to_neutron is not None:
                    fuel_cost = ship.get_fuel_cost(fuel, dist / 4)
                else:
                    fuel_cost = ship.get_fuel_cost(fuel, dist)

                new_fuel = fuel - fuel_cost

            open_queue.add(OpenContext(neighbor, new_fuel), f_score)


def run(db):
    time_start = time.time()

    galaxy = Galaxy(db)
    base_jump_range = ship.get_max_jump_range()

    star_colonia = Star(1, "Colonia", -9530, -910, 19808)
    star_hillary_depot = Star(7, "Blu Thua AI-A c14-10", -54, 149, 2099)
    star_omega_mining = Star(2, "Omega Sector VE-Q b5-15",
                             -1444, -85, 5319)
    star_rohini = Star(3, "Rohini", -3374, -47, 6912)
    star_sacaqawea = Star(4, "Skaudai CH-B d14-34", -5481, -579, 10429)
    star_sagittarius = Star(5, "Sagittarius A*", 25, -20, 25899)
    star_sol = Star(6, "Sol", 0, 0, 0)

    start = star_omega_mining
    goal = star_rohini

    lowest_dist_to_goal = start.dist(goal)

    def h(star): return star.dist(goal)/(4*base_jump_range)

    # came_from[n] is the node immediately preceding it on the cheapest path currently known
    came_from = {}

    # g[n] is the cost of the cheapest path from start to n currently known
    g = defaultdict(lambda: 1000000)
    g[start.id] = 0

    # f[n] is g[n]+h(n)
    f = defaultdict(lambda: 1000000)
    f[start.id] = h(start)

    open_queue = OpenQueue()
    open_queue.add(OpenContext(start, ship.fuel_capacity), f[start.id])

    while open_queue.any():
        [f_score, ctx] = open_queue.pop()
        current = ctx.star

        # a better route has been found already
        if f[current.id] < f_score:
            continue

        dist = current.dist(goal)
        lowest_dist_to_goal = min(lowest_dist_to_goal, dist)
        print("%7d %6.3f %5d %5d   %s" %
              (len(open_queue), f[current.id], lowest_dist_to_goal, dist, current.name))

        if current.id == goal.id:
            print()
            for line in reconstruct_path(came_from, current):
                print(line)
            break

        # direct route to goal
        handle_neighbors(
            came_from, g, f, h, open_queue, ctx, [goal], False
        )

        neighbors = galaxy.get_neighbors(current, 500)

        # neighbors without refueling
        handle_neighbors(
            came_from, g, f, h, open_queue, ctx, neighbors, False
        )

        # neighbors with refueling
        if current.distance_to_scoopable is not None:
            handle_neighbors(
                came_from, g, f, h, open_queue, ctx, neighbors, True
            )

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
