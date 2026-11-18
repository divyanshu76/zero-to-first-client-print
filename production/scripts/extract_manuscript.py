#!/usr/bin/env python3
"""Extract the tagged structure of the original manuscript PDF into JSON.

Source of truth: manuscript/ZERO_TO_FIRST_CLIENT_2026.pdf (read-only).

The manuscript is a tagged PDF (Chrome output). MuPDF exposes the structure
tree per page (TEXT_COLLECT_STRUCTURE) with correctly decoded Unicode,
including Devanagari matras and conjuncts. Each structure element carries
its index inside its parent, so the path of indices from the root identifies
an element uniquely across pages. Elements that continue across a page
break (paragraphs, tables, lists) are merged back into one node by path.

Output: production/source/manuscript_tree.json
  node = {"tag": "H2", "path": [..], "pages": [..], "children": [...]}
  text run = {"t": "text", "font": "...", "size": 9.2, "color": "#rrggbb",
              "bold": bool, "uri": "https://..." | null, "page": n,
              "bbox": [x0,y0,x1,y1], "nl": bool  (run starts a new visual line)}

Usage: python3 extract_manuscript.py [manuscript.pdf] [out.json]
"""
import json
import sys
from pathlib import Path

import re

import pymupdf

ROOT = Path(__file__).resolve().parents[2]
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "manuscript/ZERO_TO_FIRST_CLIENT_2026.pdf"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "production/source/manuscript_tree.json"

FLAGS = (pymupdf.TEXT_COLLECT_STRUCTURE | pymupdf.TEXT_PRESERVE_WHITESPACE
         | pymupdf.TEXT_PRESERVE_LIGATURES | pymupdf.TEXT_MEDIABOX_CLIP)


# Running header (y≈25pt) and footer (y≈807pt) bands on the A4 source pages.
HEADER_MAX_Y0, FOOTER_MIN_Y0 = 40, 800

# Source text-layer defect (Chrome/Skia ToUnicode): some zero-advance Devanagari
# mark glyphs decode to "mark + vowel sign", so the following real vowel-sign glyph
# doubles it (e.g. "ड़ाा", "पहुँँच"). An identical combining mark repeated back to
# back is never valid Hindi orthography, so the repeat is collapsed. Every fix
# is logged to production/audit/devanagari_textlayer_fixes.json.
DUP_MARK = re.compile(r"([\u0900-\u0903\u093A-\u094F\u0951-\u0957\u0962\u0963])\1+")
FIXES = []


def fix_marks(text, page):
    def rep(m):
        FIXES.append({"page": page, "found": m.group(0), "context": text[max(0, m.start() - 8):m.end() + 8]})
        return m.group(1)
    return DUP_MARK.sub(rep, text)


def hexcolor(c):
    return "#%06x" % c


def link_for(bbox, links):
    """Return the URI/internal target of the link annotation covering bbox."""
    x0, y0, x1, y1 = bbox
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for ln in links:
        r = ln["from"]
        if r.x0 - 1 <= cx <= r.x1 + 1 and r.y0 - 1 <= cy <= r.y1 + 1:
            if ln.get("uri"):
                return ln["uri"]
            if ln.get("page") is not None and ln["page"] >= 0:
                return f"#page={ln['page'] + 1}"
            if ln.get("nameddest") or ln.get("name"):
                return "#" + (ln.get("nameddest") or ln.get("name"))
    return None


def main():
    doc = pymupdf.open(SRC)
    nodes = {}          # path tuple -> node
    root = {"tag": "Document", "path": [], "pages": [], "children": []}
    nodes[()] = root
    order = []          # first-seen order of paths, for stable child ordering

    def get_node(path, tag, page):
        key = tuple(path)
        n = nodes.get(key)
        if n is None:
            n = {"tag": tag, "path": list(path), "pages": [], "children": []}
            nodes[key] = n
            parent = nodes[key[:-1]]
            parent["children"].append(n)
        if page not in n["pages"]:
            n["pages"].append(page)
        return n

    for pno in range(doc.page_count):
        page = doc[pno]
        links = page.get_links()
        d = page.get_text("dict", flags=FLAGS)

        def walk(block, path, parent_node):
            if block.get("type") == 2:  # structure element
                tag = block.get("raw") or block.get("std")
                if tag == "Document":
                    # the Document element repeats on every page at path []
                    for c in block.get("blocks", []):
                        walk(c, [], root)
                    return
                p = path + [block["index"]]
                n = get_node(p, tag, pno + 1)
                for c in block.get("blocks", []):
                    walk(c, p, n)
            elif block.get("type") == 0:  # text block
                first = True
                for line in block["lines"]:
                    newline = True
                    for s in line["spans"]:
                        if s["text"] == "":
                            continue
                        if pno >= 2 and (s["bbox"][1] < HEADER_MAX_Y0 or s["bbox"][1] > FOOTER_MIN_Y0):
                            continue  # running header / footer / folio
                        parent_node["children"].append({
                            "t": fix_marks(s["text"], pno + 1),
                            "font": s["font"],
                            "size": round(s["size"], 2),
                            "color": hexcolor(s["color"]),
                            "bold": bool(s["flags"] & 16) or any(w in s["font"] for w in ("Bold", "SemiBold", "Black")),
                            "uri": link_for(s["bbox"], links),
                            "page": pno + 1,
                            "bbox": [round(v, 1) for v in s["bbox"]],
                            "nl": newline and not first,
                            "blockstart": first and newline,
                        })
                        newline = False
                    first = False
            else:
                # images/vector blocks carry no text; record presence for figures
                parent_node.setdefault("graphics", []).append({"page": pno + 1, "type": block.get("type"),
                                                              "bbox": [round(v, 1) for v in block.get("bbox", (0, 0, 0, 0))]})

        for b in d["blocks"]:
            walk(b, [], root)

    # page labels and bookmarks for cross-checking
    meta = {
        "source": str(SRC.relative_to(ROOT)),
        "page_count": doc.page_count,
        "page_labels": [doc[i].get_label() for i in range(doc.page_count)],
        "toc": doc.get_toc(),
        "page_size_pt": [doc[0].rect.width, doc[0].rect.height],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"meta": meta, "tree": root}, ensure_ascii=False))
    fx = ROOT / "production/audit/devanagari_textlayer_fixes.json"
    fx.parent.mkdir(parents=True, exist_ok=True)
    fx.write_text(json.dumps({"count": len(FIXES), "rule": DUP_MARK.pattern, "fixes": FIXES}, ensure_ascii=False, indent=1))
    print(f"devanagari text-layer fixes: {len(FIXES)} (logged to {fx.relative_to(ROOT)})")
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB), {len(nodes)} structure nodes")


if __name__ == "__main__":
    main()
