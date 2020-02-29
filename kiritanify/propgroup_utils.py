from bpy.types import Context

from kiritanify import KiritanifyGlobalSetting, KiritanifyScriptSequenceSetting
from kiritanify.types import KiritanifyScriptSequence


def _global_setting(context: Context) -> KiritanifyGlobalSetting:
  return context.scene.kiritanify


def _seq_setting(seq: KiritanifyScriptSequence) -> KiritanifyScriptSequenceSetting:
  return seq.kiritanify
