import logging

logging.basicConfig(level=logging.DEBUG)

import bpy

from kiritanify.ops import OP_CLASSES
from kiritanify.panels import PANEL_CLASSES
from kiritanify.propgroups import (
  KiritanifyGlobalSetting,
  KiritanifyScriptSequenceSetting,
  PROPGROUP_CLASSES,
)

bl_info = {
  "name": "kiritanify",
  "category": "Sequencer",
  "author": "mohuton",
  "version": (1, 0),
  "blender": (2, 80, 2),
  "description": "Generate voiceroid sound data from caption data.",
}

CLASSES = (
    PROPGROUP_CLASSES
    + OP_CLASSES
    + PANEL_CLASSES
)


def register():
  for cls in CLASSES:
    bpy.utils.register_class(cls)

  bpy.types.AdjustmentSequence.kiritanify = bpy.props.PointerProperty(
    name="Kiritanify Settings",
    type=KiritanifyScriptSequenceSetting,
  )
  bpy.types.Scene.kiritanify = bpy.props.PointerProperty(
    name="Kiritanify Global Settings",
    type=KiritanifyGlobalSetting,
  )


def unregister():
  for cls in reversed(CLASSES):
    bpy.utils.unregister_class(cls)
  del bpy.types.Scene.kiritanify
  del bpy.types.ImageSequence.kiritanify


if __name__ == "__main__":
  register()
