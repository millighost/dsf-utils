import bpy
import re

# an operator to link materials of objects by name.
# e.g. if two objects have the materials named "material" and "material.001"
# this operation makes both of them refer to "material".

bl_info = {
  'name': 'link materials',
  'description': 'link materials by name',
  'author': 'millighost',
  'version': (1, 0),
  'blender': (2,6,0),
  'category': 'Material',
  'warning': '',
  'wiki_url': 'http://www.google.com',
}

class link_mats (bpy.types.Operator):
  bl_idname = "link_mats.op"
  bl_label = "link-materials-by-name"
  def __init__ (self, *arg, **kwarg):
    super (link_mats, self).__init__ (*arg, **kwarg)
    # create the regular expression for extracting the materials
    # basename. The basename is everything minus any
    # ':<number>' and '.<number>' suffix.
    self.mat_name_re = re.compile ("^(\\w+)(?:[.:](?:\\d+)*)$")
  def execute (self, ctx):
    active_obj = ctx.scene.objects.active
    for obj in self.get_selected_objects (ctx):
      if obj != active_obj:
        self.link_materials (active_obj, obj)
    return {'FINISHED'}
  def link_materials (self, src, dst):
    """copy materials matching names from src to dst.
    """
    # build a dictionary with material basename of src
    mat_dic = {
      self.mat_basename (mat): mat
      for mat in self.collect_materials (src)
    }
    # check the material of each material slot of the dst-object.
    # the slots material attribute gets assigned to the src-material
    # whenever the name matches.
    for dst_matslot in  dst.material_slots:
      dst_mat = dst_matslot.material
      if dst_mat is not None:
        dst_basename = self.mat_basename (dst_mat)
        if dst_basename in mat_dic:
          dst_matslot.material = mat_dic[dst_basename]
  @classmethod
  def get_selected_objects (self, ctx):
    """get the list of selected objects from the context.
    """
    return [obj for obj in ctx.scene.objects if obj.select]
  def mat_basename (self, mat):
    match = self.mat_name_re.match (mat.name)
    if match is not None:
      return match.group (1)
    else:
      return mat.name
  @classmethod
  def collect_materials (self, obj):
    """get the list of materials of the object.
    """
    mats = list ()
    for mslot in obj.material_slots:
      mat = mslot.material
      if mat is not None:
        mats.append (mat)
    return mats

def register ():
  bpy.utils.register_class (link_mats)

def unregister ():
  bpy.utils.unregister_class (link_mats)
