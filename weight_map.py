import types, itertools, array
import mathutils

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
       Subclasses should overwrite this function to narrow down the range.
    """
    # default: return an unlimited range (here: up to 1 billion weights).
    return (0, 10 ** 9)

class geometric_map (weight_map):
  """weight map that is based on geometric location of a vertex
     rather than on an index. subclasses must implement get_coord_weight
     which gets called by the implementation of get_weight.
  """
  def __init__ (self, lookup = None):
    """initialize with a lookup function. The lookup function
       transforms a vertex number to its coordinates.
    """
    assert (callable (lookup))
    self.lookup = lookup
  def get_weight (self, index):
    """gets the coordinates of vertex index and calls get_coord_weight.
    """
    return self.get_coord_weight (self.lookup (index))
  def get_coord_weight (self, coord):
    """default implementation of a weight.
    """
    raise NotImplementedError ("get_coord_weight undefined.")

class transform_map (geometric_map):
  """weight map helper for weight maps based on a geometric transformation
     to calculate a weight. implements the get-coord-weight function by calling
     the get_local_weight function to be implemented by subclasses.
  """
  def __init__ (self, transformation = None, lookup = None):
    """initialize with a transformation which transforms
       a point in 3d-space to another coordinate system.
    """
    super (transform_map, self).__init__ (lookup = lookup)
    assert (callable (transformation))
    self.transformation = transformation
  def get_coord_weight (self, coord):
    """transform coord and call the get_local_weight function on self.
    """
    return self.get_local_weight (self.transformation (coord))
  def get_local_weight (self, coords):
    """calculate a weight for a vertex that is given in local coordinates.
    """
    raise NotImplementedError ("calc_vertex undefined.")

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
  def get_local_weight (self, coords):
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
  def get_local_weight (self, coords):
    """calculate the weight for the vertex with the given coordinates.
       coords are the vertex position in local space.
    """
    # todo
    return 0
  pass

class sphere_dist_map (transform_map):
  """weight map that uses the inclusion of a vertex within a ellipsoid
     to return a weight between 0 (in the center of the ellipsoid) and
     infinity (somewhere outside the ellipsoid). The exact border of
     the ellipsoid gets weight 1. This is basically the relative distance
     to the center.
  """
  def __init__ (self, sphere_mat, **kwarg):
    """initialize a sphere_dist_map with a given matrix sphere_mat which
       transforms the unit sphere into an ellipsoid in global space.
    """
    sphere_inv_func = sphere_mat.inverted ().__mul__
    super (sphere_dist_map, self).__init__\
        (transformation = sphere_mat.inverted ().__mul__, **kwarg)
  def get_local_weight (self, coord):
    """return how near coord is to the center of the ellipsoid.
    """
    return coord.length

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
    self.inner_map = sphere_dist_map (inner, **kwarg)
    self.outer_map = sphere_dist_map (outer, **kwarg)
  def get_weight (self, index):
    """calculate a weight for vertex at the given index.
    """
    global_coord = self.lookup (index)
    # greedily calculate the inner and outer weight; it would be more
    # performant to calculate the inner first and the outer only when
    # needed. something todo when it is too slow.
    inner_weight = self.inner_map.get_coord_weight (global_coord)
    outer_weight = self.outer_map.get_coord_weight (global_coord)
    if inner_weight <= 1:
      return 1.0
    elif outer_weight > 1:
      return 0
    else:
      # todo: do some interpolation here, perhaps use the relation
      # between inner and outer scaled to [0, 1]
      return 0.5

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
