import bpy
import logging

from serial.base import codec_base
from serial.repo import codec_repo

log = logging.getLogger ('serial.node')

def get_attrs (node):
  def is_normal_aname (aname):
    return not aname.startswith ('__')\
        and aname not in ['bl_rna', 'outputs', 'inputs', 'rna_type', 'parent']
  return list (filter (is_normal_aname, dir (node)))

class c_node (codec_base):
  def encode (self, bobj):
    log.info ("serializing node: %s", bobj)
    return {
      key: getattr (bobj, key)
         for key in get_attrs (bobj)
    }
  def decode (self, data):
    pass

codec_repo.register_codec_class ('OUTPUT_MATERIAL', c_node)
codec_repo.register_codec_class ('BSDF_DIFFUSE', c_node)
