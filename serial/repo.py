import logging

log = logging.getLogger ('repo')

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
  def register_codec_class_builtin (self, type, name, cls):
    self.codec_class_mapping[type] = cls
    self.codec_class_mapping[name] = cls
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

