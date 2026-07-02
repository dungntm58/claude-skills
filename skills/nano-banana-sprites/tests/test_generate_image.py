import pytest
from lib import client as C


def test_generate_image_requires_key():
    with pytest.raises(RuntimeError):
        C.generate_image("a knight", model=C.FLASH, env={})


def test_generate_image_rejects_empty_prompt():
    with pytest.raises(ValueError):
        C.generate_image("", model=C.FLASH, env={"GEMINI_API_KEY": "k"})
