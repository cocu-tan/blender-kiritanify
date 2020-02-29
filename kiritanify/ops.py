import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

import bpy
from bpy.types import AdjustmentSequence, Context, ImageSequence, Sequence, SoundSequence

import kiritanify.types
from kiritanify.models import CharacterScript
from kiritanify.propgroups import KiritanifyCharacterSetting, _global_setting, get_selected_script_sequence
from kiritanify.utils import _current_frame, _datetime_str, _fps, _sequences

logger = logging.getLogger(__file__)
logger.setLevel(level=logging.DEBUG)


class KIRITANIFY_OT_RunKiritanifyForScripts(bpy.types.Operator):
  bl_idname = "kiritanify.run_kiritanify_for_scripts"
  bl_label = "Run KiritanifyForScripts"

  def execute(self, context: Context) -> Set[Union[int, str]]:
    global_setting = _global_setting(context)
    chara_for_chan: Dict[int, KiritanifyCharacterSetting] = {
      chara.script_channel(global_setting): chara
      for chara in global_setting.characters
    }
    logger.debug(f"chara_for_chan: {chara_for_chan!r}")

    for seq in context.selected_sequences:
      logger.debug(f"seq: {seq!r}")
      if not isinstance(seq, AdjustmentSequence):
        continue
      seq: kiritanify.types.KiritanifyScriptSequence
      chara = chara_for_chan[seq.channel]
      if chara is None:
        continue
      cs = CharacterScript.create_from(chara, seq, context)
      logger.debug(f"cs: {cs!r}")
      cs.maybe_update_voice()
      cs.maybe_update_caption()
    return {'FINISHED'}


class KIRITANIFY_OT_NewScriptSequence(bpy.types.Operator):
  bl_idname = "kiritanify.new_script_sequence"
  bl_label = "NewScriptSequence"

  character_name: bpy.props.StringProperty(name='character name')

  def execute(self, context: Context):
    current_frame = _current_frame(context)
    chara = self.find_character(context)
    global_setting = _global_setting(context)

    if chara is None:
      return {'FINISHED'}
    bpy.ops.sequencer.select_all(action='DESELECT')
    result = bpy.ops.sequencer.effect_strip_add(
      frame_start=current_frame,
      frame_end=current_frame + _fps(context) // 2,
      channel=chara.script_channel(global_setting),
      type='ADJUSTMENT',
    )
    if 'FINISHED' not in result:
      return result
    script_sequence = get_selected_script_sequence(context)
    script_sequence.name = f'Script:{chara.chara_name}:{_datetime_str()}'
    return {'FINISHED'}

  def find_character(self, context: Context) -> Optional[KiritanifyCharacterSetting]:
    setting = _global_setting(context)
    for chara in setting.characters:
      if chara.chara_name == self.character_name:
        return chara


class KIRITANIFY_OT_AddCharacter(bpy.types.Operator):
  bl_idname = 'kiritanify.add_character'
  bl_label = 'AddCharacter'

  def execute(self, context):
    charas = _global_setting(context).characters
    charas.add()
    return {'FINISHED'}


class KIRITANIFY_OT_SetDefaultCharacters(bpy.types.Operator):
  bl_idname = 'kiritanify.set_default_characters'
  bl_label = 'SetDefaultCharacters'

  def execute(self, context):
    charas = _global_setting(context).characters
    charas.clear()
    kiritan: KiritanifyCharacterSetting = charas.add()
    kiritan.chara_name = "Kiritan"
    kiritan.cid = 1700
    kiritan.caption_style.stroke_color = [0.23, 0.23, 0.23, 1.]
    kiritan.tachie_style.offset_x_px = 1400
    kiritan.tachie_style.offset_y_px = -400
    kiritan.tachie_style.use_flip_x = True
    kiritan.voice_style.speed = 1.3
    kiritan.voice_style.intonation = 1.1

    akari: KiritanifyCharacterSetting = charas.add()
    akari.chara_name = "Akari"
    akari.cid = 2000
    akari.caption_style.stroke_color = [0.75, 0.38, 0.03, 1.4]
    akari.tachie_style.offset_x_px = 1400
    akari.tachie_style.offset_y_px = -400
    akari.voice_style.speed = 1.25
    akari.voice_style.pitch = 1.08
    akari.voice_style.intonation = 1.60
    return {'FINISHED'}


class KIRITANIFY_OT_ToggleRamCaching(bpy.types.Operator):
  bl_idname = 'kiritanify.toggle_ram_caching'
  bl_label = 'ToggleRamCaching'

  def execute(self, context):
    target_channels = [
      chara.voice_channel
      for chara in _global_setting(context).characters
    ]
    for seq in _sequences(context):  # type: Sequence
      if seq.channel in target_channels and isinstance(seq, SoundSequence):
        seq.sound.use_memory_cache = not seq.sound.use_memory_cache
    return {'FINISHED'}


class KIRITANIFY_OT_RemoveCacheFiles(bpy.types.Operator):
  bl_idname = 'kiritanify.remove_cache_files'
  bl_label = 'Clear caches'

  def execute(self, context):
    referred_files: Set[Path] = set(sum(map(
      self.get_paths_from,
      _sequences(context)
    ), []))

    path = _global_setting(context).cache_setting.root_dir()
    png_paths = set(p.resolve() for p in path.glob('caption/*/*.png'))
    ogg_paths = set(p.resolve() for p in path.glob('voice/*/*.ogg'))
    existing_paths = png_paths.union(ogg_paths)
    logger.debug(f'referred_files: {referred_files}')
    logger.debug(f'existing_files: {existing_paths}')

    deletable_paths = existing_paths - referred_files
    for path in deletable_paths:  # type: Path
      path.unlink()

    return {'FINISHED'}

  def get_paths_from(self, seq: Sequence) -> List[Path]:
    if isinstance(seq, ImageSequence):
      return [
        Path(bpy.path.abspath(f'{seq.directory}/{elem.filename}'))
        for elem in seq.elements  # type: SequenceElement
      ]
    elif isinstance(seq, SoundSequence):
      return [
        Path(bpy.path.abspath(seq.sound.filepath))
      ]
    elif isinstance(seq, AdjustmentSequence):
      return []
    else:
      logger.debug(f'RemoveCacheFiles: unexpected seq{seq}')
      return []


OP_CLASSES = [
  KIRITANIFY_OT_RunKiritanifyForScripts,
  KIRITANIFY_OT_NewScriptSequence,
  KIRITANIFY_OT_AddCharacter,
  KIRITANIFY_OT_SetDefaultCharacters,
  KIRITANIFY_OT_ToggleRamCaching,
  KIRITANIFY_OT_RemoveCacheFiles,
]
