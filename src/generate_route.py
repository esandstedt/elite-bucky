import datetime
import mysql.connector
import time
from model.star import Star
from model.galaxy import Galaxy
from model.pathfind import Pathfind, FuelRange
from model.ship import Ship


def print_path(path):
    for node in path:
        star = node.star
        refuel = node.refuel

        name = star.name
        coords = "%.2f,%.2f,%.2f" % (star.x, star.y, star.z)

        types = []
        if star.distance_to_neutron is not None:
            types.append("NS")
        if refuel:
            types.append("SC")

        print("%s [%s;%s]" % (name, coords, ",".join(types)))


def print_path_yaml(path):
    print("route:")
    for node in path:
        star = node.star
        neutron = star.distance_to_neutron
        scoopable = star.distance_to_scoopable
        refuel = node.refuel

        print("  - name: %s" % (star.name,))

        if neutron is not None and 0 < neutron:
            print("    neutron: true")

        if refuel is not None:
            refuel_avg = (refuel.min + refuel.max)/2
            print("    scoopable: true")
            print("    fuel: %d" % (refuel_avg,))
        elif scoopable == 0:
            print("    scoopable: false")


SHIPS = {
    "phoenix": Ship({
        "name": "DSV Phoenix (Bucky)",
        "dry_mass": 480,
        "fuel_capacity": 128,
        "fsd": "6A",
        "max_fuel_per_jump": 8,
        "optimised_mass": 2902,
        "guardian_bonus": 10.5,
        "fuel_scoop_rate": 1.245,
        "refuel_levels": [
            FuelRange(12, 20),
            FuelRange(28, 36),
            FuelRange(44, 52),
            FuelRange(60, 68),
            FuelRange(76, 84),
            FuelRange(92, 100),
            FuelRange(108, 116),
            FuelRange(124, 128),
        ],
        "minimum_fuel": 1
    }),
    "phoenix_2": Ship({
        "name": "DSV Phoenix (Bucky)",
        "dry_mass": 482,
        "fuel_capacity": 128,
        "fsd": "6A",
        "max_fuel_per_jump": 8,
        "optimised_mass": 2902,
        "guardian_bonus": 10.5,
        "fuel_scoop_rate": 1.245,
        "refuel_levels": [
            FuelRange(12, 20),
            FuelRange(28, 36),
            FuelRange(44, 52),
            FuelRange(60, 68),
            FuelRange(76, 84),
            FuelRange(92, 100),
            FuelRange(108, 116),
            FuelRange(124, 128),
        ],
        "minimum_fuel": 1
    }),
    "aurora": Ship({
        "name": "DSV Aurora (Bucky)",
        "dry_mass": 281,
        "fuel_capacity": 32,
        "fsd": "5A",
        "max_fuel_per_jump": 5,
        "optimised_mass": 1693,
        "guardian_bonus": 10.5,
        "fuel_scoop_rate": 0.878,
        "refuel_levels": [
            FuelRange(32, 32),
        ],
        "minimum_fuel": 1
    }),
    "sidewinder": Ship({
        "name": "DSV Too Cheap to Ignore",
        "dry_mass": 34,
        "fuel_capacity": 6,
        "fsd": "2A",
        "max_fuel_per_jump": 1,
        "optimised_mass": 140,
        "guardian_bonus": 6.0,
        "fuel_scoop_rate": 0.075,
        "refuel_levels": [
            FuelRange(6, 6),
        ],
        "minimum_fuel": 1
    })
}


STARS = {
    "attenborough": "Lagoon Sector FW-W d1-122",
    "bucky_start": "3 Capricorni",
    "bucky_end": "Phua Aub QT-W b1-4",
    "colonia": "Colonia",
    "eagle": "Eagle Sector IR-W d1-105",
    "hillary_depot": "Blu Thua AI-A c14-10",
    "omega_mining": "Omega Sector VE-Q b5-15",
    "rohini": "Rohini",
    "sacaqawea": "Skaudai CH-B d14-34",
    "sagittarius": "Sagittarius A*",
    "sol": "Sol",
}


def run(db):

    ship = SHIPS["phoenix_2"]

    galaxy = Galaxy(db)

    start = galaxy.get_by_name("Graea Hypue HC-M d7-9")
    goal = galaxy.get_by_name("Sagittarius A*")

    t_start = time.time()
    path = Pathfind(ship, galaxy, start, goal).run()
    t_end = time.time()

    print()
    print_path_yaml(path)

    t_delta = datetime.timedelta(seconds=t_end-t_start)

    print()
    print("time: " + str(t_delta))


if __name__ == "__main__":
    db = mysql.connector.connect(
        host="localhost",
        user="elite",
        passwd="elite",
        database="elite"
    )
    run(db)
