import json, logging
import bpy

log = logging.getLogger ('jcodec')

class codec_repo (object):
  # singleton instance of a dictionary mapping the type of an object
  # to a codec class.
  codec_class_mapping = {}
  def __init__ (self):
    """initialize an instance of a codec repo that caches
       specific codec instances.
    """
    self.codec_instance_mapping = {}

  @classmethod
  def register_codec_class (self, type, cls):
    self.codec_class_mapping[type] = cls
  def get_instance (self, key):
    """instantiate the codec_class for the given type key and return
       the codec-instance.
    """
    instance = self.codec_instance_mapping.get (key)
    if instance is None:
      cls = self.codec_class_mapping.get (key)
      if cls is not None:
        instance = cls ()
        self.codec_instance_mapping[key] = instance
    return instance
  def codec_for_object (self, bobj):
    """return a codec instance for the given blender object.
    """
    if hasattr (bobj, 'type'):
      return self.get_instance (getattr (bobj, 'type'))
    else:
      return self.get_instance (type (bobj))
  def codec_for_data (self, data):
    log.info ("codec for data: %s", data)
    return self.get_instance (data['type'])

class base_codec (object):
  def __init__ (self, *arg, repo = None, **kwarg):
    self.repo = repo

class codec_base (object):
  """all data type specific codecs should inherit from this class.
  """
  def __init__ (self, *arg, **kwarg):
    pass
  def encode (self, bobj):
    """encode the data object into a dictionary.
       values of this dictionary do not need to be json objects, their
       codecs are called by the framework.
    """
    return {}

class image_codec (codec_base):
  def encode (self, bobj):
    return { 'type': bobj.type, 'filepath': bobj.filepath, 'name': bobj.name }
  def decode (self, data):
    log.info ("decode image %s", data)
    bobj = bpy.data.images.load (filepath = data['filepath'])
    return bobj
  def initialize (self, data, obj):
    return
codec_repo.register_codec_class ('IMAGE', image_codec)

class material_codec (codec_base):
  def encode (self, bobj):
    return { 'type': 'SURFACE' }
  def decode (self, data):
    pass
  def initialize (self, data, obj):
    pass
codec_repo.register_codec_class ('SURFACE', material_codec)


class encoder (object):
  def __init__ (self, *arg, **kwarg):
    self.repo = codec_repo ()
  def encode_object (self, bobj):
    codec_instance = self.repo.codec_for_object (bobj)
    flat_dic = codec_instance.encode (bobj)
    deep_dic = {
      key: self.encode (value)
        for (key, value) in flat_dic.items ()
    }
    return deep_dic
  def encode_list (self, bobj):
    return []
  def encode (self, bobj):
    if type (bobj) in [str, bool, int, float, type (None)]:
      return bobj
    elif type (bobj) == list:
      return self.encode_list (bobj)
    else:
      return self.encode_object (bobj)

class decoder (object):
  def __init__ (self, *arg, **kwarg):
    self.repo = codec_repo ()
  def decode_object (self, data):
    flat_dic = {
      key: self.decode (value)
        for (key, value) in data.items ()
    }
    codec_instance = self.repo.codec_for_data (flat_dic)
    return codec_instance.decode (flat_dic)
  def decode (self, data):
    if type (data) in [str, bool, int, float, type (None)]:
      return data
    elif type (data) == list:
      pass
    else:
      return self.decode_object (data)

def encode (bobj):
  enc = encoder ()
  jdata = enc.encode (bobj)
  return jdata

def decode (jdata):
  dec = decoder ()
  bobj = dec.decode (jdata)
  return bobj

