#!/usr/bin/env python3
"""Debug helper: print a compact outline of manuscript_tree.json for given source pages."""
import json, sys
d = json.load(open(sys.argv[1]))
pages = set()
for a in sys.argv[2].split(","):
    lo, _, hi = a.partition("-"); pages.update(range(int(lo), int(hi or lo) + 1))
maxw = int(sys.argv[3]) if len(sys.argv) > 3 else 100
def text(n):
    out = []
    for c in n["children"]:
        if "t" in c: out.append(("⏎" if c.get("nl") else "") + c["t"])
        else: out.append(text(c))
    return "".join(out)
def show(n, depth):
    if not set(n.get("pages", [])) & pages: return
    kids = [c for c in n["children"] if "tag" in c]
    runs = [c for c in n["children"] if "t" in c]
    label = n["tag"]
    if runs:
        r = runs[0]; label += f" ⟨{r['font'].split('+')[-1][:18]} {r['size']} {r['color']}{' B' if r['bold'] else ''}{' L' if r['uri'] else ''}⟩"
    if n.get("graphics"): label += f" [gfx {len(n['graphics'])}]"
    t = text(n) if (not kids or len(text(n)) < 60) else ""
    print("  " * depth + label + (" " + repr(t[:maxw]) if t else ""))
    if t and kids and len(text(n)) < 60: return
    for c in kids: show(c, depth + 1)
for c in d["tree"]["children"]:
    if "tag" in c: show(c, 0)
