import os.path, itertools

# uv-data:
#   "layer-name": name of the blender uv-layer
#   "map-name": name of the blender uv-texture
#   "long-id": external id of the uv; must be unique within file.
#   "short-id": only the local id part (same as map-name?).
# geom-data:
#   "mesh-name": name of the mesh contained in the geometry-lib.
#   "node-name": name of the node contained in the geometry-lib.
#   +materials
# object-inst:
#   "dsf-name": name of the object in the scene-subset
#   "blender-name": name of the object in blender.
#   "geometry-id": name of the geometry to use
#   "node-id": name of the node to use
#   "uvs": name of the uvs (first is default/active).
# modifier-data:
#

def create_object_ids (objs):
  """create an id for each object suitable for usage in a scene-subset."""
  obj_ids = { obj: obj.name for obj in objs }
  return obj_ids

def get_uvs_for_object (obj):
  """create a list of uv-information for the given object.
     obj is a blender object (must be a mesh)."""
  mesh_name = obj.data.name
  layer_names = [uvl.name for uvl in obj.data.uv_layers]
  map_names = [uvt.name for uvt in obj.data.uv_textures]
  assert (len (layer_names) == len (map_names))
  uvs = []
  for (uvl, uvt) in itertools.zip_longest (layer_names, map_names):
    uv_record = {
      'type': 'uv',
      'layer_name': uvl,
      'map_name': uvt,
      'long_id': "%s-%s" % (obj.data.name, uvt),
      'short_id': uvt
    }
    uvs.append (uv_record)
  active_name = obj.data.uv_textures.active.name
  uvs.sort (key = lambda u: u['map_name'] != active_name)
  return uvs

def get_geom_for_object (obj):
  """return information about the data for the object obj (must be mesh)."""
  geom_rec = {
    'type': 'geom',
    'mesh_name': obj.data.name + '-g',
    'node_name': obj.data.name + '-n',
  }
  return geom_rec

def group_objects_by_mesh (objs):
  """group the objects by their equivalent meshes.
     within each group objects are guaranteed to have the same mesh.
     returns a dictionary: distinguished-object => list of objects
  """
  # dic: list of all objects
  dic = {}
  for obj in objs:
    if obj.type == 'MESH':
      key = (obj.data, len (obj.vertex_groups), len (obj.modifiers))
      # objects that have the same mesh, same number of vertex groups
      # and same number of modifiers go into the same group.
      if key not in dic:
        dic[key] = [obj]
      else:
        dic[key].append (obj)
  obj_dic = {}
  for (k, v) in dic.items ():
    obj_dic[v[0]] = v
  return obj_dic

class planner (object):
  def __init__ (self, **kwarg):
    self.opts = kwarg
  def plan (self, context):
    scene = context.scene
    objs = context.selected_objects
    # map a mesh-object to the list of object-instances:
    obj_group_dic = group_objects_by_mesh (objs)
    # determine base directory for data files
    data_dir = os.path.join ('/data', context.scene.dsf_category)
    data_file = os.path.join (data_dir, 'test.dsf')
    # determining file names:
    #   scene files (per object)
    #   geometry files (per mesh)
    #   modifier files (per mesh)
    #   uvset files (per mesh)
