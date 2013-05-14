import collections

relocation_rec = collections.namedtuple\
  ('relocation_rec', ['dic', 'key', 'context'])
reference_rec = collections.namedtuple\
  ('reference_rec', ['obj', 'type', 'context'])
id_rec = collections.namedtuple\
  ('id_rec', ['dic', 'key', 'obj', 'type', 'context'])

class linker (object):
  def __init__ (self):
    self.reloc = []
    self.definition = []
    self.context = []

  def push_context (self, path):
    self.context.append (path)
  def pop_context (self):
    self.context.pop ()

  def add_reloc (self, dic, key):
    """add a relocation entry to the list of relocations.
       dic is a dictionary which contains a relocation at key.
    """
    self.reloc.append (relocation_rec (dic, key, self.context[-1]))

  def get_url (self, obj, type):
    """create a relocation to a blender object;
       type corresponds to the addressing mode.
    """
    return reference_rec (obj, type, self.context[-1])

  def add_id (self, dic, key, obj, type):
    """add a id definition to the linker.
    """
    self.definition.append (id_rec (dic, key, obj, type, self.context[-1]))
    return self.definition[-1]
