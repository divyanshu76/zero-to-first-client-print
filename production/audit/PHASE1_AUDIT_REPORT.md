# PHASE 1 — Repository and Manuscript Audit

**ZERO TO FIRST CLIENT — The AI-Powered Business Starter Kit** · 2026 Edition, First Edition
Audit date: 18 Nov 2026 · Branch `claude/ztfc-paperback-production-lj5f4b` · Authoritative source: `manuscript/ZERO_TO_FIRST_CLIENT_2026.pdf`

All facts below come from the files themselves. Machine-readable versions: `audit/asset_inventory.json`, `audit/content_inventory.json`, `validation/*.json`.

---

## 1. Repository inventory

Git: 2 existing commits preserved (`e6bf48b` initial structure, `56d2aea` genuine signature). No force-push or history rewrite. New work lives only under `production/`.

| File | Bytes | SHA-256 (first 12) | Facts | Role |
|---|---:|---|---|---|
| `manuscript/ZERO_TO_FIRST_CLIENT_2026.pdf` | 4,497,962 | `04d4405eac9a` | 142 pp, A4 (594.96 × 841.92 pt = 209.9 × 297.0 mm), PDF 1.4, tagged, Chrome + PyMuPDF, 157 bookmarks, page labels i–xiii + 1–129 | **Original manuscript, read-only** |
| `author-assets/divyanshu-portrait.jpg` | 974,925 | `62e67e8d0bfa` | 1220 × 1707 px, RGB container with greyscale content, 72 dpi tag | **Original portrait, read-only** |
| `author-assets/originals/DIVYANSHU_VERMA_SIGNATURE_ORIGINAL_UPLOAD.png` | 1,155,862 | `a0519ccbd66d` | 2172 × 724 px RGB, painted checkerboard (no real transparency), blue ballpoint | **Genuine signature as uploaded, read-only** |
| `author-assets/DIVYANSHU_VERMA_AUTHOR_SIGNATURE.png` | 103,917 | `b3834e4d777a` | 1796 × 668 px RGBA, 600 dpi, transparent, original blue ink | Genuine signature, cleaned (digital/colour) |
| `production/SOURCE_AND_BUILD/DIVYANSHU_VERMA_AUTHOR_SIGNATURE_BLACK.png` | 103,923 | `3f0a3c6be680` | 1796 × 668 RGBA, ink RGB(17,17,17) | Genuine signature, cleaned (B&W interior) |
| `production/SOURCE_AND_BUILD/DIVYANSHU_VERMA_AUTHOR_SIGNATURE_WHITE.png` | 103,884 | `805137717703` | 1796 × 668 RGBA, white | Genuine signature, cleaned (dark backgrounds) |
| `production/SOURCE_AND_BUILD/process_signature.py` | 3,004 | `e507b1188b52` | Pillow/numpy/scipy | Signature cleanup script (alpha from ink density; no redrawing) |
| `production/about-the-author/ASSETS.md` | 1,390 | `3e7186eb53b9` | | Asset spec for About page |
| `production/validation/validate.sh` + `originals.sha256` | | | | Original-asset integrity check |
| `production/validation/signature_light_dark_check.png` | 211,498 | `4a7d2dba4083` | 898 × 1002 | Earlier QA sheet |
| `README.md`, `.gitattributes`, `.gitignore` | | | | Repo docs/config |

**Integrity:** `validation/validate.sh` → PASS (manuscript, portrait and signature upload byte-identical to recorded hashes; signature PNG valid, transparent, 600 dpi; no generated author mark present).

---

## 2. Manuscript audit

**Every one of the 142 pages was rendered and inspected visually** (contact sheets at 60 dpi plus close-ups), and the full text layer was extracted.

### Format and production facts
- A4 portrait, single column with frequent two-column card grids; Chrome-rendered HTML; **all diagrams are vector** (the PDF contains no raster images at all).
- Fonts embedded: Manrope (ExtraBold/Bold/SemiBold), Inter (Regular/Medium/SemiBold), Noto Sans Devanagari (Regular/Medium/Bold).
- **Language: Hinglish.** Explanations in Hindi (Devanagari), business terms in English, prompts and message scripts in English / Roman Hinglish (stated in "How to use this book", item 3). Devanagari shaping is a first-class production requirement.
- Tagged PDF with a real structure tree (H1/H2/H3, P, L/LI, Table/TR/TH/TD, Figure/Caption, Link): **used to reconstruct the content faithfully** instead of re-typing or OCR.

### Text-layer defect found in the source (and fixed, documented)
The source PDF's ToUnicode map (Chrome/Skia) decodes some zero-width Devanagari mark glyphs as two characters, which **doubles a vowel sign or candrabindu in exactly 135 places** (e.g. `बड़ाा`, `पहुँँच`, `ज़ोोर`). The printed glyphs in the original are correct; only the text layer is wrong. An identical combining mark repeated back-to-back is never valid Hindi orthography, so the repeat is collapsed. All 135 fixes are logged with page and context in `audit/devanagari_textlayer_fixes.json`. This count equals the independent disagreement count between two decoders (PyMuPDF vs Poppler), and there were no other disagreements.

### Page map (PDF page → printed label → content)
| PDF pp. | Label | Content |
|---|---|---|
| 1–2 | i–ii | Cover, inner title (redesigned for paperback; not interior content) |
| 3 | iii | Copyright |
| 4 | iv | Disclaimer; About DEADCODE LABS |
| 5 | v | Welcome note; Who should read this book? |
| 6 | vi | What you will achieve |
| 7 | vii | How to use this book |
| 8 | viii | Learning roadmap (Figure 1) |
| 9–10 | ix–x | Table of Contents (A4 page numbers; to be rebuilt) |
| **11–12** | **xi–xii** | **Download Your Resources: REMOVE** |
| 13 | xiii | Stage 01 divider |
| 14–21 | 1–8 | Ch 01 Find Your First Business Idea |
| 22–33 | 9–20 | Ch 02 Build Your AI Toolkit (25 essential prompts) |
| 34–41 | 21–28 | Ch 03 Turn Your Skill Into a Service |
| 42 | 29 | Stage 02 divider |
| 43–50 | 30–37 | Ch 04 Market Research |
| 51–58 | 38–45 | Ch 05 Brand, Identity and Portfolio |
| 59–67 | 46–54 | Ch 06 Pricing, Proposals and Business Setup |
| 68 | 55 | Stage 03 divider |
| 69–75 | 56–62 | Ch 07 Marketing and Client Acquisition |
| 76–86 | 63–73 | Ch 08 How to Get Your First Paying Client |
| 87–94 | 74–81 | Ch 09 Client Delivery, Payment and Retention |
| 95 | 82 | Stage 04 divider |
| 96–102 | 83–89 | Ch 10 Your First 30 Days |
| 103–118 | 90–105 | Bonus A: 100+ AI Prompt Library (#001–#104) |
| 119–132 | 106–119 | Bonus B: 20 Ready-to-Use Templates |
| 133 | 120 | Bonus C: Business Calculators (index of an Excel workbook) |
| 134–138 | 121–125 | Bonus D: Business Resource Directory |
| 139–142 | 126–129 | Appendix: Sources and Further Reading; What could not be fully verified; Glossary |

### Component counts (from the structure, not from text search)
10 chapters · 4 stage dividers · **141 prompt cards** · 12 workflow cards · 40 callout boxes (8 warning, 2 tip, 1 note, 7 hypothetical, 3 India, 9 international, 10 next-step assignment) · 89 tables · **24 figures with captions** · 20 checklists · **20 templates** · **7 calculator sheets** · **30-day plan with all 30 days** · **17 glossary terms** · **91 numbered sources**.

### Reconstruction fidelity
`source/extracted.html` was rebuilt from the tag tree. **Fidelity check: PASS.** All 36,584 word tokens of the original are present with exact counts. The only differences are four documented allowances (`validation/fidelity_allow_extracted.json`): decorative stage-progress labels, letter-spaced "S TAG E", table header rows repeated on A4 continuation pages, and hidden diagram label data. Because the check tokenises Devanagari, it also proves no Hindi word was split or glued during reconstruction.

---

## 3. Content preservation checklist

| Item | Status | Evidence |
|---|---|---|
| 10 chapters, original order and titles | ✅ present | `audit/content_inventory.json` → chapters |
| Chapter sections (H2/H3), learning objectives, summaries, checklists, exercises, next-step assignments | ✅ present | 10 assignments, 20 checklists |
| Exactly 141 AI prompts (25 + 12 + 104) | ✅ 141 / 141 | `validation/prompts_*.json` |
| 20 templates | ✅ 20 / 20 | inventory |
| 7 calculator sheets / explanations | ✅ 7 / 7 (index + Ch 4/6/10 formulas) | inventory |
| 24 diagrams | ✅ 24 / 24 with captions; 1 rebuilt as vector (Fig. 2), 23 in Phase 6 | inventory |
| 30-day action plan | ✅ 30 / 30 days | Ch 10 tables |
| Bonus D resource directory | ✅ all tables | inventory |
| Appendix sources + "What could not be fully verified" | ✅ 91 sources | inventory |
| Glossary | ✅ 17 terms | inventory |
| Copyright, disclaimer, About DEADCODE LABS, welcome, who-should-read, achievements, how-to-use, roadmap | ✅ kept | front matter |
| Reference markers [n] → Appendix numbering | ✅ kept (set as superior refs in print) | |
| No new facts, statistics, testimonials or promises added | ✅ | edits limited to `source/print_edits.yaml` |

---

## 4. Resource-download removal checklist

All changes are exact-match, count-checked edits in `source/print_edits.yaml`, applied by `scripts/apply_edits.py`. After applying them, a residual scan finds **0** references in both editions (`validation/removed_content_{print,digital}.json`).

| Location (original) | What depended on the portal/files | Edit | Treatment |
|---|---|---|---|
| pp. xi–xii | Whole "Download Your Resources" section (3 tables, ZIP/XLSX/PDF/DOCX links) | FM-01 | **Removed** |
| pp. ix–x | Old TOC (lists the resource page, A4 numbers) | FM-02 | Removed; rebuilt from final pagination |
| p. vii item 5 | "PDF में इन पर click कर सकते हैं" | FM-03 | Print: points to Appendix. Digital: unchanged |
| p. vii item 6 | "Bonus files … download links Download Your Resources page पर" | FM-04 | Rewritten: says what is printed in Bonus A–D |
| Ch 3 workflow card (TOOL, TOOL USE) | BUSINESS_CALCULATORS.xlsx, "Workbook" | CH03-01/02 | → Bonus C Project Pricing sheet |
| Ch 3 tools | BUSINESS_CALCULATORS.xlsx | CH03-03 | → Bonus C calculators |
| Ch 4 Demand Scoring | "Workbook में भी…" | CH04-01 | → Bonus C Demand Score sheet |
| Ch 6 project example | "Workbook में यह अपने आप calculate होता है" | CH06-01 | → Bonus C step-by-step |
| Ch 6 prompt #C-G VERIFY note | "workbook" | CH06-02 | → Bonus C sheet (prompt text untouched) |
| Ch 6 assignment | BUSINESS_CALCULATORS.xlsx | CH06-03 | → Bonus C sheets |
| Ch 10 Day 8 / Day 30 tools | "Workbook" | CH10-01/02 | → Bonus C |
| Ch 10 lead tracking | "Workbook में Client Acquisition Tracker" | CH10-03 | → Bonus C Client Tracker |
| Ch 10 tools & links | XLSX + Download Your Resources page | CH10-04 | → Bonus B/C |
| Ch 10 exercise 2 | "Workbook के tracker" | CH10-05 | → Bonus C Client Tracker |
| Bonus A #080 VERIFY note | "Workbook से जाँचिए" | BA-01 | → Bonus C Profit sheet (prompt text untouched) |
| Bonus B intro | editable versions, download link, resource page | BB-01 | Rewritten for print |
| Templates 01–20 | 20 × "Download: NN_….docx/.xlsx" | BB-02 | Removed (count = 20 verified) |
| Template 07 | "Yellow cells… formula" | BB-03 | Paper instructions + Ch 6 formulas |
| Template 17 | "Status dropdown" | BB-04 | Allowed values listed (from Ch 10) |
| Templates 17/18/19 | "पूरी tracker table Excel file में है…" | BB-05 | → printed blank tracker sheet |
| Template 20 | "Spreadsheet में वही 30 rows…" | BB-06 | → printed planner sheet |
| Bonus C intro + end | XLSX download, yellow/purple cells, 07_pricing_calculator.xlsx | BC-01/02 | Printed calculator sheets; Template 07 |

Checked and **kept** on purpose: Vercel listed as a hosting tool (Ch 2 figure, Bonus D, Appendix source 58). It is a genuine tool listing, not the resource portal.

---

## 5. AI prompt inventory and count

**141 / 141 prompts verified** (`validation/prompts_print.json`, full list in `reports/PROMPT_INVENTORY.md`)
- Chapter 2 essential prompts #C01–#C25: **25 / 25**, in order, each with PURPOSE, prompt text, OUTPUT, EXAMPLE, VERIFY
- Chapter-specific #C-A–#C-L: **12 / 12**, each in its original chapter (A,B→Ch1; C,D→Ch3; E→Ch4; F→Ch5; G,H→Ch6; I→Ch7; J→Ch8; K→Ch9; L→Ch10)
- Bonus A #001–#104: **104 / 104**, in order, 18 categories
- No duplicate IDs, no duplicate prompt text, no unknown IDs. Every prompt title and body is identical to the original (hash-compared), and all [placeholders] are preserved.

## 6. Template inventory — 20 / 20
See `reports/TEMPLATE_CALCULATOR_FIGURE_INVENTORY.md`. Important production finding: in the original, the templates' **writing space consisted of empty table cells**, which carry no text, so a mechanical conversion would lose them. Each template therefore gets a deliberate print layout with real writing lines and cells (Template 10 shown in the proof).

## 7. Calculator inventory — 7 / 7
Hourly Rate · Project Pricing · Profit · Monthly Target · Lead Conversion · Client Tracker · Demand Score. The original Bonus C is only a one-page index of a removed Excel file, but **every formula needed already exists in the manuscript** (Ch 4 demand score; Ch 6 hourly rate, project floor price and profit margin; Ch 8 effective rate; Ch 10 conversion rates). Proposal: print seven fill-in calculator sheets built only from those formulas (needs your approval, see §9).

## 8. Asset verification report
| Asset | Check | Result |
|---|---|---|
| Portrait original | unchanged (hash) | ✅ |
| Portrait print derivative `about-the-author/portrait_print_gray.jpg` | single-channel grey, 4:5 framing crop (x 50–1170, y 210–1610), no retouching/resizing; 1120 × 1400 px → ~918 ppi at 31 mm | ✅ |
| Signature original upload | unchanged (hash) | ✅ |
| Cleaned signature (blue) | genuine strokes, transparent, 600 dpi | ✅ used in digital edition |
| Cleaned signature (black) | same strokes, ink RGB(17,17,17) | ✅ used in print interior |
| Generated / replacement signature | none in repo | ✅ |

## 9. Production risks and missing information

| # | Risk / gap | Impact | Proposed handling |
|---|---|---|---|
| R1 | **Author is not named anywhere in the original manuscript**; copyright is "© 2026 DEADCODE LABS" | The paperback adds "Divyanshu Verma" (cover, title page, About page), as the brief requires | Keep © holder unchanged; add "by Divyanshu Verma" only on title/cover/About. **Confirm** the copyright line wording |
| R2 | Repo README called the imprint "CRAFT & CODE / DEADCODE LABS"; the manuscript and brief say DEADCODE LABS | Inconsistent imprint | README corrected to DeadCode Labs; **confirm** |
| R3 | Printer not chosen: no paper caliper, binding gutter rule, colour-page policy or PDF standard | Spine width, final gutter, colour pages and PDF/X profile cannot be final | Provisional values below; printer questionnaire in `reports/PRODUCTION_PLAN.md` |
| R4 | Mixed colour/mono interior | For a 20-copy digital run, colour pages may be priced per page or force the whole book to colour | Interior designed fully readable in greyscale; colour only on selected diagrams after printer confirms |
| R5 | WeasyPrint SVG text does not shape Devanagari | Broken matras in diagrams | **Fixed by design**: diagram labels are HTML text over SVG shapes (verified in proof) |
| R6 | Source text-layer doubled marks (135) | Corrupted Hindi if copied | Fixed + logged; orthography lint in PDF QA |
| R7 | 10 rewritten Hinglish passages (print accuracy) | Voice and meaning | Marked `author_review: true` in `print_edits.yaml` for your approval |
| R8 | ISBN, MRP, printer, publication date, legal deposit | Must not be invented | Left as documented pending fields; barcode placeholder only |
| R9 | Research cutoff "5 November 2026" in copyright | Prices/rules may change before print | Kept as written; no new claims |
