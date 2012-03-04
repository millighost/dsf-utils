import json, logging

log = logging.getLogger ('import_uvset')

class dsf_uvset_load (object):
  """class to load data for definition of uvsets.
  """
  @classmethod
  def read_dsf_data (self, filename):
    """load the given filename, check it for a uvset and return
       the contents in some form usable for the definition function.
    """
    jdata = json.load (open (filename, 'r'))
    if 'uv_set_library' not in jdata:
      raise TypeError ('file does not contain a uv set library.')
    uvlibs = jdata['uv_set_library']
    if len (uvlibs) == 0:
      raise TypeError ('file does contain at least one uv set.')
    log.info ("found %d uv sets in %s", len (uvlibs), filename)
    return uvlibs[0]
