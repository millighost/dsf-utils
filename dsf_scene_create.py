
class node_creator (object):
  """create node instances for scene content.
  """
  def __init__ (self, linker):
    """initialize with an object to resolve references.
    """
    self.linker = linker
  def get_pose_rot (self, obj):
    """return xyz for the rotation of obj.
    """
    (x,y,z) = obj.rotation_euler
    return [
      { "id" : "x", "current_value" : x },
      { "id" : "y", "current_value" : y },
      { "id" : "z", "current_value" : z }
    ]
  def get_pose_trans (self, obj):
    """get the xyz translation of the object.
    """
    (x,y,z) = obj.location
    return [
      { "id" : "x", "current_value" : x },
      { "id" : "y", "current_value" : y },
      { "id" : "z", "current_value" : z }
    ]
  def get_geometries (self, obj):
    """get the geometries section of a scene (contains only references).
       generate those tags:
       { id, url, name, label, type }
    """
    jdata = {
      'name': obj.name,
      'label': obj.name,
      'type': 'polygon_mesh'
    }
    jdata['id'] = self.linker.add_id (jdata, 'id', obj, 'gref')
    jdata['url'] = self.linker.get_ref (jdata, 'url', obj, 'geom')
    return jdata
  def create_node_instance (self, obj):
    """create an instantiated node for the object.
       So that this will work correctly, the node should have
       a default orientation and axes named x,y,z.
       the id the node is given is the object name.
    """
    # required tags to generate:
    # id, url, name, label, geometry
    # geomtry: { id, url, name, label, type }
    jdata = {
      'name': obj.name,
      'label': obj.name,
      'geometries': [ self.get_geometries (obj) ],
      'rotation': self.get_pose_rot (obj),
      'translation': self.get_pose_trans (obj)
    }
    jdata['id'] = self.linker.add_id (jdata, 'id', obj, 'nref')
    jdata['url'] = self.linker.get_ref (jdata, 'url', obj, 'node')
    return jdata
