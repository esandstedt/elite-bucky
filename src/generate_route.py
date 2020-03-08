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


STARS = {
    "colonia": Star(1, "Colonia", -9530, -910, 19808),
    "hillary_depot": Star(2, "Blu Thua AI-A c14-10", -54, 149, 2099),
    "omega_mining": Star(3, "Omega Sector VE-Q b5-15", -1444, -85, 5319),
    "rohini": Star(4, "Rohini", -3374, -47, 6912),
    "sacaqawea": Star(5, "Skaudai CH-B d14-34", -5481, -579, 10429),
    "sagittarius": Star(6, "Sagittarius A*", 25, -20, 25899),
    "sol": Star(7, "Sol", 0, 0, 0)
}


def run(db):
    #ship = Ship("DSV Phoenix (Exploration)", 578, 4, 64, "6A", 8, 2902, 10.5)
    ship = Ship("DSV Phoenix (Bucky)", 479, 0, 64, "6A", 8, 2902, 10.5)

    galaxy = Galaxy(db)

    start = STARS["sol"]
    goal = STARS["hillary_depot"]

    t_start = time.time()
    path = Pathfind(ship, galaxy, start, goal).run()
    t_end = time.time()

    print()
    print_path(path)

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
