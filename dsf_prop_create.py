
from . import dsf_asset_create
from . import dsf_geom_create

class prop_creator (object):
  """creating props from objects.
  """
  def __init__ (self, linker):
    self.linker = linker
  def create_prop (self, obj, datapath):
    """create a prop data from a blender object (must be a mesh-like object).
       returns the complete data-dsf file.
       @todo: do the uv-mapping also here.
    """
    self.linker.push_context (datapath)
    asset_creator = dsf_asset_create.asset_creator (self.linker)
    geom_creator = dsf_geom_create.geom_creator (self.linker)
    node_creator = dsf_geom_create.node_creator (self.linker)
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
