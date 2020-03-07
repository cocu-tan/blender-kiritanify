import base64
import hashlib
import logging
from pathlib import Path
from typing import Optional, Tuple

from PIL.Image import Image
from bpy.types import Context, Sequence

from kiritanify.caption_renderer import render_text
from kiritanify.propgroups import CaptionStyle, KiritanifyCharacterSetting, _global_setting, _seq_setting
from kiritanify.seika_center import synthesize_voice, trim_silence
from kiritanify.types import ImageSequence, KiritanifyScriptSequence, SoundSequence
from kiritanify.utils import _sequences

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class CharacterScript:
  """
  Represents character script, which basically holds two sequence; caption image sequence (KiritanifyScriptSequence)
  and voice sound sequence.

  Expected to be used as one-time data structure. Do not store permanently and do not use cross Operator.
  """
  chara: KiritanifyCharacterSetting
  seq: KiritanifyScriptSequence
  voice_seq: Optional[SoundSequence]
  caption_seq: Optional[ImageSequence]

  context: Context

  def __init__(
      self,
      chara: KiritanifyCharacterSetting,
      seq: KiritanifyScriptSequence,
      voice_seq: Optional[SoundSequence],
      caption_seq: Optional[ImageSequence],
      context: Context,
  ):
    self.chara = chara

    self.seq = seq
    self.voice_seq = voice_seq
    self.caption_seq = caption_seq

    self.context = context

  @classmethod
  def create_from(
      cls,
      chara: KiritanifyCharacterSetting,
      seq: KiritanifyScriptSequence,
      context: Context,
  ) -> 'CharacterScript':
    voice_seq = _seq_setting(seq).find_voice_seq(context)
    caption_seq = _seq_setting(seq).find_caption_seq(context)
    return cls(
      chara=chara,
      seq=seq,
      voice_seq=voice_seq,
      caption_seq=caption_seq,
      context=context,
    )

  def maybe_update_voice(self):
    ss = _seq_setting(self.seq)
    if not ss.gen_voice:
      return

    seq_missing = self.voice_seq is None
    is_changed = _seq_setting(self.seq).voice_cache_state \
      .is_changed(_global_setting(self.context), self.chara, self.seq)
    should_regenerate: bool = seq_missing or is_changed
    if should_regenerate:
      if self.voice_seq is not None:
        self._remove_sequence(self.voice_seq)
        self.voice_seq = None
      self.voice_seq = self._generate_voice_sequence()
      self._seq_setting.voice_seq_name = self.voice_seq.name
      self._seq_setting.voice_cache_state.update(
        global_setting=_global_setting(self.context),
        chara=self.chara,
        seq=self.seq,
      )
    assert self.voice_seq is not None

    self._align_sequence(
      seq=self.voice_seq,
      channel=self.chara.voice_channel(self._global_setting),
      frame_start=self.seq.frame_start,
    )
    frame_final_end = max(self.voice_seq.frame_final_end, self.seq.frame_final_end)
    if self.seq.frame_final_end != frame_final_end:
      self.seq.frame_final_end = frame_final_end

  def _generate_voice_sequence(self) -> SoundSequence:
    sound_path = self._global_setting.cache_setting.voice_path(self.chara, self.seq)
    voice_text = self._seq_setting.voice_text()

    segment = synthesize_voice(
      seika_setting=self._global_setting.seika_center,
      chara=self.chara,
      style=self._seq_setting.voice_style(self._global_setting, self.chara),
      script=voice_text,
    )
    trim_silence(segment).export(str(sound_path), format='ogg')

    voice_seq = _sequences(self.context).new_sound(
      name=f'Voice:{self.chara.chara_name}:{self.hash_text(voice_text)}',
      filepath=str(sound_path),
      channel=self.chara.voice_channel(self._global_setting),
      frame_start=self.seq.frame_final_start,
    )
    voice_seq.show_waveform = True

    return voice_seq

  def maybe_update_caption(self):
    ss = _seq_setting(self.seq)
    if not ss.gen_caption:
      return

    seq_missing = self.caption_seq is None
    is_changed = _seq_setting(self.seq).caption_cache_state \
      .is_changed(_global_setting(self.context), self.chara, self.seq)
    should_regenerate: bool = seq_missing or is_changed
    if should_regenerate:
      if self.caption_seq is not None:
        self._remove_sequence(self.caption_seq)
        self.caption_seq = None
      self.caption_seq = self._generate_caption()
      self._seq_setting.caption_seq_name = self.caption_seq.name
      self._seq_setting.caption_cache_state.update(
        global_setting=_global_setting(self.context),
        chara=self.chara,
        seq=self.seq,
      )
    assert self.caption_seq is not None

    self._align_sequence(
      seq=self.caption_seq,
      channel=self.chara.caption_channel(self._global_setting),
      frame_start=self.seq.frame_start,
      frame_final_end=self.seq.frame_final_end,
    )

  def _generate_caption(self):
    caption_style: CaptionStyle = self._seq_setting.caption_style(self._global_setting, self.chara)
    caption_text: str = self._seq_setting.caption_text()
    caption_path: Path = self._global_setting.cache_setting.caption_path(self.chara, self.seq)

    canvas_size: Tuple[int, int] = (
      self.context.scene.render.resolution_x,
      caption_style.max_height_px,
    )

    image: Image = render_text(
      canvas_size=canvas_size,
      text=caption_text,
      background_color=(0, 0, 0, 0),
      fill_color=caption_style.fill_color,
      stroke_color=caption_style.stroke_color,
      stroke_width=caption_style.stroke_width,
      font_path=caption_style.font_path,
      font_size=caption_style.font_size,
    )
    image.save(caption_path.open('bw'))

    logger.debug(f'caption_path: {caption_path}')

    image_seq: ImageSequence = _sequences(self.context).new_image(
      name=f'Caption:{self.chara.chara_name}:{self.hash_text(caption_text)}',
      filepath=str(caption_path),
      channel=self.chara.caption_channel(self._global_setting),
      frame_start=self.seq.frame_start,
    )
    image_seq.use_translation = True
    return image_seq

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

  def hash_text(self, text):
    text = self._seq_setting.voice_text()
    digest = hashlib.blake2s(text.encode('UTF-8')).digest()
    base64encoded = base64.b64encode(digest, altchars=b'-_')
    return base64encoded[:16].decode('UTF-8')

  def __repr__(self):
    return f'<CharaScript chara={self.chara.name} seq={self.seq} vseq={self.voice_seq}>'
