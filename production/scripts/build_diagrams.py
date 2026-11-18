#!/usr/bin/env python3
"""Rebuild the manuscript's 24 diagrams as vector, print-safe HTML/SVG fragments.

Every diagram is a measured canvas 102 mm wide (the text block):
  * boxes and all labels are HTML text (shaped by HarfBuzz: correct Devanagari)
  * connectors, bars and markers are SVG
Label wording is the original's, unchanged (verified by validate_diagrams.py
against the label text stored from the original PDF).

Colour tokens inside the SVG are written as DGINK / DGSOFT / DGACC / DGMID and
replaced per edition by typeset.py (print: K-only DeviceCMYK; digital: navy/violet).
HTML boxes use CSS variables from the edition's token file.

Output: production/design-system/diagrams/fig-NN.html  (Figure 2 is hand-built: fig-02.html)
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "design-system/diagrams"
W = 102.0


class Canvas:
    def __init__(self, h, desc):
        self.h, self.desc, self.svg, self.html = h, desc, [], []

    # ---- svg primitives (mm units) ----
    def line(self, pts, arrow=True, dash=False, color="DGINK", width=0.35):
        d = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        da = ' stroke-dasharray="1.2 0.9"' if dash else ""
        self.svg.append(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="{width}"{da}/>')
        if arrow:
            (x0, y0), (x1, y1) = pts[-2], pts[-1]
            import math
            a = math.atan2(y1 - y0, x1 - x0)
            L, s = 1.5, 0.75
            p1 = (x1 - L * math.cos(a) + s * math.sin(a), y1 - L * math.sin(a) - s * math.cos(a))
            p2 = (x1 - L * math.cos(a) - s * math.sin(a), y1 - L * math.sin(a) + s * math.cos(a))
            self.svg.append(f'<polygon points="{x1:.2f},{y1:.2f} {p1[0]:.2f},{p1[1]:.2f} {p2[0]:.2f},{p2[1]:.2f}" fill="{color}"/>')

    def rect(self, x, y, w, h, fill="none", stroke="DGINK", sw=0.35, rx=0.8, op=None):
        o = ""
        if op is not None:             # solid tint instead of transparency (print-safe, no RGB groups)
            fill, o = f"DGTINT:{float(op):.3f}", ""
        self.svg.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" fill="{fill}"{o} stroke="{stroke}" stroke-width="{sw}"/>')

    def circle(self, cx, cy, r, fill="DGINK", stroke="none", sw=0.35):
        self.svg.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    # ---- html items ----
    def box(self, x, y, w, h, title, sub="", style="plain", align="center"):
        s = f'<span class="dgb-s">{sub}</span>' if sub else ""
        self.html.append(f'<div class="dgb dgb-{style}" style="left:{x:.2f}mm;top:{y:.2f}mm;width:{w:.2f}mm;height:{h:.2f}mm;text-align:{align}">'
                         f'<span class="dgb-t">{title}</span>{s}</div>')

    def text(self, x, y, w, html, cls="", align="left"):
        self.html.append(f'<div class="dgt {cls}" style="left:{x:.2f}mm;top:{y:.2f}mm;width:{w:.2f}mm;text-align:{align}">{html}</div>')

    def flow(self, items, y, h, x0=0.0, w_total=W, gap=3.6, arrows=True):
        n = len(items)
        bw = (w_total - (n - 1) * gap) / n
        xs = []
        for i, it in enumerate(items):
            title, sub, style = (list(it) + ["", "plain"])[:3]
            x = x0 + i * (bw + gap)
            xs.append(x)
            self.box(x, y, bw, h, title, sub, style or "plain")
            if arrows and i:
                self.line([(x - gap + 0.5, y + h / 2), (x - 0.5, y + h / 2)])
        return xs, bw

    def render(self):
        import re as _re
        # stroke transparency -> solid tint (print-safe, no transparency groups)
        self.svg = [_re.sub(r'stroke="DGINK"([^>]*?) stroke-opacity="([0-9.]+)"', r'stroke="DGTINT:\2"\1', x) for x in self.svg]
        # SVG default fill is black (RGB); lines are stroke-only
        self.svg = [x.replace("<line ", '<line fill="none" ') for x in self.svg]
        return (f"<!-- {self.desc} -->\n"
                f'<div class="dg dgc" style="height:{self.h:.2f}mm">'
                f'<svg class="dg-shapes" viewBox="0 0 {W} {self.h:.2f}" width="{W}mm" height="{self.h:.2f}mm">'
                + "".join(self.svg) + "</svg>" + "".join(self.html) + "</div>\n")


def save(n, c):
    (OUT / f"fig-{n:02d}.html").write_text(c.render())


HDR = "Vector rebuild for the 135 × 210 mm paperback from the original Figure {n} (source PDF p.{p}). Labels are the original's text, unchanged."

# ---------------------------------------------------------------- Fig 1 roadmap
c = Canvas(66, HDR.format(n=1, p=8) + " Bars rise chapter by chapter; tone marks the four stages.")
c.text(0, 0, 40, '<b class="dg-big">Zero</b><br>बिना service, बिना proof')
stages = ["Stage 1 Find", "Stage 2 Build", "Stage 3 Get client", "Stage 4 Execute"]
tone = ["0.06", "0.13", "0.22", "0.32"]
for i, s in enumerate(stages):
    c.rect(0.4, 14.6 + i * 4.4, 2.6, 2.6, fill="DGINK", stroke="DGINK", sw=0.2, rx=0.3, op=tone[i])
    c.text(4.2, 13.9 + i * 4.4, 30, s, "dg-small")
steps = [("Idea", "Ch 1"), ("AI toolkit", "Ch 2"), ("Offer", "Ch 3"), ("Research", "Ch 4"), ("Portfolio", "Ch 5"),
         ("Price", "Ch 6"), ("Marketing", "Ch 7"), ("Outreach", "Ch 8"), ("Delivery", "Ch 9"), ("30 days", "Ch 10")]
bw, gap, base = 9.6, 0.62, 66
for i, (t, ch) in enumerate(steps):
    x = i * (bw + gap)
    top = base - 12 - i * 5.0
    st = 0 if i < 3 else 1 if i < 6 else 2 if i < 9 else 3
    c.rect(x, top, bw, base - top, fill="DGINK", stroke="none", sw=0, rx=0.4, op=tone[st])
    c.svg.append(f'<line x1="{x:.2f}" y1="{top:.2f}" x2="{x + bw:.2f}" y2="{top:.2f}" stroke="DGINK" stroke-width="0.7"/>')
    c.text(x - 1, top + 1.2, bw + 2, f"<b>{t}</b><br>{ch}", "dg-tiny", "center")
save(1, c)

# ---------------------------------------------------------------- Fig 3 human-in-the-loop
c = Canvas(54, HDR.format(n=3, p=23) + " Two lanes: YOU (top) and AI (bottom).")
c.rect(0, 0, W, 21, fill="DGINK", stroke="none", op="0.05", rx=0.8)
c.rect(0, 24, W, 21, fill="DGINK", stroke="none", op="0.0", rx=0.8)
c.svg.append('<rect x="0" y="24" width="102" height="21" rx="0.8" fill="none" stroke="DGINK" stroke-width="0.25" stroke-dasharray="1 0.8"/>')
c.text(1.4, 1.0, 12, "YOU", "dg-lane")
c.text(1.4, 25.0, 12, "AI", "dg-lane")
bw, bh = 20.5, 12.5
c.box(4, 6.0, bw, bh, "Brief", "goal, audience, constraints")
c.box(26, 29.5, bw, bh, "Draft", "ideas, outline, first version")
c.box(50, 6.0, bw, bh, "Verify", "facts, numbers, links, tone", "em1")
c.box(54, 29.5, bw, bh, "Revise", "specific feedback के साथ")
c.box(78.5, 6.0, 22.5, bh, "Deliver", "आपका नाम, आपकी ज़िम्मेदारी", "em2")
c.line([(14.25, 18.5), (14.25, 35.75), (25.5, 35.75)])
c.line([(46.5, 35.75), (49, 35.75), (55, 18.9)])
c.line([(62, 18.5), (62, 29.0)])
c.line([(70, 29.0), (68, 18.9)])
c.line([(70.5, 12.25), (78, 12.25)])
c.text(0, 47.4, W, "<b>नियम:</b> AI के हाथ में draft, आपके हाथ में decision. Client का private data AI में तभी जब client और tool की policy allow करे.", "dg-note", "center")
save(3, c)

# ---------------------------------------------------------------- Fig 4 tools by job
rows = [("Think + write", "ChatGPT, Claude, Gemini", "Ideas, drafts, summaries, role-play"),
        ("Research", "Google, Trends, Perplexity, NotebookLM", "सवाल, sources, comparison"),
        ("Design", "Canva, Figma", "Posts, decks, portfolio visuals"),
        ("Organise", "Notion, Google Sheets, Trello", "Tracker, CRM, project boards"),
        ("Communicate", "Gmail, WhatsApp Business, Calendly", "Outreach, scheduling, updates"),
        ("Automate", "Zapier, Make, n8n", "बार-बार वाले simple steps"),
        ("Publish code", "GitHub Pages, Netlify, Vercel", "Portfolio और demo sites")]
rh = 7.6
c = Canvas(len(rows) * (rh + 1.0), HDR.format(n=4, p=25) + " One row per job.")
for i, (a, b, d) in enumerate(rows):
    y = i * (rh + 1.0)
    c.box(0, y, 21, rh, a, "", "em1", "left")
    c.box(22, y, 41, rh, b, "", "plain", "left")
    c.text(65, y + 2.0, 37, d, "dg-small")
save(4, c)

# ---------------------------------------------------------------- Fig 5 RCTFV
c = Canvas(27, HDR.format(n=5, p=26) + " Five parts of a prompt; Verify is part of the prompt.")
items = [("R", "Role", "किस expert की तरह सोचे"), ("C", "Context", "आपकी स्थिति और audience"), ("T", "Task", "एक exact काम"),
         ("F", "Format", "Output का रूप"), ("V", "Verify", "क्या flag करे, क्या न बनाए")]
xs, bw = c.flow([(f'<span class="dg-letter">{l}</span> {t}', s, "em1" if l == "V" else "plain") for l, t, s in items], 0, 17)
c.text(0, 20.2, W, "पहला output draft है। Improve loop: general feedback नहीं, specific line और specific बदलाव बताइए।", "dg-note", "center")
save(5, c)

# ---------------------------------------------------------------- Fig 6 skill to service
c = Canvas(42, HDR.format(n=6, p=34) + " Top row: five steps. Bottom row: hypothetical video-editor example.")
c.flow([("Skill", "जो आप कर सकते हो"), ("Problem", "जिससे customer परेशान है"), ("Offer", "clear outcome, clear buyer", "em1"),
        ("Package", "scope, time, price, revisions"), ("Proof", "demo या pilot project", "em2")], 0, 15)
c.text(0, 18.2, W, "<b>Example:</b> एक ही skill, पाँच steps के बाद", "dg-small")
c.flow([("", "I can edit video", "ex"), ("", "Clinic Reels irregular आते हैं", "ex"), ("", "8 Reels a month for clinics", "ex"),
        ("", "Fixed price, 2 revisions, 48 h", "ex"), ("", "3 sample Reels from stock", "ex")], 23.5, 14, arrows=False)
save(6, c)

# ---------------------------------------------------------------- Fig 7 packages
c = Canvas(48, HDR.format(n=7, p=35) + " Three tiers; the difference is scope.")
c.text(0, 0, 66, "<b>Scope बढ़ता है, सिर्फ़ price नहीं।</b><br>Standard को best value बनाओ।", "dg-small")
tiers = [("BASIC", "Starter fix", ["1 core deliverable", "1 revision round", "Short timeline"], "plain", 22),
         ("STANDARD", "Most buyers", ["Core + 2 add-ons", "2 revision rounds", "Handover call"], "em1", 15),
         ("PREMIUM", "Full outcome", ["Core + add-ons + setup", "3 revision rounds", "30-day support"], "plain", 8)]
for i, (t, s, bl, st, top) in enumerate(tiers):
    x = 0 + i * 34.4
    li = "".join(f"<li>{b}</li>" for b in bl)
    c.box(x, top, 32.6, 48 - top, f'<span class="dg-tier">{t}</span>', f'{s}<ul class="dg-bullets">{li}</ul>', st, "left")
save(7, c)

# ---------------------------------------------------------------- Fig 8 research steps + decision rule
c = Canvas(38, HDR.format(n=8, p=43) + " Five research steps, then the decision rule.")
c.flow([("1 Problem", "Google, forums: लोग क्या पूछते हैं?"), ("2 Persona", "कौन सा exact buyer?"), ("3 Competitors", "5 players का price और gap"),
        ("4 Interviews", "5 real बातचीत, सच्ची problem", "em1"), ("5 Pre-sell", "offer दिखाओ: हाँ/ना/कितना?", "em2")], 0, 15)
c.text(0, 18.0, 40, "<b>Decision rule</b>", "dg-small")
for i, (k, t, st) in enumerate([("GO", "Demand score 16+ और कम से कम 1 serious buyer signal", "em1"),
                                 ("REFINE", "Score 10 से 15: niche या offer बदलकर फिर test", "plain"),
                                 ("DROP", "Score 10 से कम या कोई paying signal नहीं", "dash")]):
    c.box(i * 34.4, 23.0, 32.6, 14, f'<span class="dg-tier">{k}</span>', t, st, "left")
save(8, c)

# ---------------------------------------------------------------- Fig 9 persona card
c = Canvas(56, HDR.format(n=9, p=45) + " Persona card; all details fictional.")
c.rect(0, 0, W, 56, fill="none", stroke="DGINK", sw=0.4, rx=1)
c.rect(0, 0, 32, 56, fill="DGINK", stroke="none", op="0.07", rx=1)
c.text(3, 3, 27, '<span class="dg-tier">PERSONA CARD</span><br><b class="dg-big">Riya</b><br><span class="dg-tiny">काल्पनिक उदाहरण</span>', "dg-small")
c.text(3, 23, 27, "Dental clinic owner<br>Tier 2 city<br>Staff: 4<br>Decides alone", "dg-small")
c.text(3, 45, 27, "<b>एक person, पूरा market नहीं।</b>", "dg-small")
cells = [("Problem", "Google पर आसानी से नहीं मिलती, calls कम"), ("Trigger", "नया competitor पास में खुला"),
         ("Current fix", "Nephew का पुराना Instagram page"), ("Budget signal", "Ads पर पहले से खर्च हो रहा है"),
         ("Where to find", "Local WhatsApp groups, Instagram, Google"), ("Objection", "\"पिछले designer ने बीच में छोड़ दिया\"")]
for i, (k, v) in enumerate(cells):
    col, row = i % 2, i // 2
    x, y = 35 + col * 34, 3 + row * 17.5
    c.text(x, y, 31, f"<b>{k}</b><br>{v}", "dg-small")
    if row < 2:
        c.svg.append(f'<line x1="{x:.1f}" y1="{y + 15.6:.1f}" x2="{x + 31:.1f}" y2="{y + 15.6:.1f}" stroke="DGINK" stroke-width="0.2" stroke-opacity="0.5"/>')
save(9, c)

# ---------------------------------------------------------------- Fig 10 positioning map
c = Canvas(50, HDR.format(n=10, p=47) + " Positioning map illustration (not market data).")
mx, my, mw, mh = 9, 1, 57, 41
c.rect(mx, my, mw, mh, fill="none", stroke="DGINK", sw=0.3, rx=0.6)
c.svg.append(f'<line x1="{mx + mw / 2}" y1="{my}" x2="{mx + mw / 2}" y2="{my + mh}" stroke="DGINK" stroke-width="0.25" stroke-dasharray="1 0.8"/>')
c.svg.append(f'<line x1="{mx}" y1="{my + mh / 2}" x2="{mx + mw}" y2="{my + mh / 2}" stroke="DGINK" stroke-width="0.25" stroke-dasharray="1 0.8"/>')
c.text(0, 7, 8.5, "High", "dg-tiny", "right")
c.text(0, 19.6, 8.5, "<b>Price</b>", "dg-tiny", "right")
c.text(0, 33, 8.5, "Low", "dg-tiny", "right")
c.text(mx, 43.6, mw, "<b>Generalist ← Focus → Specialist</b>", "dg-tiny", "center")
for (px, py, lab) in [(15, 8, "Big agency"), (42, 7, "Premium niche studio"), (18, 31, "Local print shop"), (26, 37.5, "Marketplace gig")]:
    c.circle(px, py, 1.1, fill="DGMID")
    c.text(px + 1.9, py - 1.6, 30, lab, "dg-tiny")
c.circle(57, 27, 2.0, fill="DGACC")
c.text(46, 30.2, 20, "<b>YOU: clear niche, fair price</b>", "dg-tiny", "center")
c.rect(69, 1, 33, 41, fill="none", stroke="DGINK", sw=0.25, rx=0.6)
c.text(71, 3, 29.5, "<b>कैसे पढ़ें</b><br>खाली हिस्सा हमेशा gap नहीं होता। Check करो:<br>1. क्या वहाँ buyers हैं?<br>2. क्या वे pay करते हैं?<br>3. क्या आप deliver कर सकते हो?<br>तीन हाँ, तभी position लो। यह illustration है, market data नहीं।", "dg-tiny")
save(10, c)

# ---------------------------------------------------------------- Fig 11 brand layers
c = Canvas(52, HDR.format(n=11, p=51) + " Brand identity layers; each layer decides the ones below.")
layers = [("Positioning", "किसके लिए, कौन सी problem, क्यों आप", "em2", 0, 102),
          ("Name + Domain", "बोलने और लिखने में आसान, legal check", "plain", 5, 92),
          ("Voice", "Clear, helpful, बिना बढ़ा-चढ़ाकर", "plain", 10, 82),
          ("Visual system", "1 logo, 2 fonts, 2 से 3 colours", "plain", 15, 72),
          ("Touchpoints", "Email, profile, proposal, invoice", "em2", 20, 62)]
for i, (t, s, st, x, w) in enumerate(layers):
    c.box(x, i * 10.6, w, 9.4, t, s, st, "left")
save(11, c)

# ---------------------------------------------------------------- Fig 12 portfolio tree
c = Canvas(54, HDR.format(n=12, p=53) + " Simple portfolio structure.")
c.box(33, 0, 36, 11, "Home", "5 seconds में clear: किसके लिए, क्या", "em2")
xs = [0, 26, 52, 78]
kids = [("Services", "packages, scope, starting price"), ("Work", "3 case studies, demo labelled"),
        ("About", "आप कौन, क्यों, real details"), ("Contact", "form, email, next step")]
c.svg.append('<line x1="51" y1="11" x2="51" y2="14.5" stroke="DGINK" stroke-width="0.35"/>')
c.svg.append('<line x1="12" y1="14.5" x2="90" y2="14.5" stroke="DGINK" stroke-width="0.35"/>')
for x, (t, s) in zip(xs, kids):
    c.line([(x + 12, 14.5), (x + 12, 18.2)])
    c.box(x, 18.5, 24, 12, t, s)
c.line([(38, 30.5), (38, 37.2)])
c.box(26, 37.5, 24, 11.5, "Case study", "Problem, Process, Result", "em1")
c.line([(90, 30.5), (90, 37.2)])
c.box(78, 37.5, 24, 11.5, "Discovery call", "एक clear CTA", "em1")
c.text(0, 40, 24, "<b>हर page का एक काम, एक main button।</b>", "dg-small")
save(12, c)

# ---------------------------------------------------------------- Fig 13 price limits
c = Canvas(40, HDR.format(n=13, p=60) + " Floor from your cost, range from the market, ceiling from client value.")
c.text(0, 0, W, "<b>आपकी price इन तीन limits के बीच बैठती है</b>", "dg-small")
c.box(0, 6, 28, 7, "Loss zone", "", "dash")
c.box(28, 6, 40, 7, "Sustainable price zone", "", "em1")
c.box(68, 6, 34, 7, "Hard to justify", "", "plain")
for x in (28, 68):
    c.svg.append(f'<line x1="{x}" y1="4.6" x2="{x}" y2="14.4" stroke="DGINK" stroke-width="0.7"/>')
c.text(0, 16, 32, "<b>FLOOR: आपकी cost</b><br>Hours × minimum hourly rate<br>+ tools और fees<br>+ tax reserve<br>इससे नीचे = घाटा", "dg-tiny")
c.text(35, 16, 32, "<b>MARKET: buyers क्या देखते हैं</b><br>5 से 10 real competitors की range<br>Position: value vs. price<br>भरोसा भी price है", "dg-tiny")
c.text(70, 16, 32, "<b>CEILING: client का value</b><br>इस काम से client को क्या फ़ायदा या बचत?<br>बिना सबूत value claim मत करो", "dg-tiny")
save(13, c)

# ---------------------------------------------------------------- Fig 14 revenue example
c = Canvas(46, HDR.format(n=14, p=60) + " Hypothetical revenue arithmetic.")
c.box(0, 0, 18, 11, '<span class="dg-num">2</span>', "clients")
c.text(18, 3.2, 8, '<b class="dg-op">×</b>', "", "center")
c.box(26, 0, 30, 11, '<span class="dg-num">₹15,000</span>', "avg. project")
c.text(56, 3.2, 8, '<b class="dg-op">=</b>', "", "center")
c.box(64, 0, 38, 11, '<span class="dg-num">₹30,000</span>', "revenue", "em1")
rows = [("− Tools, domain, fees", "₹2,000"), ("− Direct costs", "₹3,000"), ("− Tax reserve at 15% of revenue (planning assumption)", "₹4,500")]
for i, (a, b) in enumerate(rows):
    y = 14 + i * 5.4
    c.text(0, y, 84, a, "dg-small")
    c.text(84, y, 18, b, "dg-small", "right")
    c.svg.append(f'<line x1="0" y1="{y + 4.6:.1f}" x2="102" y2="{y + 4.6:.1f}" stroke="DGINK" stroke-width="0.2" stroke-opacity="0.45"/>')
c.text(0, 31, 80, "<b>= Take-home before your time cost</b>", "dg-small")
c.text(80, 30.4, 22, '<b class="dg-num">₹20,500</b>', "", "right")
c.text(0, 39, W, "सभी numbers hypothetical हैं, income promise नहीं। अपने numbers calculator में डालो।", "dg-note")
save(14, c)

# ---------------------------------------------------------------- Fig 15 proposal to payment
c = Canvas(52, HDR.format(n=15, p=61) + " Two lanes: YOU (top) and CLIENT (bottom); sequence left to right.")
c.rect(0, 0, W, 19, fill="DGINK", stroke="none", op="0.05", rx=0.8)
c.svg.append('<rect x="0" y="22" width="102" height="19" rx="0.8" fill="none" stroke="DGINK" stroke-width="0.25" stroke-dasharray="1 0.8"/>')
c.text(1.4, 1.0, 14, "YOU", "dg-lane")
c.text(1.4, 23.0, 18, "CLIENT", "dg-lane")
bw, bh = 19.5, 12.5
you = [(4, "Proposal", "scope, price, date"), (37, "Agreement", "written scope, milestones"), (69, "Deliver M1", "review link")]
cli = [(20.5, "Questions", "negotiate scope, not just price"), (53, "Advance", "invoice पर payment"), (82.5, "Approve + pay", "balance, then final files")]
for x, t, s in you:
    c.box(x, 4.5, bw, bh, t, s)
for x, t, s in cli:
    c.box(x, 26.5, bw, bh, t, s, "em1" if t == "Approve + pay" else "plain")
seq = [(you[0], cli[0]), (cli[0], you[1]), (you[1], cli[1]), (cli[1], you[2]), (you[2], cli[2])]
for a, b in seq:
    ay = 17.0 if a in you else 27.0
    by = 27.0 if b in cli else 17.0
    c.line([(a[0] + bw * 0.75, ay), (b[0] + bw * 0.25, by - (0.4 if by > ay else -0.4))])
c.text(0, 43.4, W, "Advance मिलने से पहले काम शुरू नहीं। Balance मिलने से पहले final source files handover नहीं, अगर agreement में ऐसा लिखा हो।", "dg-note", "center")
save(15, c)

# ---------------------------------------------------------------- Fig 16 GST map
c = Canvas(60, HDR.format(n=16, p=63) + " Educational decision map, not legal or tax advice.")
c.box(30, 0, 42, 8, "क्या GST registration चाहिए?", "", "em2")
heads = [(0, "Mandatory category?", "Section 24 cases, जैसे reverse charge, agent"),
         (35, "Turnover test", "All-India aggregate turnover threshold से ऊपर?"),
         (70, "Client demand", "Client GST invoice माँगता है (voluntary route)")]
for x, t, s in heads:
    c.line([(51, 8), (x + 16, 13.6)])
    c.box(x, 14, 32, 12.5, t, s)
c.line([(16, 26.5), (16, 31.6)])
c.box(0, 32, 32, 10.5, "Likely yes", "CA से category confirm", "em1")
c.line([(44, 26.5), (43, 31.6)])
c.box(35, 32, 15.4, 10.5, "Yes", "Register", "em1")
c.line([(58, 26.5), (59, 31.6)])
c.box(51.6, 32, 15.4, 10.5, "No", "Monitor monthly")
c.line([(86, 26.5), (86, 31.6)])
c.box(70, 32, 32, 10.5, "Possible", "Compliance cost vs benefit जाँचो")
c.rect(0, 46, W, 13.5, fill="none", stroke="DGINK", sw=0.35, rx=0.8)
c.text(2, 47.6, 98, "<b>Threshold reference:</b> services में सामान्यतः ₹20 lakh; Manipur, Mizoram, Nagaland, Tripura से ₹10 lakh (शर्तें Chapter 6 में)। Educational map है, legal या tax advice नहीं। State, service type और latest notification अपने CA/GST practitioner से confirm करो।", "dg-small")
save(16, c)

# ---------------------------------------------------------------- Fig 17 funnel
data = [("100", "Qualified prospects", 62), ("30", "Personal messages sent", 54), ("10", "Replies", 46),
        ("4", "Discovery calls", 38), ("2", "Proposals", 30), ("1", "Paid project", 22)]
c = Canvas(6 * 6.6 + 7, HDR.format(n=17, p=70) + " Illustrative funnel, not a benchmark.")
for i, (n_, lab, w) in enumerate(data):
    y = i * 6.6
    x = (64 - w) / 2
    c.rect(x, y, w, 5.6, fill="DGINK", stroke="none", op=f"{0.07 + i * 0.07:.2f}", rx=0.5)
    c.text(x, y + 0.9, w, f"<b>{n_}</b>", "dg-small", "center")
    c.svg.append(f'<line x1="{x + w + 1:.1f}" y1="{y + 2.8:.1f}" x2="66" y2="{y + 2.8:.1f}" stroke="DGINK" stroke-width="0.2" stroke-dasharray="0.6 0.6" stroke-opacity="0.6"/>')
    c.text(67, y + 0.9, 35, lab, "dg-small")
c.text(0, 6 * 6.6 + 1.2, W, "Illustrative assumption, benchmark नहीं। अपना funnel अपने tracker से measure करो।", "dg-note")
save(17, c)

# ---------------------------------------------------------------- Fig 18 lead generation
c = Canvas(44, HDR.format(n=18, p=77) + " Lead generation process with weekly review loop.")
xs, bw = c.flow([("Source", "Maps, directories, Instagram, LinkedIn"), ("Qualify", "fit, signal, ability to pay"),
                 ("Find person", "owner, public business contact"), ("Personalise", "1 real observation per prospect", "em1"),
                 ("Track", "sheet: status, next date", "em2")], 0, 18)
c.svg.append(f'<polyline points="{xs[4] + bw / 2:.2f},18 {xs[4] + bw / 2:.2f},22 {xs[0] + bw / 2:.2f},22" fill="none" stroke="DGINK" stroke-width="0.35"/>')
c.line([(xs[0] + bw / 2, 22), (xs[0] + bw / 2, 18.4)])
c.text(xs[0] + bw, 22.6, xs[4] - xs[0] - bw, "हर हफ़्ते review: कौन सा source reply लाता है? वहीं ज़्यादा समय दो।", "dg-tiny", "center")
c.text(0, 30, 16, "<b>Allowed</b>", "dg-small")
c.text(16, 30, 86, "Public business information manually पढ़ना, relevant एक-एक message भेजना", "dg-small")
c.text(0, 36.5, 16, "<b>Avoid</b>", "dg-small")
c.text(16, 36.5, 86, "Scraping tools, bought lists, bulk WhatsApp, LinkedIn automation extensions", "dg-small")
save(18, c)

# ---------------------------------------------------------------- Fig 19 outreach timeline
c = Canvas(34, HDR.format(n=19, p=79) + " Suggested rhythm, not a fixed rule.")
pts = [(12, "Day 0", "First message", "personal observation + small question"), (34.5, "Day 3", "Follow-up 1", "extra value, कोई guilt नहीं"),
       (57, "Day 7", "Follow-up 2", "short example या sample link"), (79.5, "Day 14", "Close the loop", "polite last note, door open")]
c.svg.append('<line x1="3" y1="7" x2="99" y2="7" stroke="DGINK" stroke-width="0.45"/>')
for x, d, t, s in pts:
    c.circle(x, 7, 1.3, fill="DGINK")
    c.text(x - 10, 1, 20, f"<b>{d}</b>", "dg-small", "center")
    c.text(x - 11, 10, 22, f"<b>{t}</b><br>{s}", "dg-tiny", "center")
c.circle(97, 7, 1.3, fill="#fff" if False else "DGPAPER", stroke="DGINK", sw=0.6)
c.text(91, 1, 11, "<b>Stop</b>", "dg-small", "right")
c.text(0, 26.5, W, "\"Not interested\" या \"stop\" मिलते ही list से हटाओ और दोबारा contact मत करो।", "dg-note", "center")
save(19, c)

# ---------------------------------------------------------------- Fig 20 discovery call
c = Canvas(44, HDR.format(n=20, p=81) + " Segment widths are proportional to minutes.")
segs = [("Open", "3 min", 3, "plain"), ("Situation", "7 min", 7, "plain"), ("Problem", "8 min", 8, "em1"),
        ("Fit", "5 min", 5, "em1"), ("Next step", "4 min", 4, "em2"), ("Q&A", "3 min", 3, "plain")]
x = 0.0
unit = (W - 5 * 0.8) / 30
for t, m, mins, st in segs:
    w = mins * unit
    c.box(x, 0, w, 10, t, m, st)
    x += w + 0.8
c.text(0, 12.6, W, "<b>30-minute call: client 70% बोले, आप 30%</b>", "dg-small")
c.text(0, 18.0, W, "<b>Open:</b> \"आज 30 minute हैं। पहले आपकी situation समझते हैं, फिर देखते हैं fit है या नहीं। ठीक है?\"<br>"
       "<b>Problem:</b> \"यह problem पिछले महीने में business को कैसे affect कर रही है?\"<br>"
       "<b>Fit:</b> \"आपके दिमाग में इसके लिए कोई budget range है?\"<br>"
       "<b>Next step:</b> \"शुक्रवार तक 1-page proposal आपके पास होगा। Decision में और कौन शामिल है?\"", "dg-small")
save(20, c)

# ---------------------------------------------------------------- Fig 21 onboarding
c = Canvas(33, HDR.format(n=21, p=87) + " First 48 hours of onboarding.")
c.flow([("Welcome", "same day message"), ("Agreement + Invoice", "scope signed, advance"), ("Brief + Access", "form, logins, assets", "em1"),
        ("Kickoff", "20 min call, plan"), ("First update", "date fixed, expectation set", "em2")], 0, 17)
c.text(0, 19.6, W, "<b>Access rule:</b> client से password chat में मत माँगो। Delegate access या password manager share, और project के बाद access remove करो।", "dg-tiny")
c.text(0, 27.0, W, "<b>Goal:</b> पहले 48 घंटे में client को लगे कि काम सही हाथों में है।", "dg-tiny")
save(21, c)

# ---------------------------------------------------------------- Fig 22 delivery lifecycle
c = Canvas(42, HDR.format(n=22, p=89) + " Delivery lifecycle with a limited revision loop.")
bw, bh = 28, 10
P = {"1": (0, 0), "2": (37, 0), "3": (74, 0), "4": (74, 24), "5": (37, 24), "6": (0, 24)}
c.box(*P["1"], bw, bh, "1 Plan", "milestones, dates")
c.box(*P["2"], bw, bh, "2 Build", "focused work blocks")
c.box(*P["3"], bw, bh, "3 Self QA", "checklist before sharing", "em1")
c.box(*P["4"], bw, bh, "4 Client review", "one consolidated list")
c.box(*P["5"], bw, bh, "5 Revise", "within agreed rounds")
c.box(*P["6"], bw, bh, "6 Deliver", "files, handover, invoice", "em2")
c.line([(28.5, 5), (36.5, 5)]); c.line([(65.5, 5), (73.5, 5)]); c.line([(88, 10.2), (88, 23.6)])
c.line([(73.5, 29), (65.5, 29)])
c.svg.append('<polyline points="51,24 51,17 82,17" fill="none" stroke="DGINK" stroke-width="0.35"/>')
c.line([(82, 17), (82, 10.4)])
c.text(38, 12.2, 36, "changes दोबारा QA से गुज़रते हैं", "dg-tiny", "center")
c.svg.append('<polyline points="88,34 88,37.6 14,37.6" fill="none" stroke="DGINK" stroke-width="0.35"/>')
c.line([(14, 37.6), (14, 34.4)])
c.text(16, 38.0, 70, "Approved: सीधे delivery। Scope से बाहर की request: नया quote।", "dg-tiny", "center")
save(22, c)

# ---------------------------------------------------------------- Fig 23 retention loop
c = Canvas(46, HDR.format(n=23, p=92) + " Client retention loop.")
xs, bw = c.flow([("Deliver well", "on time, no surprises"), ("Check in", "day 7: सब ठीक चल रहा?"), ("Feedback", "form + written permission", "em1"),
                 ("Referral", "specific ask, no pressure", "em1"), ("Retainer", "monthly scope, clear hours", "em2")], 0, 17)
c.svg.append(f'<polyline points="{xs[4] + bw / 2:.2f},17 {xs[4] + bw / 2:.2f},21.5 {xs[0] + bw / 2:.2f},21.5" fill="none" stroke="DGINK" stroke-width="0.35"/>')
c.line([(xs[0] + bw / 2, 21.5), (xs[0] + bw / 2, 17.4)])
c.text(xs[0] + bw, 22.0, xs[4] - xs[0] - bw, "Results share करो, अगला छोटा project suggest करो, repeat", "dg-tiny", "center")
c.text(0, 28.5, W, "<b>क्यों:</b> पुराने client को पहले से trust है। उनसे बात करना अक्सर cold outreach से आसान होता है।<br>"
       "Testimonial तभी publish करो जब client ने exact text और name के लिए लिखित हाँ कही हो।<br>कोई fake review, कोई बढ़ाया हुआ result नहीं।", "dg-tiny")
save(23, c)

# ---------------------------------------------------------------- Fig 24 weekly milestones
weeks = [("Week 1", "Choose + validate", ["Idea matrix", "5 interviews", "Demand score", "Business statement"]),
         ("Week 2", "Portfolio + offer", ["3 demo projects", "1-page portfolio", "3 packages", "Case studies"]),
         ("Week 3", "Prospects + outreach", ["50 qualified leads", "20+ personal messages", "Follow-ups running", "Daily tracker"]),
         ("Week 4", "Calls + proposals", ["Discovery calls", "Proposals sent", "Follow-up + close", "Review + next 30"])]
c = Canvas(52, HDR.format(n=24, p=96) + " Four weekly milestones and their outputs.")
for i, (w, s, items) in enumerate(weeks):
    x = i * 25.8
    c.svg.append(f'<line x1="{x:.1f}" y1="0.4" x2="{x + 24.6:.1f}" y2="0.4" stroke="DGINK" stroke-width="{0.5 + i * 0.35:.2f}"/>')
    c.box(x, 1.6, 24.6, 8.6, f"<b>{w}</b>", s, "em1", "left")
    li = "".join(f"<li>{t}</li>" for t in items)
    c.box(x, 11.2, 24.6, 27, "", f'<ul class="dg-checks">{li}</ul>', "plain", "left")
c.text(0, 41.5, W, "<b>Milestone:</b> 30 दिन में client की guarantee नहीं है। Guarantee सिर्फ़ यह है कि आपके पास offer, proof, pipeline और data होगा जिससे आगे का decision साफ़ हो।", "dg-tiny")
save(24, c)

print("diagrams written:", sorted(p.name for p in OUT.glob("fig-*.html")))
