import pytest
from PIL import Image
from lib import image as I


def test_slice_returns_row_major_cells():
    img = Image.new("RGBA", (8, 4))  # cols=4, rows=2 -> 8 cells of 2x2
    cells = I.slice_sheet(img, rows=2, cols=4)
    assert len(cells) == 8
    assert all(c.size == (2, 2) for c in cells)


def test_slice_cell_content_row_major():
    img = Image.new("RGBA", (2, 2))
    img.putpixel((0, 0), (1, 1, 1, 255))   # top-left cell
    img.putpixel((1, 1), (9, 9, 9, 255))   # bottom-right cell
    cells = I.slice_sheet(img, rows=2, cols=2)  # 4 cells of 1x1
    assert cells[0].getpixel((0, 0)) == (1, 1, 1, 255)  # index 0 = row0,col0
    assert cells[3].getpixel((0, 0)) == (9, 9, 9, 255)  # index 3 = row1,col1


def test_slice_raises_on_non_divisible():
    img = Image.new("RGBA", (5, 4))
    with pytest.raises(ValueError):
        I.slice_sheet(img, rows=2, cols=2)
