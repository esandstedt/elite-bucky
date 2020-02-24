import gzip, heapq, json, math, mysql.connector, time
from collections import defaultdict
from scipy.spatial import KDTree



class Coords:
  def __init__(self, x, y, z):
    self.x = x
    self.y = y
    self.z = z

  def dist(self, other):
    return math.sqrt(self.dist_squared(other))

  def dist_squared(self, other):
    return (self.x-other.x)**2 + (self.y-other.y)**2 + (self.z-other.z)**2



class Star: 
  def __init__(self, id, name, coords, neutron = False):
    self.id = id
    self.name = name
    self.coords = coords
    self.is_neutron = neutron

  def __lt__(self, other):
    return self.id < other.id



class StarCollection:
  def __init__(self, list):
    self._list = list
    self._tree_array = [[star.coords.x, star.coords.y, star.coords.z] for star in list]
    self._tree = KDTree(self._tree_array)

  def get_by_id(self, id):
    return [x for x in self._list if x.id == id][0]

  def get_neighbors(self, current, min_dist, max_dist, goal):
    #return [x for x in self._list if min_dist**2 < current.coords.dist_squared(x.coords) < max_dist**2 and x is not current]
    indexes = self._tree.query_ball_point([current.coords.x, current.coords.y, current.coords.z], max_dist)
    stars = [self._list[i] for i in indexes]

    dist_current_to_goal = current.coords.dist(goal.coords)

    results = []
    for star in stars:
      dist_goal_to_star = goal.coords.dist(star.coords)
      dist_current_to_star = current.coords.dist(star.coords)

      if dist_current_to_star < min_dist: 
        continue
      if dist_current_to_goal < dist_goal_to_star:
        continue 

      results.append(star)

    return results


class OpenCollection:
  def __init__(self):
    self._heap = []
    #self._set = set([])

  def add(self, star, f_score):
    heapq.heappush(self._heap, [f_score, star])
    #self._set.add(star)

  def any(self):
    return len(self._heap) != 0
    #return len(self._set) != 0
  
  def pop(self):
    return heapq.heappop(self._heap)
    #result = sorted([(f[x.id], x) for x in self._set])[0][1]
    #self._set.remove(result)
    #return result

  def __len__(self):
    return len(self._heap)
    #return len(self._set)



db = mysql.connector.connect(
  host="localhost",
  user="elite",
  passwd="elite",
  database="elite"
)
cursor = db.cursor()

print("loading dataset...")

time_start = time.time()

query = "SELECT `id64`, `name`, `x`, `y`, `z` FROM `system` WHERE `x`"
cursor.execute(query)
stars = [Star(x[0], x[1], Coords(x[2],x[3],x[4]), True) for x in cursor.fetchall()]

jump_range = 65.27

#node_start = Star(1, "Sol", Coords(0,0,0))
#node_goal = Star(2, "Hypio Pri IZ-D d13-6549", Coords(425, -111, 25682))
#node_goal = Star(2, "Sagittarius A*", Coords(25.21875, -20.90625, 25899.96875))

node_start = Star(1, "Froarks GM-D d12-355", Coords(-533.59375, 209.6875, 15375.09375))
node_goal = Star(2, "Sol", Coords(0,0,0))

lowest_dist_to_goal = node_start.coords.dist(node_goal.coords)

star_collection = StarCollection(stars + [node_start, node_goal])

h = lambda s: s.coords.dist(node_goal.coords) / (4*jump_range)



# came_from[n] is the node immediately preceding it on the cheapest path currently known
came_from = {}

def reconstruct_path(id):
  path = [star_collection.get_by_id(id)]
  while id in came_from:
    id = came_from[id]
    path.insert(0, star_collection.get_by_id(id))
  return path

# g[n] is the cost of the cheapest path from start to n currently known
g = defaultdict(lambda: 1000000)
g[node_start.id] = 0

# f[n] is g[n]+h(n)
f = defaultdict(lambda: 1000000)
f[node_start.id] = h(node_start)

open_collection = OpenCollection()
open_collection.add(node_start, f[node_start.id])

while open_collection.any():
  [f_score, current] = open_collection.pop()

  if f_score != f[current.id]:
    continue

  dist = current.coords.dist(node_goal.coords)
  lowest_dist_to_goal = min(lowest_dist_to_goal, dist)
  print("%7d %4.3f %5d %5d" % (len(open_collection), f[current.id], lowest_dist_to_goal, int(dist)))


  if dist < 4*jump_range:
    path = reconstruct_path(current.id)
    print()
    for x in path:
      print(x.name)
    break


  neighbors = star_collection.get_neighbors(current, 100, 500, node_goal)
  for neighbor in neighbors:

    dist = current.coords.dist(neighbor.coords)
    g_score = g[current.id]

    if current.is_neutron:
      g_score += max(1, math.ceil(dist / jump_range) - 3)
    else:
      g_score += math.ceil(dist/jump_range)

    if g_score < g[neighbor.id]:
      came_from[neighbor.id] = current.id
      g[neighbor.id] = g_score
      f[neighbor.id] = g_score + h(neighbor)
      open_collection.add(neighbor, f[neighbor.id])

time_end = time.time()

print()
print("time: " + str(time_end - time_start))