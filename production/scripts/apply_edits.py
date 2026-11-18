#!/usr/bin/env python3
"""Apply the documented editorial changes (source/print_edits.yaml) to the
faithful extraction and write one source per edition.

  source/extracted.html  --print_edits.yaml-->  source/book_print.html
                                                source/book_digital.html

Every edit must match exactly `count` times or the script fails.
Afterwards the edition is scanned for anything that still depends on the
removed resource portal or downloadable files (validation/removed_content_<ed>.json).

Print edition: all hyperlinks are removed (text kept), so the print PDF
carries no link annotations. Digital edition: external links are kept;
internal '#page=N' links (A4 page targets) are resolved later by the typesetter.
"""
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "production/source/extracted.html"
EDITS = ROOT / "production/source/print_edits.yaml"

FORBIDDEN = {
    "resource portal URL": r"ztfc-resources",
    "Download Your Resources": r"Download Your Resources",
    "Download label/button": r"\bDownload\b|download कीजिए|से download",
    "DOCX/XLSX file": r"\.docx|\.xlsx|\bDOCX\b|\bXLSX\b",
    "workbook": r"[Ww]orkbook",
    "spreadsheet UI (yellow/purple cells, dropdown, Excel file)": r"Yellow cells|Purple cells|dropdown|Excel file",
    "editable version / download link": r"editable version|नीचे दिए गए link",
}
FORBIDDEN_PRINT_ONLY = {"click instruction": r"click कर सकते"}


def remove_section(html, h1):
    m = re.search(r'<section class="frontmatter"><h1>' + re.escape(h1) + r"</h1>.*?</section>\n?", html, re.S)
    if not m:
        raise SystemExit(f"remove_section: section '{h1}' not found")
    return html[:m.start()] + html[m.end():], 1


def apply(edition):
    html = SRC.read_text()
    log = []
    for e in yaml.safe_load(EDITS.read_text())["edits"]:
        if e["edition"] not in ("both", edition):
            continue
        op = e.get("op", "replace")
        if op == "remove_section":
            html, n = remove_section(html, e["h1"])
            want = 1
        elif op == "regex":
            html, n = re.subn(e["pattern"], e["new"], html)
            want = e["count"]
        else:
            n = html.count(e["old"])
            want = e["count"]
            if n == want:
                html = html.replace(e["old"], e["new"])
        if n != want:
            raise SystemExit(f"EDIT {e['id']} ({edition}): expected {want} match(es), found {n}. Nothing written.")
        log.append({"id": e["id"], "matches": n, "category": e["category"],
                    "author_review": bool(e.get("author_review"))})

    if edition == "print":
        html = re.sub(r"<a\b[^>]*>(.*?)</a>", r"\1", html, flags=re.S)

    out = ROOT / f"production/source/book_{edition}.html"
    out.write_text(html)

    # residual scan (visible text + hrefs)
    visible = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    visible = re.sub(r'<div class="diagram-src"[^>]*>.*?</div>', "", visible, flags=re.S)
    hits = []
    rules = dict(FORBIDDEN, **(FORBIDDEN_PRINT_ONLY if edition == "print" else {}))
    for name, rx in rules.items():
        for m in re.finditer(rx, visible):
            ctx = re.sub(r"<[^>]+>", "", visible[max(0, m.start() - 90):m.end() + 60])
            hits.append({"rule": name, "match": m.group(0), "context": re.sub(r"\s+", " ", ctx)})
    rep = {"edition": edition, "edits_applied": log, "edit_count": len(log),
           "residual_hits": hits, "status": "PASS" if not hits else "FAIL"}
    (ROOT / f"production/validation/removed_content_{edition}.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1))
    print(f"{edition}: {len(log)} edits applied -> {out.name}; residual download/portal references: {len(hits)} [{rep['status']}]")
    for h in hits:
        print("   ", h["rule"], "|", h["context"])
    return rep["status"] == "PASS"


if __name__ == "__main__":
    ok = all([apply("print"), apply("digital")])
    sys.exit(0 if ok else 1)
