from typing import Union

import bpy

TextSequence = Union[bpy.types.TextSequence, bpy.types.Sequence]
ImageSequence = Union[bpy.types.ImageSequence, bpy.types.Sequence]
SoundSequence = Union[bpy.types.SoundSequence, bpy.types.Sequence]
AdjustmentSequence = Union[bpy.types.AdjustmentSequence, bpy.types.Sequence]

KiritanifyScriptSequence = AdjustmentSequence
