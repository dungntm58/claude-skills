#!/usr/bin/env python3
"""Post-process a raw generation into pixel art.

Pipeline order: bg->alpha -> slice -> snap -> quantize -> upscale.
Slicing before snap so each cell snaps independently.
"""
import argparse
import os
import sys

from PIL import Image, ImageColor

from lib import image as I
from lib.paths import numbered_path

HERE = os.path.dirname(os.path.abspath(__file__))
PALETTE_DIR = os.path.join(HERE, "..", "references", "palettes")


def parse_color(spec):
    """'color:#RRGGBB' -> (r, g, b)."""
    hexpart = spec.split(":", 1)[1] if ":" in spec else spec
    if not hexpart.startswith("#"):
        hexpart = "#" + hexpart
    return ImageColor.getrgb(hexpart)


def parse_size(spec):
    """'32' -> (32, 32); '16x24' -> (16, 24)."""
    if "x" in spec:
        w, h = spec.lower().split("x")
        return (int(w), int(h))
    n = int(spec)
    return (n, n)


def palette_path(name):
    """Resolve a palette name or path to a .gpl file path."""
    if os.path.isfile(name):
        return name
    cand = os.path.join(PALETTE_DIR, name if name.endswith(".gpl") else name + ".gpl")
    if not os.path.isfile(cand):
        available = sorted(
            f[:-4] for f in os.listdir(PALETTE_DIR) if f.endswith(".gpl")
        )
        raise SystemExit(f"palette '{name}' not found. Available: {available}")
    return cand


def apply_pipeline(img, size=None, colors=None, palette=None, bg="none",
                   slice_dims=None, upscale_factor=None):
    imgs = [img.convert("RGBA")]
    if bg and bg != "none":
        key = None if bg == "corner" else parse_color(bg)
        imgs = [I.bg_to_alpha(x, key) for x in imgs]
    if slice_dims:
        rows, cols = slice_dims
        imgs = [cell for x in imgs for cell in I.slice_sheet(x, rows, cols)]
    if size:
        imgs = [I.snap_to_grid(x, size) for x in imgs]
    if palette:
        pal = I.load_palette(palette_path(palette))
        imgs = [I.quantize_to_palette(x, pal) for x in imgs]
    elif colors:
        imgs = [I.quantize(x, colors) for x in imgs]
    if upscale_factor:
        imgs = [I.upscale(x, upscale_factor) for x in imgs]
    return imgs


def _write(imgs, out_path):
    for i, im in enumerate(imgs):
        p = numbered_path(out_path, i, len(imgs))
        im.save(p)
        print(p)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Pixelize a raw sprite generation.")
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--size", default=None, help="N or WxH")
    ap.add_argument("--colors", type=int, default=None)
    ap.add_argument("--palette", default=None, help="name (e.g. gameboy) or .gpl path")
    ap.add_argument("--bg", default="none", help="none | corner | color:#RRGGBB")
    ap.add_argument("--slice", dest="slc", default=None, help="RxC (rows x cols)")
    ap.add_argument("--upscale", type=int, default=None)
    args = ap.parse_args(argv)

    size = parse_size(args.size) if args.size else None
    slice_dims = parse_size(args.slc) if args.slc else None

    with Image.open(args.inp) as img:
        imgs = apply_pipeline(
            img, size=size, colors=args.colors, palette=args.palette,
            bg=args.bg, slice_dims=slice_dims, upscale_factor=args.upscale,
        )
    _write(imgs, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
