import logging
import pz3.input

import rig.poser_armature
import rig.rig_define

log = logging.getLogger ("import_rig")

def read_cr2_figure (pathname):
  """read a cr2 file and return the first data block.
  """
  pdata = pz3.input.read_pz3_data (pathname)
  return pdata[0]

def import_cr2_rig (pathname, ctx):
  """import a rig from a cr2 file into blender.
     ctx is the blender context.
  """
  figure_data = read_cr2_figure (pathname)
  si_arm = rig.poser_armature.armature (figure_data)
  rig.rig_define.define_armature (si_arm, ctx)
