import mysql.connector
import os
from model.galaxy import Galaxy


def load_route(path):
    with open(path, 'r') as f:
        return [line.strip() for line in f.readlines()]


def run(db, route):
    galaxy = Galaxy(db)
    for name in route:
        star = galaxy.get_by_name(name)
        neighbors = [
            x for x in galaxy.get_neighbors(star, 300) if x.distance_to_neutron < 10
        ]

        ab_neighbors = [
            x for x in neighbors if x.distance_to_scoopable is not None and x.distance_to_scoopable < 10
        ]

        print("%-30s %4d %4d" % (name, len(neighbors), len(ab_neighbors)))


if __name__ == "__main__":
    """
    db = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        passwd=os.getenv("MYSQL_PASSWD"),
        database=os.getenv("MYSQL_DATABASE"),
    )
    run(
        db,
        load_route("./.route")
    )
    """
    db = mysql.connector.connect(
        host="localhost",
        user="elite",
        passwd="elite",
        database="elite"
    )
    run(
        db,
        load_route("./.route")
    )
