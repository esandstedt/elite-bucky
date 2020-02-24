import gzip, json, math, time

def load_systems():
  time_start = time.time()
  c = 0

  sectors = dict([])

  x_min = 0
  x_max = 0
  y_min = 0
  y_max = 0
  z_min = 0
  z_max = 0

  with gzip.open("./data/systemsWithCoordinates.json.gz") as input_file:
    for line in input_file:
      try: 
        data = line.decode("utf-8").strip()[:-1]
        obj = json.loads(data)

        id = obj["id64"]
        name = obj["name"]
        x = obj["coords"]["x"]
        y = obj["coords"]["y"]
        z = obj["coords"]["z"]

        sector_x = math.floor(x/1000)
        sector_y = math.floor(y/1000)
        sector_z = math.floor(z/1000)

        sector_id = ((sector_x+128) << 16) + ((sector_y+128) << 8) + ((sector_z+128) << 0)

        if sector_id not in sectors:
          sectors[sector_id] = 0
        
        sectors[sector_id] += 1
        

        x_min = min(x_min, x)
        x_max = max(x_max, x)
        y_min = min(y_min, y)
        y_max = max(y_max, y)
        z_min = min(z_min, z)
        z_max = max(z_max, z)

        c += 1

        if c%50000 == 0:
          print("%10d: %s" % (c, name))

      except json.decoder.JSONDecodeError:
        pass

  time_end = time.time()

  print()
  print("systems: " + str(c))
  print("x: " + str(x_min) + " -> " + str(x_max))
  print("y: " + str(y_min) + " -> " + str(y_max))
  print("z: " + str(z_min) + " -> " + str(z_max))
  print("time: " + str(time_end - time_start))

  with open("sectors.json", "w") as sectors_file:
    sectors_file.write(json.dumps(sectors))

def load_bodies():
  time_start = time.time()

  c = 0
  d = 0

  with open("neutrons.json", "w") as neutrons_file:
    neutrons_file.write("[\n")

    with gzip.open("./data/bodies.json.gz") as input_file:
      for line in input_file:
        try: 
          data = line.decode("utf-8").strip()[:-1]
          obj = json.loads(data)

          c += 1

          if obj["type"] != "Star":
            continue

          if obj["subType"] != "Neutron Star":
            continue

          valid = obj["isMainStar"] or obj["distanceToArrival"] < 500
          if not valid:
            continue

          d += 1

          print("%9d - %7d - %s" % (c, d, obj["systemName"]))
          neutrons_file.write("  " + json.dumps(obj)+ ",\n")

        except:
          print("error")

    neutrons_file.write("]")

  time_end = time.time()

  print()
  print("bodies: " + str(c))
  print("neutrons: " + str(d))
  print("time: " + str(time_end - time_start))
    
  
load_bodies()