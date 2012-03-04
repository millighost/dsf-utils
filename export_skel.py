# skeleton (example) file for exporting stuff from blender.
import sys, os.path, logging
import bpy
from bpy.props import BoolProperty, StringProperty

log = logging.getLogger ('import_skel')

bl_info = {
  'name': 'export skel',
  'description': 'export skeleton file',
  'author': 'millighost',
  'version': (1, 0),
  'blender': (2,5,8),
  'category': 'Import-Export',
  'warning': '',
  'wiki_url': 'http://nonexistent',
}

def export_skel_file (filename, context = None):
  """main function for importing something. Called after the user
     has selected some filename.
  """
  # if the to be loaded file affects the currently selected object,
  # use this to get it:
  active_obj = context.active_object
  log.info ("active object is %s", active_obj.name)
  log.info ("exporting file %s", filename)

# the rest defines the gui and the blender operator
class export_skel (bpy.types.Operator):
  """Write something."""
  # the doc text is displayed in the tooltip of the menu entry.
  # the bl_label is displayed in the operator-menu (with space-KEY).
  bl_label = 'export skel'
  # the bl_idname member is used by blender to call this class.
  bl_idname = 'export.skel'
  # the filepath seems to be hidden magic; the file-selector
  # menu places the chosen filename-string into it.
  # (changes sometimes; look for path/dirname/filepath)
  filepath = StringProperty\
      (name = 'file path', description = 'file path for exporting skel-file.',
       maxlen = 1000, default = '')
  filter_glob = StringProperty (default = '*.*')

  def execute (self, context):
    """display the gui and load a file. This function should be
       called after the menu entry for the file is selected."""
    # call the main import function. This function should work
    # independent of this context-manager/operator logic.
    filename = self.properties.filepath
    log.info ("user selected %s", filename)
    export_skel_file (filename, context = context);
    return 'FINISHED'

  def invoke (self, context, event):
    """The invoke function should be called when the menu-entry for
       this operator is selected. It displays a file-selector and
       waits for execute() to be called."""
    context.window_manager.fileselect_add (self)
    return {'RUNNING_MODAL'}

def menu_func (self, context):
  """display the menu entry for calling the importer."""
  # the first parameter is the operator to call (by its bl_idname),
  # the text parameter is displayed in the menu.
  self.layout.operator (export_skel.bl_idname, text = 'skel-fileexport')

def register ():
  bpy.utils.register_module (__name__)
  bpy.types.INFO_MT_file_export.append (menu_func)

def unregister ():
  bpy.utils.unregister_module (__name__)
  bpy.types.INFO_MT_file_export.remove (menu_func)

logging.basicConfig (level = logging.INFO)
