import math, mathutils, collections

from . import dsf_asset_create
from . import dsf_geom_create

class prop_creator (object):
  """creating props from objects.
  """
  def __init__ (self, scene = None, reorient = False, scale = 1, **kwarg):
    self.export_opts = kwarg
    self.scene = scene
    self.scale = scale
    self.reorient = reorient

  @classmethod
  def generate_geom_ids (self, objs):
    """generate ids for the geometry-lib entries of the objects in objs.
       The objects in objs must be distinct.
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
       The objects are given as the keys of the obj_map. The ids
       are the values of obj-map.
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
  for (obj, id) in obj_map.items ():
    geoms.append (geom_creator.create_geometry (obj, id))
    nodes.append (node_creator.create_node (obj, id))
  jdata = {
    'node_library': nodes,
    'geometry_library': geoms
  }
  return jdata

  def create_prop (self, obj, datapath):
    """create a prop data from a blender object (must be a mesh-like object).
       returns the complete data-dsf file.
       @todo: do the uv-mapping also here.
    """
    if self.scale == 1:
      transform = mathutils.Matrix.Identity (3)
    else:
      transform = self.scale\
        * mathutils.Euler ([-math.pi/2, 0, 0], 'XYZ').to_matrix ()
    asset_creator = dsf_asset_create.asset_creator ()
    geom_creator = dsf_geom_create.geom_creator\
      (scene = self.scene, transform = transform)
    node_creator = dsf_geom_create.node_creator (**self.export_opts)
    uv_creator = dsf_geom_create.uv_creator ()
    jdata = {
      'file_version': '0.6.0.0',
    }
    jdata['asset_info'] = asset_creator.create_asset_info (datapath)
    jdata['geometry_library'] = [
      geom_creator.create_geometry (obj)
    ]
    jdata['node_library'] = [
      node_creator.create_node (obj)
    ]
    return jdata
