
from . import dsf_asset_create
from . import dsf_geom_create

class prop_creator (object):
  """creating props from objects.
  """
  def __init__ (self):
    pass
  def create_prop (self, obj):
    """create a prop data from a blender object (must be a mesh-like object).
    """
    asset_creator = dsf_asset_create.asset_creator ()
    geom_creator = dsf_geom_create.geom_creator ()
    node_creator = dsf_geom_create.node_creator ()
    jdata = {
      'file_version': '0.6.0.0',
    }
    jdata['asset_info'] = asset_creator.create_asset_info ()
    jdata['geometry_library'] = [
      geom_creator.create_geometry (obj)
    ]
    jdata['node_library'] = [
      node_creator.create_node (obj)
    ]
    return jdata
