import gzip
from itertools import islice
import json
import math
import mysql.connector
import os
import sys

from dotenv import load_dotenv
load_dotenv()


def get_existing_system_ids(cursor):
    cursor.execute(
        "SELECT `id` FROM `system`"
    )
    return set([x[0] for x in cursor.fetchall()])


def enumerate_systems(file_path):
    with gzip.open(file_path) as input_file:
        for line in input_file:
            try:
                data = line.strip()[:-1]
                yield json.loads(data)
            except json.decoder.JSONDecodeError:
                pass


def run(cursor, systems, index_from, index_to):
    c = index_from
    for system in islice(systems, index_from, index_to):
        c += 1

        id = system["id64"]
        name = system["name"]
        x = system["coords"]["x"]
        y = system["coords"]["y"]
        z = system["coords"]["z"]
        sectorX = math.floor(x/1000)
        sectorY = math.floor(y/1000)
        sectorZ = math.floor(z/1000)

        cursor.execute(
            "INSERT IGNORE INTO `system`(`id`,`name`,`x`,`y`,`z`,`sectorX`,`sectorY`,`sectorZ`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (id, name, x, y, z, sectorX, sectorY, sectorZ)
        )

        print("%9d %s" % (c, name))

        if c % 1000 == 0:
            db.commit()

    db.commit()


if __name__ == "__main__":
    index_from = int(sys.argv[1])
    index_to = int(sys.argv[2])

    db = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        passwd=os.getenv("MYSQL_PASSWD"),
        database=os.getenv("MYSQL_DATABASE"),
    )
    run(
        db.cursor(),
        enumerate_systems("./data/systemsWithCoordinates.json.gz"),
        index_from,
        index_to
    )
    """
    db = mysql.connector.connect(
        host="localhost",
        user="elite",
        passwd="elite",
        database="elite"
    )
    run(
        db.cursor(),
        enumerate_systems("./data/200419_systemsWithCoordinates7days.json.gz"),
        0,
        None
    )
    """
