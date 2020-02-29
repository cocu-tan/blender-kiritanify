from typing import Optional

from bpy.types import Context

from kiritanify.propgroups import KiritanifyCharacterSetting
from kiritanify.types import KiritanifyScriptSequence, SoundSequence
from kiritanify.utils import _seq_setting


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
