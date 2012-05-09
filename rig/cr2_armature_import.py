import sys, os.path, logging
import bpy
from bpy.props import StringProperty

import rig.import_rig

log = logging.getLogger ('import_cr2_arm')

class import_cr2_armature (bpy.types.Operator):
  # the doc text is displayed in the tooltip of the menu entry.
  """Load an armature from a poser cr2 figure file."""
  # the bl_label is displayed in the operator-menu (with space-KEY).
  bl_label = 'import cr2-armature'
  # the bl_idname member is used by blender to call this class.
  # it is also the name under which a callable function can be found
  # in bpy.ops.
  bl_idname = 'imp.cr2arm'

  # properties of this operator
  filepath = StringProperty\
      (name = 'file path', description = 'file path for importing cr2-file.',
       maxlen = 1000, default = '')
  filter_glob = StringProperty (default = '*.cr2')

  def execute (self, context):
    """display the gui and load a file. This function should be
       called after the menu entry for the file is selected."""
    # call the main import function. This function should work
    # independent of this context-manager/operator logic.
    rig.import_rig.import_cr2_rig (self.properties.filepath, context)
    return { 'FINISHED' }
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
  self.layout.operator\
      (import_cr2_armature.bl_idname, text = 'cr2-armature (.cr2)')

def register ():
  """add an operator for importing dsf-files and
     registers a menu function for it."""
  bpy.utils.register_class (import_cr2_armature)
  bpy.types.INFO_MT_file_import.append (menu_func)

def unregister ():
  """remove the operator for importing dsf-files."""
  bpy.utils.unregister_class (import_cr2_armature)
  bpy.types.INFO_MT_file_import.remove (menu_func)
