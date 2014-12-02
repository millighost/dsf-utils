import bpy, mathutils

import dsf.path_util
import dsf.geom_create
import json, math

class prop_writer (object):
  """write props for a single export-operation.
  """
  def __init__ (self, filepath, transform):
    """initialize state for writing to the given scene-file.
    """
    self.lib = dsf.path_util.daz_library (filepath = filepath)
    self.duf_libpath = self.lib.get_libpath (filepath)
    self.dsf_libpath = self.lib.get_data_libpath (self.duf_libpath)
    self.transform = transform
  @classmethod
  def get_selected_objects (self, scene):
    """return the selected objects of the scene.
    """
    objects = [obj for obj in scene.objects if obj.select]
    return objects

  @classmethod
  def get_selected_objects_by_data (self, scene):
    """get one object for each unique data instance.
    """
    all_objs = self.get_selected_objects (scene)
    groups = dsf.geom_create.group_objects_by_mesh (all_objs)
    objs = [obj[0] for obj in groups]
    return objs

  def create_data_file (self, ctx):
    objects = self.get_selected_objects_by_data (ctx.scene)
    gcreator = dsf.geom_create.geom_creator (ctx.scene, self.transform)
    geometries = [gcreator.create_geometry (obj) for obj in objects]
    data = {
      "asset_info": {},
      "geometry_library": geometries
    }
    return data

  def create_node_ref (self, obj):
    """get the node geometry instantiation for an object.
    """
    data_name = obj.data.name
    return {
      "url": self.dsf_libpath,
      "name": obj.name,
      "geometries": [
        {
          "url": "%s#%s" % (self.dsf_libpath, data_name)
        }
      ]
    }
  def create_scene_file (self, ctx):
    objects = self.get_selected_objects (ctx.scene)
    scene_nodes = [self.create_node_ref (obj) for obj in objects]
    data = {
      "asset_info": {},
      "scene": {
        "nodes": scene_nodes
      }
    }
    return data

  def write_json (self, libpath, data):
    ofh = self.lib.create_output_stream (libpath)
    json.dump (data, ofh)

  def write_scene (self, ctx):
    scene = ctx.scene
    objecs = self.get_selected_objects (scene)
    self.write_json (self.dsf_libpath, self.create_data_file (ctx))
    self.write_json (self.duf_libpath, self.create_scene_file (ctx))

def make_transform (scale, rotate):
  if rotate:
    trans = scale * mathutils.Euler ([-math.pi/2, 0, 0], 'XYZ').to_matrix ()
  else:
    trans = scale * mathutils.Matrix.Identity (3)
  return trans

def export_prop (ctx, filepath, group, scale, rotate):
  """export the active object to the filepath.
     group is a hint for the subdirectory.
     scale is a scale factor that is applied to exported objects.
     if rotate is true, rotate geometry by 90degrees around x.
  """
  transform = make_transform (scale, rotate)
  writer = prop_writer (filepath, transform)
  writer.write_scene (ctx)

