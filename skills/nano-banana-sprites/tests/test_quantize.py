from PIL import Image
from lib import image as I


def _stripes(colors):
    """Vertical stripes, one column per color, height 4."""
    img = Image.new("RGBA", (len(colors), 4))
    px = img.load()
    for x, c in enumerate(colors):
        for y in range(4):
            px[x, y] = c
    return img


def _unique_rgb(img):
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size
    seen = set()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 0:
                seen.add((r, g, b))
    return seen


def test_quantize_reduces_colors():
    src = _stripes([
        (255, 0, 0, 255), (250, 0, 0, 255),
        (0, 0, 255, 255), (0, 0, 250, 255),
    ])
    out = I.quantize(src, colors=2)
    assert len(_unique_rgb(out)) <= 2


def test_quantize_preserves_alpha():
    src = Image.new("RGBA", (2, 1), (255, 0, 0, 0))
    src.putpixel((1, 0), (0, 255, 0, 255))
    out = I.quantize(src, colors=2)
    assert out.getpixel((0, 0))[3] == 0
    assert out.getpixel((1, 0))[3] == 255


def test_quantize_ignores_transparent_bg_color():
    # Magenta background keyed out to alpha=0, plus 4 distinct visible colors.
    # quantize(colors=4) must keep all 4 visible colors — the invisible bg
    # must NOT consume a palette slot.
    img = Image.new("RGBA", (8, 1), (255, 0, 255, 255))  # left half = magenta bg
    visible = [(200, 0, 0, 255), (0, 200, 0, 255),
               (0, 0, 200, 255), (200, 200, 0, 255)]
    for x, c in enumerate(visible):
        img.putpixel((4 + x, 0), c)  # right half = 4 visible colors
    keyed = I.bg_to_alpha(img, key_color=(255, 0, 255))
    out = I.quantize(keyed, colors=4)
    visible_out = {out.getpixel((4 + x, 0))[:3] for x in range(4)}
    assert len(visible_out) == 4
