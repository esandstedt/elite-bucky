import json, mysql.connector

db = mysql.connector.connect(
  host="localhost",
  user="elite",
  passwd="elite",
  database="elite"
)
cursor = db.cursor()

c = 0

with open("./neutrons.json") as input_file:
  for line in input_file:
    try: 
      data = line.strip()[:-1]
      obj = json.loads(data)

      c += 1

      print("%7d: %s" % (c, obj["name"]))

      id64 = obj["systemId64"]
      name = obj["systemName"]
      neutronName = obj["name"][len(name)+1:]
      distanceToNeutron = obj["distanceToArrival"]

      cursor.execute(
        "SELECT `id64`, `distanceToNeutron` FROM `system` WHERE `id64`=%s", 
        (id64,)
      )
      result = cursor.fetchall()


      if len(result) == 0:
        cursor.execute(
          "INSERT INTO `system`(`id64`,`name`,`neutronName`,`distanceToNeutron`) VALUES (%s,%s,%s,%s)",
          (id64, name, neutronName, distanceToNeutron)
        )
      elif distanceToNeutron < result[0][1]:
        cursor.execute(
          "UPDATE `system` SET `neutronName`=%s, `distanceToNeutron`=%s WHERE `id64` = %s",
          (neutronName, distanceToNeutron, id64)
        )

      if c%1000==0:
        db.commit()

    except json.decoder.JSONDecodeError:
      pass

db.commit()