import bpy, mathutils

import dsf.path_util
import dsf.geom_create
import dsf.scene_writer
import json, math
import urllib.parse as urp

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
    self.transform_inv = transform.inverted ()
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
    geometry_datas = [gcreator.create_geometry_and_uvs (obj) for obj in objects]
    for gdata in geometry_datas:
      geo = gdata.geometry
      uvs = gdata.uvs
      if uvs:
        geo['default_uv_set'] = '#' + urp.quote (uvs[0]['id'])
    data = {
      "asset_info": {},
      "geometry_library": [g.geometry for g in geometry_datas],
      "uv_set_library": sum ([g.uvs for g in geometry_datas], [])
    }
    return data

  def write_json (self, libpath, data):
    ofh = self.lib.create_output_stream (libpath)
    json.dump (data, ofh, indent = 2, sort_keys = True)

  def build_objmap (self, objs):
    """build the object-map, i.e. a mapping for each object to
       its data-url.
    """
    objmap = {
      obj: "%s#%s" % (self.dsf_libpath, obj.data.name)
      for obj in objs
    }
    return objmap
  def write_scene (self, ctx):
    scene = ctx.scene
    objects = self.get_selected_objects (scene)
    objmap = self.build_objmap (objects)
    scene_writer = dsf.scene_writer.scene_writer (self.transform, objmap)
    self.write_json (self.dsf_libpath, self.create_data_file (ctx))
    self.write_json (self.duf_libpath, scene_writer.create_scene_file (objects))

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
  writer = prop_writer (filepath, transform.to_4x4 ())
  writer.write_scene (ctx)

