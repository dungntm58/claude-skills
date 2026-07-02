# Recipe: Tilesets / Props

1. Generate a grid of tiles/props:
   ```bash
   PYTHONPATH=scripts python scripts/generate.py \
     --prompt "tileset, 4 by 4 even grid of 16 seamless top-down grass and stone tiles, consistent lighting, tileable edges, 2D pixel art, 16-bit, flat colors, no anti-aliasing, solid magenta (#FF00FF) background" \
     --out out/tiles_raw.png
   ```
2. Slice 4x4 and snap each tile to 32px:
   ```bash
   PYTHONPATH=scripts python scripts/pixelize.py \
     --in out/tiles_raw.png --out out/tile.png \
     --slice 4x4 --bg color:#FF00FF --size 32 --colors 16
   ```
For props (items, no tiling), drop the "seamless/tileable" clause and keep the
magenta background for clean cutout.
