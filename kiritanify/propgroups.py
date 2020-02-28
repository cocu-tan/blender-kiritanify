from pathlib import Path

import bpy
from bpy.types import Context
from typing import Optional

from .types import KiritanifyScriptSequence
from .utils import _datetime_str, _seq_setting


class CaptionStyle(bpy.types.PropertyGroup):
  name = 'kiritanify.caption_style'

  fill_color: bpy.props.FloatVectorProperty(
    name='Fill', subtype='COLOR_GAMMA',
    size=4, default=(1., 1., 1., 1.),
    min=0., max=1.,
  )
  stroke_color: bpy.props.FloatVectorProperty(
    name='Stroke', subtype='COLOR_GAMMA',
    size=4, default=(0., 0., 0., 1.),
    min=0., max=1.,
  )
  stroke_width: bpy.props.FloatProperty(name="Stroke width", default=8)

  def is_equal(self, style: 'CaptionStyle') -> bool:
    return (
        self.fill_color == style.fill_color
        and self.stroke_color == style.stroke_color
    )

  def update(self, style: 'CaptionStyle'):
    self.fill_color = style.fill_color
    self.stroke_color = style.stroke_color
    self.stroke_width = style.stroke_width


class TachieStyle(bpy.types.PropertyGroup):
  name = "kiritanify.tachie_style"

  offset_x_px: bpy.props.FloatProperty(name='Offset x')
  offset_y_px: bpy.props.FloatProperty(name='Offset y')
  use_flip_x: bpy.props.BoolProperty(name='Flip x', default=False)  # a.k.a mirror x

  def is_equal(self, style: 'TachieStyle') -> bool:
    return (
        self.offset_x_px == style.offset_x_px
        and self.offset_y_px == style.offset_y_px
        and self.use_flip_x == style.use_flip_x
    )

  def update(self, style: 'TachieStyle'):
    self.offset_x_px = style.offset_x_px
    self.offset_y_px = style.offset_y_px
    self.use_flip_x = style.use_flip_x


class VoiceStyle(bpy.types.PropertyGroup):
  name = 'kiritanify.voice_style'

  volume: bpy.props.FloatProperty(name="Volume", min=0, max=2.0, default=1)
  speed: bpy.props.FloatProperty(name="Speed", min=0.5, max=4.0, default=1)
  pitch: bpy.props.FloatProperty(name="Pitch", min=0.5, max=2.0, default=1)
  intonation: bpy.props.FloatProperty(name="Intonation", min=0, max=2.0, default=1)

  def is_equal(self, style: 'VoiceStyle') -> bool:
    return (
        self.volume == style.volume
        and self.speed == style.speed
        and self.pitch == style.pitch
        and self.intonation == style.intonation
    )

  def update(self, style: 'VoiceStyle'):
    self.volume = style.volume
    self.speed = style.speed
    self.pitch = style.pitch
    self.intonation = style.intonation


class ICacheState:
  def invalidate(self) -> None:
    raise NotImplementedError

  def update(
      self,
      context: Context,
      chara: 'KiritanifyCharacterSetting',
      seq: KiritanifyScriptSequence,
  ) -> None:
    raise NotImplementedError

  def is_changed(self, context, chara: 'KiritanifyCharacterSetting', seq: KiritanifyScriptSequence) -> bool:
    raise NotImplementedError


class CaptionCacheState(bpy.types.PropertyGroup, ICacheState):
  name = "kiritanify.caption_cache_state"

  invalid: bpy.props.BoolProperty(name='invalid', default=True)

  text: bpy.props.StringProperty(name='text')
  style: bpy.props.PointerProperty(type=CaptionStyle, name='style')

  def invalidate(self) -> None:
    self.ivnalid = True

  def update(
      self,
      context: Context,
      chara: 'KiritanifyCharacterSetting',
      seq: KiritanifyScriptSequence,
  ) -> None:
    _setting = _seq_setting(seq)
    text = _setting.caption_text()
    style = _setting.caption_style(context, chara)
    self.invalid = False
    self.text = text
    self.style.update(style)

  def is_changed(
      self,
      context: Context,
      chara: 'KiritanifyCharacterSetting',
      seq: KiritanifyScriptSequence,
  ) -> bool:
    if self.invalid:
      return True

    _setting = _seq_setting(seq)
    text = _setting.caption_text()
    style = _setting.caption_style(context, chara)
    return not (
        self.style.is_equal(style)
        and self.text == text
    )


class VoiceCacheState(bpy.types.PropertyGroup, ICacheState):
  name = 'kiritanify.voice_cache_state'

  invalid: bpy.props.BoolProperty(name='invalid', default=True)

  text: bpy.props.StringProperty(name='text')
  style: bpy.props.PointerProperty(type=VoiceStyle, name='style')

  def invalidate(self) -> None:
    self.invalid = True

  def update(
      self,
      context: Context,
      chara: 'KiritanifyCharacterSetting',
      seq: KiritanifyScriptSequence,
  ) -> None:
    _setting = _seq_setting(seq)
    text = _setting.voice_text()
    style = _setting.voice_style(context, chara)
    self.invalid = False
    self.text = text
    self.style.update(style)

  def is_changed(
      self,
      context: Context,
      chara: 'KiritanifyCharacterSetting',
      seq: KiritanifyScriptSequence,
  ) -> bool:
    if self.invalid:
      return True

    _setting = _seq_setting(seq)
    text = _setting.voice_text()
    style = _setting.voice_style(context, chara)

    return not (
        self.style.is_equal(style)
        and self.text == text
    )


class KiritanifyCacheSetting(bpy.types.PropertyGroup):
  name = 'kiritanify.cache_dir_setting'

  def voice_path(self, chara: 'KiritanifyCharacterSetting', seq: KiritanifyScriptSequence) -> Path:
    dir_path = self._gen_dir('voice', chara)
    return dir_path / f'{_datetime_str()}.ogg'

  def caption_path(self, chara: 'KiritanifyCharacterSetting', seq: KiritanifyScriptSequence) -> Path:
    dir_path = self._gen_dir('caption', chara)
    return dir_path / f'{_datetime_str()}.png'

  def _gen_dir(self, data_type: str, chara: 'KiritanifyCharacterSetting') -> Path:
    abspath = bpy.path.abspath(f'//{data_type}/{chara.chara_name}')
    path = Path(abspath)
    path.mkdir(exist_ok=True)
    return path


class KiritanifySequenceSetting(bpy.types.PropertyGroup):
  name = 'kiritanify.sequence_setting'

  text: bpy.props.StringProperty(name='text')

  use_custom_voice_text: bpy.props.BoolProperty(name='use custom voice text')
  custom_voice_text: bpy.props.StringProperty(name='custom voice text')

  use_custom_caption_style: bpy.props.BoolProperty(name='use custom property')
  custom_caption_style: bpy.props.PointerProperty(type=CaptionStyle, name='caption style')

  def voice_text(self) -> str:
    if self.use_custom_voice_text:
      return self.custom_voice_text
    return self.text

  def voice_style(
      self,
      context: Context,
      chara: 'KiritanifyCharacterSetting',
  ) -> VoiceStyle:
    return chara.voice_style

  def caption_text(self) -> str:
    return self.text

  def caption_style(
      self,
      context: Context,
      chara: 'KiritanifyCharacterSetting',
  ) -> CaptionStyle:
    if self.use_custom_caption_style:
      return self.custom_caption_style
    return chara.caption_style


class KiritanifyCharacterSetting(bpy.types.PropertyGroup):
  name = 'kiritanify.character_setting'

  chara_name: bpy.props.StringProperty(name='Name')
  cid: bpy.props.IntProperty(name='cid', min=0)

  caption_style: bpy.props.PointerProperty(name='Caption style', type=CaptionStyle)
  tachie_style: bpy.props.PointerProperty(name='Tachie style', type=TachieStyle)
  voice_style: bpy.props.PointerProperty(name='Voice style', type=VoiceStyle)

  tachie_directory: bpy.props.StringProperty(name="Tachie dir", subtype="DIR_PATH", default="")

  def __repr__(self):
    return f'<KiritanifyCharacterSetting chara_name={self.chara_name} cid={self.cid}>'


class SeikaServerSetting(bpy.types.PropertyGroup):
  addr: bpy.props.StringProperty(name='SeikaCenter Addr', default='http://192.168.88.7:7180')
  user: bpy.props.StringProperty(name='User name', default='SeikaServerUser')
  password: bpy.props.StringProperty(name='Password', default='SeikaServerPassword')


class KiritanifyGlobalSetting(bpy.types.PropertyGroup):
  name = "kiritanify.global_setting"

  seika_server: bpy.props.PointerProperty(type=SeikaServerSetting)

  start_channel_for_scripts: bpy.props.IntProperty('Script start channel', min=1, default=10)
  characters: bpy.props.CollectionProperty(type=KiritanifyCharacterSetting)

  def character_index(
      self,
      chara: KiritanifyCharacterSetting,
  ) -> int:
    for _idx, _chara in enumerate(self.characters):
      if chara == _chara:
        return _idx
    raise ValueError(f'Unexpected character: {chara!r}')


PROPGROUP_CLASSES = [
  CaptionStyle,
  TachieStyle,
  VoiceStyle,
  CaptionCacheState,
  VoiceCacheState,
  KiritanifyCacheSetting,
  KiritanifySequenceSetting,
  KiritanifyCharacterSetting,
  KiritanifyGlobalSetting,
]
