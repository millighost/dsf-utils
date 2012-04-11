import sys, os.path

from bpy_extras.io_utils import ImportHelper
from bpy.props import BoolProperty, StringProperty
import bpy

def import_pz3_file (filename, props):
  """load the pz3-file and create a return the model.
     Props is a list containing flags to be set.
  """
  import pz3.input
  pz3data = pz3.input.read_pz3_data (filename)

# define a blender operator that gets called when the import function
# is activated.
class import_pz3 (bpy.types.Operator):
  # the doc text is displayed in the tooltip of the menu entry.
  """Load a poser pz3 file."""
  # the bl_label is displayed in the operator-menu (with space-KEY).
  bl_label = 'import pz3'
  # the bl_idname member is used by blender to call this class.
  bl_idname = 'import.pz3'
  # the filepath seems to be hidden magic; the file-selector
  # menu places the chosen filename-string into it.
  # (changes sometimes; look for path/dirname/filepath)
  filepath = StringProperty\
      (name = 'file path', description = 'file path for importing pz3-file.',
       maxlen = 1000, default = '')
  filter_glob = StringProperty (default = '*.cr2')

  def execute (self, context):
    """display the gui and load a file. This function should be
       called after the menu entry for the file is selected."""
    import_props = { }
    print ("execute (path = {0}, kwargs = {1})".format\
             (self.properties.filepath, str (import_props)))
    # call the main import function. This function should work
    # independent of this context-manager/operator logic.
    import_pz3_file (self.properties.filepath, import_props)
    return {'FINISHED'}
  def invoke (self, context, event):
    """The invoke function should be called when the menu-entry for
       this operator is selected. It displays a file-selector and
       waits for execute() to be called."""
    print ("invoke called.")
    context.window_manager.fileselect_add (self)
    return {'RUNNING_MODAL'}

def menu_func (self, context):
  """display the menu entry for calling the importer."""
  # the first parameter is the operator to call (by its bl_idname),
  # the text parameter is displayed in the menu.
  self.layout.operator (import_pz3.bl_idname, text = 'pz3-file (.cr2)')

def register ():
  """add an operator for importing pz3-files and
     registers a menu function for it."""
  bpy.utils.register_class (import_pz3)
  bpy.types.INFO_MT_file_import.append (menu_func)

def unregister ():
  """remove the operator for importing pz3-files."""
  bpy.utils.unregister_class (import_pz3)
  bpy.types.INFO_MT_file_import.remove (menu_func)


