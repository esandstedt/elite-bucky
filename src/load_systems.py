import gzip, json, mysql.connector

def enumerate_systems(file_path):
  with gzip.open(file_path) as input_file:
    for line in input_file:
      try: 
        data = line.strip()[:-1]
        yield json.loads(data)
      except json.decoder.JSONDecodeError:
        pass

def run(db, systems):
  cursor = db.cursor()
  c = 0
  d = 0
  for system in systems:
    c += 1

    id = system["id64"]
    name = system["name"]
    x = system["coords"]["x"]
    y = system["coords"]["y"]
    z = system["coords"]["z"]

    # Filter out systems that won't help with the SagA* route
    if x<-5000 or 5000<x or y<-5000 or 5000<y or z<-1000 or 27000<z:
      continue

    d += 1

    cursor.execute(
      "INSERT IGNORE INTO `system`(`id`,`name`,`x`,`y`,`z`) VALUES (%s,%s,%s,%s,%s)",
      (id, name, x, y, z)
    )

    if d%1000 == 0:
      print("%9d %9d %s" % (c, d, name))
      db.commit()
  db.commit()

if __name__=="__main__":
  run(
    mysql.connector.connect(
      host="localhost",
      user="elite",
      passwd="elite",
      database="elite"
    ),
    enumerate_systems("./data/systemsWithCoordinates.json.gz")
  )
