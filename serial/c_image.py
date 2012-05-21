import bpy
import logging

from serial.base import codec_base
from serial.repo import codec_repo

log = logging.getLogger ('serial.image')

class c_image (codec_base):
  def encode (self, bobj):
    return { 'type': bobj.type, 'filepath': bobj.filepath, 'name': bobj.name }
  def decode (self, data):
    log.info ("decode image %s", data)
    bobj = bpy.data.images.load (filepath = data['filepath'])
    return bobj
  def initialize (self, data, obj):
    return

codec_repo.register_codec_class ('IMAGE', c_image)

