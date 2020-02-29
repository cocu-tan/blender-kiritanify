import base64
import hashlib
from typing import Optional

from bpy.types import Context, Sequence

from kiritanify.propgroups import KiritanifyCharacterSetting
from kiritanify.seika_center import synthesize_voice, trim_silence
from kiritanify.types import KiritanifyScriptSequence, SoundSequence
from kiritanify.utils import _global_setting, _seq_setting, _sequences


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
      self.voice_seq = self._generate_voice_sequence()
      self._seq_setting.voice_cache_state.update(
        global_setting=_global_setting(self.context),
        chara=self.chara,
        seq=self.seq
      )

    self._align_sequence(
      seq=self.voice_seq,
      channel=self.channel,
      frame_start=self.seq.frame_start,
    )
    frame_final_end = max(self.voice_seq.frame_final_end, self.seq.frame_final_end)
    if self.seq.frame_final_end != frame_final_end:
      self.seq.frame_final_end = frame_final_end

  def _generate_voice_sequence(self) -> SoundSequence:
    sound_path = self._global_setting.cache_setting.voice_path(self.chara, self.seq)

    segment = synthesize_voice(
      seika_setting=self._global_setting.seika_server,
      chara=self.chara,
      style=self._seq_setting.voice_style(self._global_setting, self.chara),
      script=self._seq_setting.voice_text(),
    )
    trim_silence(segment).export(str(sound_path), format='ogg')

    voice_seq = _sequences(self.context).new_sound(
      name=f'Voice:{self.chara.chara_name}:{self.hash_text()}',
      filepath=str(sound_path),
      channel=self.chara.voice_channel(self._global_setting),
      frame_start=self.seq.frame_final_start,
    )
    voice_seq.show_waveform = True

    return voice_seq

  def hash_text(self):
    text = self._seq_setting.voice_text()
    digest = hashlib.blake2s(data=text.encode('UTF-8')).digest()
    base64encoded = base64.b64encode(digest, altchars=b'-_')
    return base64encoded[:16]

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
      frame_start: Optional[int] = None,
      frame_end: Optional[int] = None,
      frame_final_start: Optional[int] = None,
      frame_final_end: Optional[int] = None,
  ):
    if channel is not None and seq.channel != channel:
      seq.channel = channel
    if frame_start is not None and seq.frame_start != frame_start:
      seq.frame_start = frame_start
    if frame_end is not None and seq.frame_end != frame_end:
      seq.frame_end = frame_end
    if frame_final_start is not None and seq.frame_final_start != frame_final_start:
      seq.frame_final_start = frame_final_start
    if frame_final_end is not None and seq.frame_final_end != frame_final_end:
      seq.frame_final_end = frame_final_end

  def _remove_sequence(self, seq):
    self.context.scene.sequence_editor.sequences.remove(seq)

  @property
  def _global_setting(self):
    return _global_setting(self.context)

  @property
  def _seq_setting(self):
    return _seq_setting(self.seq)
