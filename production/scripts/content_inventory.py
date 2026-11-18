#!/usr/bin/env python3
"""Build the content inventory from a book HTML source.

Usage: content_inventory.py <book.html> <out.json>
Counts chapters, sections, prompts, workflow cards, callouts, tables, figures,
templates (Bonus B), calculator sheets (Bonus C), 30-day plan days (Ch 10),
glossary terms and appendix sources.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup


def txt(el):
    if el is None:
        return ""
    return re.sub(r"\s+", " ", el.get_text(" ")).strip()


def main():
    src, out = sys.argv[1], sys.argv[2]
    soup = BeautifulSoup(Path(src).read_text(), "lxml")
    inv = {"source": src}

    inv["frontmatter"] = [txt(s.find("h1")) for s in soup.select("section.frontmatter")]
    inv["stages"] = [{"stage": s["data-stage"], "title": txt(s.select_one(".stage-title"))} for s in soup.select("section.stage")]

    chapters = []
    for s in soup.select("section.chapter"):
        h2 = [txt(h) for h in s.find_all("h2")]
        chapters.append({
            "chapter": s["data-chapter"],
            "title": txt(s.select_one(".chapter-title")),
            "subtitle": txt(s.select_one(".chapter-sub")),
            "sections_h2": h2,
            "h3_count": len(s.find_all("h3")),
            "prompts": [p["data-id"] for p in s.select("div.prompt")],
            "workflow_cards": [txt(w.select_one(".workflow-title")) for w in s.select("div.workflow")],
            "callouts": dict(Counter(c["class"][1].replace("callout-", "") for c in s.select("aside.callout"))),
            "tables": len(s.find_all("table")),
            "figures": [f.get("data-fig") for f in s.select("figure.diagram")],
            "checklists": len(s.select("ul.checklist")),
        })
    inv["chapters"] = chapters

    bonus = {}
    for s in soup.select("section.bonus, section.appendix"):
        title = txt(s.find("h1"))
        bonus[title] = {"h2": [txt(h) for h in s.find_all("h2")], "tables": len(s.find_all("table")),
                        "prompts": len(s.select("div.prompt"))}
    inv["back_matter"] = bonus

    # templates
    templates = []
    for h in soup.find_all(["h2", "h3"]):
        m = re.match(r"Template (\d{2}): (.+)", txt(h))
        if m:
            tbl = h.find_next("table")
            rows = []
            if tbl is not None and tbl.find_previous(["h2", "h3"]) is h:
                rows = [txt(tr.find(["td", "th"])) for tr in tbl.select("tbody tr")]
            templates.append({"number": m.group(1), "title": m.group(2), "fields_or_rows": rows})
    inv["templates"] = templates

    # calculators: Bonus C sheet table (or printed calculator sections)
    calcs = []
    sec = next((s for s in soup.select("section.bonus") if txt(s.find("h1")).startswith("Bonus C")), None)
    if sec is not None:
        printed = sec.select("div.calculator")
        if printed:
            calcs = [{"id": c.get("data-calc"), "title": txt(c.find(["h2", "h3"]))} for c in printed]
        else:
            t = sec.find("table")
            for tr in t.select("tbody tr"):
                cells = [txt(td) for td in tr.find_all("td")]
                calcs.append({"sheet": cells[0], "when": cells[1], "inputs": cells[2], "outputs": cells[3]})
    inv["calculators"] = calcs

    figs = []
    for f in soup.select("figure.diagram"):
        cap = f.find("figcaption")
        sec = f.find_parent("section")
        figs.append({"figure": f.get("data-fig"), "source_page": f.get("data-src-page"),
                     "section": (sec.get("data-chapter") and "Chapter " + sec["data-chapter"]) or txt(sec.find("h1"))[:40],
                     "caption": txt(cap) if cap else ""})
    inv["figures"] = figs

    # 30-day plan: day rows in chapter 10 week tables
    ch10 = soup.select_one('section.chapter[data-chapter="10"]')
    days = []
    if ch10 is not None:
        for t in ch10.find_all("table"):
            head = [txt(th) for th in t.select("thead th")]
            if head[:2] == ["Day", "Main task"]:
                days += [txt(tr.find("td")) for tr in t.select("tbody tr")]
    inv["thirty_day_plan_days"] = days

    gl = next((h for h in soup.find_all("h2") if txt(h) == "Glossary"), None)
    terms = []
    if gl is not None:
        for t in gl.find_all_next("table"):
            terms += [txt(tr.find("td")) for tr in t.select("tbody tr")]
    inv["glossary_terms"] = terms

    app = next((s for s in soup.select("section.appendix")), None)
    sources = []
    if app is not None:
        for t in app.find_all("table"):
            head = [txt(th) for th in t.select("thead th")]
            if head and head[0] == "#":
                sources += [txt(tr.find("td")) for tr in t.select("tbody tr")]
    inv["appendix_sources"] = sources

    inv["totals"] = {
        "chapters": len(chapters),
        "prompts": len(soup.select("div.prompt")),
        "workflow_cards": len(soup.select("div.workflow")),
        "callouts": dict(Counter(c["class"][1].replace("callout-", "") for c in soup.select("aside.callout"))),
        "tables": len(soup.find_all("table")),
        "figures": len(figs),
        "templates": len(templates),
        "calculators": len(calcs),
        "thirty_day_plan_days": len(days),
        "glossary_terms": len(terms),
        "appendix_sources": len(sources),
    }
    Path(out).write_text(json.dumps(inv, ensure_ascii=False, indent=1))
    print(json.dumps(inv["totals"], ensure_ascii=False))


if __name__ == "__main__":
    main()
