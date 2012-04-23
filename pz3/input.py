# provide input functions for pz3 files.
import sys, logging, os.path
import pz3.pz3p1

log = logging.getLogger ("pz3")

def read_pz3_data (filename):
  """read a pz3file and return its parsed data structure;
     the return value is a list of pz3object instances.
  """
  basename = os.path.basename (filename)
  class feedback (object):
    def __init__ (self):
      self.pct = 0
    def __call__ (self, value):
      pct = int (value * 10)
      if pct != self.pct:
        self.pct = pct
        log.info ("%s: %d0%% done.", basename, pct)
  pz3_datas = pz3.pz3p1.data_builder.create_from_file (filename, feedback ())
  return pz3_datas

