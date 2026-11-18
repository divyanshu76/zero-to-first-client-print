#!/usr/bin/env python3
"""Convert manuscript_tree.json (tagged-PDF structure) into semantic book HTML.

Output: production/source/extracted.html — a faithful, structure-only
reconstruction of the manuscript text. No editorial changes happen here
(print edits live in content_edits.py), so this file can always be rebuilt
from the original PDF and diffed.

Component classes emitted (styled later by the design system):
  section.stage            stage divider (Stage 01–04)
  section.chapter          chapter, with header.chapter-open
  section.frontmatter / .bonus / .appendix
  div.prompt               AI prompt card  (data-id="C01" | "C-A" | "001")
  div.workflow             workflow card (WHAT/WHY/HOW/TOOL/… rows)
  aside.callout            tip / note / warning / hypothetical / india / intl / assignment …
  figure.diagram           diagram placeholder (data-fig="N"), labels kept for rebuild
  table / ul / ol / ul.checklist
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TREE = ROOT / "production/source/manuscript_tree.json"
OUT = ROOT / "production/source/extracted.html"

DEVA = re.compile(r"[ऀ-ॿ]")
PROMPT_ID = re.compile(r"^#(C\d{2}|C-[A-L]|\d{3})$")
WF_LABELS = ["WHAT", "WHY", "HOW", "TOOL", "TOOL USE", "OUTPUT", "VERIFY", "MISTAKES"]
PROMPT_LABELS = ["PURPOSE", "OUTPUT", "EXAMPLE", "VERIFY"]
CHECKLIST_HEADINGS = {"Learning objectives", "Completion checklist"}

# Callout label → kind. Labels come from the original box headers.
CALLOUT_KINDS = [
    (re.compile(r"^TIP$"), "tip"),
    (re.compile(r"^NOTE$"), "note"),
    (re.compile(r"^WARNING$"), "warning"),
    (re.compile(r"^HYPOTHETICAL$"), "hypothetical"),
    (re.compile(r"^WORKFLOW$"), "workflow-label"),
    (re.compile(r"^International"), "intl"),
    (re.compile(r"^Indian market application$|^India"), "india"),
    (re.compile(r"^Next-step assignment$"), "assignment"),
]


# ---------------------------------------------------------------- text helpers
def runs_of(n, ctx=()):
    """Yield (run, ctx) in reading order; ctx is the tuple of ancestor tags."""
    for c in n["children"]:
        if "t" in c:
            if c["t"].strip() == "WORKFLOW" and c["size"] < 9:
                continue  # stray card label (re-created by the workflow component)
            yield c, ctx
        else:
            yield from runs_of(c, ctx + (c["tag"],))


def plain(n):
    if "t" in n:
        return n["t"]
    return "".join(r["t"] for r, _ in runs_of(n))


def is_newline(prev, cur):
    if prev["page"] != cur["page"]:
        return True
    pc = (prev["bbox"][1] + prev["bbox"][3]) / 2
    cc = (cur["bbox"][1] + cur["bbox"][3]) / 2
    # baseline moved down by more than ~half a line: a wrapped line (also for
    # centred/short lines where the new line starts right of the previous end)
    return cc - pc > 0.6 * min(prev["size"], cur["size"])


URLISH_END = re.compile(r"(https?://|www\.)\S*$|\S+\.(com|in|org|net|io|ai|app|gov|co|space|html?)/\S*$|\S*/$")


def joiner(prev, cur):
    """Separator to put between two runs."""
    a, b = prev["t"], cur["t"]
    if not is_newline(prev, cur):
        # same visual line: a visible horizontal gap between runs is a word space
        gap = cur["bbox"][0] - prev["bbox"][2]
        if gap > 0.18 * min(prev["size"], cur["size"]) and not a.endswith((" ", "\u00a0", "(", "[", "“", '"')) \
                and not b.startswith((" ", "\u00a0", "।", ",", ".", ")", "]", ":", ";", "?", "!", "”")) \
                and prev["page"] == cur["page"]:
            return " "
        return ""
    if a.endswith((" ", " ")) or b.startswith((" ", " ")):
        return ""
    if prev.get("uri") and prev.get("uri") == cur.get("uri") and URLISH_END.search(a) and " " not in a.strip():
        return ""  # one URL-text link wrapped over two lines
    if a.endswith(("-", "/", "_", "–")) and not a.endswith(" -"):
        return ""
    if URLISH_END.search(a) and not DEVA.search(b[:1]) and re.match(r"[a-z0-9/_\-.?=&#%]", b[:1] or " "):
        return ""
    return " "


def inline_html(n, skip_first_label=False, digital_links=True):
    """Serialize runs of n with <strong>/<em>/<a>, joining wrapped lines."""
    out, prev = [], None
    open_a = None
    items = list(runs_of(n))
    for r, ctx in items:
        if prev is not None:
            out.append(joiner(prev, r))
        t = html.escape(r["t"], quote=False)
        if "Strong" in ctx or ("TH" in ctx):
            t = f"<strong>{t}</strong>" if "Strong" in ctx else t
        if "Em" in ctx:
            t = f"<em>{t}</em>"
        if "Code" in ctx:
            t = f"<code>{t}</code>"
        uri = r.get("uri")
        if uri:
            t = f'<a href="{html.escape(uri)}">{t}</a>'
        out.append(t)
        prev = r
    s = "".join(out)
    s = re.sub(r"</strong><strong>", "", s)
    # merge adjacent fragments of the same link (a URL wrapped over lines)
    while True:
        s2 = re.sub(r'<a href="([^"]+)">((?:(?!</a>).)*)</a>(\s*)<a href="\1">', r'<a href="\1">\2\3', s)
        if s2 == s:
            break
        s = s2
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()


def esc(s):
    return html.escape(s, quote=False)


# ---------------------------------------------------------------- tables
def table_html(n):
    rows = [c for c in n["children"] if c.get("tag") == "TR"]
    # TR may be nested under THead/TBody in some outputs
    if not rows:
        rows = [r for c in n["children"] if "tag" in c for r in c["children"] if r.get("tag") == "TR"]
    head, body = [], []
    for tr in rows:
        cells = [c for c in tr["children"] if c.get("tag") in ("TH", "TD")]
        is_head = cells and all(c["tag"] == "TH" for c in cells)
        cell_html = []
        for c in cells:
            if c["tag"] == "TH" and len(c["pages"]) > 1:
                # repeated <thead> on continuation pages: keep first page's runs only
                c = dict(c, children=[x for x in c["children"] if "t" not in x or x["page"] == c["pages"][0]])
                c["children"] = [x if "t" in x else dict(x, children=[y for y in x["children"] if "t" not in y or y["page"] == c["pages"][0]]) for x in c["children"]]
            tag = "th" if c["tag"] == "TH" else "td"
            cell_html.append(f"<{tag}>{inline_html(c)}</{tag}>")
        (head if is_head else body).append("<tr>" + "".join(cell_html) + "</tr>")
    out = "<table>"
    if head:
        out += "<thead>" + "".join(head) + "</thead>"
    out += "<tbody>" + "".join(body) + "</tbody></table>"
    return out


# ---------------------------------------------------------------- lists
def list_html(n, checklist=False):
    items = [c for c in n["children"] if c.get("tag") == "LI"]
    texts = []
    for li in items:
        lbl = next((c for c in li["children"] if c.get("tag") == "Lbl"), None)
        body = dict(li, children=[c for c in li["children"] if c is not lbl])
        texts.append((plain(lbl).strip() if lbl else "", inline_html(body)))
    ordered = all(re.match(r"^\d+\.\s", (l + " " + t).strip()) for l, t in texts) and texts
    lis = []
    for l, t in texts:
        if ordered:
            full = ((l + " " + t).strip() if l else t)
            m = re.match(r"^(\d+)\.\s*(.*)$", full, re.S)
            lis.append(f'<li><span class="li-num">{m.group(1)}.</span> {m.group(2)}</li>')
        else:
            lis.append(f"<li>{t}</li>")
    if checklist:
        return '<ul class="checklist">' + "".join(lis) + "</ul>"
    return ("<ol>" if ordered else "<ul>") + "".join(lis) + ("</ol>" if ordered else "</ul>")


# ---------------------------------------------------------------- components
def first_label(n):
    """Text of the first run if it is a small uppercase box label."""
    for r, _ in runs_of(n):
        return r["t"].strip(), r
    return "", None


def callout_kind(label):
    for rx, kind in CALLOUT_KINDS:
        if rx.search(label):
            return kind
    return None


def prompt_html(n):
    kids = [c for c in n["children"] if "tag" in c]
    pid = plain(kids[0]).strip().lstrip("#")
    title = inline_html(kids[1])
    # chapter prompts carry a category line; Bonus A prompts go straight to PURPOSE
    has_cat = len(kids) > 2 and kids[2]["tag"] == "NonStruct" and \
        not any(plain(kids[2]).strip().startswith(L) for L in PROMPT_LABELS) and len(plain(kids[2])) < 40
    cat = plain(kids[2]).strip() if has_cat else ""
    rest = kids[3:] if has_cat else kids[2:]
    parts = [f'<div class="prompt" data-id="{pid}">',
             f'<div class="prompt-head"><span class="prompt-id">#{esc(pid)}</span>'
             f'<span class="prompt-title">{title}</span><span class="prompt-cat">{esc(cat)}</span></div>']
    for k in rest:
        t = plain(k).strip()
        lab = next((L for L in PROMPT_LABELS if t.startswith(L)), None)
        if k["tag"] == "P" and lab:
            sub = [c for c in k["children"] if "tag" in c]
            body = dict(k, children=sub[1:]) if sub and plain(sub[0]).strip() == lab else k
            txt = inline_html(body)
            if txt.startswith(lab):
                txt = txt[len(lab):].strip()
            parts.append(f'<p class="pf pf-{lab.lower()}"><span class="pf-label">{lab}</span> {txt}</p>')
        else:
            parts.append(f'<div class="prompt-body">{inline_html(k)}</div>')
    parts.append("</div>")
    return "\n".join(parts)


def callout_html(n, kind, label):
    kids = [c for c in n["children"] if "tag" in c]
    # direct label runs (untagged) or first NonStruct child holding the label
    inner = []
    title = None
    rest = kids
    direct = [c for c in n["children"] if "t" in c]
    if not direct and kids and plain(kids[0]).strip() == label:
        rest = kids[1:]
    if rest and rest[0]["tag"] == "NonStruct" and not any("tag" in c for c in rest[0]["children"] if c.get("tag") not in ("NonStruct",)) \
            and len(plain(rest[0])) < 120 and len(rest) > 1:
        title = inline_html(rest[0])
        rest = rest[1:]
    for k in rest:
        inner.append(block_html(k))
    head = f'<p class="callout-label">{esc(label)}</p>' if kind not in ("india", "intl", "assignment") else f'<p class="callout-label">{esc(label)}</p>'
    t = f'<p class="callout-title">{title}</p>' if title else ""
    return f'<aside class="callout callout-{kind}">{head}{t}' + "\n".join(inner) + "</aside>"


def block_html(n):
    tag = n["tag"]
    if tag == "P":
        return f"<p>{inline_html(n)}</p>"
    if tag in ("H1", "H2", "H3"):
        return f"<{tag.lower()}>{inline_html(n)}</{tag.lower()}>"
    if tag == "Table":
        return table_html(n)
    if tag == "L":
        return list_html(n)
    if tag == "Figure":
        return figure_html(n, None)
    if tag == "Link":
        return f"<p>{inline_html(n)}</p>"
    # NonStruct container
    kids = [c for c in n["children"] if "tag" in c]
    if kids and PROMPT_ID.match(plain(kids[0]).strip()):
        return prompt_html(n)
    label, r = first_label(n)
    kind = callout_kind(label)
    if kind and len(plain(n)) > len(label) + 5:
        return callout_html(n, kind, label)
    if kids and all(k["tag"] == "NonStruct" and not any("tag" in c for c in k["children"]) for k in kids):
        return "<p>" + " ".join(inline_html(k) for k in kids) + "</p>"
    if kids:
        return "\n".join(block_html(k) for k in kids)
    return f"<p>{inline_html(n)}</p>"


FIG_COUNTER = [0]


def figure_html(fig, caption):
    """Diagram placeholder. The vector diagram is rebuilt separately
    (design-system/diagrams/fig-NN.svg); its source labels are kept here."""
    caps = [c for c in fig["children"] if c.get("tag") == "Caption"]
    if caption is None and caps:
        caption = caps[0]
    body = dict(fig, children=[c for c in fig["children"] if c is not caption])
    labels = [r["t"].strip() for r, _ in runs_of(body) if r["t"].strip()]
    num, cap = "", ""
    if caption is not None:
        cap = inline_html(caption)
        m = re.match(r"Figure (\d+)\.", plain(caption).strip())
        num = m.group(1) if m else ""
    return (f'<figure class="diagram" data-fig="{num}" data-src-page="{fig["pages"][0]}">'
            f'<div class="diagram-src" hidden>{esc(" | ".join(labels))}</div>'
            + (f"<figcaption>{cap}</figcaption>" if cap else "") + "</figure>")


# ---------------------------------------------------------------- top level
def main():
    d = json.loads(TREE.read_text())
    top = d["tree"]["children"]
    out = []
    i = 0
    stack = []  # open section types

    def close():
        while stack:
            out.append("</section>")
            stack.pop()

    in_checklist_section = False
    pending_wf = None  # (title_html, rows[])

    def flush_wf():
        nonlocal pending_wf
        if pending_wf:
            title, rows = pending_wf
            out.append('<div class="workflow"><p class="workflow-label">WORKFLOW</p>'
                       f'<p class="workflow-title">{title}</p><dl>'
                       + "".join(f"<dt>{esc(k)}</dt><dd>{v}</dd>" for k, v in rows) + "</dl></div>")
            pending_wf = None

    while i < len(top):
        n = top[i]
        if "t" in n:  # stray untagged run (WORKFLOW labels)
            i += 1
            continue
        tag = n["tag"]
        txt = plain(n).strip()
        pg = n["pages"][0]

        # covers (pages 1–2) are redesigned; keep text for reference only
        if pg <= 2:
            out.append(f'<!-- source cover p{pg}: {esc(txt[:200])} -->')
            i += 1
            continue

        # workflow card rows
        if tag == "NonStruct" and txt in WF_LABELS and i + 1 < len(top) and top[i + 1].get("tag") == "P":
            if pending_wf is None:
                # title is the previous emitted paragraph
                title = out.pop()
                title = re.sub(r"^<p>|</p>$", "", title)
                title = re.sub(r"^WORKFLOW\s*", "", title)
                pending_wf = (title, [])
            pending_wf[1].append((txt, inline_html(top[i + 1])))
            i += 2
            continue
        flush_wf()

        # stage divider
        if tag == "NonStruct" and txt.startswith("S TAG E"):
            close()
            pk = [k for k in n["children"][0]["children"] if "tag" in k]
            num, name = plain(pk[1]).strip(), inline_html(pk[2])
            sub = inline_html(pk[3]) if len(pk) > 3 else ""
            chapters = [plain(k).strip() for k in n["children"][-1]["children"] if "tag" in k]
            out.append(f'<section class="stage" data-stage="{num}"><p class="stage-label">Stage</p><p class="stage-num">{esc(num)}</p>'
                       f'<h1 class="stage-title">{name}</h1><p class="stage-sub">{sub}</p>'
                       '<ul class="stage-chapters">' + "".join(f"<li>{esc(c)}</li>" for c in chapters) + "</ul></section>")
            i += 1
            continue

        # chapter opener
        if tag == "NonStruct" and txt.startswith("CHAPTER"):
            close()
            kids = [k for k in n["children"] if "tag" in k]
            num = plain(kids[1]).strip()
            title = inline_html(kids[2])
            sub = inline_html(kids[3]) if len(kids) > 3 else ""
            out.append(f'<section class="chapter" data-chapter="{num}"><header class="chapter-open">'
                       f'<p class="chapter-label">CHAPTER</p><p class="chapter-num">{esc(num)}</p><h1 class="chapter-title">{title}</h1>'
                       f'<p class="chapter-sub">{sub}</p></header>')
            stack.append("chapter")
            i += 1
            continue

        if tag == "H1":
            t = inline_html(n)
            if t.startswith("Bonus") or t.startswith("Appendix"):
                close()
                cls = "bonus" if t.startswith("Bonus") else "appendix"
                out.append(f'<section class="{cls}"><h1>{t}</h1>')
                stack.append(cls)
            else:
                close()
                out.append(f'<section class="frontmatter"><h1>{t}</h1>')
                stack.append("frontmatter")
            i += 1
            continue

        if tag in ("H2", "H3"):
            in_checklist_section = txt in CHECKLIST_HEADINGS
            out.append(block_html(n))
            i += 1
            continue

        if tag == "L":
            out.append(list_html(n, checklist=in_checklist_section))
            i += 1
            continue

        if tag == "Figure":
            cap = None
            # caption may be the next NonStruct/P starting with "Figure N."
            if i + 1 < len(top) and re.match(r"Figure \d+\.", plain(top[i + 1]).strip()):
                cap = top[i + 1]
                i += 1
            else:
                # or nested inside the figure's parent; search inside
                pass
            out.append(figure_html(n, cap))
            i += 1
            continue

        # caption nested inside a NonStruct wrapper together with Figure
        if tag == "NonStruct":
            figs = [k for k in n["children"] if k.get("tag") == "Figure"]
            caps = [k for k in n["children"] if "tag" in k and re.match(r"Figure \d+\.", plain(k).strip())]
            if figs and caps:
                out.append(figure_html(figs[0], caps[0]))
                i += 1
                continue

        out.append(block_html(n))
        i += 1
    flush_wf()
    close()

    body = "\n".join(out)
    OUT.write_text("<!doctype html>\n<html lang=\"hi\"><head><meta charset=\"utf-8\">"
                   "<title>ZERO TO FIRST CLIENT — extracted manuscript</title></head><body>\n"
                   + body + "\n</body></html>\n")
    print(f"wrote {OUT} ({len(body) // 1024} KB)")


if __name__ == "__main__":
    main()
