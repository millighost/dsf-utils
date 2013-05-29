import logging, json, os.path

import bpy
from bpy.props import StringProperty
from bpy.props import BoolProperty
from bpy.props import FloatProperty
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

def create_export_dic (context, filepath):
  """construct asset ids for the various things exported.
     returns a map: (type, object) -> (fileid)
     types: {geometry, instance, uv, morph}
  """
  libdir = context.scene.dsf_asset_dir
  # filepath is the filename chosen by the user.
  # construct a filename for the data-file:
  basename = os.path.basename (filepath)
  (basename_base, basename_ext) = os.path.splitext (basename)
  data_basename = basename_base + '.dsf'
  # construct the directory where all data files go:
  data_basedir = os.path.join ('/data', context.scene.dsf_category)
  data_id = os.path.join (data_basedir, data_basename)
  # if the scene is to be saved in the library, use a library-relative
  # id for the scene, else an absolute.
  scene_relpath = os.path.relpath (filepath, start = libdir)
  if scene_relpath[0] not in ['/', '.']:
    scene_id = os.path.join ('/', scene_relpath)
  else:
    scene_id = filepath
    log.warn ("writing scene-files outside of library not supported.")
  export_objs = get_selected_objects (context)
  export_objs_grouped = dsf_geom_create.group_objects_by_mesh (export_objs)
  export_dic = {}
  for objs in export_objs_grouped:
    export_dic[('geometry', objs[0])] = data_id
    for obj in objs:
      export_dic[('instance', obj)] = scene_id
  return export_dic

def construct_datapath (basedir, subdir, filename):
  (basename, suffix) = os.path.splitext (filename)
  return os.path.join ('/data', subdir, basename + '.dsf')

def export_dsf_prop_file (context, basedir, subdir, filepath):
  """main function for exporting a prop something.
     Called after the user has selected some filename.
  """
  # basedir/data/subdir/filename: geometry file
  # basedir/data/subdir/UV Sets: extra uvs
  # basedir/data/subdir/Morphs: extra morphs
  # filename: main-scene file
  export_dic = create_export_dic (context, filepath)
  export_scale = context.scene.dsf_scale
  jdata_dic = dsf_prop_write.create_assets\
    (export_dic, export_scale = export_scale)
  dsf_prop_write.write_assets (jdata_dic, context.scene.dsf_asset_dir)

# the rest defines the gui and the blender operator
class export_dsf_prop (bpy.types.Operator):
  """Export a set of objects as dsf files."""
  # the doc text is displayed in the tooltip of the menu entry.
  # the bl_label is displayed in the operator-menu (with space-KEY).
  bl_label = 'export dsf-prop'
  # the bl_idname member is used by blender to call this class.
  bl_idname = 'export.dsfp'
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
    export_dsf_prop_file (context, base_dir, sub_dir, filename)
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
    col.operator ('export.dsfp')

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
  bpy.utils.register_class (export_dsf_prop)
  bpy.utils.register_class (dsf_prop_panel)

def unregister ():
  unregister_scene_props ()
  bpy.utils.unregister_class (dsf_prop_panel)
  bpy.utils.unregister_class (export_dsf_prop)
