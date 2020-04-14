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

        return self._get_range(fuel, self._get_boosted_fuel_multiplier(fuel))

    def get_fuel_cost(self, fuel, dist):
        total_mass = self.dry_mass + fuel
        return self._get_boosted_fuel_multiplier(fuel) * math.pow(dist * total_mass / self.optimised_mass, self.fsd_fuel_power)

    def _get_boosted_fuel_multiplier(self, fuel):
        base_range = self._get_range(fuel)
        return self.fsd_fuel_multiplier * math.pow(base_range / (base_range + self.guardian_bonus), self.fsd_fuel_power)

    def _get_range(self, fuel, fuel_multiplier=None):
        if fuel_multiplier is None:
            fuel_multiplier = self.fsd_fuel_multiplier

        max_fuel = min(self.max_fuel_per_jump, fuel)
        total_mass = self.dry_mass + fuel

        return (self.optimised_mass / total_mass) * math.pow(max_fuel / fuel_multiplier, 1.0 / self.fsd_fuel_power)
