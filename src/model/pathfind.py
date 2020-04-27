import datetime
import heapq
import math
import time
from collections import defaultdict


class Open:
    def __init__(self):
        self._heap = []

    def add(self, node, weight):
        heapq.heappush(self._heap, [weight, node])

    def any(self):
        return len(self._heap) != 0

    def pop(self):
        return heapq.heappop(self._heap)

    def __len__(self):
        return len(self._heap)


class Node:
    def __init__(self, ship, star, refuel, fuel):
        fuel_avg = (fuel.min + fuel.max)/2
        self.id = "%s %d" % (
            star.id,
            int(fuel_avg/(ship.max_fuel_per_jump))
        )
        self.star = star
        self.refuel = refuel
        self.fuel = fuel

    def __lt__(self, other):
        return self.id < other.id


class FuelRange:
    def __init__(self, min, max):
        self.min = min
        self.max = max


TIME_PER_JUMP = 50


class Pathfind:
    def __init__(self, ship, galaxy, start, goal):
        self.ship = ship
        self.galaxy = galaxy
        self.start = start
        self.goal = goal

        self.came_from = {}
        self.g = defaultdict(lambda: 1000000)
        self.f = defaultdict(lambda: 1000000)
        self.open = Open()

    def h(self, node):
        # neutron boosted with no fuel remaining
        max_jump_range = 4 * \
            self.ship.get_max_jump_range(self.ship.max_fuel_per_jump)
        return TIME_PER_JUMP * node.star.dist(self.goal) / max_jump_range

    def handle_neighbor(self, current, neighbor, refuel):
        result_min = self.handle_neighbor_with_exact_fuel(
            current,
            neighbor,
            current.fuel.min,
            refuel.min if refuel is not None else None
        )

        if result_min is None:
            return

        result_max = self.handle_neighbor_with_exact_fuel(
            current,
            neighbor,
            current.fuel.max,
            refuel.max if refuel is not None else None
        )

        if result_max is None:
            return

        (neighbor_fuel_min, num_of_jumps_min, g_score_min) = result_min
        (neighbor_fuel_max, num_of_jumps_max, g_score_max) = result_max

        if num_of_jumps_min != num_of_jumps_max:
            return

        neighbor_node = Node(
            self.ship,
            neighbor,
            refuel,
            FuelRange(
                neighbor_fuel_min,
                neighbor_fuel_max
            )
        )

        g_score = max(g_score_min, g_score_max)
        if g_score < self.g[neighbor_node.id]:

            self.came_from[neighbor_node.id] = current
            self.g[neighbor_node.id] = g_score
            f_score = g_score + self.h(neighbor_node)
            self.f[neighbor_node.id] = f_score

            self.open.add(neighbor_node, f_score)

    def handle_neighbor_with_exact_fuel(self, current, neighbor, fuel, refuel):
        star = current.star

        jump_range = self.ship.get_max_jump_range(fuel)
        neutron_penalty = 0
        if star.distance_to_neutron is not None:
            jump_range = 4*jump_range
            # time to travel to neutron star
            neutron_penalty = self.get_travel_time(
                star.distance_to_neutron)

        if jump_range == 0:
            return

        dist = star.dist(neighbor)

        remaining_jump_range = self.ship.get_max_jump_range()
        remaining_dist = max(0, dist - jump_range)
        num_of_jumps = 1 + math.ceil(remaining_dist / remaining_jump_range)

        fuel_cost = 0
        if star.distance_to_neutron is not None:
            fuel_cost = self.ship.get_fuel_cost(
                fuel, min(jump_range / 4, dist / 4))
        else:
            fuel_cost = self.ship.get_fuel_cost(fuel, min(jump_range, dist))

        neighbor_fuel = fuel - fuel_cost

        # not a valid neighbor because too low fuel
        if neighbor_fuel < self.ship.minimum_fuel:
            return None

        refuel_penalty = 0
        if num_of_jumps > 1:
            # fill back to full tank
            delta = self.ship.fuel_capacity - (neighbor_fuel)
            t_fst = (delta / self.ship.fuel_scoop_rate) + 20
            # refill after each jump
            t_rst = (num_of_jumps - 1) * \
                ((self.ship.max_fuel_per_jump / self.ship.fuel_scoop_rate) + 20)

            neighbor_fuel = fuel - self.ship.max_fuel_per_jump
            refuel_penalty = t_fst + t_rst

        if refuel is not None:

            # can't refuel below the current level
            if refuel < neighbor_fuel:
                return None

            # time to travel to scoopable star
            t_travel = self.get_travel_time(neighbor.distance_to_scoopable)
            # time to refuel
            delta = refuel - neighbor_fuel
            t_refuel = (delta / self.ship.fuel_scoop_rate) + 20

            neighbor_fuel = refuel
            refuel_penalty = t_travel + t_refuel

        g_score = self.g[current.id] + \
            (TIME_PER_JUMP * num_of_jumps) + refuel_penalty + neutron_penalty

        return (neighbor_fuel, num_of_jumps, g_score)

    def get_travel_time(self, distance):
        if distance < 1:
            return 0
        return 12 * math.log(distance)

    def reconstruct_path(self, node):
        path = [node]
        id = node.id
        while id in self.came_from:
            node = self.came_from[id]
            path.append(node)
            id = node.id
        return reversed(path)

    def run(self):
        for level in self.ship.refuel_levels:
            node = Node(
                self.ship,
                self.start,
                level,
                level
            )
            self.g[node.id] = 0
            self.f[node.id] = self.h(node)
            self.open.add(node, self.f[node.id])

        lowest_dist_to_goal = self.start.dist(self.goal)
        lowest_time_to_goal = 0

        i = 0
        while self.open.any():
            i += 1
            [f_score, node] = self.open.pop()
            star = node.star

            # a better route has been found already
            if self.f[node.id] < f_score:
                continue

            dist = star.dist(self.goal)

            if dist < lowest_dist_to_goal:
                lowest_dist_to_goal = dist
                lowest_time_to_goal = int(self.f[node.id]-self.g[node.id])

            print("%8d %8d %8d %9s %9s %6d %6d   %s" % (
                i,
                len(self.open),
                len(self.came_from),
                datetime.timedelta(seconds=int(self.f[node.id])),
                datetime.timedelta(seconds=lowest_time_to_goal),
                lowest_dist_to_goal,
                dist,
                star.name
            ))

            # reached goal
            if star.id == self.goal.id:
                return self.reconstruct_path(node)

            # direct route to goal
            self.handle_neighbor(node, self.goal, None)

            neighbors = self.galaxy.get_neighbors(star, 500)
            for neighbor in neighbors:

                # cylinder constraint
                if 2000 < self.distance_from_center_line(neighbor):
                    continue

                # backtracking constraint
                neighbor_dist = neighbor.dist(self.goal)
                if dist < neighbor_dist:
                    continue

                # without refueling
                self.handle_neighbor(node, neighbor, None)
                if neighbor.distance_to_scoopable is not None:
                    # with refueling
                    for level in self.ship.refuel_levels:
                        self.handle_neighbor(node, neighbor, level)

    def distance_from_center_line(self, star):

        # https://mathworld.wolfram.com/Point-LineDistance3-Dimensional.html

        x0 = [star.x, star.y, star.z]
        x1 = [self.start.x, self.start.y, self.start.z]
        x2 = [self.goal.x, self.goal.y, self.goal.z]

        x1m0 = [x1[i]-x0[i] for i in range(3)]
        x2m1 = [x2[i]-x1[i] for i in range(3)]

        t = -1 * sum([x1m0[i]*x2m1[i] for i in range(3)]) / \
            sum([x2m1[i]**2 for i in range(3)])

        x3 = [x1[i] + t * x2m1[i] for i in range(3)]

        if t < 0:
            # distance from start
            return math.sqrt(sum([(x0[i]-x1[i])**2 for i in range(3)]))
        elif 1 < t:
            # distance from goal
            return math.sqrt(sum([(x0[i]-x2[i])**2 for i in range(3)]))
        else:
            # distance from line point
            return math.sqrt(sum([(x0[i]-x3[i])**2 for i in range(3)]))
