# skeleton (example) file for importing stuff into blender.
import sys, os.path, logging
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import BoolProperty, StringProperty

log = logging.getLogger ('import_skel')

bl_info = {
  'name': 'import skel',
  'description': 'import skeleton file',
  'author': 'millighost',
  'version': (1, 0),
  'blender': (2,5,8),
  'category': 'Import-Export',
  'warning': '',
  'wiki_url': 'http://nonexistent',
}

def import_skel_file (filename, context = None):
  """main function for importing something. Called after the user
     has selected some filename.
  """
  # if the to be loaded file affects the currently selected object,
  # use this to get it:
  active_obj = context.active_object
  log.info ("active object is %s", active_obj.name)
  log.info ("importing file %s", filename)

# the rest defines the gui and the blender operator
class import_skel (bpy.types.Operator):
  """Load something."""
  # the doc text is displayed in the tooltip of the menu entry.
  # the bl_label is displayed in the operator-menu (with space-KEY).
  bl_label = 'import skel'
  # the bl_idname member is used by blender to call this class.
  bl_idname = 'import.skel'
  # the filepath seems to be hidden magic; the file-selector
  # menu places the chosen filename-string into it.
  # (changes sometimes; look for path/dirname/filepath)
  filepath = StringProperty\
      (name = 'file path', description = 'file path for importing skel-file.',
       maxlen = 1000, default = '')
  filter_glob = StringProperty (default = '*.*')

  def execute (self, context):
    """display the gui and load a file. This function should be
       called after the menu entry for the file is selected."""
    # call the main import function. This function should work
    # independent of this context-manager/operator logic.
    filename = self.properties.filepath
    log.info ("user selected %s", filename)
    import_skel_file (filename, context = context);
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
  self.layout.operator (import_skel.bl_idname, text = 'skel-fileimport')

def register ():
  """add an operator for importing dsf-files and
     registers a menu function for it."""
  bpy.utils.register_module (__name__)
  bpy.types.INFO_MT_file_import.append (menu_func)

def unregister ():
  """remove the operator for importing dsf-files."""
  bpy.utils.unregister_module (__name__)
  bpy.types.INFO_MT_file_import.remove (menu_func)

logging.basicConfig (level = logging.INFO)
