from PIL import Image
from lib import image as I


def _magenta_border_red_center():
    img = Image.new("RGBA", (4, 4), (255, 0, 255, 255))  # magenta bg
    for y in (1, 2):
        for x in (1, 2):
            img.putpixel((x, y), (200, 0, 0, 255))  # red center block
    return img


def test_bg_color_key_removes_key_color():
    img = _magenta_border_red_center()
    out = I.bg_to_alpha(img, key_color=(255, 0, 255))
    assert out.getpixel((0, 0))[3] == 0    # corner magenta -> transparent
    assert out.getpixel((1, 1))[3] == 255  # red center kept


def test_bg_corner_auto_samples_corner():
    img = _magenta_border_red_center()
    out = I.bg_to_alpha(img, key_color=None)  # sample top-left = magenta
    assert out.getpixel((0, 0))[3] == 0
    assert out.getpixel((1, 1))[3] == 255


def test_bg_tolerance_matches_near_color():
    img = Image.new("RGBA", (2, 1), (250, 2, 250, 255))  # near-magenta
    img.putpixel((1, 0), (0, 0, 0, 255))
    out = I.bg_to_alpha(img, key_color=(255, 0, 255), tolerance=10)
    assert out.getpixel((0, 0))[3] == 0
    assert out.getpixel((1, 0))[3] == 255
