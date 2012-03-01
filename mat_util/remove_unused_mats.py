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
    for obj in [obj for obj in ctx.scene.objects if obj.select]:
      self.remove_unused_mats_obj (obj)
    return {'FINISHED'}
  @classmethod
  def get_used_mat_indices (self, obj):
    """return a set of used material indices from the object obj.
       @todo: this currently works only for material indices referenced by
       mesh-data faces.
    """
    mats = set ()
    if obj.type == 'MESH':
      for face in obj.data.faces:
        mats.add (face.material_index)
    else:
      # @todo: if this is not a mesh, determine the used indices somehow else.
      mats = set (range (len (obj.material_slots)))
    return mats
  @classmethod
  def remove_unused_mats_obj (self, obj):
    """remove all unused material slots of a single object.
    """
    keep = self.compress_material_slots (obj)
    self.remove_unused_slots (obj, keep = keep)
  @classmethod
  def compress_material_slots (self, obj):
    """reassign all material indices, so that they are in the range 0 to N-1,
       with N being the number of used materials. This function returns the
       list of used material indices after its application.
    """
    used_indices = list (self.get_used_mat_indices (obj))
    used_indices.sort ()
    translate = array ('i', [0] * len (obj.material_slots))
    for (new_idx, old_idx) in enumerate (used_indices):
      translate[old_idx] = new_idx
      obj.material_slots[new_idx].material = obj.material_slots[old_idx].material
    for face in obj.data.faces:
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
