import gzip, json, math, time

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