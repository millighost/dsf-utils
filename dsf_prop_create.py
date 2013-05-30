import math, mathutils, collections

from . import dsf_asset_create
from . import dsf_geom_create

class prop_creator (object):
  """creating props from objects.
  """
  def __init__ (self, scene = None, scale = 1, **kwarg):
    self.export_opts = kwarg
    self.scene = scene
    self.scale = scale

  @classmethod
  def generate_geom_ids (self, objs):
    """generate ids for the geometry-lib entries of the objects in objs.
       @todo: currently the objects in objs must be distinct.
    """
    id_dic = {}
    for obj in objs:
      geom_id = "%s-g" % (obj.name,)
      node_id = "%s-n" % (obj.name,)
      id_dic[obj] = (geom_id, node_id)
    return id_dic

  @classmethod
  def generate_export_mapping (self, objs):
    """sort the objects and their data for exporting.
    """
    obj_groups = dsf_geom_create.group_objects_by_mesh (objs)
    mesh_mapping = {}
    for obj_group in obj_groups:
      # use sample_obj as a representant for providing mesh-data for
      # every object in the group of objects.
      sample_obj = list (obj_group)[0]
      for obj in obj_group:
        mesh_mapping[obj] = sample_obj
    return mesh_mapping

  def create_geometry_libs (self, obj_map):
    """create the node-library and geometry-library for the objects.
       The objects are given as the keys of the obj_map.
       for each object in obj_map contains a tuple:
         (the id of the mesh, the id of the node).
    """
    if self.scale == 1:
      transform = mathutils.Matrix.Identity (3)
    else:
      transform = self.scale\
        * mathutils.Euler ([-math.pi/2, 0, 0], 'XYZ').to_matrix ()
    geom_creator = dsf_geom_create.geom_creator\
      (scene = self.scene, transform = transform)
    node_creator = dsf_geom_create.node_creator (**self.export_opts)
    geoms = []
    nodes = []
    for (obj, ids) in obj_map.items ():
      geom_id, node_id = ids
      geoms.append (geom_creator.create_geometry (obj, geom_id))
      nodes.append (node_creator.create_node (obj, node_id))
    jdata = {
      'node_library': nodes,
      'geometry_library': geoms
    }
    return jdata

  def create_data (self, obj_map, datapath):
    """create a prop data from a blender object (must be a mesh-like object).
       returns the complete data-dsf file.
       @todo: do the uv-mapping also here.
    """
    if self.scale == 1:
      transform = mathutils.Matrix.Identity (3)
    else:
      transform = self.scale\
        * mathutils.Euler ([-math.pi/2, 0, 0], 'XYZ').to_matrix ()
    # create: node_library, geometry_library
    geom_libs = jdata = self.create_geometry_libs (obj_map)
    # create: asset_info
    asset_creator = dsf_asset_create.asset_creator ()
    asset_info = asset_creator.create_asset_info (datapath)
    global_jdata = {
      'file_version': '0.6.0.0',
      'asset_info': asset_info,
    }
    jdata = geom_libs
    jdata.update (global_jdata)
    return jdata
