import json
from array import array

class dsf_geom_load (object):
  def __init__ (self):
    pass

  @classmethod
  def intern_geometry (self, jdata):
    v = array ('f')
    f = list ()
    m = array ('i')
    g = array ('i')
    for vertex in jdata['vertices']['values']:
      v.extend (vertex)
    group_list = jdata['polygon_groups']['values']
    mat_list = jdata['polygon_material_groups']['values']
    for polygon in jdata['polylist']['values']:
      (gidx, midx, verts) = (polygon[0], polygon[1], polygon[2:])
      f.append (verts)
      m.append (midx)
      g.append (gidx)
    return {
      'v': v, 'g': g, 'm': m, 'f': f,
      'gm': group_list, 'mm': mat_list
    }

  @classmethod
  def load_geometry (self, filename, feats = ['vt', 'g', 'm']):
    """create a model from the json-data in jdata.
       g - include face-groups
       m - include materials
    """
    jdata = json.load (open (filename, 'r', encoding = 'latin1'))
    geom = self.intern_geometry\
        (jdata['geometry_library'][0])
    geom['id_path'] =\
        jdata['asset_info']['id'] + "#" + jdata['node_library'][0]['id']
    return geom

  @classmethod
  def load_file (self, filename):
    geom_data = self.load_geometry (filename)
    return geom_data
  genesis = '/images/winshare/dsdata4/data/DAZ 3D/Genesis/Base/Genesis.dsf'

