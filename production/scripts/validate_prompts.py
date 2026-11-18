#!/usr/bin/env python3
"""Validate the AI prompt set: exactly 141 prompts, correct IDs, no duplicates,
correct sequence and chapter association, all fields present, and prompt
wording unchanged against the baseline extracted from the original PDF.

Expected distribution (locked by the production brief):
  Chapter 2 essential prompts  #C01–#C25   25
  Chapter-specific prompts     #C-A–#C-L   12
  Bonus A library              #001–#104  104
                                   total 141

Usage:
  validate_prompts.py <book.html> <report.json> [--baseline extracted.html]
Exit code 0 only if every check passes.
"""
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = {
    "chapter2": [f"C{n:02d}" for n in range(1, 26)],
    "chapter_specific": [f"C-{c}" for c in "ABCDEFGHIJKL"],
    "bonus_a": [f"{n:03d}" for n in range(1, 105)],
}
# chapter each chapter-specific prompt belongs to (from the original manuscript)
CHAPTER_OF = {"C-A": "01", "C-B": "01", "C-C": "03", "C-D": "03", "C-E": "04", "C-F": "05",
              "C-G": "06", "C-H": "06", "C-I": "07", "C-J": "08", "C-K": "09", "C-L": "10"}
REQUIRED_FIELDS = ["purpose", "body", "output", "verify"]


def norm(s):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", s)).strip()


def prompts(path):
    soup = BeautifulSoup(Path(path).read_text(), "lxml")
    out = []
    for div in soup.select("div.prompt"):
        pid = div.get("data-id", "")
        sec = div.find_parent("section")
        loc = "?"
        if sec is not None:
            if "chapter" in sec.get("class", []):
                loc = "chapter-" + sec.get("data-chapter", "?")
            elif "bonus" in sec.get("class", []):
                h = sec.find("h1")
                loc = "bonus-" + (h.get_text()[6:7] if h else "?")
            else:
                loc = sec.get("class", ["?"])[0]
        f = {
            "id": pid,
            "title": norm(div.select_one(".prompt-title").get_text()) if div.select_one(".prompt-title") else "",
            "category": norm(div.select_one(".prompt-cat").get_text()) if div.select_one(".prompt-cat") else "",
            "location": loc,
            "purpose": norm(" ".join(x.get_text() for x in div.select(".pf-purpose"))).removeprefix("PURPOSE").strip(),
            "body": norm(" ".join(x.get_text() for x in div.select(".prompt-body"))),
            "output": norm(" ".join(x.get_text() for x in div.select(".pf-output"))).removeprefix("OUTPUT").strip(),
            "example": norm(" ".join(x.get_text() for x in div.select(".pf-example"))).removeprefix("EXAMPLE").strip(),
            "verify": norm(" ".join(x.get_text() for x in div.select(".pf-verify"))).removeprefix("VERIFY").strip(),
        }
        f["body_sha256"] = hashlib.sha256(f["body"].encode()).hexdigest()[:16]
        f["placeholders"] = sorted(set(re.findall(r"\[[^\]]{1,60}\]", f["body"])))
        out.append(f)
    return out


def main():
    book, rep = sys.argv[1], sys.argv[2]
    base = sys.argv[4] if len(sys.argv) > 4 and sys.argv[3] == "--baseline" else None
    ps = prompts(book)
    ids = [p["id"] for p in ps]
    checks = []

    def check(name, ok, detail=""):
        checks.append({"check": name, "status": "PASS" if ok else "FAIL", "detail": detail})

    groups = {k: [i for i in ids if i in set(v)] for k, v in EXPECTED.items()}
    unknown = [i for i in ids if not any(i in v for v in EXPECTED.values())]
    for k, v in EXPECTED.items():
        got = groups[k]
        check(f"{k} count", len(got) == len(v), f"{len(got)} / {len(v)}")
        missing = [x for x in v if x not in got]
        check(f"{k} missing identifiers", not missing, ", ".join(missing) or "none")
        check(f"{k} sequence order", got == [x for x in v if x in got], "in order" if got == [x for x in v if x in got] else str(got))
    dups = sorted({i for i in ids if ids.count(i) > 1})
    check("duplicate identifiers", not dups, ", ".join(dups) or "none")
    check("unknown identifiers", not unknown, ", ".join(unknown) or "none")
    bodies = [p["body"] for p in ps]
    dup_bodies = sorted({p["id"] for p in ps if bodies.count(p["body"]) > 1})
    check("duplicate prompt text", not dup_bodies, ", ".join(dup_bodies) or "none")
    check("total count", len(ids) == 141, f"{len(ids)} / 141")

    # location / chapter association
    bad_loc = []
    for p in ps:
        want = ("chapter-02" if p["id"] in EXPECTED["chapter2"] else
                "chapter-" + CHAPTER_OF.get(p["id"], "") if p["id"] in CHAPTER_OF else "bonus-A")
        if p["location"] != want:
            bad_loc.append(f"{p['id']}@{p['location']} (want {want})")
    check("chapter association", not bad_loc, "; ".join(bad_loc) or "all prompts in their original chapter/section")

    # required fields
    missing_f = [f"{p['id']}:{f}" for p in ps for f in REQUIRED_FIELDS if not p[f]]
    check("required fields (purpose, prompt text, output, verify)", not missing_f, ", ".join(missing_f) or "all present")
    ex_missing = [p["id"] for p in ps if p["id"] in EXPECTED["chapter2"] and not p["example"]]
    check("Chapter 2 prompts carry EXAMPLE field", not ex_missing, ", ".join(ex_missing) or "all 25 present")

    # integrity against baseline (original manuscript extraction)
    if base:
        bp = {p["id"]: p for p in prompts(base)}
        changed = [p["id"] for p in ps if p["id"] in bp and (p["body"] != bp[p["id"]]["body"] or p["title"] != bp[p["id"]]["title"])]
        check("prompt title + text unchanged vs original", not changed, ", ".join(changed) or "all 141 identical")
        ph = [p["id"] for p in ps if p["id"] in bp and p["placeholders"] != bp[p["id"]]["placeholders"]]
        check("placeholders preserved", not ph, ", ".join(ph) or "all [placeholders] preserved")

    ok = all(c["status"] == "PASS" for c in checks)
    summary = {
        "chapter2": f"{len(groups['chapter2'])} / 25",
        "chapter_specific_C-A_to_C-L": f"{len(groups['chapter_specific'])} / 12",
        "bonus_a_001_to_104": f"{len(groups['bonus_a'])} / 104",
        "total": f"{len(ids)} / 141",
        "verdict": f"{len(ids)} / 141 prompts verified" if ok else "FAILED — see checks",
    }
    Path(rep).write_text(json.dumps({"source": str(book), "summary": summary, "checks": checks,
                                     "prompts": ps}, ensure_ascii=False, indent=1))
    for c in checks:
        print(f"{c['status']}  {c['check']}: {c['detail']}")
    print("RESULT:", summary["verdict"])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
