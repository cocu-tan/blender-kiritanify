import datetime
import re
from typing import Dict, Generator, Iterator, List, Optional, Tuple, TypeVar, Union

from bpy.types import Context, Sequence, Sequences

T = TypeVar('T')

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


def find_neighbor_sequence(context: Context, channel: int, target_frame: int) -> Tuple[
  Optional[Sequence],
  Optional[Sequence],
  Optional[Sequence],
]:
  seq_prev = None
  seq_target = None
  seq_next = None
  frame_prev = -float('inf')
  frame_next = float('inf')

  for seq in get_sequences_by_channel(context, channel):  # type: Sequence
    _start = seq.frame_final_start
    _end = seq.frame_final_end
    if frame_prev < _start and _end < target_frame:
      seq_prev = seq
      frame_prev = _start
    if _start <= target_frame <= _end:
      seq_target = seq
    if target_frame < _start and _end < frame_next:
      seq_next = seq
      frame_next = _end
  return (
    seq_prev,
    seq_target,
    seq_next,
  )


def split_per_num(elements: List[T], num: int) -> Generator[Iterator[T]]:
  num_split = len(elements) // num
  for n in range(num_split):
    yield elements[n * num:(n + 1) * num]
