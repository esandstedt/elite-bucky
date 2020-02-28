import gzip
import json
import mysql.connector


def enumerate_bodies(file_path):
    with gzip.open(file_path) as input_file:
        for line in input_file:
            try:
                data = line.strip()[:-1]
                yield json.loads(data)
            except json.decoder.JSONDecodeError:
                pass


def run(cursor, bodies):
    c = 0
    d = 0

    for body in bodies:
        c += 1

        name = body["name"]
        type = body["type"]
        sub_type = body["subType"]
        distance_to_arrival = body["distanceToArrival"]
        system_id = body["systemId64"]

        if type != "Star":
            continue

        within_distance = distance_to_arrival <= 65535
        is_neutron = sub_type == "Neutron Star"
        is_scoopable = sub_type in [
            "O (Blue-White) Star",
            "B (Blue-White) Star",
            "A (Blue-White super giant) Star",
            "A (Blue-White) Star",
            "F (White) Star",
            "G (White-Yellow super giant) Star",
            "G (White-Yellow) Star",
            "K (Yellow-Orange giant) Star",
            "K (Yellow-Orange) Star",
            "M (Red dwarf) Star",
            "M (Red giant) Star",
            "M (Red super giant) Star"
        ]

        if is_neutron and within_distance:
            d += 1
            cursor.execute(
                "UPDATE `system` SET `distanceToNeutron`=%s WHERE `id`=%s AND (`distanceToNeutron` IS NULL OR %s<`distanceToNeutron`)",
                (distance_to_arrival, system_id, distance_to_arrival)
            )

            if d % 1000 == 0:
                db.commit()
                print("%9d %9d %s" % (c, d, name))

        elif is_scoopable and within_distance:
            d += 1
            cursor.execute(
                "UPDATE `system` SET `distanceToScoopable`=%s WHERE `id`=%s AND (`distanceToScoopable` IS NULL OR %s<`distanceToScoopable`)",
                (distance_to_arrival, system_id, distance_to_arrival)
            )

            if d % 1000 == 0:
                db.commit()
                print("%9d %9d %s" % (c, d, name))


if __name__ == "__main__":
    db = mysql.connector.connect(
        host="localhost",
        user="elite",
        passwd="elite",
        database="elite"
    )
    run(
        db.cursor(),
        enumerate_bodies("./data/bodies.json.gz")
    )
