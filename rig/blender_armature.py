import mathutils

class bone (object):
  """a class to represent a single bone of an armature.
     This class should not be blender dependent, but uses mathutils
     to perform some geometric transformations. Upon initialization these
     properties must be given:
     @property id string (the parameter of the 'actor' in poser)
     @property head: 3d-vector
     @property orientation euler-triple(xyz)
     @property order string 'XYZ' for rot order

     optional properties; might be given or might be none or non-present:
     @property tail: 3d-vector if given, the general direction.
     @property name string (display-name; the name within the actor)
     @property parent reference to parent bone if given must be an id.

     calculated or cached (private use):
     @property children list of hard-references to child bones.
     @property parent hard-reference to parent bone
     @property local_transform (private)
     @property armature_transform (local to global tf)
  """
  def __init__ (self, **kwarg):
    """create a bone from the 'actor'-attribute node.
    """
    # required:
    self.id = kwarg['id']
    self.origin = kwarg['head']
    self.orientation = kwarg['orientation']
    self.order = kwarg['order']
    # optional:
    self.endpoint = kwarg.get ('tail')
    self.name = kwarg.get ('name') or self.id
    self.parent_id = kwarg.get ('parent')
    # private:
    self.children = list ()
    self.parent = None
    self.local_transform = None
    self.armature_transform = None

  def set_parent (self, other_bone):
    """set the parent bone of self.
    """
    assert (self.parent is None)
    self.parent = other_bone
  def add_child (self, other_bone):
    """add other bone to self.children.
    """
    self.children.append (other_bone)

  def get_local_to_global_rot (self):
    """return the local transformation (ie only the rotations).
       applying the rotation to a vector in bone-space gives the vector
       in worldspace minus the origin.
    """
    if self.local_transform is None:
      xyz_angles = [math.radians (angle) for angle in self.orientation]
      self.local_transform\
          = mathutils.Euler (xyz_angles, 'XYZ').to_matrix ().to_3x3 ()
    return self.local_transform

  def get_global_to_local_tf (self):
    """return a matrix that transforms from world to local coordinates.
    """
    # simply use the inverted here; stable would be: split the translation
    # part off and use transpose on the rest (transformation is normal).
    return mathutils.Matrix (self.get_local_to_global_tf ()).inverted ()
  def get_local_to_global_tf (self):
    """return the transformation (world, resp armature-local).
       Applying the transformation to a vector in bone-space, gives the
       vector in world (ie armature-) space.
    """
    if self.armature_transform is None:
      rot = self.get_local_to_global_rot ().to_4x4 ()
      trans = mathutils.Matrix.Translation (self.origin)
      self.armature_transform = trans * rot
    return self.armature_transform

  def descendant_length (self):
    """return the preferred of the twist-axis of self. When the twist-axis
       should point into negative direction, return the negative length.
    """
    # calculate the best target in bone-local space.
    if len (self.children) == 1:
      # if self has exactly one child bone, always use the child's
      # origin as the the target point
      target = mathutils.Vector (self.children[0].origin) - self.origin
      if target == self.origin:
        # the only child has the same origin as self. Use endpoint as a fallback.
        target = self.endpoint - self.origin
    elif len (self.children) == 0:
      # if no children are there, the only hint we can have is the endpoint
      # of self.
      target = mathutils.Vector (self.endpoint) - self.origin
    else:
      # for more than one child, check if there is any specific child
      # which is directly on the twist-axis.
      best_collin = self.find_best_collinear_child ()
      if best_collin is not None:
        target = best_collin.origin - self.origin
      else:
        children_origins = [c.origin for c in self.children]
        avg = sum (children_origins, mathutils.Vector ((0, 0, 0)))
        target = avg / len (children_origins) - self.origin
    # now we have target, a location that the twist-axis should at best
    # be pointing to in bone-space.
    if target == self.origin:
      # the twist should actually to the origin. Use the endpoint to bring
      # some more sense to it.
      target = self.endpoint - self.origin
    # use the target to find the approximate length and direction
    if target.length == 0:
      # length of 0 means: endpoint and all children are at the origin;
      # return a 1
      return 1
    else:
      twist_axis = named_axis (self.rotation_order[0])
      transformed_twist = self.get_local_to_global_rot () * twist_axis
      twist_angle = transformed_twist.angle (target)
      if math.degrees (twist_angle) < 90:
        return target.length
      else:
        return -target.length

  def distance_to (self, other):
    """return the distance to another bones origin.
    """
    return (self.origin - other.origin).length
  def find_best_collinear_child (self):
    """get the nearest child-bone that is on the twist axis. If there is
       no child on the twist-axis, return None. Returns a value relative
       to the origin.
    """
    collin_children = list ()
    for child in self.children:
      # only check for children that do not start at the same
      # position as self.
      if child.origin != self.origin and self.check_collinear (child):
        collin_children.append (child)
    if len (collin_children) == 0:
      return None
    else:
      # pick the child with the minimum distance to self.
      best = min (collin_children, key = self.distance_to)
      return best

  def check_collinear (self, other):
    """return true, if other bone is (with a small tolerance) on the
       twist-axis of self.
    """
    twist_axis = named_axis (self.rotation_order[0])
    transformed_twist = self.get_local_to_global_rot () * twist_axis
    other_local = other.origin - self.origin
    if other_local.length == 0:
      # the child starts at the same position as self.
      return True
    other_angle = math.degrees (transformed_twist.angle (other_local))
    if other_angle < 1 or other_angle > 179:
      # Angle to the child is close to 0 or close to 180; consider it being
      # on the twist-axis.
      return True
    else:
      return False
  rot_dic = {
    'XYZ': ((-90, 'Z'), (-90, 'X'), '+'),
    'XZY': ((-90, 'Z'), (0, 'X'), '-'),
    'YZX': ((0, 'Z'), (0, 'X'), '+'),
    'YXZ': ((0, 'Z'), (90, 'Y'), '-'),
    'ZXY': ((90, 'X'), (90, 'Z'), '+'),
    'ZYX': ((90, 'X'), (180, 'Z'), '-'),
  }
  def order_rotation (self):
    """return a transformation that is to be applied before the normal
       bone orientation to rename axes according to the rotation order.
       The resulting orientation is always yzx.
       Returns a rotation matrix.
    """
    # contains two rotations for each orientation to transform that
    # orientation into yzx-order. The sign is '-' if that results in
    # an uneven orientation (which means, the x-axis is inverted).
    (r1, r2, sign) = self.rot_dic[self.rotation_order]
    r1_mat = mathutils.Matrix.Rotation (math.radians (r1[0]), 3, r1[1])
    r2_mat = mathutils.Matrix.Rotation (math.radians (r2[0]), 3, r2[1])
    rot_mat = r2_mat * r1_mat
    return rot_mat
  def calc_pre_trans (self):
    """use the orientation of self, and the descendants of self to
       to caclulate the transformation needed to align y to the twist-axis,
       z to the secondary rotation axis and scale the bone.
    """
    order_mat = self.order_rotation ()
    twist_length = self.descendant_length ()
    scale_mat = mathutils.Matrix.Scale (abs (twist_length), 3)
    if twist_length < 0:
      switch_mat = mathutils.Matrix.Rotation (math.radians (180), 3, 'Z')
    else:
      switch_mat = mathutils.Matrix.Rotation (math.radians (0), 3, 'Z')
    return order_mat * scale_mat * switch_mat
  def get_weight_angle_tf (self, axis):
    """return a transformation that is to be applied to a 3d-coordinate
       to calculate the angle-/twist falloff from.
    """
    # poser has a different notion of what angle should be 0 for each
    #   different rotation-axis:
    # for jointx: -z-axis is 0, ccw; ie project along x with y up.
    # for jointy: x-axis is 0, cw; ie project along -y with z up.
    # for jointz: x-axis is 0, ccw; ie project along z with y up.
    #
    # 1 transform from global coordinates to local
    # 2 transform the axes so that the x=0 constraint is met.
    local_transform = self.get_global_to_local_tf ()
    if axis.lower () == 'x':
      axis_transform = mathutils.Matrix.Rotation (math.radians (-90), 3, 'Y')
    elif axis.lower () == 'y':
      axis_transform = mathutils.Matrix.Rotation (math.radians (-90), 3, 'X')
    elif axis.lower () == 'z':
      axis_transform = mathutils.Matrix.Identity (3)
    else:
      raise KeyError ("invalid rotation axis: %s" % (axis))
    transform = axis_transform.to_4x4 () * local_transform
    return transform

  def get_weight_twist_func (self, axsi):
    """return a function that, when called with a coordinate in world-space
       returns a value in the axis-direction of this bone. This value can
       be used to apply twist-axis-weights.
    """
    transform = self.get_weight_angle_tf (axis)
    def transform_func (coords):
      # apply the transformation and then return the z-value.
      local_coords = transform * coords
      return local_coords[3]
  def get_weight_bend_func (self, axis):
    """return a function that, when called with a coordinate in world-space
       returns an angle between 0 and 360 which represents the angle used
       for angular falloff-zones (in local space). The transformed coordinate
       by that function has only x and y values with the positive x axis
       mapped to angle 0 degrees.
    """
    transform = self.get_weight_angle_tf (axis)
    def transform_func (coords):
      # apply the transformation to local space, rotate the axes
      # and finally return an angle between 0 and 360
      local_coords = transform * coords
      angle = math.degrees (math.atan2 (local_coords[1], local_coords[0]))
      if angle < 0:
        return angle + 360
      else:
        return angle
    return transform_func

