import sys, os.path, logging, json
import bpy

from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper

import dsf.dsf_weightmap

log = logging.getLogger ("dsf-wm-imp")

def load_mod_lib (filepath):
  """load the dsf file and return the modifier-library.
  """
  ifh = open (filepath, 'r')
  jdata = json.load (ifh)
  ifh.close ()
  if 'node_library' in jdata:
    # return the first modifier library.
    return jdata['modifier_library'][0]
  else:
    raise KeyError ("data does not contain modifier-library.")
def load_skin (filepath):
  """load the dsf file and return a skin.
  """
  jdata = load_mod_lib (filepath)
  skin = dsf.dsf_weightmap.skin (jdata['skin'])
  return skin

class import_dsf_wm (bpy.types.Operator):
  """operator to import a dsf armature.
  """
  bl_label = 'import dsf-wm'
  bl_idname = 'wm.dsf'

  filepath = StringProperty\
      ('file path', description = 'file path for dsf modifier-library.',\
         maxlen = 1000, default = '')
  filter_glob = StringProperty (default = '*.dsf')
  def define_wm (self, ctx, jdata):
    """weight paint a mesh based on the loaded data.
    """
    log.info ("define: %s", self.properties.filepath)
  def execute (self, ctx):
    """load the modifier-library and put in onto the mesh.
    """
    log.info ("loading: %s", self.properties.filepath)
    skin = load_skin (self.properties.filepath)
    self.define_wm (ctx, skin)
    return {'FINISHED'}
  def invoke (self, ctx, event):
    """called by the menu entry or the operator menu.
    """
    ctx.window_manager.fileselect_add (self)
    return {'RUNNING_MODAL'}

def menu_func (self, ctx):
  """render the menu entry.
  """
  self.layout.operator (import_dsf_wm.bl_idname, text = 'dsf-weightmap (.dsf)')

def register ():
  """add the operator to blender.
  """
  bpy.utils.register_class (import_dsf_wm)
  bpy.types.INFO_MT_file_import.append (menu_func)

def unregister ():
  """remove the operator from blender.
  """
  bpy.utils.unregister_class (import_dsf_wm)
  bpy.types.INFO_MT_file_import.remove (menu_func)

genesis = '/images/winshare/dsdata4/data/DAZ 3D/Genesis/Base/Genesis.dsf'
