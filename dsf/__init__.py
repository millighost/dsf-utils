# union module for inclusion of all dsf-related modules into
# one directory. This should be the only module directly
# included/executed from blender.
import logging

import dsf.dsf_geom_import
import dsf.dsf_morph_import
import dsf.dsf_morph_export

logging.basicConfig (level = logging.INFO)

bl_info = {
  'name': 'dsf-utils',
  'description': 'scripts for dsf files.',
  'author': 'millighost',
  'version': (1, 0),
  'blender': (2,5,8),
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

def unregister ():
  """call unregister functions of the submodules in
     reverse order.
  """
  dsf_morph_export.unregister ()
  dsf_morph_import.unregister ()
  dsf_geom_import.unregister ()
