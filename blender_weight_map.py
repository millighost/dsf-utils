
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
