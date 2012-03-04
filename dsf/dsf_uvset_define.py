
#format:
# 'uvs' { 'count': int, 'values': [ (triples) ] }
# 'polygon_vertex_indices' [ (triple: fidx, vidx, uvidx) ]
# 'vertex_indices': [ int ]
# 'id': string

class dsf_uvset_define (object):
  """class to define uvsets; mainly the define_uvset function is exported.
  """
  @classmethod
  def define_uvset (self, obj, uvlib):
    """uvlib is the object returned by the loader.
       (currently it simply contains the uv_set_library from the dsf).
    """
    pass
