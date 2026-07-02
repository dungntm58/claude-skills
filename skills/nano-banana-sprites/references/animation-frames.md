# Recipe: Animation Frames (consistent character)

Identity drift across frames is the hard part. Feed each finished frame back as
a reference for the next.

1. Frame 0:
   ```bash
   PYTHONPATH=scripts python scripts/generate.py \
     --prompt "<identity block>, walk cycle frame 1 of 4, contact pose, 2D pixel art, 16-bit, solid magenta (#FF00FF) background, side view" \
     --out out/walk0_raw.png --pro
   PYTHONPATH=scripts python scripts/pixelize.py \
     --in out/walk0_raw.png --out out/walk0.png --bg color:#FF00FF --size 48 --colors 16
   ```
2. Frame 1 conditioned on frame 0:
   ```bash
   PYTHONPATH=scripts python scripts/generate.py \
     --prompt "<identity block>, walk cycle frame 2 of 4, passing pose, same character and palette as reference, 2D pixel art, solid magenta (#FF00FF) background, side view" \
     --reference out/walk0.png --out out/walk1_raw.png --pro
   PYTHONPATH=scripts python scripts/pixelize.py \
     --in out/walk1_raw.png --out out/walk1.png --bg color:#FF00FF --size 48 --colors 16
   ```
3. Repeat for remaining frames, always passing the previous finished frame via
   `--reference`. Use `--pro` for best coherence. Enforce one palette across
   frames with `--palette <name>` so colors match exactly.
