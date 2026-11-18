#!/usr/bin/env python3
"""Assemble and typeset the complete book (paperback interior or digital edition).

  source/book_{edition}.html  (documented edits applied)
  + front matter (half-title, title page), rebuilt Contents, Bonus C calculator sheets,
    About the Author, rebuilt diagrams, worksheet writing space
  -> WeasyPrint (two passes: page map -> literal TOC numbers -> verify)
  -> folio overlay (roman front matter, arabic from Chapter 1, as in the original)
  -> final/ZTFC_<edition>.pdf

Usage: build_book.py print|digital
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import pikepdf
import pymupdf
from bs4 import BeautifulSoup, NavigableString
from pypdf import PdfReader, PdfWriter

sys.path.insert(0, str(Path(__file__).parent))
import typeset  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PROD = ROOT / "production"
FINAL = PROD / "final"
BUILD = PROD / "interior/build"
FINAL.mkdir(parents=True, exist_ok=True)
BUILD.mkdir(parents=True, exist_ok=True)
EDITION = sys.argv[1] if len(sys.argv) > 1 else "print"


def slug(t):
    t = re.sub(r"<[^>]+>", "", t)
    s = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
    return s or "x"


def new(soup, html):
    return BeautifulSoup(html, "html.parser")


# ---------------------------------------------------------------- worksheet writing space
FILL_COL = re.compile(r"^(Idea [ABC]|Your\b.*|आपका जवाब|Notes|Evidence.*|Score \(0 से 5\)|Done|Due|Basic|Standard|Premium)$")
EXTRA_BLANK_ROWS = {  # heading text -> minimum number of blank write-in rows
    "Step 1: Skill assessment": 5, "Template 02: Skill Assessment": 5, "Template 04: Competitor Analysis": 6,
    "Competitor Analysis Worksheet": 6, "Daily tracker": 7,
}


def pad_tables(soup, log):
    for t in soup.find_all("table"):
        head = [th.get_text(" ", strip=True) for th in t.select("thead th")]
        if not head:
            continue
        L = len(head)
        fill = [j for j, h in enumerate(head) if FILL_COL.match(h)]
        anchor_last = head[-1].startswith("Example")
        h = t.find_previous(["h2", "h3"])
        htxt = h.get_text(" ", strip=True) if h else ""
        blank_rows = 0
        for tr in t.select("tbody tr"):
            cells = tr.find_all(["td", "th"])
            if not cells:
                blank_rows += 1
                for _ in range(L):
                    tr.append(new(soup, '<td class="w"></td>'))
                continue
            if len(cells) >= L or any(c.get("colspan") for c in cells):
                continue
            need = L - len(cells)
            real = [c.extract() for c in cells]
            last = real.pop() if anchor_last and len(real) > 1 else None
            out = []
            for j in range(L):
                if j == L - 1 and last is not None:
                    out.append(last)
                elif j in fill and need > 0:
                    out.append(new(soup, '<td class="w"></td>'))
                    need -= 1
                elif real:
                    out.append(real.pop(0))
                else:
                    out.append(new(soup, '<td class="w"></td>'))
            log["cells_restored"] += L - len(cells)
            for c in out:
                tr.append(c)
        want = EXTRA_BLANK_ROWS.get(htxt, 0)
        body = t.find("tbody")
        if want and blank_rows < want:
            for _ in range(want - blank_rows):
                body.append(new(soup, "<tr>" + '<td class="w"></td>' * L + "</tr>"))
        if head[-1] == "Done":
            for tr in t.select("tbody tr"):
                tds = tr.find_all("td")
                if tds and not tds[-1].get_text(strip=True):
                    tds[-1]["class"] = ["w", "tick"]
        if L >= 6:
            t["class"] = t.get("class", []) + ["dense"]
        # URLs / domains may break anywhere (so long links cannot push columns off the page);
        # ordinary words elsewhere never split mid-word
        for td in t.find_all(["td", "th"]):
            if re.search(r"https?://|www\.|\b[\w-]+\.(com|in|org|net|io|ai|app|gov|co|dev|space|site|me|so)\b", td.get_text()):
                td["class"] = td.get("class", []) + ["url"]
        if L >= 9:
            t["class"] = t.get("class", []) + ["xdense"]
        # keep short parenthetical ranges in headers together, e.g. "Level (1 से 5)"
        for th in t.select("thead th"):
            html = th.decode_contents()
            html2 = re.sub(r"\(([^()<>]{1,14})\)", r'<span class="nw">(\1)</span>', html)
            if html2 != html:
                th.clear(); th.append(new(soup, html2))


# ---------------------------------------------------------------- templates 07, 17-20
def tracker_sheet(soup, columns, title, records=3):
    wide = {"Observation", "Notes", "Note"}
    rows, cur = [], []
    for c in columns:
        if c in wide:
            if cur:
                rows.append(cur); cur = []
            rows.append([c])
        else:
            cur.append(c)
            if len(cur) == 3:
                rows.append(cur); cur = []
    if cur:
        rows.append(cur)
    cards = []
    for r in range(records):
        trs = []
        for row in rows:
            span = 3 // len(row) if len(row) in (1, 3) else None
            tds = []
            for i, c in enumerate(row):
                cs = 3 if len(row) == 1 else (2 if (len(row) == 2 and i == 1) else 1)
                tds.append(f'<td colspan="{cs}"><span class="cl">{c}</span></td>')
            trs.append("<tr>" + "".join(tds) + "</tr>")
        cards.append(f'<table class="record"><tbody>{"".join(trs)}</tbody></table>')
    return new(soup, f'<div class="tracker-sheet"><p class="sheet-label">{title}</p>' + "".join(cards) + "</div>")


def templates_extra(soup, plan_rows):
    for h in soup.find_all("h2"):
        t = h.get_text(" ", strip=True)
        m = re.match(r"Template (\d{2}): ", t)
        if not m:
            continue
        n = m.group(1)
        h["id"] = f"tpl-{n}"
        tbls = []
        node = h.next_sibling
        while node is not None and not (getattr(node, "name", None) == "h2" and node.get_text().startswith("Template ")) \
                and not (getattr(node, "name", None) == "section"):
            if getattr(node, "name", None) == "table":
                tbls.append(node)
            node = node.next_sibling
        if n == "07" and tbls:
            t0 = tbls[0]
            t0.select_one("thead tr").append(new(soup, "<th>Your value</th>"))
            for tr in t0.select("tbody tr"):
                tr.append(new(soup, '<td class="w"></td>'))
            t0.insert_after(new(soup, '<p class="calc-note">Result: buffered hours = Estimated hours × (1 + Buffer %). '
                                      'Result: floor price = Buffered hours × Minimum hourly rate + Direct costs. '
                                      '(Chapter 6 project example: 25 × 1.3 = 32.5 hours × ₹412 = ₹13,390 + ₹1,500 = ₹14,890.)</p>'))
        if n in ("17", "18", "19") and tbls:
            cols = [tr.find("td").get_text(" ", strip=True) for tr in tbls[0].select("tbody tr") if tr.find("td")]
            names = {"17": "Outreach tracker sheet", "18": "Client CRM sheet", "19": "Follow-up tracker sheet"}
            tbls[0].insert_after(tracker_sheet(soup, cols, names[n]))
        if n == "20":
            rows = "".join(f'<tr><td>{d}</td><td>{task}</td><td class="w tick"></td><td class="w"></td><td class="w"></td></tr>'
                           for d, task in plan_rows)
            anchor = h.find_next("p")
            while anchor is not None and anchor.find_next_sibling() is not None and anchor.find_next_sibling().name == "p":
                anchor = anchor.find_next_sibling()
            anchor.insert_after(new(soup, '<div class="planner"><p class="sheet-label">30-day planner sheet</p>'
                                          '<table class="planner-table"><thead><tr><th>Day</th><th>Main task (Chapter 10)</th>'
                                          '<th>Done</th><th>Actual hours</th><th>Note</th></tr></thead><tbody>'
                                          + rows + "</tbody></table></div>"))


def ch10_plan_rows(soup):
    rows = []
    ch = soup.select_one('section.chapter[data-chapter="10"]')
    for t in ch.find_all("table"):
        head = [th.get_text(" ", strip=True) for th in t.select("thead th")]
        if head[:2] == ["Day", "Main task"]:
            for tr in t.select("tbody tr"):
                tds = tr.find_all("td")
                rows.append((tds[0].get_text(" ", strip=True), tds[1].decode_contents()))
    return rows


# ---------------------------------------------------------------- front matter
HALF_TITLE = '<section class="half-title" id="nofolio-half"><p class="ht">ZERO TO FIRST CLIENT</p></section>'
TITLE_PAGE = '''<section class="title-page" id="nofolio-title">
  <p class="tp-imprint">DEADCODE LABS</p>
  <h1 class="tp-title"><span>ZERO TO</span><span>FIRST</span><span>CLIENT</span></h1>
  <div class="tp-rule"></div>
  <p class="tp-sub">The AI-Powered Business Starter Kit</p>
  <p class="tp-edition">2026 Edition · First Edition</p>
  <p class="tp-author">Divyanshu Verma</p>
  <p class="tp-pub">DEADCODE LABS · https://deadcode.space/</p>
</section>'''


def toc_entries(soup):
    """Original bookmark list -> (level, title, target id). Levels normalised."""
    meta = json.loads((PROD / "source/manuscript_tree.json").read_text())["meta"]["toc"]
    skip = {"Download Your Resources", "Table of Contents"}
    entries, ctx = [], None
    used = set()

    def find_h2(title, scope):
        for h in scope.find_all(["h2"]):
            if h.get_text(" ", strip=True) == title and id(h) not in used:
                used.add(id(h))
                if not h.get("id"):
                    h["id"] = "s-" + slug(title)[:60] + f"-{len(used)}"
                return h["id"]
        return None

    for lvl, title, _ in meta:
        if title in skip:
            continue
        if title.startswith("STAGE "):
            n = re.search(r"STAGE (\d+)", title).group(1)
            entries.append((1, title, f"nofolio-stage-{n}", "stage")); ctx = None; continue
        m = re.match(r"^(\d{2}) ", title)
        if m and lvl == 2 and soup.select_one(f'section.chapter[data-chapter="{m.group(1)}"]'):
            ctx = soup.select_one(f'section.chapter[data-chapter="{m.group(1)}"]')
            entries.append((2, title, f"ch-{m.group(1)}", "chapter")); continue
        sec = None
        for s in soup.select("section.frontmatter, section.bonus, section.appendix"):
            h1 = s.find("h1")
            if h1 and h1.get_text(" ", strip=True) == title:
                sec = s
        if sec is not None:
            ctx = sec
            kind = "front" if "frontmatter" in sec["class"] else "back"
            entries.append((1, title, sec.find("h1")["id"], kind)); continue
        if ctx is not None:
            hid = find_h2(title, ctx)
            if hid:
                lv = 3 if "chapter" in ctx.get("class", []) else 2
                entries.append((lv, title, hid, "sub"))
                if title.startswith("Bonus C") or (ctx.find("h1") and ctx.find("h1").get_text().startswith("Bonus C")):
                    pass
                continue
        raise SystemExit(f"TOC entry not found in book: {title!r}")
    # calculators under Bonus C, About at the end
    out = []
    for e in entries:
        out.append(e)
        if e[1].startswith("Bonus C"):
            for c in soup.select("div.calculator"):
                out.append((2, c.find("h2").get_text(" ", strip=True), c["id"], "sub"))
    out.append((1, "About the Author", "about-the-author", "back"))
    return out


def toc_html(entries, labels=None):
    lis = []
    for lvl, title, tid, kind in entries:
        pg = (labels or {}).get(tid, "000")
        cls = f"l{lvl} k-{kind}"
        lis.append(f'<li class="{cls}"><a href="#{tid}"><span class="tt">{title}</span><span class="pg">{pg}</span></a></li>')
    return ('<section class="frontmatter toc" id="fm-contents"><h1 id="h-contents">Contents</h1>'
            f'<ul class="toc-list">{"".join(lis)}</ul></section>')


# ---------------------------------------------------------------- digital links
def resolve_links(soup, log):
    for a in soup.find_all("a", href=True):
        h = a["href"]
        if not h.startswith("#page="):
            continue
        t = a.get_text(" ", strip=True)
        target = None
        if (m := re.match(r"^Chapter (\d+)$", t)):
            target = f"ch-{int(m.group(1)):02d}"
        elif (m := re.match(r"^Template (\d+)$", t)):
            target = f"tpl-{int(m.group(1)):02d}"
        elif (m := re.match(r"^#?(C\d{2}|C-[A-L]|\d{3})$", t)):
            target = f"prompt-{m.group(1)}"
        elif (m := re.match(r"^\[(\d+)\]", t)):
            target = f"src-{m.group(1)}"
        if target and soup.find(id=target):
            a["href"] = "#" + target
            log["links_resolved"] += 1
        else:
            a.unwrap()
            log["links_unresolved"].append(t)


# ---------------------------------------------------------------- assemble
def assemble():
    src = BeautifulSoup((PROD / f"source/book_{EDITION}.html").read_text(), "lxml")
    body = src.body
    log = {"cells_restored": 0, "links_resolved": 0, "links_unresolved": []}

    plan_rows = ch10_plan_rows(src)

    # ids + bookmarks
    for s in body.select("section.frontmatter, section.bonus, section.appendix"):
        h1 = s.find("h1")
        h1["id"] = ("fm-" if "frontmatter" in s["class"] else "bk-") + slug(h1.get_text())
        h1["data-bm"] = h1.get_text(" ", strip=True)
        h1["class"] = h1.get("class", []) + ["bm1"]
        if h1.get_text(" ", strip=True) in ("Who should read this book?", "About DEADCODE LABS"):
            s["class"] = s["class"] + ["fm-continue"]
        if h1.get_text(" ", strip=True) == "Copyright":
            s["class"] = s["class"] + ["copyright"]
            s["id"] = "nofolio-copyright"
    for s in body.select("section.stage"):
        s["id"] = f"nofolio-stage-{s['data-stage']}"
        t = s.select_one(".stage-title")
        t["data-bm"] = f"Stage {s['data-stage']}: " + t.get_text(" ", strip=True).title()
        t["class"] = t.get("class", []) + ["bm1"]
    for s in body.select("section.chapter"):
        hd = s.select_one("header.chapter-open")
        hd["id"] = f"ch-{s['data-chapter']}"
        t = s.select_one(".chapter-title")
        t["data-bm"] = f"{s['data-chapter']} " + t.get_text(" ", strip=True)
        t["class"] = t.get("class", []) + ["bm2"]
    for p in body.select("div.prompt"):
        p["id"] = f"prompt-{p['data-id']}"
        pur = p.select_one(".pf-purpose")
        if pur is not None:
            pur["data-cont"] = f"#{p['data-id']} continued"
        p.append(new(src, '<div class="prompt-end"></div>'))
    app = body.select_one("section.appendix")
    for t in app.find_all("table"):
        if [th.get_text(strip=True) for th in t.select("thead th")][:1] == ["#"]:
            for tr in t.select("tbody tr"):
                td = tr.find("td")
                if td and td.get_text(strip=True).isdigit():
                    tr["id"] = f"src-{td.get_text(strip=True)}"

    # Bonus C: printed calculator sheets after the index + assumptions
    bc = next(s for s in body.select("section.bonus") if s.find("h1").get_text().startswith("Bonus C"))
    calc = BeautifulSoup((PROD / "source/calculators_bonus_c.html").read_text(), "html.parser")
    for c in calc.select("div.calculator"):
        c["id"] = f"calc-{c['data-calc']}"
    bc.append(calc)

    pad_tables(body, log)
    templates_extra(body, plan_rows)

    # front matter: half-title, title page; Contents where the original TOC stood (after Learning roadmap)
    first = body.find("section")
    first.insert_before(new(src, HALF_TITLE))
    first.insert_before(new(src, TITLE_PAGE))
    roadmap = next(s for s in body.select("section.frontmatter") if s.find("h1").get_text().strip() == "Learning roadmap")
    roadmap.insert_after(new(src, '<div id="toc-slot"></div>'))

    # About the Author at the end
    body.append(new(src, typeset.about(EDITION)))
    ab = body.select_one("#about-the-author .about-name")
    ab["class"] = ab.get("class", []) + ["bm1"]
    ab["data-bm"] = "About the Author"

    entries = toc_entries(body)
    if EDITION == "digital":
        resolve_links(body, log)
    return body.decode_contents(), entries, log


EXTRA_CSS = """
h1, h2, h3, h4 { bookmark-level: none; }
.bm1 { bookmark-level: 1; bookmark-label: attr(data-bm); }
.bm2 { bookmark-level: 2; bookmark-label: attr(data-bm); }
"""


def render_pass(body, entries, labels):
    html_body = body.replace('<div id="toc-slot"></div>', toc_html(entries, labels))
    html, pending = typeset.compose(html_body, EDITION, extra_css=EXTRA_CSS)
    if pending:
        raise SystemExit(f"diagrams not rebuilt: {pending}")
    from weasyprint import HTML
    doc = HTML(string=html, base_url=str(typeset.DS)).render()
    return html, doc


def roman(n):
    vals = [(10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]
    out = ""
    for v, s in vals:
        while n >= v:
            out += s; n -= v
    return out


def page_map(doc):
    anchors = {}
    for i, p in enumerate(doc.pages):
        for a in p.anchors:
            anchors.setdefault(a, i)
    ch1 = anchors["ch-01"]
    labels = {}
    for a, i in anchors.items():
        labels[a] = roman(i + 1) if i < ch1 else str(i - ch1 + 1)
    return anchors, labels, ch1


def folio_overlay(n_pages, ch1, nofolio, out):
    pages = []
    for i in range(n_pages):
        lab = "" if i in nofolio else (roman(i + 1) if i < ch1 else str(i - ch1 + 1))
        side = "r" if i % 2 == 0 else "v"
        pages.append(f'<div class="pg"><span class="f {side}">{lab}</span></div>')
    color = "device-cmyk(0 0 0 0.72)" if EDITION == "print" else "#3d3d3d"
    html = f"""<html><head><style>
@font-face {{ font-family: Inter; font-weight: 500; src: url(fonts/Inter-Medium.otf); }}
@page {{ size: 135mm 210mm; margin: 0; }}
.pg {{ position: relative; width: 135mm; height: 210mm; break-after: page; }}
.f {{ position: absolute; top: 196.5mm; font: 500 7.4pt/1 Inter; color: {color}; font-variant-numeric: lining-nums; }}
.f.r {{ right: 14mm; }} .f.v {{ left: 14mm; }}
</style></head><body>{''.join(pages)}</body></html>"""
    from weasyprint import HTML
    HTML(string=html, base_url=str(typeset.DS)).write_pdf(out)


def main():
    body, entries, log = assemble()
    labels = None
    for attempt in range(4):
        html, doc = render_pass(body, entries, labels)
        anchors, new_labels, ch1 = page_map(doc)
        if labels is not None and all(new_labels.get(e[2]) == labels.get(e[2]) for e in entries):
            break
        labels = new_labels
    else:
        raise SystemExit("TOC page numbers did not converge")
    (BUILD / f"book_{EDITION}.html").write_text(html)
    raw = BUILD / f"raw_{EDITION}.pdf"
    doc.write_pdf(raw)

    # pages without folio: half-title, title page, copyright, stage dividers, blank pages
    nofolio = set()
    for a, i in anchors.items():
        if a.startswith("nofolio-"):
            nofolio.add(i)
    md = pymupdf.open(raw)

    def is_blank(p):
        """No text, no images, no drawings other than a full-page background fill."""
        area = p.rect.width * p.rect.height
        marks = [d for d in p.get_drawings() if d["rect"].width * d["rect"].height < 0.95 * area]
        return not p.get_text().strip() and not p.get_image_info() and not marks

    band = lambda p: pymupdf.Rect(0, p.rect.height - 16 * 72 / 25.4, p.rect.width, p.rect.height)  # noqa: E731
    stray = [i + 1 for i, p in enumerate(md) if p.get_text(clip=band(p)).strip()]
    if stray:   # single source of folios: the typeset pages must carry none of their own
        raise SystemExit(f"typeset pages already contain folio-band text (duplicate numbering source): {stray[:10]}")
    for i, p in enumerate(md):
        if is_blank(p):
            nofolio.add(i)
    ov = BUILD / f"folios_{EDITION}.pdf"
    folio_overlay(len(doc.pages), ch1, nofolio, ov)

    # merge folios onto pages
    r = PdfReader(str(raw)); fo = PdfReader(str(ov))
    w = PdfWriter(clone_from=r)
    for i, p in enumerate(w.pages):
        p.merge_page(fo.pages[i])
    pad = 0
    if EDITION == "print" and len(w.pages) % 2:
        # a bound book has an even number of pages: close with a blank verso after About the Author
        w.add_blank_page(width=w.pages[0].mediabox.width, height=w.pages[0].mediabox.height)
        pad = 1
    meta = {"/Title": "ZERO TO FIRST CLIENT: The AI-Powered Business Starter Kit",
            "/Author": "Divyanshu Verma", "/Subject": "2026 Edition, First Edition — " +
            ("paperback interior, 135 × 210 mm" if EDITION == "print" else "digital edition"),
            "/Creator": "DeadCode Labs production pipeline", "/Producer": "WeasyPrint + pypdf",
            "/Keywords": "entrepreneurship, freelancing, AI, client acquisition, India, Hinglish"}
    w.add_metadata(meta)
    out = FINAL / ("ZTFC_2026_paperback_interior_135x210_PRINT.pdf" if EDITION == "print" else "ZTFC_2026_digital_edition.pdf")
    with open(out, "wb") as fh:
        w.write(fh)

    if EDITION == "print":
        # print interior carries no link annotations (TOC and bookmarks stay)
        pdf = pikepdf.open(out, allow_overwriting_input=True)
        removed = 0
        for p in pdf.pages:
            if "/Annots" in p:
                keep = [a for a in p.Annots if a.get("/Subtype") != "/Link"]
                removed += len(p.Annots) - len(keep)
                if keep:
                    p.Annots = pikepdf.Array(keep)
                else:
                    del p["/Annots"]
        pdf.save(out)
        log["link_annotations_removed"] = removed

    # Devanagari text layer: add /ActualText so copy, search and accessibility return correct Hindi
    subprocess.run([sys.executable, str(Path(__file__).parent / "fix_text_layer.py"), str(out),
                    str(BUILD / f"book_{EDITION}.html"), str(PROD / f"validation/text_layer_{EDITION}.json")], check=True)

    n_total = len(doc.pages) + pad
    if pad:
        nofolio.add(n_total - 1)
    pm = {"edition": EDITION, "pages": n_total, "blank_pages_added_for_even_count": pad, "front_matter_pages": ch1,
          "main_pages": len(doc.pages) - ch1, "no_folio_pages": sorted(i + 1 for i in nofolio),
          "intentional_blank_pages": sorted([i + 1 for i, p in enumerate(md) if is_blank(p)]
                                            + ([n_total] if pad else [])),
          "toc": [{"level": e[0], "title": e[1], "id": e[2], "page": labels.get(e[2])} for e in entries], **log}
    (PROD / f"validation/page_map_{EDITION}.json").write_text(json.dumps(pm, ensure_ascii=False, indent=1))
    print(f"{EDITION}: {n_total} pages ({ch1} front matter + {len(doc.pages) - ch1}) -> {out.relative_to(ROOT)}")
    print("links resolved:", log["links_resolved"], "unresolved:", log["links_unresolved"])


if __name__ == "__main__":
    main()
