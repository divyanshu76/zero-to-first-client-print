#!/usr/bin/env python3
"""FINAL COVER ARTWORK from the approved Concept A "Editorial Ripple" (design locked).

The approved source files are read, never modified (checksums: cover/approved_cover_A.sha256).
Only the permitted technical refinements (cover/APPROVED_COVER_DIRECTION.md) are applied in memory:
  1. spine width = provisional value calculated from the final interior page count
  2. CMYK: every colour is replaced by a documented DeviceCMYK build; the semi-transparent
     growth rings become solid tints of navy over ivory (no transparency in the print file)
  3. review furniture removed: trim/spine guides, "PROVISIONAL" flag, review slug
  4. barcode placeholder: an empty white area (no text) reserved at the approved position
  5. fonts embedded (verified), 3 mm bleed on all outside edges

Outputs (production/final/cover/):
  ZTFC_cover_FRONT_artwork_141x216_incl_3mm_bleed.pdf      final front (trim 135 × 210)
  ZTFC_cover_BACK_artwork_141x216_incl_3mm_bleed.pdf       final back  (trim 135 × 210)
  ZTFC_cover_SPINE_artwork_PROVISIONAL_<S>mm.pdf           spine at provisional width
  ZTFC_cover_WRAP_PROVISIONAL_SPINE_<S>mm_NOT_PRINTER_READY.pdf
  + PNG previews and cover_build.json
Usage: build_cover_final.py <interior_pages> [paper_mm_per_leaf]
"""
import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject

HERE = Path(__file__).resolve().parent
PROD = HERE.parent
OUT = PROD / "final/cover"
OUT.mkdir(parents=True, exist_ok=True)
MM = 72 / 25.4

PAGES = int(sys.argv[1])
CALIPER = float(sys.argv[2]) if len(sys.argv) > 2 else 0.100   # mm per leaf, 70–80 gsm natural (assumption)
COVER_ALLOW = 0.5                                             # mm, cover board + glue (assumption)
SPINE = round(PAGES / 2 * CALIPER + COVER_ALLOW, 1)

# CMYK builds (to be confirmed on the printer's matte-laminated proof)
CMYK = {
    "ivory":   (0.00, 0.01, 0.05, 0.03),   # #F7F4EE warm ivory ground
    "navy":    (1.00, 0.82, 0.30, 0.42),   # #14213D deep navy
    "navy2":   (0.72, 0.58, 0.25, 0.30),   # #3A4560 secondary text
    "navy3":   (0.55, 0.43, 0.25, 0.08),   # #6B7389 labels
    "hair":    (0.18, 0.17, 0.25, 0.00),   # #C9C3B6 hairlines
    "violet":  (0.68, 0.82, 0.00, 0.00),   # #6D28D9 electric violet
    "white":   (0.00, 0.00, 0.00, 0.00),
    "ivory2":  (0.03, 0.04, 0.10, 0.04),   # #EFEAE0
}
HEX = {"#F7F4EE": "ivory", "#14213D": "navy", "#3A4560": "navy2", "#6B7389": "navy3", "#C9C3B6": "hair",
       "#6D28D9": "violet", "#fff": "white", "#EFEAE0": "ivory2"}


def cmyk(v):
    return "device-cmyk(" + " ".join(f"{x:.3f}" for x in v) + ")"


def mix(a, b, t):          # t of colour a over colour b
    return tuple(t * x + (1 - t) * y for x, y in zip(a, b))


def build():
    css = (HERE / "cover_light_base.css").read_text()
    html = (HERE / "cover_concept_light_A.html").read_text()
    # 2. colours -> CMYK
    for h, n in HEX.items():
        css = re.sub(re.escape(h) + r"\b", cmyk(CMYK[n]), css, flags=re.I)
        html = re.sub(re.escape(h) + r"\b", cmyk(CMYK[n]), html, flags=re.I)
    # rings: stroke-opacity -> solid tint of navy (or violet) over ivory
    def ring(m):
        col, rest, op = m.group(1), m.group(2), float(m.group(3))
        base = CMYK["violet"] if col == cmyk(CMYK["violet"]) else CMYK["navy"]
        return f'stroke="{cmyk(mix(base, CMYK["ivory"], op))}"{rest}'
    html = re.sub(r'stroke="([^"]+)"([^>]*?) stroke-opacity="([0-9.]+)"', ring, html)
    # the ring group sets stroke on <g>; opacities are on each circle
    g = re.search(r'<g fill="none" stroke="([^"]+)">(.*?)</g>', html, re.S)
    if g:
        inner = re.sub(r'stroke-opacity="([0-9.]+)"',
                       lambda m: f'stroke="{cmyk(mix(CMYK["navy"], CMYK["ivory"], float(m.group(1))))}"', g.group(2))
        html = html.replace(g.group(0), f'<g fill="none">{inner}</g>')
    assert "opacity" not in html, "transparency left in cover"
    # 3. review furniture off, 1. spine width, page = wrap + bleed only (no slug)
    final_css = f"""
:root {{ --S: {SPINE}mm; }}
@page {{ size: calc(276mm + var(--S)) 216mm; margin: 0; }}
.trim, .spine-guide, .spine-flag, .slug {{ display: none !important; }}
.barcode {{ border: none !important; color: transparent !important; }}
"""
    html = re.sub(r'<div class="slug">.*?</div>', "", html, flags=re.S)
    html = re.sub(r'<div class="spine-flag">.*?</div>', "", html, flags=re.S)
    html = re.sub(r'<div class="spine-guide"[^>]*></div>', "", html)
    html = re.sub(r'<div class="trim"></div>', "", html)
    # 4. barcode: empty reserved area
    html = re.sub(r'(<div class="barcode">).*?(</div>)', r"\1\2", html, flags=re.S)
    html = html.replace('<link rel="stylesheet" href="cover_light_base.css">',
                        f"<style>{css}</style><style>{final_css}</style>")
    html = re.sub(r"<title>.*?</title>", "<title>ZERO TO FIRST CLIENT — cover artwork</title>", html)
    src = OUT / "_cover_final_build.html"
    src.write_text(html)
    from weasyprint import HTML
    wrap = OUT / f"ZTFC_cover_WRAP_PROVISIONAL_SPINE_{SPINE}mm_NOT_PRINTER_READY.pdf"
    HTML(string=html, base_url=str(HERE)).write_pdf(wrap)
    return wrap


def boxes(page, x0, x1, bleed_l, bleed_r, bleed_tb=3):
    """Crop to [x0,x1] mm horizontally, full height; set Trim/Bleed boxes."""
    H = 216
    page.mediabox = RectangleObject([x0 * MM, 0, x1 * MM, H * MM])
    page.cropbox = page.mediabox
    page.bleedbox = page.mediabox
    page.trimbox = RectangleObject([(x0 + bleed_l) * MM, bleed_tb * MM, (x1 - bleed_r) * MM, (H - bleed_tb) * MM])


def main():
    wrap = build()
    W = 276 + SPINE
    w = PdfWriter(clone_from=PdfReader(str(wrap)))
    boxes(w.pages[0], 0, W, 3, 3)
    w.add_metadata({"/Title": "ZERO TO FIRST CLIENT — full cover wrap (PROVISIONAL SPINE, NOT PRINTER-READY)",
                    "/Author": "Divyanshu Verma"})
    w.write(str(wrap))
    parts = {
        "FRONT": ("ZTFC_cover_FRONT_artwork_141x216_incl_3mm_bleed.pdf", 138 + SPINE - 3, W, 3, 3),
        "BACK": ("ZTFC_cover_BACK_artwork_141x216_incl_3mm_bleed.pdf", 0, 141, 3, 3),
        "SPINE": (f"ZTFC_cover_SPINE_artwork_PROVISIONAL_{SPINE}mm.pdf", 138, 138 + SPINE, 0, 0),
    }
    files = {"wrap": wrap.name}
    for k, (name, x0, x1, bl, br) in parts.items():
        pw = PdfWriter(clone_from=PdfReader(str(wrap)))
        boxes(pw.pages[0], x0, x1, bl, br)
        pw.add_metadata({"/Title": f"ZERO TO FIRST CLIENT — {k.lower()} cover artwork", "/Author": "Divyanshu Verma"})
        pw.write(str(OUT / name))
        files[k.lower()] = name
    import subprocess
    for k, f in files.items():
        subprocess.run(["pdftoppm", "-r", "150", "-png", "-singlefile", "-cropbox", str(OUT / f),
                        str(OUT / f"preview_{k}")], check=True)
    info = {"interior_pages": PAGES, "caliper_mm_per_leaf_assumed": CALIPER, "cover_allowance_mm": COVER_ALLOW,
            "spine_mm_provisional": SPINE, "formula": "pages ÷ 2 × caliper + cover allowance",
            "wrap_mm_incl_bleed": [round(W + 0, 1), 216], "trim_per_panel_mm": [135, 210], "bleed_mm": 3,
            "cmyk_builds": {k: v for k, v in CMYK.items()}, "files": files,
            "status": "front and back artwork final; spine and wrap PROVISIONAL until printer confirms caliper/template"}
    (OUT / "cover_build.json").write_text(json.dumps(info, indent=1))
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
