from typing import Optional, Union

import bpy
from bpy.types import Context, ImageSequence, Sequence, UILayout

from kiritanify import KiritanifyScriptSequenceSetting
from kiritanify.ops import KIRITANIFY_OT_NewScriptSequence, KIRITANIFY_OT_RunKiritanifyForScripts, \
  KIRITANIFY_OT_ToggleRamCaching
from kiritanify.propgroup_utils import _global_setting, _seq_setting
from kiritanify.propgroups import KiritanifyCharacterSetting
from kiritanify.types import KiritanifyScriptSequence


def get_selected_script_sequence(context: Context) -> Optional[KiritanifyScriptSequence]:
  global_setting = _global_setting(context)
  channels = set([
    chara.caption_channel(global_setting)
    for chara in global_setting.characters  # type: KiritanifyCharacterSetting
  ])
  for seq in context.selected_sequences:  # type: Union[Sequence, ImageSequence]
    if not isinstance(seq, ImageSequence):
      continue
    if not seq.channel in channels:
      continue
    return seq


def get_character_from_channel(context, channel) -> KiritanifyCharacterSetting:
  global_channel = _global_setting(context)
  for chara in global_channel.characters:  # type: KiritanifyCharacterSetting
    if channel == chara.caption_channel(global_channel):
      return chara


class KIRITANIFY_PT_KiritanifyPanel(bpy.types.Panel):
  """Kiritanify main panel"""
  bl_space_type = 'SEQUENCE_EDITOR'
  bl_region_type = 'UI'
  bl_label = 'Kiritanify'
  bl_category = 'Kiritanify'

  def draw(self, context: Context):
    layout = self.layout

    layout.operator(KIRITANIFY_OT_RunKiritanifyForScripts.bl_idname, text="Run Kiritanify for Scripts")

    layout.separator()
    for chara in _global_setting(context).characters:  # type: KiritanifyCharacterSetting
      op: KIRITANIFY_OT_NewScriptSequence \
        = layout.operator(
        operator=KIRITANIFY_OT_NewScriptSequence.bl_idname,
        text=f'NewScript: {chara.chara_name}',
      )
      op.character_name = chara.name

    layout.separator()

    self._draw_ui_for_text_settings(context, layout)

    layout.separator()
    _row = layout.row()
    _row.operator(KIRITANIFY_OT_ToggleRamCaching.bl_idname, text="ToggleRamCache")

  @staticmethod
  def _draw_ui_for_text_settings(context: Context, layout: UILayout):
    seq: Optional[KiritanifyScriptSequence] = get_selected_script_sequence(context)
    if seq is None:
      return
    setting: KiritanifyScriptSequenceSetting = _seq_setting(seq)

    layout.prop(seq, "text")
    layout.label(text=f"Chara: {get_character_from_channel(context, seq.channel).chara_name}")

    row = layout.row()
    row.prop(setting, "gen_voice")
    if setting.gen_voice:
      row.prop(setting, "voice_seq_name", text="", emboss=False)


PANEL_CLASSES = [
  KIRITANIFY_PT_KiritanifyPanel,
]
