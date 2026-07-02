from PIL import Image
from lib import image as I


GPL = """GIMP Palette
Name: Test
Columns: 2
#
  0   0   0	black
255 255 255	white
"""


def test_load_palette_parses_gpl(tmp_path):
    p = tmp_path / "test.gpl"
    p.write_text(GPL)
    colors = I.load_palette(str(p))
    assert colors == [(0, 0, 0), (255, 255, 255)]


def test_quantize_to_palette_maps_into_palette(tmp_path):
    src = Image.new("RGBA", (2, 1))
    src.putpixel((0, 0), (10, 10, 10, 255))     # near black
    src.putpixel((1, 0), (240, 240, 240, 255))  # near white
    out = I.quantize_to_palette(src, [(0, 0, 0), (255, 255, 255)])
    assert out.getpixel((0, 0))[:3] == (0, 0, 0)
    assert out.getpixel((1, 0))[:3] == (255, 255, 255)


def test_quantize_to_palette_preserves_alpha():
    src = Image.new("RGBA", (2, 1), (10, 10, 10, 0))
    src.putpixel((1, 0), (240, 240, 240, 255))
    out = I.quantize_to_palette(src, [(0, 0, 0), (255, 255, 255)])
    assert out.getpixel((0, 0))[3] == 0
    assert out.getpixel((1, 0))[3] == 255
