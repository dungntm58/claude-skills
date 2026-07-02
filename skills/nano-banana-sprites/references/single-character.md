# Recipe: Single Character Sprite

1. Generate on a keyable background:
   ```bash
   PYTHONPATH=scripts python scripts/generate.py \
     --prompt "a dwarf knight, 2D pixel art sprite, 16-bit, flat colors, no anti-aliasing, centered full body, solid magenta (#FF00FF) background, side view" \
     --out out/knight_raw.png
   ```
2. Pixelize to a 64px grid, transparent bg, 16 colors:
   ```bash
   PYTHONPATH=scripts python scripts/pixelize.py \
     --in out/knight_raw.png --out out/knight.png \
     --bg color:#FF00FF --size 64 --colors 16 --upscale 6
   ```
Tune `--size` (32/48/64) and `--colors`, or swap `--colors N` for
`--palette gameboy`. Re-run pixelize freely — it never re-hits the API.
