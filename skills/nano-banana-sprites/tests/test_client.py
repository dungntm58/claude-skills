import pytest
from lib import client as C


def test_model_id_defaults_to_flash():
    assert C.model_id(pro=False) == C.FLASH
    assert C.FLASH == "gemini-3.1-flash-image"


def test_model_id_pro():
    assert C.model_id(pro=True) == C.PRO
    assert C.PRO == "gemini-3-pro-image"


def test_resolve_key_prefers_gemini():
    env = {"GEMINI_API_KEY": "g1", "GOOGLE_API_KEY": "g2"}
    assert C.resolve_key(env) == "g1"


def test_resolve_key_falls_back_to_google():
    env = {"GOOGLE_API_KEY": "g2"}
    assert C.resolve_key(env) == "g2"


def test_resolve_key_missing_raises():
    with pytest.raises(RuntimeError) as e:
        C.resolve_key({})
    assert "GEMINI_API_KEY" in str(e.value)
    assert "GOOGLE_API_KEY" in str(e.value)
