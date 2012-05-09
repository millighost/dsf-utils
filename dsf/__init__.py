# union module for inclusion of all dsf-related modules into
# one directory. This should be the only module directly
# included/executed from blender.
import logging

logging.basicConfig (level = logging.INFO)
log = logging.getLogger ('dsf')

try:
  import dsf.dsf_geom_import
  import dsf.dsf_morph_import
  import dsf.dsf_uvset_import
  import dsf.dsf_morph_export
  import dsf.dsf_arm_import
except ImportError as e:
  # if the error is something like 'no module named bpy', this
  # file is not included from within blender. Do not abort in this
  # case, because parts of this module are still useful.
  if str (e).index ('bpy') >= 0:
    log.warn ("import error ignored: %s", e)
  else:
    raise


bl_info = {
  'name': 'dsf-utils',
  'description': 'scripts for dsf files.',
  'author': 'millighost',
  'version': (1, 0),
  'blender': (2,6,3),
  'category': 'Import-Export',
  'warning': '',
  'wiki_url': 'http://nonexistent',
}

def register ():
  """call register functions of the submodules.
  """
  dsf_geom_import.register ()
  dsf_morph_import.register ()
  dsf_morph_export.register ()
  dsf_uvset_import.register ()
  dsf_arm_import.register ()

def unregister ():
  """call unregister functions of the submodules in
     reverse order.
  """
  dsf_uvset_import.unregister ()
  dsf_morph_export.unregister ()
  dsf_morph_import.unregister ()
  dsf_geom_import.unregister ()
  dsf_arm_import.unregister ()
