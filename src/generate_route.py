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
    # ship = Ship("DSV Phoenix (Bucky)", 480, 0, 128, "6A", 8, 2902, 10.5, 1.245)
    # ship = Ship("DSV Aurora (Bucky)", 281, 0, 32, "6A", 5, 1693, 10.5, 0.878)
    ship = Ship("DSV Too Cheap to Ignore", 34, 0, 6, "2A", 1, 140, 6.0, 0.075)

    galaxy = Galaxy(db)

    start = galaxy.get_by_name(STARS["bucky_start"])
    goal = galaxy.get_by_name(STARS["bucky_end"])
    refuel_levels = [
        FuelRange(28, 36),
        FuelRange(44, 52),
        FuelRange(60, 68),
        FuelRange(76, 84),
        FuelRange(92, 100),
        FuelRange(108, 116),
        FuelRange(124, 128),
    ]

    start = galaxy.get_by_name("Sol")
    goal = galaxy.get_by_name(STARS["hillary_depot"])
    refuel_levels = [
        FuelRange(6, 6),
    ]

    t_start = time.time()
    path = Pathfind(ship, galaxy, start, goal, refuel_levels).run()
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
