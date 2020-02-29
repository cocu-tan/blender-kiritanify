from typing import Dict, Optional, Set, Union

import bpy
from bpy.types import Context, ImageSequence, SoundSequence

import kiritanify.types
from kiritanify.models import CharacterScript
from kiritanify.propgroups import KiritanifyCharacterSetting, _global_setting
from kiritanify.utils import _current_frame, _datetime_str, _sequences


class KIRITANIFY_OT_RunKiritanifyForScripts(bpy.types.Operator):
  bl_idname = "kiritanify.run_kiritanify_for_scripts"
  bl_label = "Run KiritanifyForScripts"

  def execute(self, context: Context) -> Set[Union[int, str]]:
    global_setting = _global_setting(context)
    chara_for_chan: Dict[int, KiritanifyCharacterSetting] = {
      chara.caption_channel(global_setting): chara
      for chara in global_setting.characters
    }
    for seq in context.selected_sequences:
      if not isinstance(seq, ImageSequence):
        continue
      seq: kiritanify.types.ImageSequence
      chara = chara_for_chan[seq.channel]
      if chara is None:
        continue
      cs = CharacterScript.create_from(chara, seq, context)
      cs.maybe_update_voice()
      cs.maybe_update_caption()
    return {'FINISHED'}


class KIRITANIFY_OT_NewScriptSequence(bpy.types.Operator):
  bl_idname = "kiritanify.new_script_sequence"
  bl_label = "NewScriptSequence"

  character_name: bpy.props.StringProperty(name='character naem')

  def execute(self, context: Context):
    current_frame = _current_frame(context)
    chara = self.find_character(context)
    if chara is None:
      return {'FINISHED'}
    bpy.ops.sequencer.select_all(action='DESELECT')
    _sequences(context).new_image(
      name=f'Script:{chara.chara_name}:{_datetime_str()}',
      filepath='',
      channel=chara.caption_channel(_global_setting(context)),
      frame_start=current_frame,
    )
    return {'FINISHED'}

  def find_character(self, context: Context) -> Optional[KiritanifyCharacterSetting]:
    setting = _global_setting(context)
    for chara in setting.characters:
      if chara.chara_name == self.character_name:
        return chara


class KIRITANIFY_OT_ToggleRamCaching(bpy.types.Operator):
  bl_idname = "kiritanify.toggle_ram_caching"
  bl_label = "ToggleRamCaching"

  def execute(self, context):
    target_channels = [
      chara.voice_channel
      for chara in _global_setting(context).characters
    ]
    for seq in _sequences(context):  # type: Sequence
      if seq.channel in target_channels and isinstance(seq, SoundSequence):
        seq.sound.use_memory_cache = not seq.sound.use_memory_cache
    return {'FINISHED'}


OP_CLASSES = [
  KIRITANIFY_OT_RunKiritanifyForScripts,
  KIRITANIFY_OT_NewScriptSequence,
  KIRITANIFY_OT_ToggleRamCaching,
]
