#!/usr/bin/env python3
"""Print derivative of the genuine signature for the black-and-white interior.

Source (unchanged): production/SOURCE_AND_BUILD/DIVYANSHU_VERMA_AUTHOR_SIGNATURE_BLACK.png
  (the supplied cleaned black version: RGBA, ink RGB(17,17,17), 1796 × 668, 600 dpi)
Output: production/about-the-author/signature_black_print_gray.png
  Greyscale + alpha ("LA"): ink = 0 (100% K when printed), alpha channel copied
  byte-for-byte, so every stroke, width and edge is identical. No redrawing, no resizing.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
src = Image.open(ROOT / "production/SOURCE_AND_BUILD/DIVYANSHU_VERMA_AUTHOR_SIGNATURE_BLACK.png")
a = np.asarray(src)[..., 3]
out = Image.fromarray(np.dstack([np.zeros_like(a), a]), "LA")
dst = ROOT / "production/about-the-author/signature_black_print_gray.png"
out.save(dst, dpi=(600, 600), optimize=True)
assert (np.asarray(out)[..., 1] == a).all()
print(dst, out.size, out.mode, "alpha identical")
