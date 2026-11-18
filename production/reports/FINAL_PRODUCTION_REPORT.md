# ZERO TO FIRST CLIENT — Final Production Report

*The AI-Powered Business Starter Kit* · 2026 Edition, First Edition · Divyanshu Verma · DeadCode Labs

**Status: interior and digital edition complete and verified. Cover front and back artwork final. Spine and full wrap are PROVISIONAL, so the cover is not yet printer-ready** (needs the printer's paper caliper and wrap template).

Reproduce everything from the original PDF: `bash production/scripts/run_checks.sh` (about 2.5 minutes; rebuilds and validates every output).

---

## 1. Deliverables

| # | Deliverable | File | Status |
|---|---|---|---|
| 1 | Paperback interior (print) | `final/ZTFC_2026_paperback_interior_135x210_PRINT.pdf` | ✅ Final, verified |
| 2 | Digital edition | `final/ZTFC_2026_digital_edition.pdf` | ✅ Final, verified |
| 3 | Front cover artwork | `final/cover/ZTFC_cover_FRONT_artwork_141x216_incl_3mm_bleed.pdf` | ✅ Final artwork (Concept A) |
| 4 | Back cover artwork | `final/cover/ZTFC_cover_BACK_artwork_141x216_incl_3mm_bleed.pdf` | ✅ Final artwork (barcode area empty) |
| 5 | Spine artwork | `final/cover/ZTFC_cover_SPINE_artwork_PROVISIONAL_13.4mm.pdf` | ⚠️ Provisional width |
| 6 | Full cover wrap | `final/cover/ZTFC_cover_WRAP_PROVISIONAL_SPINE_13.4mm_NOT_PRINTER_READY.pdf` | ⚠️ **Not printer-ready**: awaiting printer caliper and template |
| 7 | About the Author page | `final/about-the-author/About_the_Author_{print,digital}.pdf` + `.png` | ✅ |
| 8 | Validation reports | `validation/*.json` | ✅ all PASS |
| 9 | Content inventory | `audit/content_inventory*.json`, `reports/PROMPT_INVENTORY.md`, `reports/TEMPLATE_CALCULATOR_FIGURE_INVENTORY.md` | ✅ |
| 10 | Production report | this file; `reports/HINGLISH_EDITS_BEFORE_AFTER.md` | ✅ |
| 11 | Source and build files | `production/scripts/`, `production/source/`, `production/design-system/`, `production/cover/`, `production/about-the-author/` | ✅ reproducible |
| | Previews | `final/previews/` (every interior page on contact sheets, plus sample pages), `final/cover/preview_*.png` | ✅ |

SHA-256 of final files: see `reports/FINAL_CHECKSUMS.sha256`.

## 2. Interior specification (paperback)

| Item | Value |
|---|---|
| Trim | **135.00 × 210.00 mm on all 258 pages** (verified page by page; not A4, not A5) |
| Extent | **258 pages** = 20 front-matter pages (i–xx) + 237 numbered pages (1–237) + 1 closing blank verso so the count is even |
| Numbering | Roman for front matter, arabic from Chapter 1 (as in the original); no folio on title pages, stage dividers or blank pages; every folio verified |
| Margins | Top 17 mm · bottom 19 mm · **inner (gutter) 19 mm** · outer 14 mm, mirrored recto/verso; text block 102 × 174 mm; every line of text verified inside it |
| Bleed | None needed (nothing prints to the edge); can be added if the printer requires it |
| Colour | **Black only (K)**: Ghostscript ink coverage shows 0 C/M/Y on all 258 pages. Text at 100 % K; tints K5–K90 |
| Fonts | 13 faces, all embedded and subset: Inter, Manrope, Noto Sans Devanagari (SIL OFL) |
| Devanagari | Shaped by HarfBuzz; no dotted circles or broken glyphs; the text layer carries `/ActualText` on all 5,726 Devanagari runs, so copy, search and accessibility return correct Hindi |
| Images | Portrait greyscale ≈ 790 ppi effective; signature 1-channel K + alpha (strokes byte-identical) |
| Links | 0 link annotations in the print file; 28 PDF bookmarks |
| Openers | Chapters, stages, Bonus sections and Appendix open on a recto; 14 intentional blank versos |
| PDF | PDF 1.7, single pages, trim = media box. Final PDF/X conversion (if required) waits on the printer's profile |

**Colour decision:** the brief allows selected colour only where it improves a diagram. All 24 diagrams were redesigned to read fully in greyscale (tints, dashed vs solid, reversed boxes), so the paperback interior is black-only. That avoids per-page colour pricing on a 20-copy run, and any RIP colour shift. The colour (navy/violet) versions of the diagrams are in the digital edition. If you want colour pages in print, that can be switched per diagram once the printer confirms colour-page pricing.

## 3. Content validation

| Check | Result |
|---|---|
| AI prompts | **141 / 141 verified**: Chapter 2 25/25 (#C01–#C25), chapter-specific 12/12 (#C-A–#C-L, each in its original chapter), Bonus A 104/104 (#001–#104); in sequence; no duplicates; every title and prompt body identical to the original; all [placeholders] preserved |
| Templates | **20 / 20 verified**, each with writing space (ruled fields, blank rows, tick boxes, record cards for 17–19, 30-day planner sheet for 20) |
| Calculators | **7 / 7 verified**: Hourly Rate, Project Pricing, Profit, Monthly Target, Lead Conversion, Client Tracker, Demand Score, each a worksheet built only from formulas already in the manuscript (sources named on each sheet) |
| Diagrams | **24 / 24 verified**: rebuilt as vector (SVG shapes + HTML labels); every word of each original diagram's labels present; no raster |
| Chapters / stages | 10 / 10 chapters, 4 / 4 stage dividers |
| 30-day action plan | 30 / 30 days (plus printable planner) |
| Glossary / sources | 17 terms; 91 numbered sources and "What could not be fully verified" |
| Every word | All 33,883 words of the edited manuscript are present in the print PDF, so nothing was dropped, clipped or truncated |
| Language | **Hinglish preserved**: all 10,706 Devanagari words of the source are present; nothing translated |
| Fidelity to the original | The source reconstruction matches all 36,584 words of the original PDF (4 documented layout allowances) |
| Removed content | "Download Your Resources" (pp. xi–xii) removed; 0 remaining references to the portal, DOCX/XLSX, workbook, yellow/purple cells, dropdowns or Excel |
| Contents | 164 entries; every page number verified against where the heading actually prints |
| Original assets | Manuscript, portrait and signature upload byte-identical to recorded hashes |
| Approved cover | Concept A source files byte-identical to the approved version |

## 4. Editorial changes

* 25 documented, count-checked edits in `source/print_edits.yaml` (24 in the digital edition). They cover resource removal, print accuracy and Contents rebuild.
* The 10 Hinglish passages marked for author review were re-checked against the original. Each changes only what paper cannot do (click, download, spreadsheet cells, dropdown), keeps the author's register and meaning, and leaves every prompt untouched. Before and after text: `reports/HINGLISH_EDITS_BEFORE_AFTER.md`.
* Source text-layer repair: 135 doubled Devanagari marks in the original PDF's text layer (not in its printed glyphs), each logged in `audit/devanagari_textlayer_fixes.json`.
* Copyright page unchanged in wording: **© 2026 DEADCODE LABS.** No ISBN, printer, legal-deposit or registration details invented. The author is credited on the title page, cover and About page.
* No new facts, statistics, testimonials or promises added. Calculator example values are the manuscript's own numbers.

## 5. Approved proof corrections (applied)

| Correction | Applied |
|---|---|
| Blank writing rows in the Skill Assessment table | ✅ 5 blank rows (Ch 1 and Template 02); blank rows also in the Competitor and Daily-tracker tables; 278 empty write-in cells restored where the original's blank cells were lost |
| "Level (1 से 5)" kept together | ✅ all short parenthetical header ranges are non-breaking |
| "#C02 continued" label | ✅ every prompt card that crosses a page carries "#Cnn continued" in the header corner |
| Larger About-the-Author portrait | ✅ 31 → 36 mm wide, balanced with the name block |
| Templates usable as worksheets | ✅ see §3 |
| Calculators as printable worksheets | ✅ see §3 |

## 6. Digital edition

257 pages (same text and pagination as print, without the closing blank); ivory paper colour, navy/violet diagrams, original blue signature; 28 bookmarks; **140 / 140 internal cross-references resolved** (chapters, templates, prompts, sources); 1,055 working internal links in total (Contents and references); 108 external URLs, none obsolete; Devanagari `/ActualText` on every run.

## 7. Cover

Approved **Concept A "Editorial Ripple"**, locked; no design change. Technical refinements applied by `cover/build_cover_final.py` (approved source files untouched):

| Refinement | Result |
|---|---|
| Bleed | 3 mm on all outside edges; growth rings extend into the bleed |
| Trim | each panel 135 × 210 mm; Trim/Bleed boxes set |
| Spine | **13.4 mm PROVISIONAL** = 258 pages ÷ 2 × 0.10 mm/leaf (assumed 70–80 gsm natural) + 0.5 mm cover allowance |
| Wrap | 289.4 × 216 mm incl. bleed (3 + 135 + 13.4 + 135 + 3 by 3 + 210 + 3) |
| Colour | DeviceCMYK only (0 RGB operators); rings converted from transparency to solid tints (0 transparency). Builds: ivory 0/1/5/3, navy 100/82/30/42, violet 68/82/0/0 (to be confirmed on a matte-laminated proof) |
| Fonts | all embedded |
| Review furniture | trim/spine guides, "PROVISIONAL" flag and review slug removed from the artwork |
| Barcode | empty white area (38 × 23 mm) at the approved position; no ISBN or barcode invented |

## 8. Remaining printer and ISBN requirements

1. **Printer selection** and confirmation that 135 × 210 mm perfect binding is supported; page-count multiple (258 is even; some printers need a multiple of 4, which means 260 with 2 more blank pages).
2. **Paper**: 70 or 80 gsm natural shade, and the printer's **caliper** or spine calculator. The final spine replaces 13.4 mm.
3. **Printer's cover template** (wrap size, hinge/score, safe zones, bleed 3 or 5 mm), cover board gsm, matte lamination.
4. **PDF standard and colour profile** (PDF/X-1a or X-4; FOGRA39/GRACoL); then a final conversion pass and a hard-copy proof.
5. **ISBN and barcode** (optional for a 20-copy private run): if allocated, the EAN-13 barcode goes in the reserved white area and the ISBN on the copyright page.
6. **MRP** (₹299–₹399 range under consideration): not printed until you decide.
7. Printing date / printer imprint line for the copyright page, if you want one.

A full wrap must not be sent to print until items 2 and 3 are confirmed.
