# Prompt Cookbook

Nano Banana renders *stylized* pixel art, not grid-perfect output. Write prompts
that maximize post-processing success, then let `pixelize.py` enforce the grid
and palette.

## Base template

> `<subject>`, 2D pixel art game sprite, `<8-bit|16-bit>` retro style, flat
> colors, limited palette, crisp hard edges, no anti-aliasing, no gradients,
> centered, full body, solid magenta (#FF00FF) background, orthographic
> `<side|front|3/4 top-down>` view.

Why each clause:
- "solid magenta background" -> clean color-key with `--bg color:#FF00FF`.
- "no anti-aliasing / flat colors" -> cleaner `snap` + `quantize`.
- "centered, full body" -> predictable framing for slicing.

## Character identity block (reuse verbatim for consistency)

Keep a fixed description and paste it into every prompt for the same character:

> `a stocky dwarf knight, copper beard, dented iron helm, green tunic, round
> wooden shield`

## Style knobs

- Era: `8-bit (NES-like, ~4 colors)` vs `16-bit (SNES-like, richer shading)`.
- View: `side-scroller`, `top-down JRPG`, `3/4 isometric`.
- Palette: name it in the prompt AND enforce with `--palette` (e.g. gameboy).
