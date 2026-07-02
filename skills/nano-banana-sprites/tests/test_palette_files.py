import os
from lib import image as I

PAL = os.path.join(os.path.dirname(__file__), "..", "references", "palettes")


def test_gameboy_has_four_colors():
    colors = I.load_palette(os.path.join(PAL, "gameboy.gpl"))
    assert len(colors) == 4
    assert (15, 56, 15) in colors


def test_pico8_has_sixteen_colors():
    colors = I.load_palette(os.path.join(PAL, "pico8.gpl"))
    assert len(colors) == 16
    assert (0, 0, 0) in colors
    assert (255, 241, 232) in colors
