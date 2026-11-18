#!/usr/bin/env python3
"""Folio audit: exactly one, correct page number on every page (text AND pixels).

For every page of the PDF:
  1. Text layer: the folio band (bottom 16 mm) contains exactly the expected label
     (roman i, ii … for front matter; 1, 2 … from Chapter 1; nothing on title,
     divider and blank pages), as ONE text object, character for character.
  2. Pixels: the band is rendered at 200 dpi; after masking the single expected folio
     word (+0.6 mm), no ink may remain. This catches a second number drawn on top,
     a number drawn as outlines/image, or any stray mark.
  3. Position: the folio sits at the outer corner (recto right, verso left).
  4. Optional raw check (--raw build.pdf): the pre-overlay typeset PDF must have NO
     text in the band, proving the overlay is the single source of folios.
Usage: validate_folios.py <final.pdf> <page_map.json> <report.json> [--raw raw.pdf]
"""
import json
import sys
from pathlib import Path

import numpy as np
import pymupdf

MM = 72 / 25.4
BAND = 16 * MM


def roman(n):
    out = ""
    for v, s in [(10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]:
        while n >= v:
            out += s; n -= v
    return out


def main():
    pdf, pmf, rep = sys.argv[1], sys.argv[2], sys.argv[3]
    raw = sys.argv[sys.argv.index("--raw") + 1] if "--raw" in sys.argv else None
    pm = json.loads(Path(pmf).read_text())
    ch1, nofolio = pm["front_matter_pages"], set(pm["no_folio_pages"])
    doc = pymupdf.open(pdf)
    problems, labels = [], []
    for i, p in enumerate(doc):
        W, H = p.rect.width, p.rect.height
        band = pymupdf.Rect(0, H - BAND, W, H)
        exp = "" if (i + 1) in nofolio else (roman(i + 1) if i < ch1 else str(i - ch1 + 1))
        # 1. text: spans in the band
        spans = [s for b in p.get_text("dict", clip=band)["blocks"] for l in b.get("lines", []) for s in l["spans"] if s["text"].strip()]
        txt = "".join(s["text"].strip() for s in spans)
        if txt != exp or len(spans) > (1 if exp else 0):
            problems.append({"page": i + 1, "issue": "text", "found": [s["text"] for s in spans], "expected": exp})
        # 3. position
        if spans and exp:
            x0, x1 = spans[0]["bbox"][0], spans[0]["bbox"][2]
            recto = i % 2 == 0
            if (recto and x1 < W / 2) or (not recto and x0 > W / 2):
                problems.append({"page": i + 1, "issue": "position", "x_mm": round(x0 / MM, 1)})
        # 2. pixels: render band, mask folio word, look for remaining ink
        pix = p.get_pixmap(dpi=200, clip=band, colorspace=pymupdf.csGRAY, annots=False)
        a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w).copy()
        sc = 200 / 72
        for s in spans:
            bx0, by0, bx1, by1 = s["bbox"]
            m = 0.6 * MM
            c0, c1 = int(max(0, (bx0 - m) * sc)), int(min(pix.w, (bx1 + m) * sc))
            r0, r1 = int(max(0, (by0 - m - band.y0) * sc)), int(min(pix.h, (by1 + m - band.y0) * sc))
            a[r0:r1, c0:c1] = 255
        bg = np.median(a)                        # page colour (white or ivory)
        ink = int((a < bg - 40).sum())
        if ink > 4:
            problems.append({"page": i + 1, "issue": "extra ink in folio band", "dark_pixels": ink})
        labels.append(exp)
    raw_text = []
    if raw:
        rd = pymupdf.open(raw)
        for i, p in enumerate(rd):
            band = pymupdf.Rect(0, p.rect.height - BAND, p.rect.width, p.rect.height)
            t = p.get_text(clip=band).strip()
            if t:
                raw_text.append({"page": i + 1, "text": t})
    seq_ok = labels[:ch1] == [("" if (k + 1) in nofolio else roman(k + 1)) for k in range(ch1)]
    res = {"pdf": pdf, "pages": doc.page_count, "front_matter_pages": ch1,
           "pages_with_folio": sum(1 for l in labels if l), "pages_without_folio": sorted(nofolio),
           "roman_range": [l for l in labels[:ch1] if l][:1] + [l for l in labels[:ch1] if l][-1:],
           "arabic_range": [l for l in labels[ch1:] if l][:1] + [l for l in labels[ch1:] if l][-1:],
           "problems": problems, "raw_build_text_in_folio_band": raw_text,
           "status": "PASS" if not problems and not raw_text and seq_ok else "FAIL"}
    Path(rep).write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print(f"{Path(pdf).name}: {doc.page_count} pages, {res['pages_with_folio']} with folio "
          f"(roman {res['roman_range']}, arabic {res['arabic_range']}), problems {len(problems)}, "
          f"raw-build folio text {len(raw_text)} -> {res['status']}")
    for pr in problems[:12]:
        print("   ", pr)
    sys.exit(0 if res["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
