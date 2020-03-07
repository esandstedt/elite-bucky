import gzip, json, mysql.connector

db = mysql.connector.connect(
  host="localhost",
  user="elite",
  passwd="elite",
  database="elite"
)
cursor = db.cursor()

print("loading ids...")
cursor.execute("SELECT `id64` FROM `system` WHERE `x`=0 AND `y`=0 AND `z`=0")
ids = set([x[0] for x in cursor.fetchall()])
print(len(ids))

c = 0
d = 0

with gzip.open("./data/systemsWithCoordinates.json.gz") as input_file:
  for line in input_file:
    try: 
      data = line.strip()[:-1]
      obj = json.loads(data)

      c += 1

      id = obj["id64"]
      name = obj["name"]
      x = obj["coords"]["x"]
      y = obj["coords"]["y"]
      z = obj["coords"]["z"]

      if id in ids:
        cursor.execute(
          "UPDATE `system` SET `x`=%s, `y`=%s, `z`=%s WHERE `id64` = %s",
          (x, y, z, id)
        )
        print(name)
        d += 1

        if d%1000==0:
          db.commit()

      if c%1000000==0:
        print(int(c)/1000000)

    except json.decoder.JSONDecodeError:
      pass

db.commit()