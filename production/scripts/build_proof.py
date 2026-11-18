#!/usr/bin/env python3
"""PHASE 4 — five-page interior proof (brief §16).

The proof is cut from real typeset flows, produced by the same pipeline the
final book will use (source/book_print.html -> typeset.py -> WeasyPrint):

  1. Chapter-opening page        Chapter 01, first page
  2. Normal body-text page       Chapter 01, a following page (text + table + diagram)
  3. AI prompt page              Chapter 02, page where "25 essential copy-paste prompts" begins
  4. Printable template page     Bonus B, Template 10: Case Study
  5. About the Author            new editorial page

Folios are PROVISIONAL (final pagination is set only in Phase 6).
Outputs: production/previews/proof/ZTFC_interior_proof_5pp.pdf + PNG previews.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from pypdf import PdfReader, PdfWriter

sys.path.insert(0, str(Path(__file__).parent))
import typeset  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PROD = ROOT / "production"
OUT = PROD / "previews/proof"
OUT.mkdir(parents=True, exist_ok=True)
EDITION = sys.argv[1] if len(sys.argv) > 1 else "print"

src = BeautifulSoup((PROD / f"source/book_{EDITION}.html").read_text(), "lxml")


def section_html(sel):
    return str(src.select_one(sel))


def template_html(*nums):
    # the running-head strings are set by a marker element (as the Bonus B heading does in the book)
    return ('<section class="bonus-cont"><div style="height:0; string-set: running \'Bonus B: 20 Ready-to-Use Templates\', '
            'versohead \'Zero to First Client\'"></div>' + "".join(_template(n) for n in nums) + "</section>")


def _template(num):
    sec = next(s for s in src.select("section.bonus") if s.find("h1").get_text().startswith("Bonus B"))
    h = next(h for h in sec.find_all("h2") if h.get_text().startswith(f"Template {num}:"))
    parts = [str(h)]
    n = h.next_sibling
    while n is not None and not (getattr(n, "name", None) == "h2" and n.get_text().startswith("Template ")):
        parts.append(str(n))
        n = n.next_sibling
    return "".join(parts)


def build(name, body, start_page):
    css = (Path(typeset.DS / "proof-folios.css").read_text()
           + f"@page :first {{ counter-reset: page {start_page}; }}")   # odd = recto
    html, pending = typeset.compose(body, EDITION, extra_css=css)
    (OUT / f"_{name}.html").write_text(html)
    pdf = OUT / f"_{name}.pdf"
    doc = typeset.render(html, pdf)
    return pdf, len(doc.pages), pending


def page_texts(pdf):
    r = PdfReader(str(pdf))
    return [p.extract_text() or "" for p in r.pages]


def main():
    typeset_report = {}
    # provisional folios from the full trial typeset (front matter in roman numerals, Chapter 1 = page 1,
    # plus allowance for calculator/tracker pages); odd start = recto
    ch1, n1, p1 = build("ch01", section_html('section.chapter[data-chapter="01"]'), 1)
    ch2, n2, p2 = build("ch02", section_html('section.chapter[data-chapter="02"]'), 13)
    tpl, n3, p3 = build("tpl10", template_html("09", "10"), 193)
    ab, n4, p4 = build("about", typeset.about(EDITION), 243)
    typeset_report["flows"] = {"chapter01_pages": n1, "chapter02_pages": n2, "template10_pages": n3, "about_pages": n4,
                               "diagrams_pending_in_flows": sorted(set(p1 + p2 + p3 + p4), key=lambda x: int(x or 0))}

    t1 = page_texts(ch1)
    # body page: first page after the opener that shows Figure 2 (text + table + diagram)
    body_idx = next((i for i, t in enumerate(t1) if i > 0 and "Figure 2." in t), 1)
    t2 = page_texts(ch2)
    # a page that is predominantly prompt cards (and shows no unbuilt diagram)
    prompt_idx = next(i for i, t in enumerate(t2)
                      if len(re.findall(r"#C\d\d", t)) >= 3 and "pending" not in t)
    picks = [(ch1, 0, "chapter opening"), (ch1, body_idx, "body text"), (ch2, prompt_idx, "AI prompts"),
             (tpl, next(i for i, t in enumerate(page_texts(tpl)) if "Template 10:" in t), "printable template"), (ab, 0, "about the author")]

    w = PdfWriter()
    for pdf, idx, _ in picks:
        w.add_page(PdfReader(str(pdf)).pages[idx])
    w.add_metadata({"/Title": "ZERO TO FIRST CLIENT — 5-page interior proof (PROVISIONAL)",
                    "/Author": "Divyanshu Verma", "/Producer": "DeadCode Labs production pipeline (WeasyPrint)"})
    proof = OUT / f"ZTFC_interior_proof_5pp_{EDITION}.pdf"
    with open(proof, "wb") as fh:
        w.write(fh)

    # previews
    for f in OUT.glob(f"proof_{EDITION}_p*.png"):
        f.unlink()
    subprocess.run(["pdftoppm", "-r", "200", "-png", str(proof), str(OUT / f"proof_{EDITION}_p")], check=True)
    typeset_report["proof"] = str(proof.relative_to(ROOT))
    typeset_report["pages"] = [{"proof_page": i + 1, "role": r, "source_flow": p.name, "flow_page_index": k}
                               for i, (p, k, r) in enumerate(picks)]
    (OUT / f"proof_{EDITION}_manifest.json").write_text(json.dumps(typeset_report, indent=1))
    print(json.dumps(typeset_report, indent=1))


if __name__ == "__main__":
    main()
