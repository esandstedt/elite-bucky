import datetime
import gzip
import json
import mysql.connector
import os

from dotenv import load_dotenv
load_dotenv()


def enumerate_systems(file_path):
    with gzip.open(file_path) as input_file:
        for line in input_file:
            try:
                data = line.strip()[:-1]
                yield json.loads(data)
            except json.decoder.JSONDecodeError:
                pass


def run(cursor, systems):
    c = 0
    for system in systems:
        c += 1

        id = system["id64"]
        date = datetime.datetime.fromisoformat(
            system["date"]).date().isoformat()
        name = system["name"]

        print("%8d %9s %s" % (
            c,
            date,
            name
        ))

        cursor.execute(
            "UPDATE `system` SET `date`=%s WHERE `id`=%s",
            (date, id)
        )

        if c % 1000 == 0:
            db.commit()

    db.commit()


if __name__ == "__main__":
    """
    db = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        passwd=os.getenv("MYSQL_PASSWD"),
        database=os.getenv("MYSQL_DATABASE"),
    )
    run(
        db.cursor(),
        enumerate_systems(os.genenv("SYSTEMS_PATH"))
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
        enumerate_systems(os.genenv("SYSTEMS_PATH"))
    )
