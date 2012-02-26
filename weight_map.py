import types

class weight_map (object):
  """weight map interface: represents a function that order a weight
     (single value) to any given vertex of the mesh.
  """
  def __init__ (self, lookup = None, domain = None):
    """initialize a weight map.
       @param lookup is a function that transforms an index into a 3d-coord.
       @param domain are min/max for indexes for which this is defined.
    """
    assert (callable (lookup))
    self.lookup = lookup
    self.domain = domain
  def get_weight (self, index):
    """return the weight for the vertex at the given index.
    """
    # default implementation: return 0 (represents an empty weightmap).
    return 0
  def get_domain (self):
    """returns two numbers. All vertices with indexes lower than
       the first number or greater or equal the second number have
       an implicit weight of 0.
    """
    # return a default value of 1 billion, which is hopefully more
    # than any useful mesh would need.
    if self.domain is None:
      return (0, 10 ** 9)
    else:
      return self.domain

class transform_map (weight_map):
  """weight map helper for weight maps based on a geometric transformation
     to calculate a weight.
  """
  def __init__ (self, transformation = None, **kwarg):
    super (transform_map, self).__init__ (**kwarg)
    assert (callable (transformation))
    self.transformation = transformation
  def get_local_coords (self, index):
    """return the transformed coordinates of the vector with index index
       after applying transformation.
    """
    global_coords = self.lookup (index)
    local_coords = self.transformation * global_coords
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
  def __init__ (self, angle, transformation, **kwarg):
    """ranges contains 4 numbers:
      (angle[0], angle[1]) are exclusion angles between the weight is 0;
      (angle[2], angle[3]) are inclusion angles between the weight is 1,
      other angles get interpolated linearly.
    """
    super (angle_map, self).__init__ (self, transformation, **kwarg)
    self.angles = angles
  def calc_weight (self, coords):
    """calculate the weight for the vertex with the given coordinates.
    """
    return 0
  pass

class zdist_map (transform_map):
  """weight map implementation that applies a transformation to a vertex,
     measures its value along the z-axis and uses that value to check
     if a predefined interval is met.
  """
  def __init__ (self, zmin, zmax, transformation, **kwarg):
    """initialize a zdist map with the zrange [zmin, zmax]. z-values
       below zmin get a weight of 0, z-values above zmax get a weight of 1,
       intermediate values are interpolated linearly.
    """
    super (zdist_map, self).__init__ (transformation, **kwarg)
    self.zmin = zmin
    self.zmax = zmax
  def calc_weight (self, coords):
    """calculate the weight for the vertex with the given coordinates.
    """
    return 0
    pass
  pass

class sphere_map (transform_map):
  """weight map implementation that uses an inclusion/exclusion-sphere
     to calculate a weight.
  """
  def __init__ (self, inner, outer, transformation, **kwarg):
    """initialize a sphere map with two ellipsoids inner and outer.
       inner and outer are given as matrices transforming the unit-sphere
       into the respective ellipsoids.
    """
    super (self, transform_map).__init__ (transformation, **kwarg)
    self.inner = inner
    self.outer = outer
  def calc_weight (self, coords):
    """calculate a weight for the given coordinates.
    """
    pass
  pass

class table_map (weight_map):
  """weight map that simply uses a stored array of values to deliver these
     as weight values.
  """
  def __init__ (self, table, **kwarg):
    """initialize a weight map given by a table.
       @param table is an tuple of two arrays of the same length:
       indexes and weights.
    """
    range = (min (table[0]), max (table[0]) + 1)
    super (self, table_map).__init__ (self, domain = range, **kwarg)
    self.table = table
