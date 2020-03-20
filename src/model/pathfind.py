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
    def __init__(self, star, refuel, fuel):
        self.id = (star.id, refuel)
        self.star = star
        self.refuel = refuel
        self.fuel = fuel

    def __lt__(self, other):
        return self.id < other.id


TIME_PER_JUMP = 60


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

    def handle_neighbor(self, current_node, neighbor, refuel):
        star = current_node.star
        fuel = current_node.fuel

        jump_range = self.ship.get_max_jump_range(fuel)
        if star.distance_to_neutron is not None:
            jump_range = 4*jump_range

        if jump_range == 0:
            return

        dist = star.dist(neighbor)

        remaining_jump_range = self.ship.get_max_jump_range()
        remaining_dist = max(0, dist - jump_range)
        num_of_jumps = 1 + math.ceil(remaining_dist / remaining_jump_range)

        fuel_cost = 0
        if star.distance_to_neutron is not None:
            fuel_cost = self.ship.get_fuel_cost(
                fuel, min(jump_range, dist / 4))
        else:
            fuel_cost = self.ship.get_fuel_cost(fuel, min(jump_range, dist))

        neighbor_fuel = fuel - fuel_cost

        # not a valid neighbor because too low fuel
        if neighbor_fuel < 1:
            return

        refuel_penalty = 0
        if num_of_jumps > 1:
            # fill back to full tank
            delta = self.ship.fuel_capacity - (neighbor_fuel)
            t_fst = delta / self.ship.fuel_scoop_rate
            # refill after each jump
            t_rst = (num_of_jumps - 1) * \
                self.ship.max_fuel_per_jump / self.ship.fuel_scoop_rate

            neighbor_fuel = fuel - self.ship.max_fuel_per_jump
            refuel_penalty = t_fst + t_rst

        if refuel:
            # time to travel to scoopable star
            t_travel = 60 * neighbor.distance_to_scoopable / 500
            # time to refuel
            delta = self.ship.fuel_capacity - (neighbor_fuel)
            t_refuel = delta / self.ship.fuel_scoop_rate

            neighbor_fuel = self.ship.fuel_capacity
            refuel_penalty = t_travel + t_refuel

        neighbor_node = Node(neighbor, refuel, neighbor_fuel)

        g_score = self.g[current_node.id] + \
            TIME_PER_JUMP * num_of_jumps + refuel_penalty

        if g_score < self.g[neighbor_node.id]:

            self.came_from[neighbor_node.id] = current_node
            self.g[neighbor_node.id] = g_score
            f_score = g_score + self.h(neighbor_node)
            self.f[neighbor_node.id] = f_score

            self.open.add(neighbor_node, f_score)

    def reconstruct_path(self, node):
        path = [node]
        id = node.id
        while id in self.came_from:
            node = self.came_from[id]
            path.append(node)
            id = node.id
        return reversed(path)

    def run(self):
        start_node = Node(self.start, False, self.ship.fuel_capacity)
        self.g[start_node.id] = 0
        self.f[start_node.id] = self.h(start_node)
        self.open.add(start_node, self.f[start_node.id])

        lowest_dist_to_goal = self.start.dist(self.goal)

        i = 0
        while self.open.any():
            i += 1
            [f_score, node] = self.open.pop()
            star = node.star

            # a better route has been found already
            if self.f[node.id] < f_score:
                continue

            dist = star.dist(self.goal)
            lowest_dist_to_goal = min(lowest_dist_to_goal, dist)
            print("%8d %8d %9s %6d %6d   %s" %
                  (i, len(self.open), datetime.timedelta(seconds=int(self.f[node.id])), lowest_dist_to_goal, dist, star.name))

            # reached goal
            if star.id == self.goal.id:
                return self.reconstruct_path(node)

            # direct route to goal
            self.handle_neighbor(node, self.goal, False)

            neighbors = self.galaxy.get_neighbors(star, 500)
            for neighbor in neighbors:
                # without refueling
                self.handle_neighbor(node, neighbor, False)
                if neighbor.distance_to_scoopable is not None:
                    # with refueling
                    self.handle_neighbor(node, neighbor, True)
