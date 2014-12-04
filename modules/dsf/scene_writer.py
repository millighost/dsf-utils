import bpy
import mathutils
import math

class scene_writer (object):
  """write scene subset files.
  """
  def __init__ (self, transform, objmap):
    """initialize with a transformation (blender-to-ds-space).
       objmap maps objects to their geometry-definitions.
    """
    self.transform = transform
    self.transform_inv = transform.inverted ()
    self.objmap = objmap

  def create_node_ref (self, obj):
    """get the node geometry instantiation for an object.
    """
    data_name = self.objmap[obj]
    data = {
      "url": data_name,
      "name": obj.name,
      "geometries": [
        {
          "url": data_name
        }
      ],
      "rotation": self.make_rotation (obj),
      "translation": self.make_translation (obj)
    }
    return data

  def make_rotation (self, obj):
    """create the rotation entry for the instantiation
    """
    mat = self.transform * obj.matrix_local * self.transform_inv
    euler = mat.to_euler ("XYZ")
    rotation = [
      { "id": axis,
        "current_value": getattr (euler, axis) * 180 / math.pi }
      for axis in ["x", "y", "z"]
    ]
    return rotation
  def make_translation (self, obj):
    """create the translation entry for the instantiation.
    """
    mat = self.transform * obj.matrix_local * self.transform_inv
    pos = mat.translation
    translation = [
      { "id": axis,
        "current_value": getattr (pos, axis) }
      for axis in ["x", "y", "z"]
    ]
    return translation

  def create_scene_file (self, objs):
    """create a scene-subset with the given objects.
    """
    scene_nodes = [self.create_node_ref (obj) for obj in objs]
    data = {
      "asset_info": {},
      "scene": {
        "nodes": scene_nodes
      }
    }
    return data

