import datetime
from typing import Dict, List, Union

from bpy.types import Context, Sequence, Sequences

from kiritanify.propgroups import (
  KiritanifyGlobalSetting,
  KiritanifySequenceSetting
)
from kiritanify.types import KiritanifyScriptSequence


def _fps(context: Context):
  return context.scene.render.fps / context.scene.render.fps_base


def _sequences(context: Context) -> Union[Sequences, List[Sequence]]:
  return context.scene.sequence_editor.sequences


def _sequences_all(context: Context) -> Union[Dict[str, Sequence], List[Sequence]]:
  return context.scene.sequence_editor.sequences_all


def _global_setting(context: Context) -> KiritanifyGlobalSetting:
  return context.scene.kiritanify


def _seq_setting(seq: KiritanifyScriptSequence) -> KiritanifySequenceSetting:
  return seq.kiritanify


def _datetime_str():
  return datetime.datetime.now().strftime('%Y%m%d%-H%M%S')


def _current_frame(context: Context) -> int:
  return context.scene.frame_current
