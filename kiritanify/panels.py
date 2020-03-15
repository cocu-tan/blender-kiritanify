from pathlib import Path
from typing import Optional

import bpy
from bpy.types import Context, UILayout

from kiritanify.ops import (
  KIRITANIFY_OT_AddCharacter, KIRITANIFY_OT_BaisokuAlign, KIRITANIFY_OT_BaisokuCut, KIRITANIFY_OT_BaisokuInit,
  KIRITANIFY_OT_NewScriptSequence, KIRITANIFY_OT_NewTachieSequences, KIRITANIFY_OT_RemoveCacheFiles,
  KIRITANIFY_OT_RemoveCharacter, KIRITANIFY_OT_ResetVoiceStyle, KIRITANIFY_OT_RunKiritanifyForAllScripts,
  KIRITANIFY_OT_RunKiritanifyForScripts, KIRITANIFY_OT_SetDefaultCharacters, KIRITANIFY_OT_ToggleRamCaching
)
from kiritanify.propgroups import (
  KiritanifyCharacterSetting,
  KiritanifyScriptSequenceSetting,
  _global_setting,
  _script_setting,
  get_selected_script_sequence,
)
from kiritanify.types import KiritanifyScriptSequence
from kiritanify.utils import find_selected_movie_sequence, find_speed_seq_from_movie_seq, split_per_num


def get_character_from_channel(context, channel) -> KiritanifyCharacterSetting:
  global_channel = _global_setting(context)
  for chara in global_channel.characters:  # type: KiritanifyCharacterSetting
    if channel == chara.script_channel(global_channel):
      return chara


class KIRITANIFY_PT_ScriptPanel(bpy.types.Panel):
  """Kiritanify script panel"""
  bl_space_type = 'SEQUENCE_EDITOR'
  bl_region_type = 'UI'
  bl_label = 'Script'
  bl_category = 'Kiritanify'

  def draw(self, context: Context):
    layout: UILayout = self.layout
    _row = layout.row()
    _row.label(text='Run Kiritanify')
    _row = layout.row()
    _row.operator(KIRITANIFY_OT_RunKiritanifyForScripts.bl_idname, text="Selected Scripts")
    _row.operator(KIRITANIFY_OT_RunKiritanifyForAllScripts.bl_idname, text="All Scripts")

    layout.separator()
    _row = layout.row()
    _row.operator(KIRITANIFY_OT_ToggleRamCaching.bl_idname, text="ToggleRamCache")
    _row.operator(KIRITANIFY_OT_RemoveCacheFiles.bl_idname, text="RemoveCacheFiles")

    layout.separator()
    self._draw_ui_for_new_seq(context, layout)

    layout.separator()
    self._draw_ui_for_seq_settings(context, layout)

    layout.separator()
    self._maybe_draw_ui_for_voice_style(context, layout)

  @staticmethod
  def _draw_ui_for_new_seq(context: Context, layout: UILayout):
    gs = _global_setting(context)
    # new sequence button per character
    if len(gs.characters) > 0:
      _box = layout.box()
      _row = _box.row()
      for chara in gs.characters:  # type: KiritanifyCharacterSetting
        op: KIRITANIFY_OT_NewScriptSequence \
          = _row.operator(
          operator=KIRITANIFY_OT_NewScriptSequence.bl_idname,
          text=f'{chara.chara_name}',
        )
        op.chara_name = chara.chara_name

  @staticmethod
  def _draw_ui_for_seq_settings(context: Context, layout: UILayout):
    seq: Optional[KiritanifyScriptSequence] = get_selected_script_sequence(context)
    if seq is None:
      return
    setting: KiritanifyScriptSequenceSetting = _script_setting(seq)

    layout.prop(setting, "text")
    layout.label(text=f"Chara: {get_character_from_channel(context, seq.channel).chara_name}")

    row = layout.row()
    row.prop(setting, "gen_voice")
    if setting.gen_voice:
      row.prop(setting, "voice_seq_name", text="", emboss=False)

  @staticmethod
  def _maybe_draw_ui_for_voice_style(context: Context, layout: UILayout):
    seq: Optional[KiritanifyScriptSequence] = get_selected_script_sequence(context)
    if seq is None:
      return
    setting: KiritanifyScriptSequenceSetting = _script_setting(seq)

    _row = layout.row()
    _row.prop(setting, 'use_custom_voice_style', text='custom_voice')
    _row.operator(KIRITANIFY_OT_ResetVoiceStyle.bl_idname, text='Reset')
    if setting.use_custom_voice_style:
      _row = layout.row()
      _row.prop(setting.custom_voice_style, 'volume')
      _row.prop(setting.custom_voice_style, 'speed')
      _row.prop(setting.custom_voice_style, 'pitch')
      _row.prop(setting.custom_voice_style, 'intonation')


class KIRITANIFY_PT_TachiePanel(bpy.types.Panel):
  """Kiritanify tachie panel"""
  bl_space_type = 'SEQUENCE_EDITOR'
  bl_region_type = 'UI'
  bl_label = 'Tachie'
  bl_category = 'Kiritanify'

  def draw(self, context: Context):
    layout: UILayout = self.layout
    self._draw_ui_for_new_seq(context, layout)

  @staticmethod
  def _draw_ui_for_new_seq(context: Context, layout: UILayout):
    gs = _global_setting(context)
    # new sequence button per character
    if len(gs.characters) > 0:
      for chara in gs.characters:  # type: KiritanifyCharacterSetting
        _box = layout.box()
        _box.label(text=f'{chara.chara_name}')
        for seqs in split_per_num(chara.tachie_files(), 4):
          _row = _box.row()
          for e in seqs:  # type: Path
            op: KIRITANIFY_OT_NewTachieSequences \
              = _row.operator(
              operator=KIRITANIFY_OT_NewTachieSequences.bl_idname,
              text=f'{e.name}',
            )
            op.chara_name = chara.chara_name
            op.image_path = str(e)
        layout.separator()


class KIRITANIFY_PT_GlobalSettingPanel(bpy.types.Panel):
  """Kiritanify global setting panel"""
  bl_space_type = 'SEQUENCE_EDITOR'
  bl_region_type = 'UI'
  bl_label = 'GlobalSetting'
  bl_category = 'Kiritanify'

  def draw(self, context):
    layout = self.layout
    gs = _global_setting(context)

    row = layout.row()
    row.label(text="FromChan:")
    row.prop(gs, 'start_channel_for_script', slider=False, text='Script')
    row.prop(gs, 'start_channel_for_caption', slider=False, text='Caption')

    row = layout.row()
    row.label(text="Character:")
    row.operator(KIRITANIFY_OT_AddCharacter.bl_idname, text='AddChara')
    row.operator(KIRITANIFY_OT_SetDefaultCharacters.bl_idname, text='UseDefault')
    for chara in gs.characters:  # type: KiritanifyCharacterSetting
      box = layout.box()
      col = box.column(align=True)
      col.prop(chara, "chara_name")

      _row = col.row()
      _row.prop(chara, "cid", slider=False)
      op = _row.operator(KIRITANIFY_OT_RemoveCharacter.bl_idname, text='', icon='X')
      op.chara_name = chara.chara_name

      col.separator()
      _row = col.row()
      _row.prop(chara.caption_style, "fill_color")
      _row = col.row()
      _row.prop(chara.caption_style, "stroke_color")
      _row.prop(chara.caption_style, "stroke_width", slider=False)

      col.separator()
      _row = col.row()
      _row.label(text=f'Sc: {chara.script_channel(gs)}')
      _row.label(text=f'Cp: {chara.caption_channel(gs)}')
      _row.label(text=f'Vo: {chara.voice_channel(gs)}')
      _row.label(text=f'Ta: {0}')

      col.separator()
      _row = col.row()
      _row.label(text="TachieOffset")
      _row.prop(chara.tachie_style, property="offset_x_px", text="x", slider=False)
      _row.prop(chara.tachie_style, property="offset_y_px", text="y", slider=False)
      _row.prop(chara.tachie_style, property="use_flip_x", text="flip")

      col.separator()
      _row = col.row()
      _row.prop(chara.voice_style, 'volume', slider=False)
      _row.prop(chara.voice_style, 'speed', slider=False)
      _row.prop(chara.voice_style, 'pitch', slider=False)
      _row.prop(chara.voice_style, 'intonation', slider=False)


class KIRITANIFY_PT_BaisokuCutPanel(bpy.types.Panel):
  """Kiritanify seika server setting panel"""
  bl_space_type = 'SEQUENCE_EDITOR'
  bl_region_type = 'UI'
  bl_label = 'BaisokuCut'
  bl_category = 'Kiritanify'

  def draw(self, context: Context):
    layout = self.layout
    _row = layout.row()
    movie_seq = find_selected_movie_sequence(context)
    if movie_seq is None:
      return
    speed_seq = find_speed_seq_from_movie_seq(context, movie_seq)

    if speed_seq is None:
      _row.operator(KIRITANIFY_OT_BaisokuInit.bl_idname, text='Init')
    else:
      _row.operator(KIRITANIFY_OT_BaisokuCut.bl_idname, text='Cut')
      _row.operator(KIRITANIFY_OT_BaisokuAlign.bl_idname, text='Align')
      layout.label(text=movie_seq.name)
      layout.prop(speed_seq, 'speed_factor', slider=False)


class KIRITANIFY_PT_SeikaCenterSettingPanel(bpy.types.Panel):
  """Kiritanify seika server setting panel"""
  bl_space_type = 'SEQUENCE_EDITOR'
  bl_region_type = 'UI'
  bl_label = 'SeikaCenterSetting'
  bl_category = 'Kiritanify'

  def draw(self, context: Context):
    layout = self.layout
    gs = _global_setting(context)

    layout.prop(gs.seika_center, 'addr')
    layout.prop(gs.seika_center, 'user')
    layout.prop(gs.seika_center, 'password')


PANEL_CLASSES = [
  KIRITANIFY_PT_ScriptPanel,
  KIRITANIFY_PT_TachiePanel,
  KIRITANIFY_PT_BaisokuCutPanel,
  KIRITANIFY_PT_GlobalSettingPanel,
  KIRITANIFY_PT_SeikaCenterSettingPanel,
]
