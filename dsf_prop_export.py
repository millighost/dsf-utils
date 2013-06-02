import logging, json, os.path

import bpy
from bpy.props import StringProperty
from bpy.props import BoolProperty
from bpy.props import FloatProperty

from . import dsf_prop_create
from . import dsf_geom_create
from . import dsf_prop_write

log = logging.getLogger ('export-prop-dsf')

bl_info = {
  'name': 'export dsf prop',
  'description': 'export dsf prop file',
  'author': 'millighost',
  'version': (1, 0),
  'blender': (2,6,3),
  'category': 'Import-Export',
  'warning': '',
  'wiki_url': 'http://nonexistent',
}

def get_selected_objects (context):
  """return the selected meshes.
  """
  return [obj for obj in context.selected_objects if obj.type == 'MESH']

def construct_datapath (basedir, subdir, filename):
  (basename, suffix) = os.path.splitext (filename)
  return os.path.join ('/data', subdir, basename + '.dsf')

class export_props (bpy.types.Operator):
  """export some objects as a scene subset and a data file.
     internal operator that has no user interface."""
  bl_options = { 'INTERNAL' }
  bl_idname = 'dsf.export_props'
  bl_label = 'export dsf-props'
  scene_path = StringProperty\
    (name = 'scene path', description = 'file path of the scene-subset.',
     maxlen = 1000, default = '')
  data_path = StringProperty\
    (name = 'scene path', description = 'file path of the data-definition.',
     maxlen = 1000, default = '')
  base_dir = StringProperty\
    (name = 'library directory',
     description = 'base directory of scene and data.',
     subtype = 'DIR_PATH', maxlen = 1000, default = '')
  scale = FloatProperty\
    (name = 'Scale Factor', subtype = 'FACTOR',
     default = 1, min = 0, max = 1000, precision = 0,
     description = 'scale to apply when using transformation')
  def execute (self, context):
    """export the currently selected objects to an external file.
    """
    scene_path = self.properties.scene_path
    data_path = self.properties.data_path
    scale = self.properties.scale
    base_dir = self.properties.base_dir
    objs = get_selected_objects (context)
    exporter = dsf_prop_create.prop_exporter\
      (scene_path = scene_path, data_path = data_path, scale = scale,
       base_dir = base_dir)
    exporter.export_props (objs)
    log.info ("export: %d objects to %s/%s, scale=%f",
              len (objs), scene_path, data_path, scale)
    return {'FINISHED'}

# the rest defines the gui and the blender operator
class export_dsf_prop (bpy.types.Operator):
  """Export a set of objects as dsf files."""
  # the doc text is displayed in the tooltip of the menu entry.
  # the bl_label is displayed in the operator-menu (with space-KEY).
  bl_label = 'export dsf-prop'
  # the bl_idname member is used by blender to call this class.
  bl_idname = 'dsf.export_prop'
  # the filepath seems to be hidden magic; the file-selector
  # menu places the chosen filename-string into it.
  # (changes sometimes; look for path/dirname/filepath)
  filepath = StringProperty\
      (name = 'file path', description = 'file path for exporting dsf-file.',
       maxlen = 1000, default = '')
  directory = StringProperty\
      (name = 'directory', description = 'directory for exporting dsf-file.',
       maxlen = 1000, default = '')
  filter_glob = StringProperty (default = '*.*')

  def execute (self, context):
    """display the gui and load a file. This function should be
       called after the menu entry for the file is selected."""
    # call the main import function. This function should work
    # independent of this context-manager/operator logic.
    filename = self.properties.filepath
    base_dir = context.scene.dsf_asset_dir
    sub_dir = context.scene.dsf_category
    scale = context.scene.dsf_scale
    bpy.ops.dsf.export_props\
      (scene_path = 'a.duf', data_path = 'b.dsf', scale = scale)
    return { 'FINISHED' }

  def invoke (self, context, event):
    """The invoke function should be called when the menu-entry for
       this operator is selected. It displays a file-selector and
       waits for execute() to be called."""
    combined_path = os.path.join\
      (context.scene.dsf_asset_dir, context.scene.dsf_category)
    self.properties.directory = combined_path
    context.window_manager.fileselect_add (self)
    return {'RUNNING_MODAL'}

class dsf_prop_panel (bpy.types.Panel):
  """display a panel to save props.
  """
  bl_label = 'DSF Utils'
  bl_space_type = 'VIEW_3D'
  bl_region_type = 'TOOLS'
  def draw (self, context):
    """draw the panel.
    """
    layout = self.layout
    col = layout.column (align = True)
    col.label (text = "DSF Prop")
    col.prop (context.scene, 'dsf_asset_dir')
    col.prop (context.scene, 'dsf_category')
    col.prop (context.scene, 'dsf_scale')
    col.operator ('dsf.export_prop')

def register_scene_props ():
  # register scene properties:
  # - a base directory containing the content directory
  # - subdirectory within it (creator/item)
  bpy.types.Scene.dsf_asset_dir\
    = StringProperty (subtype = 'DIR_PATH', name = 'Content Directory',
                      default = '/home/rassahah/daz',
                      description = 'Location to save DSF files to.')
  bpy.types.Scene.dsf_category\
    = StringProperty (name = 'Creator/Item',
                      default = 'test',
                      description = 'Creator specific directory.')
  bpy.types.Scene.dsf_scale\
    = FloatProperty (name = 'Scale Factor', subtype = 'FACTOR',
                     default = 1, min = 0, max = 1000, precision = 0,
                     description = 'scale to apply when using transformation')
def unregister_scene_props ():
  del bpy.types.Scene.dsf_asset_dir
  del bpy.types.Scene.dsf_category
  del bpy.types.Scene.dsf_scale

def register ():
  register_scene_props ()
  bpy.utils.register_class (export_props)
  bpy.utils.register_class (export_dsf_prop)
  bpy.utils.register_class (dsf_prop_panel)

def unregister ():
  unregister_scene_props ()
  bpy.utils.unregister_class (dsf_prop_panel)
  bpy.utils.unregister_class (export_dsf_prop)
  bpy.utils.unregister_class (export_props)
