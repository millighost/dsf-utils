# helpers for using weight maps with blender.
from array import array

def collect_groups (bobj, include_zeroes = False):
  """create a mapping of group names to list of vertex indices belonging
     to each group.
     bobj is a blender object (must be mesh).
     include_zeroes if true, include members with a zero weight.
  """
  msh = bobj.data
  numeric_group_dic = dict ()
  for (vidx, vertex) in enumerate (msh.vertices):
    for vertex_group in vertex.groups:
      group_index = vertex_group.group
      if group_index not in numeric_group_dic:
        numeric_group_dic[group_index] = array ('i')
      numeric_group_dic[group_index].append (vidx)
  named_group_dic = dict ()
  for (group_idx, vertex_idxs) in numeric_group_dic.items ():
    vertex_group = bobj.vertex_groups[group_idx]
    if not include_zeroes:
      # create a new array of indices which have a nonzero weight.
      filtered = filter\
          (lambda vidx: vertex_group.weight (vidx) > 0, vertex_idxs)
    else:
      filtered = vertex_idxs
    filtered_idxs = array ('i', filtered)
    if len (filtered_idxs) > 0:
      # questionable; todo: perhaps including empty groups is better...
      named_group_dic[vertex_group.name] = filtered_idxs
  return named_group_dic

def limit_domain (domain, max_vertices):
  """intersect the index-range domain to contain only max_vertices.
  """
  idx_min = max (domain[0], 0)
  idx_max = min (domain[1], max_vertices)
  return (idx_min, idx_max)

def define_weight_map (bobj, name, wmap, min_weight = 0.01):
  """define a weight map for the given blender object bobj,
     which must be a mesh. wmap is a weight-map object.
     weights below min_weight do not get added to the group at all.
  """
  assert (isinstance (bojb.data, bpy.types.Mesh))
  if name in bobj.vertex_groups:
    # dangerous: re-creation of vertex groups can
    # cause havoc if they are used anywhere; todo: find
    # a way to clear them out.
    old_vg = bobj.vertex_groups[name]
    bobj.vertex_groups.remove (old_vg)
  vg = bobj.vertex_groups.new (name = name)
  (idx_min, idx_max)\
      = limit_domain (wmap.get_domain (), len (bobj.data.vertices))
  for idx in range (idx_min, idx_max):
    weight = wmap.get_weight (idx)
    if weight > min_weight:
      vg.add ([idx], weight, 'REPLACE')
    else:
      # matter of taste if empty weights should be actually removed,
      # but i like to keep my groups small.
      vg.remove ([idx])
