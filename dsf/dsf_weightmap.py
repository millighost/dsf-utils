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
      self.maps[('scale', 'xyz')] = weightmap (jdata['scale_weights'])
    if 'local_weights' in jdata:
      local_weights = jdata['local_weights']
      for axis in ['x', 'y', 'z']:
        if axis in local_weights:
          self.maps[('local', axis)] = weightmap (local_weights[axis])
  def get (self, key):
    """get a stored map. currently supported keys:
       (('scale', 'xyz'), ('local', 'x'), ..., ('local', 'z').
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
  def collect_paint_maps (self):
    """return a dictionary containing every paintable map of self.
       key is simply the axis.
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
  def get (self, name):
    """return the maps for the given bone name. This function returns
       the appropriate joint_map instance.
    """
    return self.joint_dic.get (name)
  def get_paint_map (self, names):
    """return a paintable map for the given joint-maps in names.
       each name in names is a tuple consisting of (body-part, joint),
       with joint being ('scale', 'xyz') or ('local', '<axis>').
    """
    paintable_maps = []
    for (joint_name, axis_name) in names:
      log.info ("joint: %s, axis: %s", joint_name, axis_name)
      joint = self.get (joint_name)
      paintable_map = joint.get_paint_map (axis_name)
      log.info ("paintable: %s", paintable_map)
      if paintable_map is not None:
        paintable_maps.append (paintable_map)
    log.info ("creating average.")
    avg_map = rig.weight_map.average_map (paintable_maps)
    log.info ("avg: %s", avg_map)
    return avg_map
  def get_single_paint_map (self, joint, axes):
    """convenience function for returning a mix of maps for a
       single body part.
    """
    joint = self.joint_dic[joint]
    return joint.get_paint_map_mix (axes)
  def collect_paint_maps (self):
    """return a dictionary containing every defined weight map in the skin.
       each key is a tuple (<joint-name>, <axis-name>).
    """
    all_maps = dict ()
    for (jname, joint) in self.joint_dic.items ():
      joint_maps = joint.collect_paint_maps ()
      for (axis, map) in joint_maps.items ():
        all_maps[(jname, axis)] = map
    return all_maps

def simple_name (complex_name):
  """helper function to generate a canonical weight map name (a string) from
     a combined name of body-part/axis.
  """
  (joint, (space, axis)) = complex_name
  if space == 'scale':
    return "def-%s.s" % (joint)
  else:
    return "def-%s.%s" % (joint, axis)

def paint_maps (maps):
  pass
