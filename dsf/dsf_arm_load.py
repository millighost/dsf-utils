import json
from array import array

def get_xyz_channels (jdata):
  """return the x,y,z components of the given list as a 3 tuple.
  """
  id_map = {
    obj['id']: obj for obj in jdata if 'id' in obj
  }
  if 'x' in id_map and 'y' in id_map and 'z' in id_map:
    return (id_map['x']['value'], id_map['y']['value'], id_map['z']['value'])
  else:
    return None

def get_static_params (actor):
  """get the static parameters of an actor
     (rotation-order, orientation, start, end).
  """
  channel_names = {
    'center_point': 'origin',
    'orientation': 'orientation',
    'end_point': 'endpoint'
  }
  data = dict ()
  for ds_name, si_name in channel_names.items ():
    if ds_name in actor:
      value = get_xyz_channels (actor[ds_name])
      if value is not None:
        data[si_name] = value
  return data

def get_dynamic_params (actor):
  """get the static parameters of an actor
     (rotation, translation, scale, general_scale).
  """
  pass

def create_bone_from_jdata (jdata):
  """create a bone from a json object; checks if all the necessary
     keys could be found.
  """
  all_keys_there = min ([key in jdata for key in
        ['rotation_order', 'id', 'center_point', 'orientation', 'end_point']])
  if not all_keys_there:
    return None
  return {
    'id': jdata['id'],
    'parent': jdata.get ('parent'),
    'order': jdata['rotation_order'].lower (),
    'orientation': get_xyz_channels (jdata.get ('orientation')),
    'head': get_xyz_channels (jdata.get ('center_point')),
    'tail': get_xyz_channels (jdata.get ('end_point')),
  }

class dsf_arm_load (object):
  @classmethod
  def get_armature_from_jdata (self, jdata):
    """extract the node-library from the decoded json-data jdata,
       which is the whole decoded file.
    """
    nodelib = jdata['node_library']
    bones = dict ()
    for node in nodelib:
      bone = create_bone_from_jdata (node)
      bones[bone['id']] = bone
      print ("node:", node['id'], bone)
    return bones

  @classmethod
  def load_file (self, filename, opts = None):
    jdata = json.load (open (filename, 'r'))
    si_arm = self.get_armature_from_jdata (jdata)
    return si_arm

genesis = '/images/winshare/dsdata4/data/DAZ 3D/Genesis/Base/Genesis.dsf'

