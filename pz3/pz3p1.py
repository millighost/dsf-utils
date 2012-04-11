import types

def convert_arg (arg):
  """semantically convert an argument from a string to something
     else, if possible.
  """
  if len (arg) == 0:
    return arg
  elif arg[0] == '"':
    return arg
  elif arg[0].isdigit () or arg[0] in '.-':
    try:
      return float (arg)
    except ValueError:
      return arg
  elif arg[0].isalpha () or arg[0] in ':/':
    return arg
  elif arg[0].isprintable () and ord (arg[0]) < 255:
    return arg
  else:
    raise ValueError ("invalid format '%s'" % arg)

class pz3attribute (object):
  """represent the key/values pair that is to be found in
     pz3 brace-enclosed lists.
  """
  def __init__ (self, key, args):
    self.key = key
    self.args = args
  def encode (self):
    """encode self to a simple list/dict-object.
    """
    return { 'key': self.key, 'args': self.args }
  @classmethod
  def decode (self, obj):
    """convert the list/dict-object into a pz3attribute.
       Corresponds to the encode method.
    """
    return pz3attribute (obj['key'], obj['args'])
  def add_arg (self, arg):
    """add an additional argument to the arguments.
    """
    self.args.append (arg)
  def child (self):
    """return the child-value of this attribute if it has a child,
       otherwise return None.
    """
    if len (self.args) == 0 or type (self.args[-1]) != pz3object:
      return None
    else:
      return self.args[-1]
  def keys (self):
    """return an iterable of all string-keys this attributes object supports.
       I.e. this attribute must have an object-part.
    """
    child = self.child ()
    if child is None:
      raise KeyError ("attribute '%s' has no keys." % (self.key))
    else:
      return child.keys ()
  def __contains__ (self, key):
    """for string-keys, check if the last argument has the named key
       for an attribute.
    """
    if type (key) == str:
      child = self.child ()
      if child is not None:
        return key in child
      else:
        return False
    else:
      return key in self.args
  def __getitem__ (self, key):
    """for integer keys get the indexed argument, string-keys
       are handled a bit differently: it is assumed that the last
       argument is an object; fetch the named attribute from that
       object.
    """
    if type (key) == int:
      return self.args[key]
    elif type (key) == str:
      child = self.child ()
      if child is None:
        raise IndexError ("attribute '%s' has no object-part." % (key))
      else:
        return child[key]
    else:
      raise IndexError ("invalid key '%s' for '%s'-attribute" % (key, self.key))
  def get (self, key):
    """for integer keys works like self[key]. For string keys
       it gets an iterator of all attributes that match the given
       key.
    """
    if type (key) == int:
      return self.args[key]
    elif type (key) == str:
      child = self.child ()
      if child is None:
        raise IndexError ("attribute '%s' has no object-part." % (key))
      else:
        return child.get (key)
    else:
      raise IndexError ("invalid key '%s' for '%s'-attribute" % (key, self.key))
  def __str__ (self):
    return self.key + ": " + str (self.args)
  def __repr__ (self):
    return self.key + ': ' + repr (self.args)

class pz3object (list):
  """represents a poser content block (the stuff between { and }).
     It is a mixture between a list and a dict. Contents can be accessed
     by key or by index.
  """
  def filter (self, pred):
    """return an iterator for all attributes whose key matches the
       given predicate.
    """
    for element in self:
      if pred (element.key):
        yield element
    return
  def get (self, key):
    """return an iterator of the attributes whose key matches key.
       the exact behaviour depends on the type of key:
       - for a string the attribute.key must match exactly key.
       - for a list the attribute.key must be included in the list key.
       - for a function this is equivalent to self.filter (key)
    """
    if isinstance (key, str):
      return self.filter (lambda k: k == key)
    elif isinstance (key, list):
      return self.filter (lambda k: k in key)
    elif isinstance (key, types.FunctionType):
      return self.filter (key)
    else:
      raise Exception ("invalid argument type to get()")
    return
  def keys (self):
    return [item.key for item in self]
  def __getitem__ (self, key):
    """key must be unique within self. return the value of it.
    """
    if type (key) == str:
      items = [item for item in self if item.key == key]
      if len (items) == 1:
        return items[0]
      elif len (items) > 1:
        raise IndexError ("ambiguous key '%s'" % key)
      else:
        raise IndexError ("no such key '%s'" % key)
    else:
      return super (pz3object, self).__getitem__ (key)
  def __contains__ (self, key):
    """return True iff at least one item named key is defined.
    """
    for item in self:
      if item.key == key:
        return True
    return False

class data_builder (object):
  def __init__ (self):
    """this function is to be used only from within this
       classes create function.
    """
    # objstack contains a stack of the nested constructed object.
    # every value must be within an object (the stuff between braces).
    self.objstack = list ()

  def handle (self, args):
    """internal function process a single statement (generalized line).
    """
    if args[0] == '{':
      # starts a new object. Subsequent statements go into this
      # object until the next right-brace.
      self.objstack.append (pz3object ())
    elif args[0] == '}':
      finished_obj = self.objstack.pop ()
      # last object after a '}' finalizes and
      # gives a return value
      if len (self.objstack) == 0:
        return finished_obj
      current_obj = self.objstack[-1]
      if len (current_obj) == 0:
        # has to be a construct with two '{' after each other,
        # should probably not happen, since i never have seen this,
        # but fits the model anyway.
        current_obj.append (finished_obj)
      else:
        # was a subobject after a statement: 'bla bla {...';
        # add the subject to the preceeding statement.
        current_obj[-1].add_arg (finished_obj)
    else:
      # normal statement. A current object must be active,
      # a standalone statement would rise an exception here
      converted_args = list (map (convert_arg, args[1:]))
      statement = pz3attribute (args[0], converted_args)
      self.objstack[-1].append (statement)
  @classmethod
  def build_object (self, joiner, feedback = None):
    """build an object from the token joiner (type0 parser).
    """
    token_count = 0
    builder = data_builder ()
    objects_read = list ()
    for token in joiner.tokens ():
      token_count += 1
      if token_count % 100 == 0 and feedback:
        feedback (joiner.position ())
      object_read = builder.handle (token)
      if object_read is not None:
        objects_read.append (object_read)
    return objects_read

  @classmethod
  def create_from_file (self, filename, feedback = None):
    import pz3.pz3p0
    joiner = pz3.pz3p0.joiner (open (filename, 'r'))
    o = data_builder.build_object (joiner, feedback)
    return o

import json

class encoder (json.JSONEncoder):
  """class to encode pz3attributes to json.
  """
  def __init__ (self, *arg, **kwarg):
    """initialize a new encoder.
    """
    super (encoder, self).__init__ (*arg, **kwarg)
  def default (self, obj):
    if type (obj) == pz3attribute:
      return { '-type': 'pz3attribute-magic', 'value': obj.encode () }
    else:
      super (encoder, self).default (obj)

class decoder (json.JSONDecoder):
  """class to decode encoded pz3attributes from json.
  """
  def __init__ (self, *arg, **kwarg):
    """initialize a new decoder.
    """
    super (decoder, self).__init__ (*arg, **kwarg)
  def default (self, data):
    if type (data) == dict\
          and '-type' in data\
          and data['-type'] == 'pz3attribute-magic':
      return pz3attribute.decode (data['value'])
    else:
      return super (decoder, self).default (data)

