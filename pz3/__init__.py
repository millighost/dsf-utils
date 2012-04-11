
bl_info = {
  'name': 'import pz3',
  'description': 'import a poser file',
  'author': 'millighost',
  'version': (1, 0),
  'blender': (2,5,6),
  'category': 'Import-Export',
  'warning': '',
  'wiki_url': 'http://www.google.com',
}

def import_blender_module ():
  """define register/unregister functions as well as an operator class
  """
  global register, unregister
  from pz3.blender_module import register
  from pz3.blender_module import unregister

# pull in the blender-addon symbols
try:
  import bpy
  import_blender_module ()
except:
  # not run from within blender; ignore.
  pass
