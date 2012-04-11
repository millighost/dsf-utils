# provide input functions for pz3 files.
import sys
import pz3.pz3p1

def read_pz3_data (filename):
  """read a pz3file and return its parsed data structure;
     the return value is a list of pz3object instances.
  """
  class feedback (object):
    def __init__ (self):
      self.pct = 0
    def __call__ (self, value):
      pct = int (value * 100)
      if pct != self.pct:
        self.pct = pct
        sys.stdout.write ("\r%02d" % (pct))
        sys.stdout.flush ()
  pz3_datas = pz3.pz3p1.data_builder.create_from_file (filename, feedback ())
  return pz3_datas

