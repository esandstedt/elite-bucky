import math

FUEL_POWERS = {
    "2": 2,
    "3": 2.15,
    "4": 2.3,
    "5": 2.45,
    "6": 2.6,
    "7": 2.75,
}

FUEL_MULTIPLIERS = {
    "A": 0.012,
    "B": 0.01,
    "C": 0.008,
    "D": 0.01,
    "E": 0.011,
}


class Ship:
    def __init__(self, params):
        self.name = params["name"]
        self.dry_mass = params["dry_mass"]
        self.fuel_capacity = params["fuel_capacity"]
        self.fsd = params["fsd"]
        self.fsd_fuel_power = FUEL_POWERS[params["fsd"][0]]
        self.fsd_fuel_multiplier = FUEL_MULTIPLIERS[params["fsd"][1]]
        self.max_fuel_per_jump = params["max_fuel_per_jump"]
        self.optimised_mass = params["optimised_mass"]
        self.guardian_bonus = params["guardian_bonus"]
        self.fuel_scoop_rate = params["fuel_scoop_rate"]
        self.refuel_levels = params["refuel_levels"]
        self.minimum_fuel = params["minimum_fuel"]

    def get_max_jump_range(self, fuel=None):
        if fuel is None:
            fuel = self.fuel_capacity

        # this algorithm can't handle restrictions when at low fuel so use the nuclear option
        if fuel < self.max_fuel_per_jump:
            return 0

        m = self.optimised_mass / (self.dry_mass + fuel)
        f = self.max_fuel_per_jump / self.fsd_fuel_multiplier
        return m * math.pow(f, 1 / self.fsd_fuel_power) + self.guardian_bonus

    def get_fuel_cost(self, fuel, dist):
        max_range = self.get_max_jump_range(fuel)

        n = dist * max_range * (self.dry_mass + fuel)
        d = (max_range + self.guardian_bonus) * self.optimised_mass

        return self.fsd_fuel_multiplier * math.pow(n / d, self.fsd_fuel_power)
