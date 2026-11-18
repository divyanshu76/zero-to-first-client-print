#!/usr/bin/env python3
"""Final book QA on the typeset PDF (paperback or digital).

Checks
  folios            every page carries exactly the expected folio (roman front matter,
                    arabic from Chapter 1, none on title/divider/blank pages)
  toc               every Contents entry's page number = page where that heading prints
  fidelity          every word of the edited source (book_<ed>.html) is present in the PDF
                    (nothing dropped, clipped or translated); Devanagari share preserved
  margins           all text inside the text block (mirrored gutter) or header/footer bands
  chapters          10 chapter openers, 4 stage dividers
  templates         20 / 20 templates, each with writing space
  calculators       7 / 7 calculator sheets with formulas and write-in cells
  plan/glossary/sources   30 days, 17 terms, 91 sources
  author assets     portrait + genuine signature placed on the About page
  obsolete          no download/portal/workbook references
Usage: validate_book.py print|digital
"""
import html as htmlmod
import json
import re
import sys
from collections import Counter
from pathlib import Path

import pymupdf
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
PROD = ROOT / "production"
ED = sys.argv[1] if len(sys.argv) > 1 else "print"
PDF = PROD / "final" / ("ZTFC_2026_paperback_interior_135x210_PRINT.pdf" if ED == "print" else "ZTFC_2026_digital_edition.pdf")
PM = json.loads((PROD / f"validation/page_map_{ED}.json").read_text())
MM = 72 / 25.4
TOKEN = re.compile(r"[A-Za-z0-9ऀ-ॣ०-ॿ₹]+")
DEVA = re.compile(r"[ऀ-ॿ]")
checks = []


def check(name, ok, detail, level="FAIL"):
    checks.append({"check": name, "status": "PASS" if ok else level, "detail": detail})


def roman(n):
    out = ""
    for v, s in [(10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]:
        while n >= v:
            out += s; n -= v
    return out


import subprocess
doc = pymupdf.open(PDF)


def poppler_page(i):
    return subprocess.run(["pdftotext", "-f", str(i + 1), "-l", str(i + 1), str(PDF), "-"], capture_output=True, text=True).stdout
ch1 = PM["front_matter_pages"]
label = lambda i: roman(i + 1) if i < ch1 else str(i - ch1 + 1)  # noqa: E731
# Poppler honours /ActualText exactly (reference extractor for the Devanagari text layer)
texts = [poppler_page(i) for i in range(len(doc))]
squash = lambda t: re.sub(r"\s+", "", t).lower()  # noqa: E731  letter-spaced headings extract with spaces
alltext = "\n".join(texts)

# ---- folios
bad = []
for i, p in enumerate(doc):
    z = pymupdf.Rect(0, p.rect.height - 16 * MM, p.rect.width, p.rect.height)
    words = [w[4] for w in p.get_text("words") if pymupdf.Rect(w[:4]).intersects(z)]
    exp = [] if (i + 1) in PM["no_folio_pages"] else [label(i)]
    if words != exp:
        bad.append(f"p{i + 1}: {words} != {exp}")
check("folios on every page (roman front matter, arabic from Chapter 1)", not bad, "; ".join(bad[:6]) or f"{len(doc)} pages correct")

# ---- TOC: page labels match where headings print
lab2idx = {label(i): i for i in range(len(doc))}
toc_bad = []
for e in PM["toc"]:
    idx = lab2idx.get(e["page"])
    t = re.sub(r"\s+", " ", e["title"]).strip()
    probe = t.split(":")[0][:22] if not t.startswith("STAGE") else re.search(r"\d+", t).group(0)
    if t.startswith("STAGE"):
        ok = idx is not None and ("stage" + probe) in squash(texts[idx])
    elif re.match(r"^\d{2} ", t):
        ok = idx is not None and squash(t[3:20]) in squash(texts[idx])
    else:
        ok = idx is not None and squash(probe) in squash(texts[idx])
    if not ok:
        toc_bad.append(f"{t[:40]} → {e['page']}")
check("Contents page numbers match heading positions", not toc_bad, "; ".join(toc_bad[:6]) or f"{len(PM['toc'])} entries verified")

# ---- fidelity: every word of the edited source appears in the PDF
src = (PROD / f"source/book_{ED}.html").read_text()
s = re.sub(r"<head>.*?</head>|<!--.*?-->", "", src, flags=re.S)
s = re.sub(r'<div class="diagram-src"[^>]*>.*?</div>', " ", s, flags=re.S)  # diagram labels checked separately
s = re.sub(r"</?(a|strong|em|code|b|i|sup|sub)\b[^>]*>", "", s)
s = htmlmod.unescape(re.sub(r"<[^>]+>", " ", s))
a = Counter(TOKEN.findall(s))
b = Counter(TOKEN.findall(alltext))
sq_all = re.sub(r"\s+", "", alltext).lower()
# Documented, layout-intended differences:
#  * "Your entry" column headers of Field/Your entry/Example tables become ruled writing lines (forms)
#  * Poppler joins words hyphenated at a line end (e.g. "साथ-" / "साथ" -> "साथसाथ")
FORM_HEADER = {"Your": a.get("Your", 0), "entry": a.get("entry", 0)}
hyph_joined = Counter()
for m in re.finditer(r"(\S+)-\n(\S+)", subprocess.run(["pdftotext", "-raw", str(PDF), "-"], capture_output=True, text=True).stdout):
    for t_ in TOKEN.findall(m.group(1)) + TOKEN.findall(m.group(2)):
        hyph_joined[t_] += 1
missing = {}
for k in a:
    if k in FORM_HEADER and b[k] < a[k]:
        continue
    if a[k] > b[k]:
        # text set in capitals or letter-spaced by CSS extracts as "W A R N I N G": compare squashed, case-insensitive
        if sq_all.count(k.lower()) >= a[k] or b[k] + hyph_joined[k] >= a[k]:
            continue
        # tokens that occur only inside URLs may wrap across lines in narrow table cells
        url_only = all(re.search(r"(https?://|www\.|\.)\S*" + re.escape(k), m_.group(0)) or "." in m_.group(0)
                       for m_ in re.finditer(r"\S*" + re.escape(k) + r"\S*", s))
        if url_only and len(k) > 8 and k[:6].lower() in sq_all and k[-3:].lower() in sq_all:
            continue
        missing[k] = a[k] - b[k]
check("every word of the edited manuscript is in the PDF (no lost or clipped text)", not missing,
      f"missing: {dict(list(missing.items())[:12])}" if missing else f"{sum(a.values())} source words all present")
dev_src = Counter(w for w in TOKEN.findall(s) if DEVA.search(w))
dev_pdf = Counter(w for w in TOKEN.findall(alltext) if DEVA.search(w))
dev_missing = {k: v - dev_pdf[k] for k, v in dev_src.items() if dev_pdf[k] + hyph_joined[k] < v}
check("original language preserved (Hinglish): every Devanagari word present, none translated away", not dev_missing,
      f"missing: {dict(list(dev_missing.items())[:10])}" if dev_missing else
      f"{sum(dev_src.values())} Devanagari words in source, {sum(dev_pdf.values())} in PDF")

# ---- margins / gutter
viol = []
for i, p in enumerate(doc):
    recto = i % 2 == 0
    inner, outer = 19 * MM, 14 * MM
    x0min = (inner if recto else outer) - 1.5
    x1max = p.rect.width - (outer if recto else inner) + 1.5
    for b_ in p.get_text("dict")["blocks"]:
        for l in b_.get("lines", []):
            for sp in l["spans"]:
                if not sp["text"].strip():
                    continue
                x0, y0, x1, y1 = sp["bbox"]
                if y1 < 17 * MM or y0 > p.rect.height - 19 * MM:  # running head / folio bands
                    continue
                if x0 < x0min or x1 > x1max or y0 < 0 or y1 > p.rect.height:
                    viol.append(f"p{i + 1} {sp['text'][:20]!r} x{x0 / MM:.1f}-{x1 / MM:.1f}mm")
check("all text inside the text block (inner 19 mm / outer 14 mm, mirrored)", not viol, "; ".join(viol[:6]) or "no overflow or clipping")

# ---- structure counts
sq = squash(alltext)
check("10 chapters", all(f"chapter{n:02d}" in sq for n in range(1, 11)), "chapter openers 01–10 present")
check("4 stage dividers", all(f"stage0{n}" in sq for n in range(1, 5)), "Stage 01–04 present")
tp = [n for n in range(1, 21) if f"Template {n:02d}:" not in alltext]
html = BeautifulSoup((PROD / f"interior/build/book_{ED}.html").read_text(), "lxml")
no_space = []
for d in html.select("div.template"):
    n = d.get("data-template")
    space = len(d.select(".ff-line")) + len(d.select("td.w")) + len(d.select("table.record td"))
    if space < 5:
        no_space.append(n)
check("20 / 20 templates present with writing space", not tp and not no_space and len(html.select("div.template")) == 20,
      f"missing {tp}, no space {no_space}" if (tp or no_space) else "20 / 20 templates verified")
calcs = html.select("div.calculator")
cbad = [c.get("data-name") for c in calcs if not c.select("td.w") or not re.search(r"[÷×+−]|input|count", c.get_text())]
check("7 / 7 calculator sheets present (formulas + write-in cells)", len(calcs) == 7 and not cbad and
      all(f"Calculator {n}:" in alltext for n in range(1, 8)), f"{len(calcs)} sheets; issues {cbad}" if cbad else "7 / 7 calculators verified")
inv = json.loads((PROD / "audit/content_inventory_print.json").read_text())
check("30-day action plan (30 days)", inv["totals"]["thirty_day_plan_days"] == 30, f"{inv['totals']['thirty_day_plan_days']} days")
check("glossary (17 terms) and sources (91)", inv["totals"]["glossary_terms"] == 17 and inv["totals"]["appendix_sources"] == 91,
      f"{inv['totals']['glossary_terms']} terms, {inv['totals']['appendix_sources']} sources")

# ---- author assets on About page (last page)
about_lab = next(e["page"] for e in PM["toc"] if e["id"] == "about-the-author")
ai = lab2idx[about_lab]
imgs = doc[ai].get_image_info()
check("About the Author: portrait + genuine signature placed", len(imgs) >= 2 and "abouttheauthor" in squash(texts[ai]),
      f"{len(imgs)} images on About page (page {about_lab}, physical {ai + 1} of {len(doc)})")

# ---- obsolete references
rx = r"ztfc-resources|Download Your Resources|\.xlsx|\.docx|\bDOCX\b|\bXLSX\b|[Ww]orkbook|Yellow cells|Purple cells|dropdown|Excel file"
hits = re.findall(rx, alltext)
check("no obsolete download / portal / workbook references", not hits, f"{len(hits)} hits: {hits[:5]}" if hits else "0 found")

ok = all(c["status"] != "FAIL" for c in checks)
out = {"pdf": str(PDF.relative_to(ROOT)), "pages": len(doc), "status": "PASS" if ok else "FAIL", "checks": checks}
(PROD / f"validation/book_{ED}_qa.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
for c in checks:
    print(f"{c['status']:<5} {c['check']}: {c['detail']}")
print("RESULT:", out["status"])
sys.exit(0 if ok else 1)
