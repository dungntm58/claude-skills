# Recipe: Sprite Sheet / Multi-Pose

Ask for a labeled grid, generate once, then slice.

1. Generate:
   ```bash
   PYTHONPATH=scripts python scripts/generate.py \
     --prompt "sprite sheet, 2 rows by 4 columns even grid, same dwarf knight in 8 poses (idle, walk1, walk2, walk3, attack, hurt, jump, fall), 2D pixel art, 16-bit, flat colors, no anti-aliasing, solid magenta (#FF00FF) background, evenly spaced cells" \
     --out out/knight_sheet_raw.png
   ```
2. Slice 2x4 and pixelize each cell to 48px:
   ```bash
   PYTHONPATH=scripts python scripts/pixelize.py \
     --in out/knight_sheet_raw.png --out out/pose.png \
     --slice 2x4 --bg color:#FF00FF --size 48 --colors 16
   ```
   Outputs `pose_0.png` … `pose_7.png` (row-major).

Model grids are rarely perfectly even. If cells are misaligned, regenerate with
`--pro` for tighter layout, or crop the raw sheet before slicing.
