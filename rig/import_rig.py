import logging
import pz3.input

import rig.poser_armature
import rig.rig_define

log = logging.getLogger ("import_rig")

def import_cr2_rig (pathname, ctx):
  """import a rig from a cr2 file into blender.
     ctx is the blender context.
  """
  pdata = pz3.input.read_pz3_data (pathname)
  si_arm = rig.poser_armature.armature (pdata[0])
  rig.rig_define.define_armature (si_arm, ctx)
