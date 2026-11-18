#!/usr/bin/env python3
"""Clean the author-supplied handwritten signature into a transparent PNG.

The supplied image is flat RGB with a light grey/white checkerboard painted
into the pixels (not real transparency). Ink is blue ballpoint, background is
neutral, so ink coverage (alpha) is derived from colour saturation and
darkness. No strokes are drawn, moved, smoothed or reshaped: every output
pixel's opacity comes from the same pixel of the original.

Steps
  1. alpha = max(saturation-based, darkness-based) ink density, per pixel
  2. contrast curve on alpha only (solid stroke cores, soft natural edges)
  3. drop isolated specks below MIN_SPECK px that touch no stroke
  4. flat ink colour taken from the darkest 5% of the original ink
  5. crop to ink bounds + small margin; 600 dpi metadata; native pixels kept

Usage: python3 process_signature.py <source.png> <out_dir>
Requires: Pillow, numpy, scipy
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
MIN_SPECK = 12      # px; connected blobs smaller than this, far from strokes, are dust
MARGIN = 40         # px transparent margin around the ink
DPI = 600

rgb = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float32)
sat = rgb.max(-1) - rgb.min(-1)
lum = rgb @ np.array([0.299, 0.587, 0.114], dtype=np.float32)

a_sat = np.clip((sat - 10) / (60 - 10), 0, 1)       # checker squares have sat <= ~3
a_drk = np.clip((222 - lum) / (222 - 110), 0, 1)     # grey squares are ~235
alpha = np.maximum(a_sat, a_drk) ** 0.75             # firmer cores, edges stay soft

# remove dust: tiny components not within 6 px of a real stroke
solid = alpha > 0.15
lab, n = ndimage.label(solid, structure=np.ones((3, 3)))
sizes = ndimage.sum(solid, lab, range(1, n + 1))
big = np.isin(lab, np.where(sizes >= MIN_SPECK)[0] + 1)
near = ndimage.binary_dilation(big, iterations=6)
alpha[~near] = 0
removed = int(((lab > 0) & ~near).sum())

ink_px = rgb[alpha > 0.85]
blue = np.percentile(ink_px, 5, axis=0).round().astype(np.uint8)

def export(color, name):
    h, w = alpha.shape
    out = np.zeros((h, w, 4), np.uint8)
    out[..., :3] = color
    out[..., 3] = (alpha * 255).round().astype(np.uint8)
    ys, xs = np.where(out[..., 3] > 0)
    y0, y1 = max(ys.min() - MARGIN, 0), min(ys.max() + MARGIN + 1, h)
    x0, x1 = max(xs.min() - MARGIN, 0), min(xs.max() + MARGIN + 1, w)
    img = Image.fromarray(out[y0:y1, x0:x1], "RGBA")
    p = OUT / name
    img.save(p, dpi=(DPI, DPI), optimize=True)
    return p, img.size

if __name__ == "__main__":
    print("ink colour (blue):", tuple(int(v) for v in blue), "| dust px removed:", removed)
    print(*export(blue, "DIVYANSHU_VERMA_AUTHOR_SIGNATURE.png"))
    print(*export(np.array([17, 17, 17], np.uint8), "DIVYANSHU_VERMA_AUTHOR_SIGNATURE_BLACK.png"))
    print(*export(np.array([255, 255, 255], np.uint8), "DIVYANSHU_VERMA_AUTHOR_SIGNATURE_WHITE.png"))
