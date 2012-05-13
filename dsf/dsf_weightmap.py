import logging
import rig.weight_map

log = logging.getLogger ('dsf-wm')

class weightmap (object):
  """contains a single weightmap input data as it occurs in the dsf.
  """
  def __init__ (self, jdata):
    """initialize a weightmap from the object containing the map data.
    """
    idxs = []
    wgts = []
    if jdata['count'] == 0:
      self.map = rig.weight_map.weight_map ()
    else:
      for [idx, wgt] in jdata['values']:
        idxs.append (int (idx))
        wgts.append (float (wgt))
      self.map = rig.weight_map.table_map (idxs, wgts)
  def get_paint_map (self):
    """returns the paintable map representing self.
    """
    return self.map

class joint_map (object):
  """aggregate the different weight maps of a single joint. Contains
     only the maps that i understand.
  """
  def __init__ (self, jdata):
    """initialize the joints weights from the entry in a skin-binding.
       use the scale-weights and local-weights sections.
    """
    self.maps = dict ()
    if 'scale_weights' in jdata:
      self.maps['s'] = weightmap (jdata['scale_weights'])
    if 'local_weights' in jdata:
      local_weights = jdata['local_weights']
      for axis in ['x', 'y', 'z']:
        if axis in local_weights:
          self.maps[axis] = weightmap (local_weights[axis])
  def get (self, key):
    """get a stored map. currently supported keys:
       's' (for scale), 'x', 'y', 'z'.
       returns None if the requested map is not there.
    """
    return self.maps.get (key)
  def get_paint_map (self, key):
    """return a paintable map for the given axis.
       Returns a normalized paintable weight map.
    """
    if key in self.maps:
      log.info ("joint_map: key %s found.", key)
      paintable_map = self.maps[key].get_paint_map ()
      log.info ("paintable_map: %s", paintable_map)
      return paintable_map
    else:
      return None
  def get_paint_map_mix (self, keys):
    """for the given list of keys, create a paintable map that mixes
       the given keys using a simple average.
    """
    pmaps = []
    for key in keys:
      pmap = self.get_paint_map (key)
      if pmap is not None:
        pmaps.append (pmap)
    if len (pmaps) == 0:
      return None
    elif len (pmaps) == 1:
      return pmaps[0]
    else:
      avg_map = rig.weight_map.average_map (pmaps)
      return avg_map
  def get_paint_map_groups (self, groups):
    """get a set of paint maps for this joint. groups is a list where
       each member is a set of map-axes. Returns a dictionary where the
       keys are the groups.
    """
    group_dic = dict ()
    for group in groups:
      pmap = self.get_paint_map_mix (group)
      if pmap is not None:
        group_dic[group] = pmap
    return group_dic

  def collect_paint_maps (self):
    """return a dictionary containing every paintable map of self.
       key is simply the axis. No averaging is done.
    """
    return {
      axis: pmap.get_paint_map ()
      for (axis, pmap) in self.maps.items ()
    }

class skin (object):
  """collect all weightmaps for a figure.
  """
  def __init__ (self, jdata):
    """scan the jdata which is the skin-node for weight-maps and make them
       retrievable by id.
    """
    self.joint_dic = dict ()
    joints = jdata['joints']
    for joint in joints:
      jid = joint['id']
      jmap = joint_map (joint)
      self.joint_dic[jid] = jmap
  def get_joint_names (self):
    """return a list of all joints this skin has.
    """
    return self.joint_dic.keys ()
  def get (self, name):
    """return the maps for the given bone name. This function returns
       the appropriate joint_map instance.
    """
    return self.joint_dic.get (name)
  def get_single_paint_map (self, joint, axes):
    """convenience function for returning a mix of maps for a
       single body part.
    """
    joint = self.joint_dic[joint]
    return joint.get_paint_map_mix (axes)
  def canonicalize_map_name (self, joint, group):
    """build a simple string from a joint name and a group of axes.
       This name can be used to create a vertex group of it.
    """
    return "def-%s.%s" % (joint, group)
  def collect_paint_maps (self, groups):
    """get all paintable maps in groups for all joints. Each group is averaged,
       in general that means the results are not normalized to the number
       of groups.
    """
    all_map_dic = dict ()
    for (jname, joint) in self.joint_dic.items ():
      pmap_dic = joint.get_paint_map_groups (groups)
      for (pmap_name, pmap_group) in pmap_dic.items ():
        canonical_name = self.canonicalize_map_name (jname, pmap_name)
        all_map_dic[canonical_name] = pmap_group
    return all_map_dic
  def collect_all_paint_maps (self, merge = True, scale = False):
    """return a dictionary containing every defined weight map in the skin.
       grouping and generation of maps depends on the kwarg:
       merge: if True, the 3 rotation axes get merged into a single map.
       scale: if True, a separate map for scaling is generated (otherwise
         no scaling information is used).
    """
    if merge:
      groups = ['xyz']
    else:
      groups = ['x', 'y', 'z']
    if scale:
      groups.append ('s')
    return self.collect_paint_maps (groups)
