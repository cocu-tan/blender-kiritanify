import time
from io import BytesIO
from typing import Optional

import pydub
import requests
from pydub import AudioSegment

from kiritanify.propgroups import KiritanifyCharacterSetting, SeikaCenterSetting, VoiceStyle


def synthesize_voice(
    seika_setting: SeikaCenterSetting,
    chara: KiritanifyCharacterSetting,
    style: VoiceStyle,
    script: str,
) -> AudioSegment:
  wav_file = maybe_run_seika_center(
    seika_setting=seika_setting, cid=chara.cid,
    body=script, style=style,
  )
  return AudioSegment.from_file(wav_file)


def maybe_run_seika_center(
    seika_setting: SeikaCenterSetting,
    cid: int, body: str,
    style: VoiceStyle,
) -> BytesIO:
  for idx in range(1, 4):
    content = _maybe_run_seika_center(
      seika_setting, cid, body,
      style,
    )
    if content is not None:
      return content
    time.sleep(idx)
  raise RuntimeError("VoiceroidRequestFailure")


def _maybe_run_seika_center(
    seika_setting: SeikaCenterSetting, cid: int, body: str,
    style: VoiceStyle,
) -> Optional[BytesIO]:
  """
  Runs voiceroid and returns path for generated voice file. 
  """
  url = f"{seika_setting.addr}/SAVE2/{cid}"
  data = {
    "talktext": f"{body}",
    "effects": {
      "volume": style.volume,
      "speed": style.speed,
      "pitch": style.pitch,
      "intonation": style.intonation,
    },
    "emotions": {
    }
  }
  print(data)
  response = requests.post(
    url=url,
    json=data,
    timeout=1000,
    auth=(seika_setting.user, seika_setting.password),
  )

  if response.status_code == 200:
    if len(response.content) == 0:
      return None
    return BytesIO(response.content)
  else:
    print(f"response is not 200\nResponse: {response}")
    return None


def trim_silence(
    segment: pydub.AudioSegment,
    chunk_size_ms=10,
    silence_threshold_db=-50.0,
) -> pydub.AudioSegment:
  while segment[0:chunk_size_ms].dBFS < silence_threshold_db:
    segment = segment[chunk_size_ms:]
  while segment[-chunk_size_ms:].dBFS < silence_threshold_db:
    segment = segment[:-chunk_size_ms]
  return segment
