from PIL import Image
from lib import image as I


def test_upscale_dims():
    img = Image.new("RGBA", (4, 4), (1, 2, 3, 255))
    out = I.upscale(img, 8)
    assert out.size == (32, 32)


def test_upscale_is_nearest_no_new_colors():
    img = Image.new("RGBA", (2, 1))
    img.putpixel((0, 0), (255, 0, 0, 255))
    img.putpixel((1, 0), (0, 0, 255, 255))
    out = I.upscale(img, 4)
    px = out.load()
    seen = {px[x, 0] for x in range(out.size[0])}
    assert seen == {(255, 0, 0, 255), (0, 0, 255, 255)}
