#!/usr/bin/env python3
"""Build the "Divyanshu Verma" calligraphic author mark.

Output: transparent PNGs (ink + reversed white) and the SVG master.
The lettering is TeX Gyre Chorus (calligraphic chancery face), slanted and
letter-spaced by hand; the underline flourish is a pressure-modulated
brush stroke generated here so it tapers like a real pen.

Usage: python3 build_author_mark.py <output_dir>
Requires: rsvg-convert, Pillow, fontconfig with TeX Gyre Chorus installed.
"""
import math, subprocess, sys
from pathlib import Path
from PIL import Image

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
OUT.mkdir(parents=True, exist_ok=True)

W, H = 2400, 900  # SVG user units


def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u**3*a + 3*u*u*t*b + 3*u*t*t*c + t**3*d for a, b, c, d in zip(p0, p1, p2, p3))


def brush(segments, w_max, w_min=0.6, n=220, profile=None):
    """Turn a chain of cubic beziers into a filled, tapered stroke outline."""
    pts = []
    for i, seg in enumerate(segments):
        for k in range(n if i == len(segments) - 1 else n - 1):
            pts.append(bez(*seg, k / (n - 1)))
    N = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, N - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        t = i / (N - 1)
        f = profile(t) if profile else math.sin(math.pi * t) ** 0.7
        # pen-angle modulation: thicker on downward-left strokes (chisel nib at ~35deg)
        nib = 0.55 + 0.45 * abs(math.sin(math.atan2(dy, dx) - math.radians(35)))
        w = w_min + (w_max - w_min) * f * nib
        left.append((x + nx * w / 2, y + ny * w / 2))
        right.append((x - nx * w / 2, y - ny * w / 2))
    poly = left + right[::-1]
    return "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in poly) + " Z"


# Main flourish: enters under the "D", sweeps right beneath the name,
# lifts and finishes with a small upward hook after the "a".
flourish = brush([
    ((215, 610), (420, 712), (1050, 728), (1580, 690)),
    ((1580, 690), (1880, 668), (2110, 628), (2200, 588)),
    ((2200, 588), (2250, 565), (2235, 538), (2192, 552)),
], w_max=16, w_min=0.8,
   profile=lambda t: (min(t / 0.12, 1.0) ** 0.8) * (1 - t) ** 0.5)


def svg(ink):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <g fill="{ink}">
    <g transform="translate(200,560) skewX(-9)">
      <text font-family="TeX Gyre Chorus" font-size="300" letter-spacing="-2">Divyanshu Verma</text>
    </g>
    <path d="{flourish}"/>
  </g>
</svg>'''


def render(name, ink, scale=2):
    s = OUT / f"{name}.svg"
    s.write_text(svg(ink))
    raw = OUT / f"_{name}_raw.png"
    subprocess.run(["rsvg-convert", "-z", str(scale), "-b", "none", "-o", str(raw), str(s)], check=True)
    im = Image.open(raw).convert("RGBA")
    bbox = im.getchannel("A").getbbox()
    pad = 80 * scale
    im = im.crop((max(bbox[0]-pad, 0), max(bbox[1]-pad, 0),
                  min(bbox[2]+pad, im.width), min(bbox[3]+pad, im.height)))
    png = OUT / f"{name}.png"
    im.save(png, dpi=(600, 600), optimize=True)
    raw.unlink()
    return png, im.size


if __name__ == "__main__":
    for name, ink in [("DIVYANSHU_VERMA_AUTHOR_SIGNATURE", "#111111"),
                      ("DIVYANSHU_VERMA_AUTHOR_SIGNATURE_WHITE", "#FFFFFF")]:
        p, size = render(name, ink)
        print(p, size)
