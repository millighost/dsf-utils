import bpy
import re
from array import array

# an operator to remove empty groups or groups with only zero weights.

bl_info = {
  'name': 'remove empty groups',
  'description': 'remove groups that are empty or have zero weight',
  'author': 'millighost@googlemail.com',
  'version': (1, 0),
  'blender': (2,6,0),
  'category': 'Mesh',
  'warning': '',
  'wiki_url': 'http://www.google.com',
}

class remove_empty_groups (bpy.types.Operator):
  bl_idname = "wm.remove_empty"
  bl_label = "remove-empty-groups"

  def __init__ (self, *arg, **kwarg):
    super (remove_empty_groups, self).__init__ (*arg, **kwarg)
  def execute (self, ctx):
    """remove empty groups of all selected objects.
    """
    for obj in [obj for obj in ctx.scene.objects if obj.select and obj.type]:
      self.remove_empty_groups_obj (obj)
    return {'FINISHED'}
  def remove_empty_groups_obj (self, obj):
    """remove empty groups from the given obj.
    """
    used = self.get_used_groups (obj)
    remove_set = set ()
    for group in obj.vertex_groups:
      if group.index not in used:
        remove_set.add (group)
    for group in remove_set:
      obj.vertex_groups.remove (group)
  @classmethod
  def get_used_groups (self, obj):
    """returns a set of all used used groups of the given object.
       the returned set contains the indices of the groups.
    """
    used_groups = set ()
    for vertex in obj.data.vertices:
      for vgroup in vertex.groups:
        if vgroup.weight > 0:
          used_groups.add (vgroup.group)
    return used_groups

def register ():
  bpy.utils.register_class (remove_empty_groups)

def unregister ():
  bpy.utils.unregister_class (remove_empty_groups)
