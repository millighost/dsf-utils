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
  def get_used_mat_indices (self, obj):
    """returns a set of all used material indices used by objs data.
       The mesh must be in edit mode.
    """
    if obj.type != 'MESH':
      # @todo: if this is not a mesh, determine the used indices somehow else.
      return set (range (len (obj.material_slots)))
    elif hasattr (obj.data, 'faces'):
      return self.count_material_indices (obj.data.faces).keys ()
    else:
      import bmesh
      bm = bmesh.new ()
      bm.from_mesh (obj.data)
      mat_counts = self.count_material_indices (bm.faces)
      bm.free ()
      return mat_counts.keys ()
  @classmethod
  def remove_unused_mats_obj (self, obj):
    """remove all unused material slots of a single object.
    """
    bpy.context.scene.objects.active = obj
    num_materials = self.compress_material_slots (obj)
    self.remove_material_slots\
        (obj, range (num_materials, len (obj.material_slots)))
  @classmethod
  def compress_material_slots (self, obj):
    """rearranges materials of obj in such a way that used materials come first,
       and after that unused materials. This number returns the number of
       used materials.
    """
    slots = obj.material_slots
    # get the used material indices;
    used_indices = list (self.get_used_mat_indices (obj))
    mapping = list (range (len (slots)))
    mapping.sort (key = lambda mi: mi not in used_indices)
    # now mapping contains for each material index the old index.
    # it needs to be the other way around, so transpose it
    transpose = [0] * len (mapping)
    for (new_idx, old_idx) in enumerate (mapping):
      transpose[old_idx] = new_idx
    # now apply the permutation transpose to the material-indices
    # and to the slots.
    if hasattr (obj.data, 'faces'):
      # old version for bpy meshes
      self.renumber_material_indices (transpose.__getitem__, obj.data.faces)
    else:
      import bmesh
      bm = bmesh.new ()
      bm.from_mesh (obj.data)
      self.renumber_material_indices (transpose.__getitem__, bm.faces)
      bm.to_mesh (obj.data)
    self.renumber_material_slots (transpose.__getitem__, slots)
    # todo: here any other reference to the material index should be
    # modified (for example strand-shader index).
    return len (used_indices)
  @classmethod
  def remove_material_slots (self, obj, removelist):
    """remove all material slots of obj that have an index in removelist.
       This function must be called in OBJECT mode.
    """
    # remove the material slots in reverse order so that the index
    # of the unprocessed slots does not change.
    sorted_remove = list (removelist)
    sorted_remove.sort (reverse = True)
    for idx in sorted_remove:
      obj.active_material_index = idx
      bpy.ops.object.material_slot_remove ()
  @classmethod
  def renumber_material_indices (self, mapping, faces):
    """mapping is a function taking an old material index and returning
       a new one. This mapping is applied to each face of the face-list.
    """
    for face in faces:
      old_idx = face.material_index
      new_idx = mapping (old_idx)
      if old_idx != new_idx and new_idx is not None:
        face.material_index = new_idx
  @classmethod
  def renumber_material_slots (self, mapping, slots):
    """mapping is a function taking an old material index and returning
       a new one. This function works like shuffling the material slots
       in place according to function.
    """
    # since there is no space to do an in-place-permutation, read out
    # the materials first, and then assign them to the slots.
    materials = [None] * len (slots)
    for index, slot in enumerate (slots):
      materials[mapping (index)] = slot.material
    for index, slot in enumerate (slots):
      slot.material = materials[index]

  @classmethod
  def count_material_indices (self, faces):
    """count the faces each material index has. Returns a
       sparse map (ie a dictionary) mapping from material index to
       number of faces that use the material index.
    """
    mapping = dict ()
    for face in faces:
      mat_idx = face.material_index
      face_count = mapping.setdefault (mat_idx, 0)
      mapping[mat_idx] = face_count + 1
    return mapping

def register ():
  bpy.utils.register_class (remove_unused_mats)

def unregister ():
  bpy.utils.unregister_class (remove_unused_mats)
