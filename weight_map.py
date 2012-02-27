import types, itertools, array

class weight_map (object):
  """weight map interface: represents a function that order a weight
     (single value) to any given vertex of the mesh.
  """
  def __init__ (self):
    """initialize a weight map. This baseclass represents an empty map.
    """
    pass
  def get_weight (self, index):
    """return the weight for the vertex at the given index.
    """
    # default implementation: return 0 (represents an empty weightmap).
    return 0
  def get_domain (self):
    """return the index range this weight map is defined on.
    """
    # default: return an unlimited range (here: up to 1 billion weights).
    return (0, 10 ** 9)

class geometric_map (weight_map):
  """weight map that is based on geometric location of a vertex
     rather than on an index.
  """
  def __init__ (self, lookup = None):
    """initialize with a lookup function. The lookup function
       transforms a vertex number to its coordinates.
    """
    assert (callable (lookup))
    self.lookup = lookup
  def get_coords (self, index):
    """return the coordinates of the vertex.
    """
    return self.lookup (index)

class transform_map (geometric_map):
  """weight map helper for weight maps based on a geometric transformation
     to calculate a weight. implements the get-weight function by calling
     the calc-weight function to be implemented by subclasses.
  """
  def __init__ (self, transformation = None, lookup = None):
    """initialize with a transformation which transforms
       a point in 3d-space to another coordinate system.
    """
    super (transform_map, self).__init__ (lookup = lookup)
    assert (callable (transformation))
    self.transformation = transformation
  def get_local_coords (self, index):
    """return the transformed coordinates of the vector with index index
       after applying transformation.
    """
    global_coords = self.get_coords (index)
    local_coords = self.transformation (global_coords)
    return local_coords
  def get_weight (self, index):
    """calculate the weight for the vertex at the given index by
       calling the subclasses calc-weight function.
    """
    local_coords = self.get_local_coords (index)
    return self.calc_weight (local_coords)
  def calc_weight (self, coords):
    """calculate a weight for a vertex that is given in local coordinates.
    """
    raise NotImplementedError ("subclass needs to define calc_vertex.")

class angle_map (transform_map):
  """a weight map that applies a transformation to a vertex,
     projects it into the xy-plane and uses the angle between the
     x-axis and the vector to create a weight-value.
  """
  def __init__ (self, angle, **kwarg):
    """ranges contains 4 numbers:
      (angle[0], angle[1]) are exclusion angles between the weight is 0;
      (angle[2], angle[3]) are inclusion angles between the weight is 1,
      other angles get interpolated linearly.
    """
    super (angle_map, self).__init__ (self, **kwarg)
    self.angles = angles
  def calc_weight (self, coords):
    """calculate the weight for the vertex with the given coordinates.
       coords are a position in local space.
    """
    # todo
    return 0
  pass

class zdist_map (transform_map):
  """weight map implementation that applies a transformation to a vertex,
     measures its value along the z-axis and uses that value to check
     if a predefined interval is met.
  """
  def __init__ (self, zmin, zmax, **kwarg):
    """initialize a zdist map with the zrange [zmin, zmax]. z-values
       below zmin get a weight of 0, z-values above zmax get a weight of 1,
       intermediate values are interpolated linearly.
    """
    super (zdist_map, self).__init__ (**kwarg)
    self.zmin = zmin
    self.zmax = zmax
  def calc_weight (self, coords):
    """calculate the weight for the vertex with the given coordinates.
       coords are the vertex position in local space.
    """
    # todo
    return 0
  pass

class sphere_map (geometric_map):
  """weight map implementation that uses an inclusion/exclusion-sphere
     to calculate a weight.
  """
  def __init__ (self, inner, outer, **kwarg):
    """initialize a sphere map with two ellipsoids inner and outer.
       inner and outer are given as matrices transforming the unit-sphere
       into the respective ellipsoids.
    """
    super (sphere_map, self).__init__ (**kwarg)
    self.inner = inner
    self.outer = outer
  def get_weight (self, index):
    """calculate a weight for vertex at the given index.
    """
    # todo
    global_coords = self.get_coords (index)
  pass

class sparse_table (object):
  """class to implement index lookup based on a dictionary.
  """
  def __init__ (self, indices, values):
    """initialize this object with an iterable of indices
       and an iterable of values.
    """
    assert (len (indices) == len (values))
    self.data = {
      idx: val for (idx, val) in itertools.zip_longest (indices, values)
    }
  def get_value (self, index):
    """return the value for the given index.
    """
    if index in self.data:
      return self.data[index]
    else:
      return 0

class dense_table (object):
  """class to implement index lookup based on a single array
     of values.
  """
  def __init__ (self, indices, values):
    """initialize this object with a list of indices
       and an iterable of values.
    """
    assert (len (indices) == len (values))
    self.low = min (indices)
    self.high = max (indices) + 1
    self.data = array.array ('f', [0.0] * (self.high - self.low))
    for index, value in itertools.zip_longest (indices, values):
      self.data[index - self.low] = value
  def get_value (self, index):
    """return the value for the given index.
    """
    if self.low <= index and index <= self.high:
      return self.data[index - self.low]
    else:
      return 0.0

class linear_table (object):
  """class to implement index lookup based on two arrays.
  """
  def __init__ (self, indices, values):
    """initialize this object with a list of indices
       and an iterable of values. indices must be sorted.
    """
    assert (len (indices) == len (values))
    self.value = array.array ('f', values)
    self.index = array.array ('i', indices)
  def get_value (self, index):
    """return the value for the given index.
    """
    idx_pos = bisect.bisect_left (self.index, index)
    if idx_pos == len (self.index):
      return 0.0
    elif self.index[idx_pos] == index:
      return self.value[idx_pos]
    else:
      return 0.0
  
class table_map (weight_map):
  """weight map that simply uses a stored array of values to deliver these
     as weight values.
  """
  def __init__ (self, indices, values, **kwarg):
    """initialize a weight map given by a table.
       @param indices is a list of indexes for the weightmap.
       @param values is an iterable return weights.
    """
    super (table_map, self).__init__ (self, **kwarg)
    (low, high) = (min (indices), max (indices) + 1)
    assert (len (indices) < high - low)
    density = len (indices) / (high - low)
    if density < 0.1:
      self.data = sparse_table (self, indices, values)
    elif density < 0.7:
      self.data = linear_table (self, indices, values)
    else:
      self.data = dense_table (self, indices, values)
    self.domain = (low, high)
  def get_domain (self):
    """overwritten domain function returns an actually usable range.
    """
    return self.domain
  def get_weight (self, index):
    """return the value for the given index.
    """
    return self.data.get_value (index)
