import bpy
from serial.base import codec_base
from serial.repo import codec_repo

class material_codec (codec_base):
  def encode (self, bobj):
    return { 'type': 'SURFACE' }
  def decode (self, data):
    pass
  def initialize (self, data, obj):
    pass

codec_repo.register_codec_class ('SURFACE', material_codec)
