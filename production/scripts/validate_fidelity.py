#!/usr/bin/env python3
"""Content-fidelity check: is every word of the original manuscript text
present, exactly as often, in a reconstructed HTML source?

Compares word-token multisets of the original PDF's text (PyMuPDF decode,
running headers/footers removed, cover pages 1–2 excluded) and the text of
an HTML file. Order-independent, so it is immune to page-vs-structure
reading order, but it catches dropped, duplicated or altered words, and
words wrongly glued together or split at line joins. Known, documented differences are allowed:
  * the 135 Devanagari doubled-mark text-layer fixes (audit log)
  * repeated table header rows on continuation pages (source artefact)
Any other insertion/deletion is reported.

Usage: validate_fidelity.py <html> <report.json> [--allow-edits edits.json]
"""
import html as htmlmod
import json
import re
import sys
from collections import Counter
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "manuscript/ZERO_TO_FIRST_CLIENT_2026.pdf"
DUP_MARK = re.compile(r"([ऀ-ःऺ-ॏ॑-ॗॢॣ])\1+")


TOKEN = re.compile(r"[A-Za-z0-9\u0900-\u097F\u20B9]+")


def original_text():
    doc = pymupdf.open(SRC)
    parts = []
    for i in range(2, doc.page_count):
        for b in doc[i].get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    if s["bbox"][1] < 40 or s["bbox"][1] > 800:
                        continue
                    parts.append(s["text"])
                parts.append("\n")
    return DUP_MARK.sub(r"\1", "".join(parts))


def html_text(path):
    s = Path(path).read_text()
    s = re.sub(r"<head>.*?</head>", "", s, flags=re.S)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", s, flags=re.S)
    s = re.sub(r"</?(a|strong|em|code|b|i|sup|sub)\b[^>]*>", "", s)  # inline: no word break
    s = re.sub(r"<[^>]+>", " ", s)
    return htmlmod.unescape(s)


def main():
    src, rep = sys.argv[1], sys.argv[2]
    allow = {"missing": Counter(), "extra": Counter()}
    reasons = []
    if len(sys.argv) > 4 and sys.argv[3] == "--allow":
        for a_ in json.loads(Path(sys.argv[4]).read_text())["allowances"]:
            allow["missing"].update(a_.get("missing", {}))
            allow["extra"].update(a_.get("extra", {}))
            reasons.append(a_["reason"])
    a = Counter(TOKEN.findall(original_text()))
    b = Counter(TOKEN.findall(html_text(src)))
    missing = {k: a[k] - b[k] for k in a if a[k] > b[k]}
    extra = {k: b[k] - a[k] for k in b if b[k] > a[k]}
    # documented, intentional differences (e.g. print edits) may be allowed
    for k, v in allow.get("missing", {}).items():
        if k in missing:
            missing[k] -= v
            if missing[k] <= 0: del missing[k]
    for k, v in allow.get("extra", {}).items():
        if k in extra:
            extra[k] -= v
            if extra[k] <= 0: del extra[k]
    res = {"html": str(src), "original_tokens": sum(a.values()), "html_tokens": sum(b.values()),
           "missing_from_html": dict(sorted(missing.items(), key=lambda x: -x[1])),
           "extra_in_html": dict(sorted(extra.items(), key=lambda x: -x[1])),
           "missing_count": sum(missing.values()), "extra_count": sum(extra.values()),
           "allowances_applied": reasons}
    res["status"] = "PASS" if not missing and not extra else "REVIEW"
    Path(rep).write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print(f"{res['status']}: original {res['original_tokens']} tokens | html {res['html_tokens']} | "
          f"missing {res['missing_count']} | extra {res['extra_count']} -> {rep}")


if __name__ == "__main__":
    main()
