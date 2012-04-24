# module for importing cr2 stuff into blender.
import logging

logging.basicConfig (level = logging.INFO)
log = logging.getLogger ('cr2')

try:
  import rig.cr2_armature_import
except ImportError as e:
  # if the error is something like 'no module named bpy', this
  # file is not included from within blender. Do not abort in this
  # case, because parts of this module are still useful.
  if str (e).index ('bpy') >= 0:
    log.warn ("import error ignored: %s", e)
  else:
    raise

bl_info = {
  'name': 'cr2-utils',
  'description': 'scripts for cr2 files.',
  'author': 'millighost',
  'version': (1, 0),
  'blender': (2,6,2),
  'category': 'Import-Export',
  'warning': '',
  'wiki_url': 'http://nonexistent',
}

def register ():
  """call register functions of the submodules.
  """
  cr2_armature_import.register ()

def unregister ():
  """call unregister functions of the submodules in
     reverse order.
  """
  cr2_armature_import.unregister ()

