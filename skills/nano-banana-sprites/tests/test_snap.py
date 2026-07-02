from PIL import Image
from lib import image as I


def _solid(size, color):
    return Image.new("RGBA", size, color)


def test_snap_square_dims():
    img = _solid((128, 128), (255, 0, 0, 255))
    out = I.snap_to_grid(img, 32)
    assert out.size == (32, 32)


def test_snap_nonsquare_dims():
    img = _solid((120, 240), (0, 255, 0, 255))
    out = I.snap_to_grid(img, (16, 24))
    assert out.size == (16, 24)


def test_snap_preserves_solid_color():
    img = _solid((128, 128), (10, 20, 30, 255))
    out = I.snap_to_grid(img, 8)
    assert out.getpixel((0, 0)) == (10, 20, 30, 255)
    assert out.getpixel((7, 7)) == (10, 20, 30, 255)
