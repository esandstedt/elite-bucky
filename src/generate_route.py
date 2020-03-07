import heapq
import math
import mysql.connector
import time
from collections import defaultdict
from model.star import Star
from model.galaxy import Galaxy
from model.ship import Ship


#ship = Ship("DSV Phoenix (Exploration)", 578, 4, 64, "6A", 8, 2902, 10.5)
ship = Ship("DSV Phoenix (Bucky)", 479, 0, 64, "6A", 8, 2902, 10.5)


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


class Context:
    def __init__(self, star, refuel, fuel):
        self.id = (star.id, refuel)
        self.star = star
        self.refuel = refuel
        self.fuel = fuel

    def __lt__(self, other):
        return self.id < other.id


def reconstruct_path(came_from, ctx):
    path = [ctx.star.name]
    id = ctx.id
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

        id = ctx.id
    return path


def handle_neighbor(came_from, g, f, h, open_queue, current_ctx, neighbor, refuel):
    star = current_ctx.star
    fuel = current_ctx.fuel

    jump_range = ship.get_max_jump_range(fuel)
    if star.distance_to_neutron is not None:
        jump_range = 4*jump_range

    if jump_range == 0:
        return

    dist = star.dist(neighbor)

    remaining_jump_range = ship.get_max_jump_range()
    remaining_dist = max(0, dist - jump_range)
    num_of_jumps = 1 + math.ceil(remaining_dist / remaining_jump_range)

    refuel_penalty = 0
    if refuel or num_of_jumps > 1:
        refuel_penalty = 0.5

    neighbor_ctx = Context(neighbor, refuel, fuel)

    if refuel:
        neighbor_ctx.fuel = ship.fuel_capacity
    elif num_of_jumps > 1:
        neighbor_ctx.fuel = ship.fuel_capacity - ship.max_fuel_per_jump
    else:
        fuel_cost = 0
        if star.distance_to_neutron is not None:
            fuel_cost = ship.get_fuel_cost(fuel, dist / 4)
        else:
            fuel_cost = ship.get_fuel_cost(fuel, dist)
        neighbor_ctx.fuel -= fuel_cost

    g_score = g[current_ctx.id] + num_of_jumps + refuel_penalty

    if g_score < g[neighbor_ctx.id]:

        came_from[neighbor_ctx.id] = current_ctx
        g[neighbor_ctx.id] = g_score
        f_score = g_score + h(neighbor_ctx)
        f[neighbor_ctx.id] = f_score

        open_queue.add(neighbor_ctx, f_score)


def run(db):
    time_start = time.time()

    galaxy = Galaxy(db)
    base_jump_range = ship.get_max_jump_range()

    star_colonia = Star(1, "Colonia", -9530, -910, 19808)
    star_hillary_depot = Star(2, "Blu Thua AI-A c14-10", -54, 149, 2099)
    star_omega_mining = Star(3, "Omega Sector VE-Q b5-15",
                             -1444, -85, 5319)
    star_rohini = Star(4, "Rohini", -3374, -47, 6912)
    star_sacaqawea = Star(5, "Skaudai CH-B d14-34", -5481, -579, 10429)
    star_sagittarius = Star(6, "Sagittarius A*", 25, -20, 25899)
    star_sol = Star(7, "Sol", 0, 0, 0)

    start = star_sol
    goal = star_sagittarius

    lowest_dist_to_goal = start.dist(goal)

    def h(ctx): return ctx.star.dist(goal)/(4*base_jump_range)

    # came_from[n] is the node immediately preceding it on the cheapest path currently known
    came_from = {}

    start_ctx = Context(start, False, ship.fuel_capacity)

    # g[n] is the cost of the cheapest path from start to n currently known
    g = defaultdict(lambda: 1000000)
    g[start_ctx.id] = 0

    # f[n] is g[n]+h(n)
    f = defaultdict(lambda: 1000000)
    f[start_ctx.id] = h(start_ctx)

    open_queue = OpenQueue()
    open_queue.add(start_ctx, f[start_ctx.id])

    i = 0

    while open_queue.any():
        i += 1

        [f_score, ctx] = open_queue.pop()
        star = ctx.star

        # a better route has been found already
        if f[ctx.id] < f_score:
            continue

        dist = star.dist(goal)
        lowest_dist_to_goal = min(lowest_dist_to_goal, dist)
        print("%8d %8d %.3f %5d %5d   %s" %
              (i, len(open_queue), f[ctx.id], lowest_dist_to_goal, dist, star.name))

        if star.id == goal.id:
            print()
            for line in reconstruct_path(came_from, ctx):
                print(line)
            break

        # direct route to goal
        handle_neighbor(
            came_from, g, f, h, open_queue, ctx, goal, False
        )

        neighbors = galaxy.get_neighbors(star, 500)
        for neighbor in neighbors:
            handle_neighbor(
                came_from, g, f, h, open_queue, ctx, neighbor, False
            )
            if neighbor.distance_to_scoopable is not None:
                handle_neighbor(
                    came_from, g, f, h, open_queue, ctx, neighbor, True
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
