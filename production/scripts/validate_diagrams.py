#!/usr/bin/env python3
"""Diagram validation: 24 / 24 figures rebuilt as vector, with the original wording.

For each Figure N:
  * design-system/diagrams/fig-NN.html exists (vector: SVG shapes + HTML text, no raster images)
  * every word of the original diagram labels (stored from the source PDF in
    source/extracted.html) occurs in the rebuilt diagram at least as often
  * the book source carries the figure with its caption "Figure N."
Usage: validate_diagrams.py <book.html> <report.json>
"""
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r"[A-Za-z0-9\u0900-\u0963\u0966-\u097F\u20B9]+")   # dandas (U+0964/5) are punctuation


def visible(s):
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    s = re.sub(r"<svg.*?</svg>", " ", s, flags=re.S)
    s = re.sub(r"</?(b|i|strong|em)\b[^>]*>", "", s)   # inline emphasis: no word break
    s = re.sub(r"<[^>]+>", " ", s)
    return html.unescape(s)


def main():
    book, rep = sys.argv[1], sys.argv[2]
    src = (ROOT / "source/extracted.html").read_text()
    orig = {m.group(1): html.unescape(m.group(2)).replace(" | ", " ")
            for m in re.finditer(r'data-fig="(\d+)"[^>]*><div class="diagram-src" hidden>(.*?)</div>', src)}
    bk = Path(book).read_text()
    res, ok_all = [], True
    for n in range(1, 25):
        f = ROOT / f"design-system/diagrams/fig-{n:02d}.html"
        r = {"figure": n, "file": str(f.relative_to(ROOT))}
        if not f.exists():
            r.update(status="FAIL", detail="not rebuilt"); res.append(r); ok_all = False; continue
        body = f.read_text()
        a = Counter(TOKEN.findall(orig.get(str(n), "")))
        b = Counter(TOKEN.findall(visible(body)))
        missing = {k: a[k] - b[k] for k in a if a[k] > b[k]}
        raster = bool(re.search(r"<img\b|<image\b|data:image", body))
        in_book = f'data-fig="{n}"' in bk and re.search(rf"Figure {n}\.", visible(bk)) is not None
        ok = not missing and not raster and in_book
        ok_all &= ok
        r.update(status="PASS" if ok else "FAIL", original_label_words=sum(a.values()),
                 missing_words=missing, raster=raster, caption_in_book=in_book)
        res.append(r)
    passed = sum(r["status"] == "PASS" for r in res)
    out = {"summary": f"{passed} / 24 diagrams verified", "status": "PASS" if ok_all else "FAIL", "figures": res}
    Path(rep).write_text(json.dumps(out, ensure_ascii=False, indent=1))
    for r in res:
        if r["status"] != "PASS":
            print("FAIL", r)
    print("RESULT:", out["summary"])
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
