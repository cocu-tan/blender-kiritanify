import bpy
from typing import Union, Set, Dict

from bpy.types import Context, ImageSequence

import kiritanify.types
from kiritanify.models import CharacterScript
from kiritanify.propgroups import KiritanifyCharacterSetting
from kiritanify.utils import _global_setting


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


OPS_CLASSES = []
