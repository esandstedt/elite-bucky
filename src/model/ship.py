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
    def __init__(self, name, dry_mass, cargo_mass, fuel_capacity, fsd, max_fuel_per_jump, optimised_mass, guardian_bonus):
        self.name = name
        self.dry_mass = dry_mass
        self.cargo_mass = cargo_mass
        self.fuel_capacity = fuel_capacity
        self.fsd = fsd
        self.fsd_fuel_power = FUEL_POWERS[fsd[0]]
        self.fsd_fuel_multiplier = FUEL_MULTIPLIERS[fsd[1]]
        self.max_fuel_per_jump = max_fuel_per_jump
        self.optimised_mass = optimised_mass
        self.guardian_bonus = guardian_bonus

    def get_max_jump_range(self, fuel=None):
        if fuel is None:
            fuel = self.fuel_capacity

        m = self.optimised_mass / (self.dry_mass + self.cargo_mass + fuel)
        f = self.max_fuel_per_jump / self.fsd_fuel_multiplier
        return m * math.pow(f, 1 / self.fsd_fuel_power) + self.guardian_bonus

    def get_fuel_cost(self, distance, fuel):
        max_jump_range = self.get_max_jump_range(fuel)

        r = max_jump_range - self.guardian_bonus
        n = (self.dry_mass + self.cargo_mass + fuel) * distance * r
        d = max_jump_range * self.optimised_mass
        return self.fsd_fuel_multiplier * math.pow(n / d, self.fsd_fuel_power)