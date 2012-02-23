import sys, os, math, re
import mathutils, bpy

import pz3.input

# mathutils used:
# Vector, Euler, Matrix.Translation, Matrix.Rotation, Matrix.Scale

def named_axis (letter):
  """return the named vector (x, y, z).
  """
  lc_letter = letter.lower ()
  if lc_letter == 'x':
    return mathutils.Vector ((1, 0, 0))
  elif lc_letter == 'y':
    return mathutils.Vector ((0, 1, 0))
  elif lc_letter == 'z':
    return mathutils.Vector ((0, 0, 1))
  else:
    raise KeyError ("invalid axis-letter '%s'." % (letter))

def strip_bone_suffix (name):
  """strip the ':<number>' suffix found often in actor names.
  """
  mat = re.match ('^(.*):\\d+$', name)
  if mat is not None:
    return mat.group (1)
  else:
    return name

class bone (object):
  """a class to represent a single bone of an armature.
     This class should not be blender dependent, but uses mathutils
     to perform some geometric transformations.
  """
  @classmethod
  def calc_rotation_order (self, node):
    """get the rotation order string from node.
       This looks into the channels-attribute and collects the
       order of the various rotate[XYZ] channels.
       @property origin: 3d-vector
       @property endpoint: 3d-vector
       @property orientation euler-triple(xyz)
       @property ref_name string (the parameter of the 'actor')
       @property int_name string (the name of the 'actor' without suffix)
       @property dis_name string (display-name; the name within the actor)
       @property reference to parent bone.
       @property children list of references to child bones.
       @property rotation_order string 'XYZ' for rot order
         (determined from channels).
       @property local_transform (private)
       @property armature_transform (local to global tf)
    """
    keys = node['channels'].keys ()
    rotates = [key[-1] for key in keys if key.startswith ('rotate')]
    order = "".join (rotates)
    assert (len (order) == 3)
    return order
  def __init__ (self, node):
    """create a bone from the 'actor'-attribute node.
    """
    self.origin = mathutils.Vector (node['origin'])
    self.endpoint = mathutils.Vector (node['endPoint'])
    self.orientation = node['orientation']
    # ref name is the name usually used for referencing the bone from
    # other parts of the model. It often has a ':123' suffix or similar.
    self.ref_name = node[0]
    # the ref name without the suffix is used for skinning.
    self.int_name = strip_bone_suffix (self.ref_name)
    # dis_name is the display name of the bone within a specific figure.
    # It is used only to be displayed to the user.
    self.dis_name = node['name'][0]
    self.parent = None
    self.children = list ()
    # pre-cache the rotation order and transformation.
    self.rotation_order = self.calc_rotation_order (node)
    self.local_transform = None # lazy
    self.armature_transform = None # lazy
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
  def get_weight_angle_func (self, axis):
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

class armature (object):
  """represent a complete skeleton for a figure given in a pz3 file.
     This class should not be dependent on blender, but uses mathutils
     to represent geometry.
  """
  def __init__ (self, figure_data, actors_map):
    """define the armature from the parsed data. actors are converted to
       bones.
    """
    self.bone_by_name = self.create_bone_map (figure_data, actors_map)
  @classmethod
  def create_bone_map (self, figure, actors):
    """create a map containing all bones that belong to the given
       figure-data-block.
       param figure figure-object of the pz3 file: pz3object.
       param actors actors-map of the pz3 file: map[string->pz3object].
    """
    # first collect all actors that belong to the figure by starting with
    # the root and adding all add-child statements.
    print ("actors:", actors.keys ())
    bone_by_name = dict ()
    root_name = figure['root'][0]
    bone_by_name[root_name] = bone (actors[root_name])
    for add_child in figure.get ('addChild'):
      child_name = add_child[0]
      if child_name in actors:
        # this condition is mainly to filter out any non-actor childs
        # from the figure. Usually there seem to be so-called
        # "GoalCenterMass" and similar objects in the figure, which
        # are not actors, but some hell-knows-what-they-are-good-for props.
        child_actor = actors[child_name]
        bone_by_name[child_name] = bone (child_actor)
    # make a second pass on the hierarchy to interconnect the bones.
    for add_child in figure.get ('addChild'):
      if add_child[0] in bone_by_name:
        # use only actors that are created as bones in the first pass
        # above.
        child_bone = bone_by_name[add_child[0]]
        parent_bone = bone_by_name[add_child[1]]
        child_bone.set_parent (parent_bone)
        parent_bone.add_child (child_bone)
    return bone_by_name
  def get_bone (self, name):
    """return the named bone.
    """
    return self.bone_by_name[name]

def create_blender_armature (name):
  """create an empty armature data and object, put the armature
     into edit-mode and return the data object. The armature
     object will be the active object.
     blender-function.
  """
  scene = bpy.context.scene
  armdat = bpy.data.armatures.new (name = name)
  armobj = bpy.data.objects.new (name = name, object_data = armdat)
  scene.objects.link (armobj)
  scene.objects.active = armobj
  bpy.ops.object.mode_set (mode = 'EDIT')
  # show axes for easier testing.
  armdat.show_axes = True
  return armdat

def insert_bones (si_bones, armdat):
  """insert the list of bones into the given armature-data block.
     Returns a mapping from bone-name to the corresponding bone.
     blender-function.
  """
  bone_mapping = dict ()
  for si_bone in si_bones:
    b_bone = armdat.edit_bones.new (name = si_bone.int_name)
    b_bone.head = (0, 0, 0)
    b_bone.tail = (0, 1, 0)
    armature_local_transform = si_bone.get_local_to_global_tf ()
    rename_mat = si_bone.order_rotation ()
    pre_orient_mat = si_bone.calc_pre_trans ()
    orient_mat = si_bone.get_local_to_global_rot ()
    b_bone.transform (orient_mat * pre_orient_mat)
    b_bone.translate (si_bone.origin)
    bone_mapping[si_bone.ref_name] = b_bone
  return bone_mapping

def build_hierarchy (si_arm, bone_map):
  """establish the parent-child-relationship of the bones.
     bone_map must be a dictionary mapping names of bones to edit-bones.
     si_arm is the armature-data containing initialized bone objects.
     blender-function.
  """
  for (bname, bobj) in bone_map.items ():
    si_bone = si_arm.bone_by_name[bname]
    if si_bone.parent is not None:
      parent_name = si_bone.parent.ref_name
      parent_bobj = bone_map[parent_name]
      bobj.parent = parent_bobj

def define_armature (si_arm):
  """create a blender-armature object from the given armature-data.
     blender-function.
  """
  armdat = create_blender_armature ('imported-arm')
  bmap = insert_bones (si_arm.bone_by_name.values (), armdat)
  build_hierarchy (si_arm, bmap)

class pz3scene (object):
  """represent the contents of a pz3-file (or cr2 file in this case).
  """
  def __init__ (self, pz3data):
    """initialize with the contents of a parsed pz3-file structure.
       pz3data can be the contents of a cr2 file, for example.
    """
    self.figures = self.get_figure_blocks (pz3data)
    self.actors = self.get_actor_blocks (pz3data)
  @classmethod
  def get_actor_blocks (self, pz3data):
    """find all actor blocks from the pz3ddata, and return a mapping
       from their refname to their data block.
       returns a dictionary string->pz3attribute.
    """
    actor_dic = dict ()
    for actor_block in pz3data.get ('actor'):
      actor_refname = actor_block[0]
      actor_dic[actor_refname] = actor_block
    return actor_dic
  @classmethod
  def get_figure_blocks (self, pz3data):
    """find all figure-blocks within the pz3data and return
       a mapping from the name of a figure to the associated figure-data-block.
    """
    figure_dic = dict ()
    for figure_block in pz3data.get ('figure'):
      figure_name = figure_block['name'][0]
      figure_dic[figure_name] = figure_block[-1]
    return figure_dic

def create_armature_data (pz3s):
  """create an system-indenpendent armature data object from
     the given pz3 scene. The scene should contain exactly one
     figure block.
     independent-function using mathutils.
  """
  assert (len (pz3s.figures) == 1)
  # dict-values do not allow for indexing, so use structured assign:
  (figure_data,) = pz3s.figures.values ()
  si_arm = armature (figure_data, pz3s.actors)
  return si_arm

def read_pz3_scene (filename):
  pz3d = pz3.input.read_pz3_data (filename)
  pz3s = pz3scene (pz3d)
  return pz3s

def main (argv):
  filename = os.getenv ('F')
  # define the system-independent armature
  pz3s = read_pz3_scene (filename)
  # create system-independent armature
  si_arm = create_armature_data (pz3s)
  # create blender armature.
  define_armature (si_arm)
  if '-b' in sys.argv:
    import code
    scene = bpy.context.scene
    ab = scene.objects.active
    ad = ab.data
    local_dic = dict (globals ())
    local_dic['p3d'] = pz3d
    local_dic['si'] = si_arm
    local_dic['scene'] = scene
    local_dic['ab'] = ab
    local_dic['ad'] = ad
    code.interact (local = local_dic)
  
if __name__ == '__main__':
  main (sys.argv)
