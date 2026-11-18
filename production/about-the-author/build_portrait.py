#!/usr/bin/env python3
"""Derive the print portrait from the original author photograph.

Original (never modified): author-assets/divyanshu-portrait.jpg  (1220×1707, greyscale content in RGB)
Output: production/about-the-author/portrait_print_gray.jpg

Treatment (documented, minimal, no retouching):
  1. Convert to a single-channel greyscale image (the photograph is already
     black-and-white; this only drops the redundant RGB channels so the
     printer receives a true grey image, not RGB that may print as 4-colour).
  2. Framing crop to 4:5 (portrait page format): x 50–1170, y 210–1610 px.
     The full face, hair, shoulders and jacket stay in frame; only sky above
     and the lower legs are trimmed. No resizing, no face/skin edits, no
     sharpening, no generative changes.
  3. Saved at quality 95 with 600 ppi metadata (effective ~770 ppi at 37 mm).
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "author-assets/divyanshu-portrait.jpg"
OUT = ROOT / "production/about-the-author/portrait_print_gray.jpg"
CROP = (50, 210, 1170, 1610)   # left, top, right, bottom → 1120 × 1400 = 4:5

im = Image.open(SRC)
g = im.convert("L").crop(CROP)
g.save(OUT, quality=95, dpi=(600, 600), subsampling=0)
print(OUT, g.size, g.mode)
