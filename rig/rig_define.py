import math, logging
import mathutils
import bpy

log = logging.getLogger ('rig-def')

def create_blender_armature (name, ctx):
  """create an empty armature data and object, put the armature
     into edit-mode and return the data object. The armature
     object will be the active object.
  """
  scene = ctx.scene
  armdat = bpy.data.armatures.new (name = name)
  armobj = bpy.data.objects.new (name = name, object_data = armdat)
  scene.objects.link (armobj)
  scene.objects.active = armobj
  armdat.show_axes = True
  return armobj

def transform_bone (orient, origin, bbone):
  """place and orient the blender bone bbone.
  """
  xyz_angles = [math.radians (angle) for angle in orient]
  orient_tf = mathutils.Euler (xyz_angles, 'XYZ').to_matrix ().to_4x4 ()
  bbone.transform (orient_tf)
  # somehow translating the bone with a combined matrix does not
  # work; the bone will always rotate a bit. So use the translate()-method.
  bbone.translate (mathutils.Vector (origin))

def insert_bone (si_bone, armdat):
  """insert the bone object into the armature data armdat and returns
     the created blender-bone.
     si_bone must provide these attributes:
     orientation, origin - basic position data of the bone used to create
       the transformation of the bone in armature-space.
  """
  b_bone = armdat.edit_bones.new (name = si_bone.get ('id'))
  orient = si_bone.get ('orientation')
  origin = si_bone.get ('origin')
  # create an initial orientation by setting the tail of
  # the bone to 0,1,0. This leaves the bone pointing in the y-orientation,
  # so the local space is the same as the global space.
  b_bone.head = (0, 0, 0)
  b_bone.tail = (0, si_bone.get ('length'), 0)
  transform_bone (orient, origin, b_bone)
  return b_bone
  
def insert_bones (si_arm, armdat):
  """traverse the bones of the armature in preorder (parent before
     children) and insert them into the armature data.
     Returns a mapping of the names of the inserted bones to their definition.
  """
  bone_mapping = dict ()
  # the parent queue holds bone-objects whose children still 
  # need to get created.
  parent_queue = [None]
  while len (parent_queue) > 0:
    parent = parent_queue.pop ()
    log.info ("inserting children of %s", parent)
    if parent is not None:
      parent_bbone = armdat.edit_bones[parent.get ('id')]
    else:
      parent_bbone = None
    children = list (si_arm.get_children (parent))
    for child in children:
      bbone = insert_bone (child, armdat)
      bbone.parent = parent_bbone
      bone_mapping[bbone.name] = child
    parent_queue.extend (children)
  return bone_mapping

def configure_bones (bone_mapping, armobj):
  """perform final fixups on the created bones.
  """
  pose_bones = armobj.pose.bones
  for (blender_bone_name, si_bone) in bone_mapping.items ():
    pbone = pose_bones[blender_bone_name]
    order = si_bone.get ('rotation_order')
    pbone.rotation_mode = order

def define_armature (si_arm, ctx):
  """create a blender-armature object from the given armature-data.
     blender-function.
     ctx is the context for defining the armature in.
  """
  armobj = create_blender_armature ('imported-arm', ctx)
  bpy.ops.object.mode_set (mode = 'EDIT')
  bone_map = insert_bones (si_arm, armobj.data)
  bpy.ops.object.mode_set (mode = 'OBJECT')
  configure_bones (bone_map, armobj)
  return armobj
