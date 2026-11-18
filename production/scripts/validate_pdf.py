#!/usr/bin/env python3
"""Print-production checks for a PDF.

  * every page exactly the expected trim (default 135 × 210 mm, ±0.05 mm)
  * every font embedded (and subset) — no Type3 / non-embedded fonts
  * no dotted-circle (U+25CC) or replacement (U+FFFD) characters in the text layer
    (dotted circles appear when Devanagari marks are shaped without their base)
  * Devanagari orthography lint: no doubled combining marks
  * link annotations counted (print interior must have 0)
  * raster images: effective resolution at placed size (warn < 300 ppi)
  * blank-page detection (pages with no text, no images and no drawings)
  * colour spaces used by images

Usage: validate_pdf.py <file.pdf> <report.json> [--trim 135x210] [--expect-links 0]
"""
import json
import re
import sys
from pathlib import Path

import pymupdf

MM = 72 / 25.4
DUP_MARK = re.compile(r"([ऀ-ःऺ-ॏ॑-ॗॢॣ])\1+")


def main():
    pdf, rep = sys.argv[1], sys.argv[2]
    args = sys.argv[3:]
    trim = (135.0, 210.0)
    expect_links = None
    if "--trim" in args:
        w, h = args[args.index("--trim") + 1].split("x")
        trim = (float(w), float(h))
    allowed_blank = set()
    if "--page-map" in args:
        allowed_blank = set(json.loads(Path(args[args.index("--page-map") + 1]).read_text()).get("intentional_blank_pages", []))
    if "--expect-links" in args:
        expect_links = int(args[args.index("--expect-links") + 1])
    doc = pymupdf.open(pdf)
    checks, pages = [], []

    def check(name, ok, detail, level="FAIL"):
        checks.append({"check": name, "status": "PASS" if ok else level, "detail": detail})

    bad_size, fonts, links, low_res, blanks, glyph_issues, ortho = [], {}, 0, [], [], [], []
    img_cs = set()
    for i, p in enumerate(doc):
        w, h = p.rect.width / MM, p.rect.height / MM
        if abs(w - trim[0]) > 0.05 or abs(h - trim[1]) > 0.05:
            bad_size.append(f"p{i + 1}: {w:.2f}×{h:.2f} mm")
        for f in p.get_fonts(full=True):
            xref, ext, ftype, name = f[0], f[1], f[2], f[3]
            fonts[name] = {"type": ftype, "embedded": ext != "n/a" and ext != "", "ext": ext}
        links += len([l for l in p.get_links()])
        text = p.get_text()
        # Devanagari checks use Poppler, which honours /ActualText (MuPDF splits ActualText spans)
        import subprocess as _sp
        ptext = _sp.run(["pdftotext", "-f", str(i + 1), "-l", str(i + 1), pdf, "-"], capture_output=True, text=True).stdout
        if "◌" in text or "�" in text:
            glyph_issues.append(f"p{i + 1}")
        for m in DUP_MARK.finditer(ptext):
            ortho.append(f"p{i + 1}: {ptext[max(0, m.start() - 6):m.end() + 6]!r}")
        imgs = p.get_image_info(xrefs=True)
        for im in imgs:
            bw, bh = im["bbox"][2] - im["bbox"][0], im["bbox"][3] - im["bbox"][1]
            if bw <= 0 or bh <= 0:
                continue
            ppi = min(im["width"] / (bw / 72), im["height"] / (bh / 72))
            img_cs.add(str(im.get("colorspace")))
            if ppi < 300:
                low_res.append(f"p{i + 1}: {im['width']}×{im['height']} px at {bw / MM:.1f}×{bh / MM:.1f} mm = {ppi:.0f} ppi")
        if not text.strip() and not imgs and not p.get_drawings() and (i + 1) not in allowed_blank:
            blanks.append(i + 1)
        pages.append({"page": i + 1, "label": p.get_label(), "size_mm": [round(w, 2), round(h, 2)],
                      "images": len(imgs)})

    check("page count", doc.page_count > 0, f"{doc.page_count} pages")
    check(f"trim size {trim[0]:g} × {trim[1]:g} mm on every page", not bad_size, "; ".join(bad_size) or "all pages exact")
    nonemb = [n for n, f in fonts.items() if not f["embedded"]]
    check("all fonts embedded", not nonemb, ", ".join(nonemb) or f"{len(fonts)} fonts, all embedded")
    t3 = [n for n, f in fonts.items() if f["type"] == "Type3"]
    check("no Type3 fonts", not t3, ", ".join(t3) or "none", level="WARN")
    check("no dotted-circle / replacement glyphs (broken shaping)", not glyph_issues, ", ".join(glyph_issues) or "none")
    check("Devanagari orthography (no doubled marks)", not ortho, "; ".join(ortho[:10]) or "clean")
    if expect_links is not None:
        check(f"link annotations = {expect_links}", links == expect_links, f"{links} found")
    else:
        check("link annotations (informational)", True, f"{links} found")
    check("raster images ≥ 300 ppi effective", not low_res, "; ".join(low_res) or "all images ≥ 300 ppi", level="WARN")
    check("no accidental blank pages", not blanks,
          (f"blank pages: {blanks}" if blanks else "none") + (f" (intentional blank versos before recto openers: {len(allowed_blank)})" if allowed_blank else ""),
          level="WARN")

    res = {"file": pdf, "pages": doc.page_count, "fonts": fonts, "image_colourspaces": sorted(img_cs),
           "checks": checks, "page_detail": pages,
           "status": "FAIL" if any(c["status"] == "FAIL" for c in checks) else "PASS"}
    Path(rep).write_text(json.dumps(res, ensure_ascii=False, indent=1))
    for c in checks:
        print(f"{c['status']:<5} {c['check']}: {c['detail']}")
    print("fonts:", ", ".join(sorted(fonts)))
    print("RESULT:", res["status"])
    sys.exit(1 if res["status"] == "FAIL" else 0)


if __name__ == "__main__":
    main()
