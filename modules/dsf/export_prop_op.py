import bpy

import dsf.prop_writer

class ExportDsfProp (bpy.types.Operator):
  """export a dsf prop file.
  """
  bl_idname = "export_scene.dsf_prop"
  bl_label = "Export Dsf Props"

  filepath = bpy.props.StringProperty\
    ('file path', description = 'file path of the .duf file')
  output_group = bpy.props.StringProperty\
    ('group', description = 'subdirectory for data directory')

  def execute (self, ctx):
    """export selected objects as dsf."""
    dsf.prop_writer.export_prop (ctx, self.filepath, self.output_group)
    return {'FINISHED'}

  def invoke (self, ctx, evt):
    """run the operator interactively.
    """
    ctx.window_manager.fileselect_add (self)
    return {'RUNNING_MODAL'}

def register ():
  bpy.utils.register_class (ExportDsfProp)

def unregister ():
  bpy.utils.unregister_class (ExportDsfProp)

def reload ():
  import imp
  import dsf.path_util, dsf.prop_writer, dsf.geom_create
  imp.reload (dsf.path_util)
  imp.reload (dsf.prop_writer)
  imp.reload (dsf.geom_create)
  unregister ()
  register ()
