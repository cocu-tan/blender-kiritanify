from typing import Optional

from bpy.types import Context, Sequence

from kiritanify.propgroups import KiritanifyCharacterSetting
from kiritanify.types import KiritanifyScriptSequence, SoundSequence
from kiritanify.utils import _seq_setting, _global_setting


class CharacterScript:
  """
  Represents character script, which basically holds two sequence; caption image sequence (KiritanifyScriptSequence)
  and voice sound sequence.

  Expected to be used as one-time data structure. Do not store permanently and do not use cross Operator.
  """
  chara: KiritanifyCharacterSetting
  seq: KiritanifyScriptSequence
  voice_seq: Optional[SoundSequence]

  context: Context

  def __init__(
      self,
      chara: KiritanifyCharacterSetting,
      seq: KiritanifyScriptSequence,
      voice_seq: Optional[SoundSequence],
      context: Context,
  ):
    self.chara = chara
    self.seq = seq
    self.voice_seq = voice_seq
    self.context = context

  @classmethod
  def create_from(
      cls,
      chara: KiritanifyCharacterSetting,
      seq: KiritanifyScriptSequence,
      context: Context,
  ) -> 'CharacterScript':
    voice_seq = _seq_setting(seq).find_voice_seq(context)
    return cls(
      chara=chara,
      seq=seq,
      voice_seq=voice_seq,
      context=context,
    )

  def maybe_update_voice(self):
    should_regenerate: bool = _seq_setting(self.seq) \
      .voice_cache_state.is_changed(
      global_setting=_global_setting(self.context),
      chara=self.chara,
      seq=self.seq,
    )
    if should_regenerate:
      if self.voice_seq is not None:
        self._remove_sequence(self.voice_seq)
        self.voice_seq = None
      # TODO: sequence generate procedure here

      _seq_setting(self.seq).voice_cache_state.update(
        global_setting=_global_setting(self.context),
        chara=self.chara,
        seq=self.seq
      )

    self._align_sequence(
      seq=self.voice_seq,
      channel=self.channel,
      frame_final_start=self.seq.frame_final_start,
    )

  def maybe_update_caption(self):
    should_regenerate: bool = _seq_setting(self.seq) \
      .caption_cache_state.is_changed(_global_setting(self.context), self.chara, self.seq)

    if should_regenerate:
      pass

  def _generate_caption(self):
    pass

  @staticmethod
  def _align_sequence(
      seq: Sequence,
      channel: Optional[int] = None,
      frame_final_start: Optional[int] = None,
      frame_final_end: Optional[int] = None,
  ):
    if channel is not None and seq.channel != channel:
      seq.channel = channel
    if frame_final_start is not None and seq.frame_final_start != frame_final_start:
      seq.frame_final_start = frame_final_start
    if frame_final_end is not None and seq.frame_final_end != frame_final_end:
      seq.frame_final_end = frame_final_end

  def _remove_sequence(self, seq):
    self.context.scene.sequence_editor.sequences.remove(seq)
