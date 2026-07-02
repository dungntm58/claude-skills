from PIL import Image
import pixelize


def _unique_rgb(img):
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size
    return {px[x, y][:3] for y in range(h) for x in range(w) if px[x, y][3] > 0}


def test_parse_color():
    assert pixelize.parse_color("color:#FF00FF") == (255, 0, 255)


def test_parse_size():
    assert pixelize.parse_size("32") == (32, 32)
    assert pixelize.parse_size("16x24") == (16, 24)


def test_pipeline_size_and_colors():
    img = Image.new("RGBA", (16, 16), (255, 0, 0, 255))
    out = pixelize.apply_pipeline(img, size=(4, 4), colors=2)
    assert len(out) == 1
    assert out[0].size == (4, 4)
    assert len(_unique_rgb(out[0])) <= 2


def test_pipeline_slice_produces_cells():
    img = Image.new("RGBA", (16, 8), (0, 128, 0, 255))
    out = pixelize.apply_pipeline(img, slice_dims=(2, 4), size=(2, 2))
    assert len(out) == 8
    assert all(c.size == (2, 2) for c in out)


def test_main_writes_files(tmp_path):
    src = tmp_path / "raw.png"
    Image.new("RGBA", (16, 16), (10, 20, 30, 255)).save(src)
    out = tmp_path / "final.png"
    rc = pixelize.main([
        "--in", str(src), "--out", str(out),
        "--size", "8", "--colors", "4",
    ])
    assert rc == 0
    assert out.exists()
    assert Image.open(out).size == (8, 8)


def test_main_slice_writes_indexed_files(tmp_path):
    src = tmp_path / "sheet.png"
    Image.new("RGBA", (16, 8), (10, 20, 30, 255)).save(src)
    out = tmp_path / "cell.png"
    rc = pixelize.main([
        "--in", str(src), "--out", str(out),
        "--slice", "2x4", "--size", "2",
    ])
    assert rc == 0
    assert (tmp_path / "cell_0.png").exists()
    assert (tmp_path / "cell_7.png").exists()
