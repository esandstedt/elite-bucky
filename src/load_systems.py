import gzip
import json
import mysql.connector


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


def run(cursor, systems):
    # existing_ids = get_existing_system_ids(cursor)

    c = 0
    d = 0
    for system in systems:
        c += 1

        id = system["id64"]
        name = system["name"]
        x = system["coords"]["x"]
        y = system["coords"]["y"]
        z = system["coords"]["z"]

        # if id in existing_ids:
        #     continue

        d += 1

        cursor.execute(
            "INSERT IGNORE INTO `system`(`id`,`name`,`x`,`y`,`z`) VALUES (%s,%s,%s,%s,%s)",
            (id, name, x, y, z)
        )

        if d % 1000 == 0:
            print("%9d %9d %s" % (c, d, name))
            db.commit()

    db.commit()


if __name__ == "__main__":
    db = mysql.connector.connect(
        host="localhost",
        user="elite",
        passwd="elite",
        database="elite"
    )
    run(
        db.cursor(),
        enumerate_systems("./data/systemsWithCoordinates.json.gz")
    )
