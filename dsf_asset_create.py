from datetime import datetime

class asset_creator (object):
  """create asset infos.
  """
  def __init__ (self):
    pass
  @classmethod
  def create_asset_info (self, type = 'prop', id = None):
    """create an assetinfo object.
    """
    asset_info = {
      'id': id,
      'type': type,
      'modified': datetime.utcnow ().strftime ("%Y-%m-%dT%H:%M:%SZ"),
      'revision': '0.0'
    }
    return asset_info

