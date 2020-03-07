from typing import Union

import bpy

AdjustmentSequence = Union[bpy.types.AdjustmentSequence, bpy.types.Sequence]
TextSequence = Union[bpy.types.TextSequence, bpy.types.Sequence]
ImageSequence = Union[bpy.types.ImageSequence, bpy.types.Sequence]
SoundSequence = Union[bpy.types.SoundSequence, bpy.types.Sequence]
SpeedControlSequence = Union[bpy.types.SpeedControlSequence, bpy.types.Sequence]
MovieSequence = Union[bpy.types.MovieSequence, bpy.types.Sequence]

KiritanifyScriptSequence = AdjustmentSequence
KiritanifyTachieSequence = ImageSequence
