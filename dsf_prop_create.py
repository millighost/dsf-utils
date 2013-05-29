import math, mathutils

from . import dsf_asset_create
from . import dsf_geom_create

class prop_creator (object):
  """creating props from objects.
  """
  def __init__ (self, linker, scene = None, reorient = False, scale = 1,
                **kwarg):
    self.linker = linker
    self.export_opts = kwarg
    self.scene = scene
    self.scale = scale
    self.reorient = reorient
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
    self.linker.push_context (datapath)
    asset_creator = dsf_asset_create.asset_creator (self.linker)
    geom_creator = dsf_geom_create.geom_creator\
      (self.linker, scene = self.scene, transform = transform)
    node_creator = dsf_geom_create.node_creator (self.linker, **self.export_opts)
    uv_creator = dsf_geom_create.uv_creator (self.linker)
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
    self.linker.pop_context ()
    return jdata
