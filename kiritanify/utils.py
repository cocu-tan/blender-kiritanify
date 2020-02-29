import datetime
import re
from typing import Dict, List, Union

from bpy.types import Context, Sequence, Sequences


def _fps(context: Context):
  return context.scene.render.fps / context.scene.render.fps_base


def _sequences(context: Context) -> Union[Sequences, List[Sequence]]:
  return context.scene.sequence_editor.sequences


def _sequences_all(context: Context) -> Union[Dict[str, Sequence], List[Sequence]]:
  return context.scene.sequence_editor.sequences_all


def _datetime_str():
  return datetime.datetime.now().strftime('%Y%m%d%-H%M%S')


def _current_frame(context: Context) -> int:
  return context.scene.frame_current


def get_sequences_by_channel(context: Context, channel: int) -> List[Sequence]:
  return [
    seq
    for seq in _sequences(context)
    if seq.channel == channel
  ]


def trim_bracketed_sentence(text: str) -> str:
  expr = re.compile(r'\([^)]+\)')
  return expr.sub('', text)
