# PHASES 3–4 — Design System and Five-Page Interior Proof

**Status: STOPPED AT THE APPROVAL GATE (Phase 5).** The complete book has **not** been produced as a deliverable. A provisional full-length typeset was run only to estimate page count and spine.

## Deliverables in this phase

| File | What it is |
|---|---|
| `previews/proof/ZTFC_interior_proof_5pp_print.pdf` | **5-page paperback interior proof** (135 × 210 mm, B&W, K-only text) |
| `previews/proof/proof_print_p-1…5.png` | 200 dpi previews of each proof page |
| `previews/proof/ZTFC_interior_proof_5pp_digital.pdf` + `proof_digital_p-*.png` | Same pages in the digital-edition palette (for comparison only) |
| `cover/ZTFC_cover_CONCEPT_not_for_print.pdf`, `previews/cover_concept-1.png` | First (dark) cover concept: **superseded**, kept for reference |
| `cover/ZTFC_cover_CONCEPT_light_{A,B}_not_for_print.pdf`, `previews/cover/` | **Revised LIGHT cover concepts A and B** (see `reports/COVER_CONCEPTS_LIGHT.md`) |
| `validation/proof_print_pdf_check.json` | Font, trim, glyph, link and image verification |

### The five proof pages (all actual manuscript content, all actual author assets)
| # | Role | Content | Provisional folio |
|---|---|---|---|
| 1 | Chapter opening | Chapter 01: number, title, subtitle, Chapter introduction, Learning objectives (checklist) | 1 |
| 2 | Body text | Ch 01 continued: services table (repeated header), **Figure 2 rebuilt as vector**, caption, H2, table | 4 |
| 3 | AI prompts | Ch 02: end of #C02, then #C03, #C04, #C05 complete | 20 |
| 4 | Printable template | Bonus B **Template 10: Case Study**: all 9 fields on one page with writing lines | 195 |
| 5 | About the Author | Original portrait (B&W derivative), approved bio verbatim, genuine signature (black), Founder — DeadCode Labs, URL | 243 |

Each page was cut from a **real typeset flow** made by the production pipeline (`scripts/build_proof.py`), not composed as a one-off mock-up. Folios are provisional until Phase 6. They follow the original's convention (front matter in roman numerals, Chapter 1 = page 1) and positions measured in a full trial typeset.

---

## Design system (`design-system/`)

**Direction:** premium contemporary business paperback. Quiet, typographic, generous; no gradients, stock imagery or decorative icon sets.

### Page geometry (exact trim 135 × 210 mm; standard A5 not used)
| | Recto | Verso |
|---|---|---|
| Top | 17 mm | 17 mm |
| Bottom | 19 mm | 19 mm |
| Inner (gutter) | **19 mm** | **19 mm** |
| Outer | 14 mm | 14 mm |
| Text block | 102 × 174 mm | |

- Interior bleed: **none needed.** Nothing prints to the edge (cleaner for digital printing). Can be added if the printer requires it.
- Gutter 19 mm suits a ~260 pp perfect-bound book. **Printer to confirm** the binding allowance.
- Running heads: verso "ZERO TO FIRST CLIENT"; recto = current chapter/section title. Suppressed on chapter openers, section openers and forced blank pages. Folios at the outer bottom corner.
- Chapters, stage dividers and Bonus sections open on a **recto**.

### Typography
| Role | Face | Size / leading |
|---|---|---|
| Body | Inter Regular + Noto Sans Devanagari (per-script fallback, HarfBuzz shaping) | 9.2 / 14.4 pt, ragged right, no automatic hyphenation (Hinglish) |
| Chapter number / title | Manrope ExtraBold | 46 pt / 19 on 22 pt |
| H2 (with short rule above) | Manrope ExtraBold | 12.4 / 15.5 pt |
| H3 | Manrope Bold | 9.8 / 13 pt |
| Tables | Inter | 7.8 / 10.6 pt; headers 6.7 pt bold; hairline rules only |
| Prompt cards | Inter | 8.3–8.5 / 12–12.6 pt; [placeholders] in semibold |
| Labels / running heads | Inter SemiBold caps, letter-spaced | 6.1–6.8 pt |
| Captions | Inter | 7.8 / 11 pt |

Widows/orphans 2; headings kept with following text; table rows never split; prompt text never split across pages; template fields never split.

### Colour (print interior)
All interior colour is **DeviceCMYK on the K channel only** (verified in the PDF content streams: 170 `/DeviceCMYK` selections, text at `0 0 0 1`). Body text prints as solid 100% K, not as a screened RGB grey. Tints are K5–K18. Ghostscript ink coverage on the proof shows pages 1–4 as K-only. The remaining 0.3% CMY on page 5 comes from the supplied black signature PNG, which is stored as RGB(17,17,17); see decision D7.
Colour (violet/navy) is reserved for **selected diagrams only**, and only if the printer confirms an economical colour-page workflow. Every diagram must read correctly in greyscale.
The digital edition swaps in the palette tokens: ivory #F7F4EE, near-black #171717, navy #14213D, violet #6D28D9, grey #777777.

### Components (all from the original "Boxes" legend, kept distinct in greyscale)
Prompt card (K5 card, black top rule, white prompt-text inset with black left bar) · Workflow card (black frame, reversed WORKFLOW tab, label column) · Warning (K10 fill, heavy left bar) · Hypothetical (dashed frame) · India / International (left rule + K5; international uses a double rule) · Tip / Note (top and bottom rules) · Next-step assignment (black frame, reversed label) · Checklists (drawn boxes) · Tables (booktabs hairlines, header repeats on continuation pages) · Template forms (label and example left, ruled writing lines right).

### Diagrams
Rebuilt as **vector**: SVG for shapes and **HTML text for all labels**. WeasyPrint's SVG text engine does not shape Devanagari, as the proof run showed (broken `क्या`). Labels set as HTML text are shaped by HarfBuzz and print correctly. Figure 2 was rebuilt this way, with original label wording unchanged. The other 23 follow in Phase 6.

---

## Font and trim verification (`validation/proof_print_pdf_check.json`)
- Page size: **382.677 × 595.276 pt = 135.00 × 210.00 mm on all 5 pages** ✅
- Fonts: 10 faces, **all embedded and subset** (Inter ×4, Manrope ×2, Noto Sans Devanagari ×4); no Type3 ✅
- No dotted-circle (U+25CC) or replacement glyphs, so no broken Devanagari shaping ✅
- Devanagari orthography lint: no doubled marks ✅
- Link annotations in the print proof: **0** ✅
- Portrait effective resolution ≥ 300 ppi (≈ 918 ppi) ✅; no blank pages ✅
- Cover concept: 289 × 230 mm (3 + 135 + 13 + 135 + 3 by 3 + 210 + 3, plus a 14 mm label slug), all fonts embedded ✅

## Provisional extent and spine
A full typeset of the edited manuscript through this design came to **233 pages**. That excludes the rebuilt TOC, title pages, 7 calculator sheets, blank tracker grids and full-size diagrams. **Estimated final extent: 256–272 pages.**
Provisional spine ≈ pages ÷ 2 × paper caliper: at 70 gsm natural (~0.09–0.10 mm/leaf) ≈ **12–13.5 mm**; at 80 gsm (~0.10–0.11 mm/leaf) ≈ **13–15 mm**. The concept uses a 13 mm placeholder. **The final spine must come from the printer's calculator for the chosen stock.**

---

## Decisions requiring your approval

| # | Decision | Recommendation |
|---|---|---|
| D1 | Overall interior design (5 proof pages) | Approve, or send revisions |
| D2 | Ragged-right, no automatic hyphenation (Hinglish) | Keep |
| D3 | Chapters and Bonus sections open on recto (≈ 8–12 blank versos) | Keep (premium); the alternative saves ~8 pages |
| D4 | Templates as label-left / writing-lines-right forms; 2-page templates open as a spread | Approve |
| D5 | Bonus C printed as 7 calculator worksheets using only formulas already in the book | Approve |
| D6 | 10 rewritten Hinglish passages flagged `author_review: true` in `source/print_edits.yaml` | Read and approve or reword |
| D7 | For print, convert the black signature PNG from RGB(17,17,17) to a greyscale+alpha file with identical strokes, so it prints as pure K | Approve (pure prepress conversion; the supplied file stays unchanged) |
| D8 | About the Author placed at the **end** of the book (after Glossary) | Approve, or move to front matter |
| D9 | Cover direction | ✅ **APPROVED: Concept A "Editorial Ripple"**, locked (`cover/APPROVED_COVER_DIRECTION.md`) |
| D10 | Copyright line stays "© 2026 DEADCODE LABS"; author credited on cover, title page and About page | Confirm |
| D11 | Back-cover copy (in concepts A/B): "Written in Hinglish", statistics as specified | Approve or edit; it only states verified features |
