import json, logging, random

log = logging.getLogger ('import_uvset')

#format:
# 'uvs' { 'count': int, 'values': [ (triples) ] }
# 'polygon_vertex_indices' [ (triple: fidx, vidx, uvidx) ]
# 'vertex_indices': [ int ]
# 'id': string
# assumption: vertex_indices contains indices into uvs-array for each vertex.
# @todo: check, if this is true.

class dsf_uvset (object):
  """class to get uv-coordinates from the dsf-data.
  """
  def __init__ (self, uvlib):
    """initialize with a given uv-library (a single item
       from the uv-set-library in the dsf.
    """
    self.name = uvlib['id']
  def get_name (self):
    """returns the name of the uvset.
    """
    return self.name
  def get_uvs (self, face, verts):
    """return a list of 2*len(verts) numbers representing
       the uv-coordinates of the given face.
    """
    return [random.random ()] * 2 * len (verts)

class dsf_uvset_load (object):
  """class to load data for definition of uvsets.
  """
  @classmethod
  def read_dsf_data (self, filename):
    """load the given filename, check it for a uvset and return
       the contents in some form usable for the definition function.
    """
    jdata = json.load (open (filename, 'r'))
    if 'uv_set_library' not in jdata:
      raise TypeError ('file does not contain a uv set library.')
    uvlibs = jdata['uv_set_library']
    if len (uvlibs) == 0:
      raise TypeError ('file does contain at least one uv set.')
    log.info ("found %d uv sets in %s", len (uvlibs), filename)
    return dsf_uvset (uvlibs[0])
