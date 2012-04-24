import operator, math, re

class bone (object):
  """proxy class for extracting properties of a pz3 actor block.
     Most functions just map from the name of an attribute to the corresponding
     name of the other attribute, but some might do something more
     (like calculating the rotation order).
  """
  def __init__ (self, actor_attr, arm):
    """initialize a bone from the given pz3 attribute node.
       actor_attr must be the attribute that actually holds the data.
       arm is a reference to the armature; for some attributes (length)
       other bones need to be consulted.
    """
    self.obj = actor_attr.child ()
    self.id = actor_attr.name ()
    self.arm = arm

  @classmethod
  def strip_name (self, name):
    """strip the numeric suffix from a name.
    """
    mat = re.match ('^(.*):(\\d+)$', name)
    if mat is None:
      return name
    else:
      return mat.group (1)

  def get_origin (self):
    """return the head of self (the origin).
    """
    return self.obj['origin'].args
  def get_id (self):
    """return the reference name of self. This removes the ':<NUM>' suffix
       from the name given in the cr2file.
    """
    return self.strip_name (self.id)
  def get_orientation (self):
    """return the orientation of self.
       orientation is the euler-rotation of the bone in fixed XYZ order.
    """
    return self.obj['orientation'].args
  def get_rotation_order (self):
    """return the rotation order of self given as a permutation of 'xyz'
    """
    # get all channels of self which are named like 'rotateX' etc.
    channel_keys = [chan.key for chan in self.obj['channels'].child ()]
    rotation_keys\
        = [key[-1] for key in channel_keys if key.startswith ('rotate')]
    order = "".join (rotation_keys)
    assert (len (order) == 3)
    return order
  def get_parent (self):
    """return the ref-name of the parent actor of this actor. This checks
       first for a nonInkyParent and then for a parent.
    """
    if 'nonInkyParent' in self.obj:
      pname = self.obj['nonInkyParent'][0]
    else:
      pname = self.obj['parent'][0]
    return self.strip_name (pname)
  def get_endpoint (self):
    """return the endpoint (tail) of self. return None if no endpoint is
       defined.
    """
    if 'endPoint' in self.obj:
      return self.obj['endPoint'].args
    else:
      return None
  def get_length (self):
    """return the approximate length of the bone.
       Mainly for display purposes; some guesswork is done here to get
       the size from either the endPoint, the child or the children positions.
    """
    endp = self.get_endpoint ()
    begp = self.get_origin ()
    norm = math.sqrt (sum ([d ** 2 for d in map (operator.sub, endp, begp)]))
    if norm > 0 and norm < 10:
      return norm
    else:
      return 1

  attr_mapping = {
    'origin': get_origin,
    'orientation': get_orientation,
    'rotation_order': get_rotation_order,
    'parent': get_parent,
    'length': get_length,
    'id': get_id,
    'endpoint': get_endpoint,
  }
  def get (self, name):
    """return the named attribute from self.
       this just calls the associated getter function.
    """
    if name in self.attr_mapping:
      return self.attr_mapping[name] (self)
    else:
      raise KeyError ("unknown key '%s'" % (name))

class armature (object):
  """proxy object for an armature defined from a pz3 file.
     provides essentially this functionality:
     - can get bones by name.
     - can identify roots.
  """
  def __init__ (self, pz3obj):
    """initialize an armature proxy from the given pz3 data object.
       The pz3obj must have a figure attribute.
    """
    self.data = pz3obj
    self.figure = pz3obj['figure'].child ()
    # pre-cache all actors of the figure as bone-proxies.
    self.bone_dic = dict ()
    for actor in self.data.get ('actor'):
      # this loop lists two types of actors: the declarations
      # and the actual definitions. Filter out the definitions
      # by checking for a 'name' attribute.
      if 'name' in actor.child ():
        proxy = bone (actor, self)
        self.bone_dic[proxy.get_id ()] = proxy
  def get_children (self, parent):
    """return all bones that have parent for a parent.
       if parent is None returns the root bones.
    """
    if isinstance (parent, bone):
      parent_name = parent.get ('id')
    else:
      parent_name = parent
    def is_child (bone):
      if parent is None:
        return bone.get ('parent') not in self.bone_dic
      else:
        return bone.get ('parent') == parent_name
    children = [b for b in self.bone_dic.values () if is_child (b)]
    return children
