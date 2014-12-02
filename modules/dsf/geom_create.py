import itertools, copy, logging
import math, mathutils

from . import dsf_data

log = logging.getLogger ('geom-create')

class geom_creator (object):
  """class to create dsf-geometry items from meshes.
  """
  def __init__ (self, scene = None, transform = None, **kwarg):
    """create an instance. This constructor should set some default arguments.
       scene: set to a scene object (for to_mesh); required for applying
        modifiers on export. If unset only the data is being used.
       transform: specify a transformation that gets applied to vertices.
    """
    self.scene = scene
    self.transform = transform or mathutils.Matrix.Identity (3)
  def get_vertices (self, msh):
    """get the vertices object from the mesh.
    """
    vs = [tuple (self.transform * v.co) for v in msh.vertices]
    jdata = {
      'count': len (vs),
      'values': vs
    }
    return jdata
  def get_face_groups (self, obj, msh):
    """returns two objects: the polygon_groups-block of the dsf
       and a list containing the group-indices (one for each face).
       obj is the mesh object (which holds the groups).
    """
    def get_common_group (vidxs):
      """get the smallest group index that is a common group index of
         all vertexes whose indices are given in vidxs.
         If there is no common index, return 0.
      """
      # list of group-objects, one for each vertex
      groups = [msh.vertices[vidx].groups for vidx in vidxs]
      # create a list of lists of group-indices
      group_idxs = [[vg.group for vg in vgroups] for vgroups in groups]
      # build the intersection of all groups
      intersection = set (group_idxs.pop ())
      for group in group_idxs:
        intersection.intersection_update (group)
      if len (intersection) == 0:
        return 0
      else:
        return min (intersection)
    # pgroups is the list of group indices to use, one for each face.
    pgroups = [get_common_group (poly.vertices) for poly in msh.polygons]
    if len (obj.vertex_groups) == 0:
      group_names = ['default']
    else:
      group_names = [group.name for group in obj.vertex_groups]
    jdata = {
      'count': len (obj.vertex_groups),
      'values': group_names
    }
    return (jdata, pgroups)
  def get_face_materials (self, obj, msh):
    """returns two objects: the polygon_material_groups as an object
       and a list of material indices, one for each face.
    """
    def get_material_name (material):
      """get a sensible name for the material
      """
      if material is None:
        return 'default'
      else:
        return material.name
    mgroups = [poly.material_index for poly in msh.polygons]
    if len (msh.materials) == 0:
      material_names = ['default']
    else:
      material_names = [get_material_name (mat) for mat in msh.materials]
    jdata = {
      'count': len (material_names),
      'values': material_names
    }
    return (jdata, mgroups)
  def create_face_data (self, obj):
    """create the polygon data of the object.
       this returns a dictionary with the keys:
       polygon_groups, polygon_material_groups, polylist, vertices
    """
    # todo: this needs to call to_mesh, but it needs a scene.
    # todo: this seriously needs to handle instances
    if self.scene:
      msh = obj.to_mesh\
        (self.scene, apply_modifiers = True, settings = 'PREVIEW')
    else:
      msh = obj.data
    (pg_jdata, pg_idxs) = self.get_face_groups (obj, msh)
    (pm_jdata, pm_idxs) = self.get_face_materials (obj, msh)
    assert len (pg_idxs) == len (pm_idxs) == len (msh.polygons)
    def create_poly_tuple (g, m, vs):
      return [g, m] + vs
    poly_vidx_list = [list (poly.vertices) for poly in msh.polygons]
    polylist_jdata ={
      'count': len (msh.polygons),
      'values': list (map (create_poly_tuple, pg_idxs, pm_idxs, poly_vidx_list))
    }
    vertices = self.get_vertices (msh)
    jdata = {
      'vertices': vertices,
      'polygon_groups': pg_jdata,
      'polygon_material_groups': pm_jdata,
      'polylist': polylist_jdata
    }
    return jdata
  def create_geometry (self, obj):
    """create a geometry_library entry from a blender object.
       The objects data name is used for the id of the geometry.
    """
    jdata = self.create_face_data (obj)
    jdata.update (self.create_face_data (obj))
    jdata['id'] = obj.data.name
    # required contents:
    # id, name, type, vertices, polygon_groups, polygon_material_groups,
    # polylist, default_uv_set (if available),
    # extra (optional): geometry_channels (for subdivision)
    return jdata

def group_objects_by_mesh (objs):
  """group the objects by their equivalent meshes.
     within each group objects are guaranteed to have the same mesh.
     returns a list of lists of objects.
  """
  dic = {}
  for obj in objs:
    if obj.type == 'MESH':
      key = (obj.data, len (obj.vertex_groups), len (obj.modifiers))
      # objects that have the same mesh, same number of vertex groups
      # and same number of modifiers go into the same group.
      dic.setdefault (key, []).append (obj)
  return list (dic.values ())

class node_creator (object):
  """class to create node entries for geometry objects.
  """
  def __init__ (self, transform = None):
    """create an instance. This constructor should set some default arguments.
    """
    if transform is None:
      self.transform = mathutils.Matrix.Identity (3)
    else:
      self.transform = transform
  def create_node (self, obj, id):
    """create the node-library entry for the object.
       The node is given an id by appending '-node' to the meshes data name.
    """
    if len (obj.rotation_mode) == 3:
      # euler rotation
      rot_mode = obj.rotation_mode
    else:
      # other rotation mode (axis/angle or quaternion); use xyz
      rot_mode = 'XYZ'
    # data of a node-lib entry without the channels.
    # the channels are pulled from the template.
    jdata = { }
    jdata.update (dsf_data.node_entry)
    jdata.update ({ 'rotation_order': rot_mode })
    jdata.update ({'id': id, 'name': obj.name, 'label': obj.name })
    return jdata

class uv_creator (object):
  """create uv library entries.
  """
  def __init__ (self):
    pass
  def create_uvlayer (self, msh, uv_layer, id):
    """create a single uv-library entry for the given uv-layer.
    """
    uv_data = uv_layer.data
    # list of all polygon/vertex pairs, should be the same size as the
    # upv_pairs := list of all (uv_idx, (poly_idx, vert_idx))
    pvs = [[(poly.index, vi) for vi in poly.vertices] for poly in msh.polygons]
    upv_pairs = list (enumerate (itertools.chain (*pvs)))
    assert (len (upv_pairs) == len (uv_data))
    # sort by vertex number
    upv_pairs.sort (key = lambda x: x[1][1])
    uvs = []
    tail = []
    d = {}
    for (v, upvs) in itertools.groupby (upv_pairs, lambda x: x[1][1]):
      # generate a list for the vertex v, containing each adjacent face
      # along with the corresponding uv coordinate:
      v_uvs = [(uv_data[u].uv, p) for (u, (p, v)) in upvs]
      # sort the list by uv-coordinates
      v_uvs.sort (key = lambda x: x[0])
      # create a mapping giving the list of polygons for a uv-coordinate
      # uv_p contains a list of tuples: (uv-coord, list of polygons)
      uv_p = [(uv, [p for (uv, p) in ups])
              for (uv, ups) in itertools.groupby (v_uvs, lambda x: x[0])]
      # sort this list by the number of polygons
      uv_p.sort (key = lambda x: len (x[1]))
      (last_uv, last_ps) = uv_p.pop ()
      uvs.append (tuple (last_uv))
      tail.extend (itertools.chain
                   (*[[(uv, (v, p)) for p in ps] for (uv, ps) in uv_p]))
    assert (len (uvs) == len (msh.vertices))
    polygon_vertex_indices = []
    uv_index = len (uvs)
    for (uv, uvps) in itertools.groupby (tail, lambda x: x[0]):
      uvs.append (tuple (uv))
      for (uv, (v, p)) in uvps:
        polygon_vertex_indices.append ((p, v, uv_index))
      uv_index += 1
    uv_lib = {
      'id': id,
      'label': uv_layer.name,
      'vertex_count': len (msh.vertices),
      'uvs': {
        'count': len (uvs),
        'values': uvs,
      },
      'polygon_vertex_indices': polygon_vertex_indices,
    }
    return uv_lib
  def create_uv (self, obj, msh):
    # get all layers
    layers = list (msh.uv_layers)
    # make the active layer the first one.
    layers.sort (key = lambda x: x != msh.uv_layers.active)
    # create uv lib entries for the uv layers.
    jdata = []
    for uvl in layers:
      uvlib = self.create_uvlayer (msh, uvl, uvl.name)
      jdata.append (uvlib)
    return jdata
