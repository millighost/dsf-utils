import math, mathutils

class node_creator (object):
  """create node instances for scene content.
  """
  def __init__ (self, linker, export_scale = 1, **kwarg):
    """initialize with an object to resolve references.
       if export-scale != 1, applies a space-transformation for exporting.
    """
    self.linker = linker
    self.export_scale = export_scale
    if export_scale != 1:
      self.export_rotation = mathutils.Euler ([-math.pi/2, 0, 0], 'XYZ')
    else:
      self.export_rotation = mathutils.Euler ([0, 0, 0], 'XYZ')
  def get_pose_rot (self, obj):
    """return xyz for the rotation of obj.
    """
    rotation = mathutils.Euler (obj.rotation_euler)
    rotation.rotate (self.export_rotation)
    (x,y,z) = rotation
    return [
      { "id" : "x", "current_value" : math.degrees (x) },
      { "id" : "y", "current_value" : math.degrees (y) },
      { "id" : "z", "current_value" : math.degrees (z) }
    ]
  def get_pose_trans (self, obj):
    """get the xyz translation of the object.
    """
    (x,y,z) = obj.location
    if self.export_scale != 1:
      (x, y, z) = (self.export_scale * x,
                   self.export_scale * z,
                   - self.export_scale * y)
    return [
      { "id" : "x", "current_value" : x },
      { "id" : "y", "current_value" : y },
      { "id" : "z", "current_value" : z }
    ]
  def get_pose_general_scale (self, obj):
    """get the general part of the scale.
    """
    return {
      "id" : "general_scale",
      "current_value" : self.export_scale
    }
  def get_pose_scale (self, obj):
    """get the axis-specific scale of the object.
    """
    (x,y,z) = obj.scale
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
      'translation': self.get_pose_trans (obj),
      'scale': self.get_pose_scale (obj),
      'general_scale': self.get_pose_general_scale (obj)
    }
    jdata['id'] = self.linker.add_id (jdata, 'id', obj, 'nref')
    jdata['url'] = self.linker.get_ref (jdata, 'url', obj, 'node')
    return jdata
