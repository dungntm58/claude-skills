import generate
from lib import client as C


def test_build_args_selects_pro_model():
    ns = generate.parse_args(["--prompt", "knight", "--out", "o.png", "--pro"])
    assert generate.chosen_model(ns) == C.PRO


def test_build_args_defaults_to_flash():
    ns = generate.parse_args(["--prompt", "knight", "--out", "o.png"])
    assert generate.chosen_model(ns) == C.FLASH


def test_main_writes_files(tmp_path, monkeypatch):
    calls = {}

    def fake_generate_image(prompt, model, reference_images=None):
        calls["prompt"] = prompt
        calls["model"] = model
        # 1x1 red PNG bytes
        import io
        from PIL import Image
        buf = io.BytesIO()
        Image.new("RGBA", (1, 1), (255, 0, 0, 255)).save(buf, "PNG")
        return buf.getvalue()

    monkeypatch.setattr(generate.C, "generate_image", fake_generate_image)

    out = tmp_path / "raw.png"
    rc = generate.main([
        "--prompt", "a knight", "--out", str(out), "--count", "2",
    ])
    assert rc == 0
    assert (tmp_path / "raw_0.png").exists()
    assert (tmp_path / "raw_1.png").exists()
    assert calls["prompt"] == "a knight"
    assert calls["model"] == C.FLASH
