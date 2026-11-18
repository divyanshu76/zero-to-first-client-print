#!/usr/bin/env python3
"""Render the LIGHT cover concepts A and B to PDF and preview images.

Outputs (production/cover/ and production/previews/cover/):
  ZTFC_cover_CONCEPT_light_{A,B}_not_for_print.pdf
  cover_{A,B}_full.png    full wrap with bleed, guides and review slug
  cover_{A,B}_front.png   front panel at trim
  cover_{A,B}_back.png    back panel at trim
  cover_{A,B}_spine.png   spine at trim (provisional 13 mm)
  cover_light_A_vs_B_fronts.png, cover_light_A_vs_B_backs.png
Spine width is a PROVISIONAL placeholder (13 mm), not final.
"""
import subprocess
from pathlib import Path

from PIL import Image
from weasyprint import HTML

HERE = Path(__file__).resolve().parent
PREV = HERE.parent / "previews/cover"
PREV.mkdir(parents=True, exist_ok=True)
DPI = 200
MM = DPI / 25.4
SPINE = 13.0


def box(x0, y0, x1, y1):
    return tuple(round(v * MM) for v in (x0, y0, x1, y1))


for c in ("A", "B"):
    pdf = HERE / f"ZTFC_cover_CONCEPT_light_{c}_not_for_print.pdf"
    HTML(HERE / f"cover_concept_light_{c}.html").write_pdf(pdf)
    stem = PREV / f"cover_{c}_full"
    subprocess.run(["pdftoppm", "-r", str(DPI), "-png", "-singlefile", str(pdf), str(stem)], check=True)
    full = Image.open(f"{stem}.png")
    full.crop(box(3, 3, 138, 213)).save(PREV / f"cover_{c}_back.png")
    full.crop(box(138, 3, 138 + SPINE, 213)).save(PREV / f"cover_{c}_spine.png")
    full.crop(box(138 + SPINE, 3, 273 + SPINE, 213)).save(PREV / f"cover_{c}_front.png")
    print("rendered", pdf.name)

for side in ("front", "back"):
    a, b = Image.open(PREV / f"cover_A_{side}.png"), Image.open(PREV / f"cover_B_{side}.png")
    pad = 40
    out = Image.new("RGB", (a.width + b.width + pad * 3, a.height + pad * 2), (150, 150, 150))
    out.paste(a, (pad, pad)); out.paste(b, (a.width + pad * 2, pad))
    out.save(PREV / f"cover_light_A_vs_B_{side}s.png")
print("previews in", PREV)
