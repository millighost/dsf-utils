import bpy
import re
from array import array

# an operator to remove unreferenced materials from mesh object.

bl_info = {
  'name': 'remove unused materials',
  'description': 'remove materials unused by a mesh',
  'author': 'millighost',
  'version': (1, 0),
  'blender': (2,6,0),
  'category': 'Material',
  'warning': '',
  'wiki_url': 'http://www.google.com',
}

class remove_unused_mats (bpy.types.Operator):
  bl_idname = "remove_mats.op"
  bl_label = "remove-unused-mats"
  def __init__ (self, *arg, **kwarg):
    super (remove_unused_mats, self).__init__ (*arg, **kwarg)
  def execute (self, ctx):
    for obj in [obj for obj in ctx.scene.objects
                if obj.select and obj.type == 'MESH']:
      self.remove_unused_mats_obj (obj)
    return {'FINISHED'}
  @classmethod
  def get_used_mat_indices_bpy (self, obj):
    """return a set of used material indices from the object obj.
       this is the implementation for bpy-style meshes.
    """
    mats = set ()
    for face in obj.data.faces:
      mats.add (face.material_index)
    return mats
  @classmethod
  def get_used_mat_indices_bmesh (self, obj):
    """return a set of used material indices from the object obj.
       this is the implementation for bmesh-style meshes.
    """
    mats = set ()
    import bmesh
    bm = bmesh.from_edit_mesh (obj.data)
    for face in bm.faces:
      mats.add (face.material_index)
    return mats
  @classmethod
  def get_used_mat_indices (self, obj):
    if obj.type == 'MESH':
      return self.get_used_mat_indices_bmesh (obj)
    else:
      # @todo: if this is not a mesh, determine the used indices somehow else.
      return set (range (len (obj.material_slots)))
  @classmethod
  def remove_unused_mats_obj (self, obj):
    """remove all unused material slots of a single object.
    """
    bpy.context.scene.objects.active = obj
    bpy.ops.object.mode_set (mode = 'EDIT')
    keep = self.compress_material_slots (obj)
    bpy.ops.object.mode_set (mode = 'OBJECT')
    self.remove_unused_slots (obj, keep = keep)
  @classmethod
  def compress_material_slots (self, obj):
    """reassign all material indices, so that they are in the range 0 to N-1,
       with N being the number of used materials. This function returns the
       list of used material indices after its application.
       This function must be called in EDIT mode.
    """
    used_indices = list (self.get_used_mat_indices (obj))
    used_indices.sort ()
    translate = array ('i', [0] * len (obj.material_slots))
    for (new_idx, old_idx) in enumerate (used_indices):
      translate[old_idx] = new_idx
      obj.material_slots[new_idx].material = obj.material_slots[old_idx].material
    if True:
      import bmesh
      bm = bmesh.from_edit_mesh (obj.data)
      face_list = bm.faces
    else:
      # old version for bpy meshes
      face_list = obj.data.faces
    for face in face_list:
      old_idx = face.material_index
      new_idx = translate[old_idx]
      if old_idx != new_idx:
        face.material_index = new_idx
    # todo: here any other reference to the material index should be
    # modified (for example strand-shader index).
    for index in range (len (used_indices), len (obj.material_slots)):
      obj.material_slots[index].material = None
    return range (0, len (used_indices))
  @classmethod
  def remove_unused_slots (self, obj, keep = None):
    """remove all unused material slots obj. The argument keep, if given,
       contains a set of all material indices not to remove. If keep is
       None, it is calculated from the mesh-data. Either way, the material
       indices are renumbered after this function.
       This function must be called in OBJECT mode.
    """
    if keep is None:
      keep = self.get_used_mat_indices (obj)
    for idx in range (len (obj.material_slots) - 1, -1, -1):
      if idx not in keep:
        obj.active_material_index = idx
        bpy.ops.object.material_slot_remove ()

def register ():
  bpy.utils.register_class (remove_unused_mats)

def unregister ():
  bpy.utils.unregister_class (remove_unused_mats)
