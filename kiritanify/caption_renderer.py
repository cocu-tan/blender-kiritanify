from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont


def lefttop_offset(outer: Tuple[int, int], inner: Tuple[int, int]):
  return tuple([
    int((o - i) / 2)
    for (o, i) in
    zip(outer, inner)
  ])


def render_text(
    canvas_size: Tuple[int, int],
    text: str,
    background_color: Tuple[float, float, float, float],
    fill_color: Tuple[float, float, float, float],
    stroke_color: Tuple[float, float, float, float],
    stroke_width: int,
    font_path: str,
    font_size: int,
) -> Image:
  _draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
  _stroke_width = int(stroke_width)
  _fill_color = tuple(
    int(c * 255)
      for c in fill_color
  )
  _stroke_color = tuple(
    int(c * 255)
      for c in stroke_color
  )
  _bg_color = tuple(
    int(c * 255)
      for c in background_color
  )
  _canvas_size = tuple(
    int(c)
      for c in canvas_size
  )

  ttf = ImageFont.truetype(
    font=font_path,
    size=font_size,
  )

  text_size = _draw.multiline_textsize(text,
    font=ttf, stroke_width=_stroke_width,
  )
  image = Image.new('RGBA',
    size=_canvas_size,
    color=_bg_color
  )

  ImageDraw.Draw(image).multiline_text(
    lefttop_offset(_canvas_size, text_size), text,
    fill=_fill_color, stroke_fill=_stroke_color, stroke_width=_stroke_width,
    font=ttf, align='center', anchor='middle',
  )
  return image


def main():
  text = "おふとん\nもぐもぐ"
  stroke_width = 5
  render_text(
    canvas_size=(1920, 1080),
    text=text,
    background_color=(1, 1, 0, 0.2),
    fill_color=(1, 1, 1, 1),
    stroke_color=(0.765, 0.175, 0.011, 1),
    stroke_width=stroke_width,
    font_path="/usr/share/fonts/TTF/mplus-1p-regular.ttf",
    font_size=80,
  ).save(Path("/tmp/ohuton.png").open('wb'))


if __name__ == '__main__':
  main()
