from typing import Optional

import bpy
from bpy.types import Context, UILayout

from kiritanify.ops import (
  KIRITANIFY_OT_AddCharacter, KIRITANIFY_OT_NewScriptSequence, KIRITANIFY_OT_RemoveCacheFiles,
  KIRITANIFY_OT_RemoveCharacter, KIRITANIFY_OT_RunKiritanifyForScripts, KIRITANIFY_OT_SetDefaultCharacters,
  KIRITANIFY_OT_ToggleRamCaching
)
from kiritanify.propgroups import (
  KiritanifyCharacterSetting,
  KiritanifyScriptSequenceSetting,
  _global_setting,
  _seq_setting,
  get_selected_script_sequence,
)
from kiritanify.types import KiritanifyScriptSequence


def get_character_from_channel(context, channel) -> KiritanifyCharacterSetting:
  global_channel = _global_setting(context)
  for chara in global_channel.characters:  # type: KiritanifyCharacterSetting
    if channel == chara.script_channel(global_channel):
      return chara


class KIRITANIFY_PT_KiritanifyPanel(bpy.types.Panel):
  """Kiritanify main panel"""
  bl_space_type = 'SEQUENCE_EDITOR'
  bl_region_type = 'UI'
  bl_label = 'Kiritanify'
  bl_category = 'Kiritanify'

  def draw(self, context: Context):
    layout = self.layout
    gs = _global_setting(context)

    _row = layout.row()
    _row.operator(KIRITANIFY_OT_RunKiritanifyForScripts.bl_idname, text="Run Kiritanify for Scripts")
    _row = layout.row()
    _row.operator(KIRITANIFY_OT_ToggleRamCaching.bl_idname, text="ToggleRamCache")
    _row.operator(KIRITANIFY_OT_RemoveCacheFiles.bl_idname, text="RemoveCacheFiles")

    layout.separator()
    _row = layout.row()
    for chara in gs.characters:  # type: KiritanifyCharacterSetting
      op: KIRITANIFY_OT_NewScriptSequence \
        = _row.operator(
        operator=KIRITANIFY_OT_NewScriptSequence.bl_idname,
        text=f'{chara.chara_name}',
      )
      op.character_name = chara.chara_name

    layout.separator()

    self._draw_ui_for_seq_settings(context, layout)

  @staticmethod
  def _draw_ui_for_seq_settings(context: Context, layout: UILayout):
    seq: Optional[KiritanifyScriptSequence] = get_selected_script_sequence(context)
    if seq is None:
      return
    setting: KiritanifyScriptSequenceSetting = _seq_setting(seq)

    layout.prop(setting, "text")
    layout.label(text=f"Chara: {get_character_from_channel(context, seq.channel).chara_name}")

    row = layout.row()
    row.prop(setting, "gen_voice")
    if setting.gen_voice:
      row.prop(setting, "voice_seq_name", text="", emboss=False)


class KIRITANIFY_PT_KiritanifyGlobalSettingPanel(bpy.types.Panel):
  """Kiritanify global setting panel"""
  bl_space_type = 'SEQUENCE_EDITOR'
  bl_region_type = 'UI'
  bl_label = 'GlobalSetting'
  bl_category = 'Kiritanify'

  def draw(self, context):
    layout = self.layout
    gs = _global_setting(context)

    _sp = layout.split()
    _sp.label(text="FromChan:")
    row = _sp.row()
    row.prop(gs, 'start_channel_for_script', slider=False, text='Script')
    row.prop(gs, 'start_channel_for_caption', slider=False, text='Caption')

    _sp = layout.split()
    _sp.label(text="Character:")
    row = _sp.row()
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
  KIRITANIFY_PT_KiritanifyPanel,
  KIRITANIFY_PT_KiritanifyGlobalSettingPanel,
  KIRITANIFY_PT_SeikaCenterSettingPanel,
]
