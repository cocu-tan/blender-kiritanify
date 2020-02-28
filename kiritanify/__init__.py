import bpy

from .ops import OPS_CLASSES
from .propgroups import (
  KiritanifyGlobalSetting,
  KiritanifySequenceSetting,
  PROPGROUP_CLASSES,
)

bl_info = {
  "name": "kiritanify",
  "category": "Sequencer",
  "author": "mohuton",
  "version": (1, 0),
  "blender": (2, 80, 0),
  "description": "Generate voiceroid sound data from caption data.",
}

CLASSES = (
    PROPGROUP_CLASSES
    + OPS_CLASSES
)


def register():
  for cls in CLASSES:
    bpy.utils.register_class(cls)

  bpy.types.ImageSequence.kiritanify = bpy.props.PointerProperty(
    name="Kiritanify Settings",
    type=KiritanifySequenceSetting,
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
