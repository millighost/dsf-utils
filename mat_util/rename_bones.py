import bpy
import re
from array import array

bl_info = {
  'name': 'rename bones',
  'description': 'rename bones in an armature',
  'author': 'millighost',
  'version': (1, 0),
  'blender': (2,6,0),
  'category': 'Material',
  'warning': '',
  'wiki_url': 'http://www.google.com',
}

class rename_bones (bpy.types.Operator):
  bl_idname = "rename_bones.op"
  bl_label = "rename-bones"
  # properties for which it could be useful to reuse them.
  # todo: look into the presets thing.
  prop_pattern = bpy.props.StringProperty ("pattern")
  prop_replace = bpy.props.StringProperty ("replacement")
  def __init__ (self, *arg, **kwarg):
    super (rename_bones, self).__init__ (*arg, **kwarg)

  def execute (self, ctx):
    try:
      regex = re.compile (str (self.prop_pattern))
    except re.error as ex:
      self.report ({'ERROR'}, "invalid regex.")
      return {'CANCELLED'}
    repl = str (self.prop_replace)
    obj = ctx.scene.objects.active
    if obj is None or obj.type != 'ARMATURE':
      self.report ({'ERROR'}, "active armature required.")
      return {'CANCELLED'}
    elif obj.mode != 'EDIT':
      self.report ({'ERROR'}, "armature must be in edit-mode")
      return {'CANCELLED'}
    else:
      arm = obj.data
      self.rename_bones (arm, regex, repl)
      return {'FINISHED'}

  def invoke (self, ctx, event):
    wm = ctx.window_manager
    return wm.invoke_props_dialog (self)

  def single_replace (self, regex, repl, subj):
    """subj is a string to which apply the replacement regex->repl.
       returns the modified string.
    """
    replaced = regex.sub (repl, subj)
    return replaced

  def rename_bones (self, arm, regex, repl):
    """apply the replacement regex->repl to each selected bone of
       the armature arm. arm must be in edit-mode.
    """
    for bone in filter (lambda bone: bone.select, arm.edit_bones):
      new_name = self.single_replace (regex, repl, bone.name)
      if new_name != bone.name:
        bone.name = new_name

def register ():
  bpy.utils.register_class (rename_bones)

def unregister ():
  bpy.utils.unregister_class (rename_bones)
