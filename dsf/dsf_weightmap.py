import rig.weight_map

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
  def getmap (self):
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
      self.maps['scale'] = weightmap (jdata['scale_weights'])
    if 'local_weights' in jdata:
      local_weights = jdata['local_weights']
      for axis in ['x', 'y', 'z']:
        if axis in local_weights:
          self.maps[('local', axis)] = weightmap (local_weights[axis])
  def get (self, key):
    """get a stored map. currently supported keys:
       'scale', ('local', 'x'), ..., ('local', 'z').
       returns None if the requested map is not there.
    """
    return self.maps.get (key)

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
    """return the maps for the given bone name.
    """
    return self.joint_dic.get (name)
