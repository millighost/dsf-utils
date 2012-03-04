import itertools

def create_uv_layer (msh, name):
  """create a new uv layer and return its name.
  """
  uvlayer = msh.uv_textures.new (name = name)
  return uvlayer

def fill_uv_coords (uvlib, msh, uvl):
  """uvlib is an object that returns uv-coordinates.
     msh is a mesh data object.
     uvl is a uv-layer data object.
     uvl must have the same length as mesh.faces.
  """
  # should not be necessary, but who knows what bmesh is doing.
  assert (len (msh.faces) == len (uvl))
  for (mshface, uvface) in itertools.zip_longest (msh.faces, uvl):
    uvcoords = uvlib.get_uvs (mshface.index, mshface.vertices)
    assert (len (uvcoords) == 2 * len (mshface.vertices))
    uvface.uv_raw = uvcoords

class dsf_uvset_define (object):
  """class to define uvsets; mainly the define_uvset function is exported.
  """
  @classmethod
  def define_uvset (self, obj, uvlib):
    """uvlib is the object returned by the loader.
       uvlib must implement get_name() and get_uvs (face, verts).
    """
    msh = obj.data
    uvl = msh.uv_textures.new (uvlib.get_name ())
    fill_uv_coords (uvlib, msh, uvl.data)
