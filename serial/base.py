from serial.repo import codec_repo
import logging

log = logging.getLogger ('base')

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

class encoder (object):
  def __init__ (self, *arg, **kwarg):
    self.repo = codec_repo ()
  def encode_object (self, bobj):
    codec_instance = self.repo.codec_for_object (bobj)
    if codec_instance is None:
      log.info ("no codec for %s", bobj)
      return None
    else:
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

