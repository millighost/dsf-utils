import logging, json

log = logging.getLogger ('write-prop-dsf')

from . import dsf_linker
from . import dsf_geom_create
from . import dsf_scene_create

def choose_data_file (scene_file):
  """determine a suitable datafile name for the given scene file.
  """
  return "datafile.dsf"

def create_geometry_content (obj, linker, filename):
  """create the geometry content for a single object.
  """
  geom_creator = dsf_geom_create.geom_creator (linker)
  node_creator = dsf_geom_create.node_creator (linker)
  linker.push_context (filename)
  geom_jdata = geom_creator.create_geometry (obj)
  node_jdata = node_creator.create_node (obj)
  linker.pop_context ()
  return {
    'node_library': [ node_jdata ],
    'geometry_library': [ geom_jdata ]
  }

def create_node_instance_content (obj, linker, filename):
  """create a scene node instance for the given object.
  """
  scene_creator = dsf_scene_create.node_creator (linker)
  linker.push_context (filename)
  scene_jdata = scene_creator.create_node_instance (obj)
  linker.pop_context ()
  return scene_jdata

def create_data_content (objs, linker, filename):
  """create the content for the data file of a prop.
  """
  contents = []
  for obj in objs:
    contents.append (create_geometry_content (obj, linker, filename))
  return contents

def create_scene_content (objs, linker, filename):
  contents = []
  for obj in objs:
    contents.append (create_node_instance_content (obj, linker, filename))
  return contents

def write_objects (objs, filename):
  """main function for writing props.
  """
  linker = dsf_linker.linker ()
  # 1 determine filenames for data files
  data_filename = choose_data_file (filename)
  # 2 create assets for datafiles and scene
  d_jdata = create_data_content (objs, linker, data_filename)
  # 3 create the scene file
  s_jdata = create_scene_content (objs, linker, filename)
  # 4 link assets
  linker.resolve ()
  # 5 write files
  print (s_jdata)
  print (d_jdata)
