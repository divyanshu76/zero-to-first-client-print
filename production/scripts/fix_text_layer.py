#!/usr/bin/env python3
"""Repair the Devanagari text layer of a WeasyPrint PDF with /ActualText.

Why: WeasyPrint writes one ToUnicode value per glyph, taken from the first cluster the
glyph appeared in. Devanagari glyphs are shared between clusters (e.g. the ह glyph is
first seen in "हि"), so copy/paste and search of the PDF return wrong Hindi ("नहिीं" for
"नहीं") even though the printed glyphs are correct. Chrome avoided this in the original
manuscript with /ActualText; this script does the same.

How: every Devanagari word in the book is shaped with HarfBuzz using the exact font files
embedded by WeasyPrint (the PDF keeps the original glyph IDs). Each Devanagari text-show
operation in the PDF is decoded by longest-match against those shaped words, then wrapped
in a marked-content span  /Span <</ActualText (…)>> BDC … EMC  carrying the correct Unicode.
The page appearance does not change (only marked-content operators are added).

Usage: fix_text_layer.py <in.pdf> <book.html> <report.json>   (rewrites in.pdf in place)
"""
import html as htmlmod
import io
import json
import re
import sys
from pathlib import Path

import pikepdf
import uharfbuzz as hb
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = {400: "noto-sans-devanagari-devanagari-400-normal.woff2", 500: "noto-sans-devanagari-devanagari-500-normal.woff2",
         600: "noto-sans-devanagari-devanagari-600-normal.woff2", 700: "noto-sans-devanagari-devanagari-700-normal.woff2"}
WORD = re.compile(r"[ऀ-ॿ‌‍]+")


def weight_of(basefont):
    b = basefont.lower()
    if "semi-bold" in b or "semibold" in b:
        return 600
    if "bold" in b:
        return 700
    if "medium" in b:
        return 500
    return 400


def hb_font(w):
    t = TTFont(ROOT / "design-system/fonts" / FONTS[w])
    t.flavor = None
    b = io.BytesIO(); t.save(b)
    return hb.Font(hb.Face(b.getvalue()))


def shape(font, text):
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); buf.language = "hi"
    hb.shape(font, buf, {})
    return tuple(i.codepoint for i in buf.glyph_infos)


def build_dicts(words):
    dicts = {}
    for w, path in FONTS.items():
        f = hb_font(w)
        d = {}
        for word in words:
            g = shape(f, word)
            if g and g not in d:
                d[g] = word
            # also single characters / short pieces (danda, digits, isolated marks)
        for ch in "।॥०१२३४५६७८९ \u00a0,.;:?!-–—'\"“”‘’()[]/&%+=×÷₹0123456789":
            g = shape(f, ch)
            if 0 not in g:          # characters absent from this font (.notdef) are never in its runs
                d.setdefault(g, ch)
        dicts[w] = (d, max(len(k) for k in d))
    return dicts


def decode(gids, d, maxlen):
    out, i = [], 0
    while i < len(gids):
        for L in range(min(maxlen, len(gids) - i), 0, -1):
            t = d.get(tuple(gids[i:i + L]))
            if t is not None:
                out.append(t); i += L
                break
        else:
            return None
    return "".join(out)


def utf16(s):
    return pikepdf.String(b"\xfe\xff" + s.encode("utf-16-be"))


def process_stream(obj, resources, dicts, stats):
    fonts = {}
    for k, f in resources.get("/Font", {}).items():
        bf = str(f.get("/BaseFont", ""))
        if "Devanagari" in bf:
            fonts[str(k)] = weight_of(bf)
    if not fonts:
        return None
    instr = pikepdf.parse_content_stream(obj)
    out, cur, changed = [], None, False
    for operands, op in instr:
        o = str(op)
        if o == "Tf":
            cur = fonts.get(str(operands[0]))
        if o in ("TJ", "Tj") and cur is not None:
            arr = operands[0] if o == "TJ" else [operands[0]]
            gids = []
            for a in arr:
                if isinstance(a, pikepdf.String):
                    bb = bytes(a)
                    gids += [int.from_bytes(bb[i:i + 2], "big") for i in range(0, len(bb), 2)]
            if gids:
                stats["runs"] += 1
                d, ml = dicts[cur]
                text = decode(gids, d, ml)
                if text is not None:
                    out.append(pikepdf.ContentStreamInstruction(
                        [pikepdf.Name("/Span"), pikepdf.Dictionary({"/ActualText": utf16(text)})], pikepdf.Operator("BDC")))
                    out.append(pikepdf.ContentStreamInstruction(operands, op))
                    out.append(pikepdf.ContentStreamInstruction([], pikepdf.Operator("EMC")))
                    stats["fixed"] += 1; changed = True
                    continue
                stats["unresolved"].append(gids[:12])
        out.append(pikepdf.ContentStreamInstruction(operands, op))
    return pikepdf.unparse_content_stream(out) if changed else None


def main():
    pdf_path, book_html, rep = sys.argv[1], sys.argv[2], sys.argv[3]
    text = htmlmod.unescape(re.sub(r"<[^>]+>", " ", Path(book_html).read_text()))
    words = set(WORD.findall(text))
    dicts = build_dicts(words)
    stats = {"runs": 0, "fixed": 0, "unresolved": [], "dictionary_words": len(words)}
    pdf = pikepdf.open(pdf_path, allow_overwriting_input=True)
    done = set()
    for page in pdf.pages:
        res = page.obj.get("/Resources", pikepdf.Dictionary())
        new = process_stream(page, res, dicts, stats)
        if new is not None:
            page.obj.Contents = pdf.make_stream(new)
        for name, xo in res.get("/XObject", {}).items():
            if xo.get("/Subtype") == "/Form" and xo.objgen not in done:
                done.add(xo.objgen)
                new = process_stream(xo, xo.get("/Resources", res), dicts, stats)
                if new is not None:
                    xo.write(new)
    pdf.save(pdf_path, min_version="1.7")   # OpenType-CFF fonts (Inter) require PDF ≥ 1.6
    stats["unresolved_count"] = len(stats["unresolved"])
    stats["unresolved"] = stats["unresolved"][:30]
    stats["status"] = "PASS" if stats["unresolved_count"] == 0 else "REVIEW"
    Path(rep).write_text(json.dumps(stats, ensure_ascii=False, indent=1))
    print(f"Devanagari runs: {stats['runs']}, ActualText added: {stats['fixed']}, unresolved: {stats['unresolved_count']}")


if __name__ == "__main__":
    main()
