#!/usr/bin/env python3
"""Typesetting pipeline: edition source HTML -> styled book HTML -> PDF (WeasyPrint).

Transforms applied (layout only, no wording changes):
  * figure placeholders  -> rebuilt vector diagrams (design-system/diagrams/fig-NN.svg)
  * figure captions      -> 'Figure N.' set as a run-in label
  * prompt bodies        -> [placeholders] emphasised for quick copying
  * reference markers    -> [n] set as small superior references (outside prompts)
  * Bonus B templates    -> wrapped as page-starting template blocks; tables with
                            Field / Your entry / Example columns become fill-in
                            forms with ruled writing lines
  * About the Author     -> inserted from production/about-the-author/about.html

Library use:  from typeset import compose, render
"""
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
PROD = ROOT / "production"
DS = PROD / "design-system"

SIGNATURE = {"print": ROOT / "production/about-the-author/signature_black_print_gray.png",
             "digital": ROOT / "author-assets/DIVYANSHU_VERMA_AUTHOR_SIGNATURE.png"}
PORTRAIT = PROD / "about-the-author/portrait_print_gray.jpg"

# writing lines per template field (default 2); generous where answers are long
FIELD_LINES = {}   # per-field overrides; default is 2 writing lines


def soupify(html):
    return BeautifulSoup(html, "lxml")


def figures(soup, strict=False):
    pending = []
    for f in soup.select("figure.diagram"):
        n = f.get("data-fig", "")
        svg = DS / f"diagrams/fig-{int(n):02d}.html" if n else None
        holder = f.select_one(".diagram-src")
        if svg and svg.exists():
            if holder:
                # SVG markup is injected verbatim after serialisation (HTML parsers
                # would lowercase case-sensitive SVG attributes such as viewBox)
                mark = soup.new_tag("div", attrs={"class": "svg-slot", "data-svg": svg.name})
                holder.replace_with(mark)
        else:
            pending.append(n)
            if holder:
                new = soup.new_tag("div", attrs={"class": "diagram-pending"})
                new.string = f"Figure {n}: vector rebuild pending"
                holder.replace_with(new)
        cap = f.find("figcaption")
        if cap and cap.contents and isinstance(cap.contents[0], str):
            m = re.match(r"(Figure \d+\.)(.*)", cap.contents[0], re.S)
            if m:
                span = soup.new_tag("span", attrs={"class": "fig-num"})
                span.string = m.group(1)
                cap.contents[0].replace_with(m.group(2))
                cap.insert(0, span)
    if strict and pending:
        raise SystemExit(f"diagrams not rebuilt: {pending}")
    return pending


def placeholders(soup):
    for body in soup.select(".prompt-body"):
        html = body.decode_contents()
        html = re.sub(r"(\[[^\]<>]{1,60}\])", r'<span class="ph">\1</span>', html)
        body.clear()
        body.append(BeautifulSoup(html, "html.parser"))


REF = re.compile(r"\[(\d{1,2}(?:\s*,\s*\d{1,2})*)\]")


def references(soup):
    for node in soup.find_all(string=REF):
        if node.find_parent(class_="prompt-body") or node.find_parent("title"):
            continue
        parts = REF.split(str(node))
        frag = []
        for i, p in enumerate(parts):
            if i % 2 == 0:
                frag.append(p)
            else:
                frag.append(f'<span class="ref">[{p}]</span>')
        node.replace_with(BeautifulSoup("".join(frag).replace("<", "<", 0), "html.parser"))


def templates(soup):
    """Group each 'Template NN: …' heading with its content into div.template."""
    for h in soup.find_all("h2"):
        if not re.match(r"Template \d{2}: ", h.get_text()):
            continue
        wrap = soup.new_tag("div", attrs={"class": "template", "data-template": h.get_text()[9:11]})
        h.insert_before(wrap)
        node = h
        while node is not None:
            nxt = node.next_sibling
            wrap.append(node.extract())
            node = nxt
            if node is not None and getattr(node, "name", None) == "h2" and re.match(r"Template \d{2}: ", node.get_text()):
                break
            if node is not None and getattr(node, "name", None) == "section":
                break
        first_p = wrap.find("p")
        if first_p and first_p.get_text().startswith("Instructions:"):
            first_p["class"] = first_p.get("class", []) + ["instructions"]
        for t in wrap.find_all("table"):
            head = [th.get_text(strip=True) for th in t.select("thead th")]
            if len(head) == 3 and head[0] in ("Field", "Column") and "Your entry" in head:
                t.replace_with(form_from_table(soup, t))


def form_from_table(soup, t):
    head = [th.get_text(strip=True) for th in t.select("thead th")]
    ex_i = next((i for i, h in enumerate(head) if h.startswith("Example")), len(head) - 1)
    box = soup.new_tag("div", attrs={"class": "form"})
    for tr in t.select("tbody tr"):
        cells = tr.find_all("td")
        if not cells:
            continue
        label = cells[0].get_text(" ", strip=True)
        example = cells[ex_i].get_text(" ", strip=True) if len(cells) > ex_i else ""
        ff = soup.new_tag("div", attrs={"class": "form-field"})
        head = soup.new_tag("div", attrs={"class": "ff-head"})
        lab = soup.new_tag("div", attrs={"class": "ff-label"}); lab.string = label
        head.append(lab)
        if example:
            ex = soup.new_tag("div", attrs={"class": "ff-example"}); ex.string = example
            head.append(ex)
        ff.append(head)
        lines = soup.new_tag("div", attrs={"class": "ff-lines"})
        for _ in range(FIELD_LINES.get(label, 2)):
            lines.append(soup.new_tag("div", attrs={"class": "ff-line"}))
        ff.append(lines)
        box.append(ff)
    return box


def about(edition):
    html = (PROD / "about-the-author/about.html").read_text()
    return (html.replace("{{PORTRAIT}}", PORTRAIT.as_uri())
                .replace("{{SIGNATURE}}", SIGNATURE[edition].as_uri()))


# diagram colour tokens (SVG cannot read CSS variables): print = K-only DeviceCMYK
DG_TOKENS = {
    "print": {"DGINK": "device-cmyk(0 0 0 0.9)", "DGMID": "device-cmyk(0 0 0 0.6)",
              "DGACC": "device-cmyk(0 0 0 1)", "DGPAPER": "device-cmyk(0 0 0 0)"},
    "digital": {"DGINK": "#14213D", "DGMID": "#6B7389", "DGACC": "#6D28D9", "DGPAPER": "#FFFFFF"},
}


def diagram_markup(name, edition):
    html = re.sub(r"<!--.*?-->", "", (DS / "diagrams" / name).read_text(), flags=re.S)
    def tint(m):
        a = float(m.group(1))
        if edition == "print":
            return f"device-cmyk(0 0 0 {0.9 * a:.3f})"
        r, g, b = 0x14, 0x21, 0x3D        # navy over white
        mix = lambda c: round(255 - (255 - c) * a)  # noqa: E731
        return f"#{mix(r):02X}{mix(g):02X}{mix(b):02X}"
    html = re.sub(r"DGTINT:([0-9.]+)", tint, html)
    for k, v in DG_TOKENS[edition].items():
        html = html.replace(k, v)
    return html


def compose(body_html, edition, title="ZERO TO FIRST CLIENT", extra_css=""):
    soup = soupify(f"<div id='book'>{body_html}</div>")
    pending = figures(soup)
    placeholders(soup)
    references(soup)
    templates(soup)
    css = [f"{DS.as_uri()}/tokens-{edition}.css", f"{DS.as_uri()}/book.css"]
    head = (f'<!doctype html><html lang="hi"><head><meta charset="utf-8"><title>{title}</title>'
            f'<meta name="author" content="Divyanshu Verma">'
            + "".join(f'<link rel="stylesheet" href="{c}">' for c in css)
            + (f"<style>{extra_css}</style>" if extra_css else "") + "</head><body>")
    inner = soup.select_one("#book").decode_contents()
    inner = re.sub(r'<div class="svg-slot" data-svg="([^"]+)"></div>',
                   lambda m: diagram_markup(m.group(1), edition), inner)
    return head + inner + "</body></html>", pending


def render(html, out_pdf, base=None):
    from weasyprint import HTML
    doc = HTML(string=html, base_url=str(base or DS)).render()
    doc.write_pdf(out_pdf)
    return doc


if __name__ == "__main__":
    print(__doc__)
    sys.exit(0)
