"""Pure, deterministic image operations for sprite post-processing.

All functions take and return PIL RGBA images. No network, no filesystem
(except load_palette). Everything here is unit-testable with synthetic PNGs.
"""
from PIL import Image


def _as_size(size):
    if isinstance(size, int):
        return (size, size)
    return tuple(size)


def snap_to_grid(img, size, resample=Image.Resampling.BOX):
    """Downscale to a fixed pixel grid so each source region collapses to one
    pixel. `size` is an int (square) or (w, h). BOX averages source pixels,
    which cleans anti-aliased model output better than NEAREST."""
    return img.convert("RGBA").resize(_as_size(size), resample)


def _first_opaque_color(rgb, alpha):
    """RGB of the first fully-or-partly opaque pixel, or (0, 0, 0) if none."""
    px_a = alpha.load()
    px_rgb = rgb.load()
    w, h = alpha.size
    for y in range(h):
        for x in range(w):
            if px_a[x, y] > 0:
                return px_rgb[x, y]
    return (0, 0, 0)


def _join_alpha(reduced, alpha):
    """Re-attach `alpha` to a quantized RGB/palette image, returning RGBA."""
    out = reduced.convert("RGBA")
    out.putalpha(alpha)
    return out


def quantize(img, colors):
    """Reduce to at most `colors` colors (adaptive median-cut), preserving the
    original alpha channel. Fully-transparent pixels are excluded from the
    palette computation (their RGB is replaced with a visible color) so the
    keyed-out background never consumes one of the `colors` slots."""
    img = img.convert("RGBA")
    alpha = img.getchannel("A")
    rgb = img.convert("RGB")
    opaque_mask = alpha.point(lambda a: 255 if a > 0 else 0)
    fill = Image.new("RGB", img.size, _first_opaque_color(rgb, alpha))
    merged = Image.composite(rgb, fill, opaque_mask)
    reduced = merged.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
    return _join_alpha(reduced, alpha)


def load_palette(path):
    """Parse a GIMP .gpl palette file into a list of (r, g, b) tuples."""
    colors = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith(("GIMP", "Name:", "Columns:")):
                continue
            parts = line.split()
            if len(parts) >= 3 and all(p.isdigit() for p in parts[:3]):
                colors.append((int(parts[0]), int(parts[1]), int(parts[2])))
    return colors


def quantize_to_palette(img, palette_colors):
    """Map every pixel to the nearest color in `palette_colors` (list of
    (r, g, b)), preserving alpha. No dithering."""
    pal_img = Image.new("P", (1, 1))
    flat = []
    for c in palette_colors:
        flat.extend(c)
    flat += [0, 0, 0] * (256 - len(palette_colors))
    pal_img.putpalette(flat)

    img = img.convert("RGBA")
    alpha = img.getchannel("A")
    reduced = img.convert("RGB").quantize(palette=pal_img, dither=Image.Dither.NONE)
    return _join_alpha(reduced, alpha)


def bg_to_alpha(img, key_color=None, tolerance=30):
    """Make background transparent by color-keying. If `key_color` is None,
    sample the top-left pixel as the key. Pixels within `tolerance` (per
    channel) of the key become fully transparent."""
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size
    if key_color is None:
        key_color = px[0, 0][:3]
    kr, kg, kb = key_color
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if abs(r - kr) <= tolerance and abs(g - kg) <= tolerance and abs(b - kb) <= tolerance:
                px[x, y] = (r, g, b, 0)
    return img


def slice_sheet(img, rows, cols):
    """Split an image into rows*cols equal cells, returned row-major
    (left-to-right, top-to-bottom). Raises ValueError if dimensions do not
    divide evenly."""
    img = img.convert("RGBA")
    w, h = img.size
    if w % cols or h % rows:
        raise ValueError(f"image {w}x{h} not divisible by {cols}x{rows}")
    cw, ch = w // cols, h // rows
    cells = []
    for r in range(rows):
        for c in range(cols):
            cells.append(img.crop((c * cw, r * ch, (c + 1) * cw, (r + 1) * ch)))
    return cells


def upscale(img, factor):
    """Nearest-neighbor integer upscale for crisp preview. Adds no new colors."""
    w, h = img.size
    return img.convert("RGBA").resize((w * factor, h * factor), Image.Resampling.NEAREST)
