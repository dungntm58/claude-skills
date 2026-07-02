---
name: nano-banana-sprites
description: Use when generating 2D pixel/retro game sprites (single characters, sprite sheets, animation frames, tilesets/props) via Google's Nano Banana image API, including converting the raw output into true pixel art with a fixed grid and limited palette.
---

# Nano Banana Sprites

Generate retro game sprites with the Nano Banana image API, then post-process
raw output into true pixel art.

## When to use

- User wants pixel/retro sprites generated from a text description.
- User has a raw AI image and wants it snapped to a pixel grid / limited palette.
- Output types: single character, sprite sheet / multi-pose, animation frames,
  tileset / props.

## Core idea

Nano Banana output is *stylized* pixel art — anti-aliased and off-grid. The
value is post-processing. Generation and post-processing are separate:
`generate.py` costs API calls; `pixelize.py` is free and re-runnable. Iterate on
size/palette with `pixelize.py` without regenerating.

## Setup

- Set `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) in the environment.
- Install deps: `pip install -r requirements.txt` (Pillow required; google-genai
  optional — falls back to REST).
- Run scripts from the skill root with `PYTHONPATH=scripts`.

## Models

- Default: `gemini-3.1-flash-image` (Nano Banana 2).
- `--pro`: `gemini-3-pro-image` (Nano Banana Pro) — better multi-image
  coherence; use for animation frames and multi-pose sheets.

## Workflow

1. Pick the output type and open the matching recipe in `references/`.
2. Write the prompt (see `references/prompt-cookbook.md`). Always request a solid
   magenta (#FF00FF) background for clean cutout.
3. Generate:
   `PYTHONPATH=scripts python scripts/generate.py --prompt "..." --out out/raw.png`
4. Pixelize:
   `PYTHONPATH=scripts python scripts/pixelize.py --in out/raw.png --out out/sprite.png --bg color:#FF00FF --size 64 --colors 16 --upscale 6`
5. Re-run step 4 with different `--size` / `--colors` / `--palette` until happy.

## pixelize.py flags

- `--size N` or `--size WxH` — target pixel grid.
- `--colors N` — adaptive palette size, OR `--palette <name>` (gameboy, pico8,
  or a .gpl path) — fixed palette.
- `--bg none|corner|color:#RRGGBB` — background → transparency.
- `--slice RxC` — split a sheet/tileset into cells (row-major, before snap).
- `--upscale N` — nearest-neighbor preview scale.

Pipeline order: bg→alpha → slice → snap → quantize → upscale.

## Recipes

- `references/single-character.md`
- `references/sprite-sheet.md`
- `references/animation-frames.md`
- `references/tilesets-props.md`
- `references/prompt-cookbook.md`
