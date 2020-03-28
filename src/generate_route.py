import datetime
import mysql.connector
import time
from model.star import Star
from model.galaxy import Galaxy
from model.pathfind import Pathfind
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
            print("    scoopable: true")
            print("    fuel: %d" % (refuel,))
        elif scoopable == 0:
            print("    scoopable: false")


STARS = {
    "colonia": Star(1, "Colonia", -9530, -910, 19808),
    "hillary_depot": Star(2, "Blu Thua AI-A c14-10", -54, 149, 2099),
    "omega_mining": Star(3, "Omega Sector VE-Q b5-15", -1444, -85, 5319),
    "rohini": Star(4, "Rohini", -3374, -47, 6912),
    "sacaqawea": Star(5, "Skaudai CH-B d14-34", -5481, -579, 10429),
    "sagittarius": Star(6, "Sagittarius A*", 25, -20, 25899),
    "sol": Star(7, "Sol", 0, 0, 0),
    "eagle": Star(8, "Eagle Sector IR-W d1-105", -2046, 104, 6699),
    "bucky_end": Star(10, "Myriesly RT-Z d13-3970", -397, 66, 25778)
}


def run(db):
    #ship = Ship("DSV Phoenix (Exploration)", 578, 4, 64, "6A", 8, 2902, 10.5, 1.245)
    ship = Ship("DSV Phoenix (Bucky)", 480, 0, 64, "6A", 8, 2902, 10.5, 1.245)

    galaxy = Galaxy(db)

    start = STARS["sol"]
    goal = STARS["rohini"]
    refuel_levels = [32, 48, 64]

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
