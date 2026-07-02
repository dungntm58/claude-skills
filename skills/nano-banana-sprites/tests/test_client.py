import pytest
from lib import client as C


def test_model_id_defaults_to_flash():
    assert C.model_id(pro=False) == C.FLASH
    assert C.FLASH == "gemini-3.1-flash-image"


def test_model_id_pro():
    assert C.model_id(pro=True) == C.PRO
    assert C.PRO == "gemini-3-pro-image"


def test_resolve_key_prefers_gemini(tmp_path):
    env = {"GEMINI_API_KEY": "g1", "GOOGLE_API_KEY": "g2"}
    assert C.resolve_key(env, project_dir=str(tmp_path)) == "g1"


def test_resolve_key_falls_back_to_google(tmp_path):
    env = {"GOOGLE_API_KEY": "g2"}
    assert C.resolve_key(env, project_dir=str(tmp_path)) == "g2"


def test_resolve_key_missing_raises(tmp_path):
    with pytest.raises(RuntimeError) as e:
        C.resolve_key({}, project_dir=str(tmp_path))
    assert "GEMINI_API_KEY" in str(e.value)
    assert "GOOGLE_API_KEY" in str(e.value)


def test_resolve_key_project_dotfile_overrides_env(tmp_path):
    (tmp_path / ".nano-banana.env").write_text("GEMINI_API_KEY=proj123\n")
    env = {"GEMINI_API_KEY": "global999"}
    assert C.resolve_key(env, project_dir=str(tmp_path)) == "proj123"


def test_resolve_key_dotfile_found_in_parent(tmp_path):
    (tmp_path / ".nano-banana.env").write_text("GOOGLE_API_KEY=pkey\n")
    sub = tmp_path / "a" / "b"
    sub.mkdir(parents=True)
    assert C.resolve_key({}, project_dir=str(sub)) == "pkey"


def test_resolve_key_dotfile_keyless_falls_back_to_env(tmp_path):
    (tmp_path / ".nano-banana.env").write_text("# no key here\nexport FOO=bar\n")
    env = {"GEMINI_API_KEY": "envkey"}
    assert C.resolve_key(env, project_dir=str(tmp_path)) == "envkey"


def test_resolve_key_dotfile_parses_quotes_and_export(tmp_path):
    (tmp_path / ".nano-banana.env").write_text('export GEMINI_API_KEY="quoted-key"\n')
    assert C.resolve_key({}, project_dir=str(tmp_path)) == "quoted-key"
