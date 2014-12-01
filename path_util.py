import os.path, os

def find_libdir_head (filepath):
  """get the root of the library directory (directory that contains data).
     filepath is a filename with in the library
  """
  path, base = os.path.split (filepath)
  while len (base) > 0:
    data_neighbor = os.path.join (path, 'data')
    if os.path.isdir (data_neighbor):
      return path
    path, base = os.path.split (path)
  raise Exception ("no library directory found.")

class daz_library (object):
  """class to manage some files within a daz library.
  """
  def __init__ (self, libdir = None, filepath = None):
    """initialize with a file within the library.
    """
    if libdir:
      self.libdir = libdir
    elif filepath:
      self.libdir = find_libdir_head (filepath)
  def get_abspath (self, libpath):
    """get the absolute filesystem path for a file within the library.
    """
    as_rel = '.' + os.sep + libpath
    return os.path.abspath (os.path.join (self.libdir, as_rel))
  def get_libpath (self, abspath):
    """get the libpath for an absolute path.
    """
    relpath = os.path.relpath (abspath, self.libdir)
    return os.sep + relpath

  @classmethod
  def get_data_filename (self, libpath, group = None):
    """get a dsf-filename for a duf-filename."""
    base, ext = os.path.splitext (os.path.basename (libpath).lower ())
    return base + '.dsf'
  def get_data_libpath (self, libpath, group = None):
    """for the filepath get an associated filepath for the data file.
    """
    if not group:
      subdir = ''
    else:
      subdir = group
    filename = self.get_data_filename (libpath)
    return os.path.join ('/data', subdir, filename)
  def create_output_stream (self, libpath):
    """open a file for output in the library, creating intermediate directories
       if necessary.
    """
    abspath = self.get_abspath (libpath)
    ofh = open (abspath, 'w')
    return ofh
