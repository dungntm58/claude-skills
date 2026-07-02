"""Shared output-path helpers for the CLIs."""
import os


def numbered_path(base, i, count):
    """Output path for item `i` of `count`. A single output uses `base`
    unchanged; multiple outputs splice `_i` before the extension."""
    if count == 1:
        return base
    root, ext = os.path.splitext(base)
    return f"{root}_{i}{ext}"
