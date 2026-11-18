# Final blank page and print pagination audit

**File audited:** `production/final/ZTFC_2026_paperback_interior_135x210_PRINT.pdf`
SHA-256 `df4626a279c7a72c5391aae05f83ef1b898d5095e2ea1034b5f14e1a8b5b536a` (identical to the file on `main`, commit `1dea4f9`) · 258 pages · 135 × 210 mm
**Type:** audit only. No file was modified, regenerated or deleted. This report is the only new file.

## Method
1. **Every page rendered** (72 dpi greyscale) and measured by ink coverage: whole page, text block, running-head band and folio band. Text, images and vector drawings were counted separately, and every flagged page was inspected visually next to its neighbours.
2. **Blank** = zero ink anywhere on the page. **Nearly blank** = some ink, but under 120 characters of body text or body content occupying under 25 % of the text-block height.
3. Opener positions were checked against the book's bookmarks/Contents page map. Folios were re-audited with `scripts/validate_folios.py` (report written to /tmp, not the repository). All 164 Contents references were re-checked against where each heading prints.
4. Causes were traced to `design-system/book.css` (break rules) and `scripts/build_book.py` (PDF assembly).

Recto = right-hand page = odd PDF page (PDF page 1 is a recto). Verso = even PDF page.

---

## 1. Completely blank pages: 14

All 14 are **versos** (even PDF pages). None carries a running head or folio (correct practice for a blank page). "Logical number" is the folio the page would carry if numbered.

| PDF p. | Logical no. | Previous page (content) | Next page (content) | Next opens on recto? | Cause | Class | Recommendation |
|---:|:--:|---|---|:--:|---|:--:|---|
| 2 | ii | 1 (r): Half-title "ZERO TO FIRST CLIENT" | 3 (r): Title page | ✅ | `section.title-page { break-before: right }` | **REQUIRED** | Keep. Back of the half-title; title page on recto is standard |
| 18 | xviii | 17 (r, xvii): last Contents page (ends "About the Author … 237") | 19 (r): Stage 01 divider | ✅ | `section.stage { break-before: right }` | **REQUIRED** | Keep. Contents ends on a recto, so a blank verso is needed before the divider |
| 20 | xx | 19 (r): Stage 01 divider "Find Your Business" | 21 (r, 1): Chapter 01 opener | ✅ | `section.stage { break-after: page }` + `header.chapter-open { break-before: right }` | **REQUIRED** | Keep. Blank back of a part/stage divider |
| 52 | 32 | 51 (r, 31): end of Chapter 02 (Next-step assignment) | 53 (r, 33): Chapter 03 opener | ✅ | `header.chapter-open { break-before: right }` | **REQUIRED** | Keep. Chapter 02 ends on a recto |
| 66 | 46 | 65 (r): Stage 02 divider "Build Your Business" | 67 (r, 47): Chapter 04 opener | ✅ | stage `break-after: page` + chapter `break-before: right` | **REQUIRED** | Keep. Back of stage divider |
| 80 | 60 | 79 (r, 59): end of Chapter 04 (Completion checklist, Next-step assignment) | 81 (r, 61): Chapter 05 opener | ✅ | chapter `break-before: right` | **REQUIRED** | Keep. Chapter 04 ends on a recto |
| 108 | 88 | 107 (r, 87): end of Chapter 06 (Next-step assignment) | 109 (r): Stage 03 divider | ✅ | stage `break-before: right` | **REQUIRED** | Keep. Chapter 06 ends on a recto |
| 110 | 90 | 109 (r): Stage 03 divider "Get Your First Client" | 111 (r, 91): Chapter 07 opener | ✅ | stage `break-after: page` + chapter `break-before: right` | **REQUIRED** | Keep. Back of stage divider |
| 122 | 102 | 121 (r, 101): end of Chapter 07 (Next-step assignment) | 123 (r, 103): Chapter 08 opener | ✅ | chapter `break-before: right` | **REQUIRED** | Keep. Chapter 07 ends on a recto |
| 150 | 130 | 149 (r, 129): end of Chapter 09 (Completion checklist, Next-step assignment) | 151 (r): Stage 04 divider | ✅ | stage `break-before: right` | **REQUIRED** | Keep. Chapter 09 ends on a recto |
| 152 | 132 | 151 (r): Stage 04 divider "Execute and Grow" | 153 (r, 133): Chapter 10 opener | ✅ | stage `break-after: page` + chapter `break-before: right` | **REQUIRED** | Keep. Back of stage divider |
| 198 | 178 | 197 (r, 177): end of Bonus A (prompts #102–#104) | 199 (r, 179): Bonus B opener | ✅ | `section.bonus { break-before: right }` | **OPTIONAL** | Keep for consistency (see §4). Only the house rule for back-matter sections requires it |
| 256 | 236 | 255 (r, 235): end of Glossary (Appendix) | 257 (r, 237): About the Author | ✅ | `.about { break-before: right }` | **OPTIONAL** | Keep, unless the printer needs a multiple of 4/8/16 pages (see §5, Option A) |
| 258 | 238 | 257 (r, 237): About the Author | (none: last page, inside back) | n/a | `build_book.py` adds one blank page when the count is odd (`if EDITION == "print" and len(w.pages) % 2`) | **REQUIRED** | Keep while the content ends on a recto. A bound book must have an even page count |

**Totals:** 14 blank pages · **12 REQUIRED** · **2 OPTIONAL** (PDF 198, 256) · **0 UNINTENTIONAL**

Classification rules used:
* **REQUIRED**: needed by standard book convention (title page, part/stage dividers and chapters open on a recto; dividers back onto a blank) or by physical parity (even page count).
* **OPTIONAL**: needed only because this book extends the recto-opening rule to back-matter sections (Bonus sections, About the Author). Removing it is possible without breaking convention, but changes the book's consistency and pagination.
* **UNINTENTIONAL**: a blank not explained by any rule (stray break, overflow, empty element, generation error). **None found.**

## 2. Nearly blank pages: 9 (content pages, none accidental blanks)

| PDF p. | Folio | Content | Cause | Assessment | Recommendation (optional, not applied) |
|---:|:--:|---|---|---|---|
| 1 | — | Half-title (title only) | design | Intentional | None |
| 11 | xi | Only item 7 ("Time…", 2 lines) of *How to use this book*, carried over from p. x | natural text overflow | Short run-over page; looks sparse | Optional: tighten pp. x–xi so item 7 fits on p. x. Front-matter page count and parity would change (blank p. 18 might no longer be needed), so it needs a rebuild and full re-validation |
| 17 | xvii | Last Contents page (7 lines) | natural end of Contents | Normal | None |
| 92 | 72 | End of Chapter 05: Next-step assignment box only | natural chapter end | Normal chapter ending | None |
| 212 | 192 | Template 11 run-over: "Next step", "Valid until" | template taller than one page | Usable (fields complete), but a 2-field page | Optional: tighten field spacing so Template 11 fits one page |
| 215 | 195 | Template 13 run-over: "Approval" only | template taller than one page | Usable, sparse | Optional: as above for Template 13 |
| 221 | 201 | Template 17 example record run-over (3 fields) | example record taller than page | Usable | Optional: as above |
| 224 | 204 | Template 18 example record run-over: "Notes" only | example record taller than page | Usable, sparse | Optional: as above |
| 228 | 208 | Template 20 heading + instructions only; planner sheet starts on p. 229 | CSS `.planner { break-before: page }` (forced break) | **Avoidable forced break**: about 80 % of the page is empty | Optional: remove the forced break before the planner sheet so it starts under the instructions |

Template pages each start a new page by design (`.template`, `.tracker-sheet`, `.calculator { break-before: page }`). The run-overs above are complete, usable worksheets, not lost content.

## 3. Numbering, Contents, folios, parity

| Check | Result |
|---|---|
| Front matter | 20 pages. Roman folios **v–xvii** on PDF 5–17. PDF 1–4 (half-title, blank, title, copyright) and 18–20 (blank, Stage 01 divider, blank) unnumbered. Odd roman numbers on rectos ✅ |
| Main text | Arabic **1–237** on PDF 21–257; page 1 = Chapter 01 on a recto; odd numbers on rectos throughout ✅ |
| Unnumbered pages | 21: half-title, title, copyright, 4 stage dividers, 14 blank pages ✅ |
| Folio audit (text + 200 dpi pixels) | 237 numbered pages, 0 problems, one folio per page at the outer corner ✅ |
| Contents | 164 entries; every page number matches where the heading prints; no entry points to a blank page ✅ |
| Running heads | none on blank pages, openers or dividers ✅ |
| Parity | 258 pages = 129 leaves (even) ✅. Not a multiple of 4, 8 or 16 (see §5) |

## 4. Recto-opening consistency

The rule is applied **consistently**. Every one of these opens on a recto:
title page (3), Contents (13), Stage 01–04 (19, 65, 109, 151), Chapters 01–10 (21, 33, 53, 67, 81, 93, 111, 123, 139, 153), Bonus A–D (163, 199, 231, 239), Appendix (247), About the Author (257).

A blank verso appears only where the previous section happened to end on a recto (or behind a divider). Where a section ended on a verso, no blank was added (e.g. Chapter 02 at 33, Stage 02 at 65, Chapter 06 at 93, Bonus A at 163, Bonus C at 231, Bonus D at 239, Appendix at 247). Front-matter sections use `break-before: page` (either side), which is normal for front matter.

**Sources of blank pages:** 13 come from CSS forced breaks (`break-before: right` on title page, Contents, stages, chapters, bonus/appendix sections and About; `break-after: page` on stage dividers). 1 (PDF 258) comes from PDF generation logic (even-count padding in `build_book.py`). None comes from an unintended break, an empty element or overflow.

## 5. Printer page-count requirements (separate check)

No printer has been chosen, so **no printer requirement can be verified yet**; 258 is not assumed invalid.
* **258 is valid for any process that needs an even page count** (each leaf has two sides). Many short-run digital perfect-binding services work this way.
* Some printers require a multiple of 4; offset printing normally uses 8-, 16- or 32-page signatures. If so: next multiple of 4 = **260**, of 8 = **264**, of 16 = **272**. Alternatively, the optional change below gives **256 = 16 × 16**, which satisfies 4, 8 and 16 at once.

## 6. Recommended changes

**Required changes: none.** There are no unintentional blank pages and no pagination errors; the current 258-page layout is correct and consistent.

**Conditional / optional (only after the printer's requirement is known; each needs a rebuild and the full validation suite):**
* **Option A, if the printer needs a multiple of 4, 8 or 16 pages:** remove the blank before About the Author (PDF 256) by letting About the Author open on either side (`.about { break-before: page }` instead of `right`). About moves to PDF 256 (a verso, facing the Glossary's last page). The parity blank 258 is then no longer needed, giving **256 pages** (2 fewer, 16 × 16). No other page moves. This is the smallest change with the largest benefit.
* **Option B, if the printer needs a multiple of 4 and you prefer to keep About on a recto:** keep everything and add 2 blank pages at the end (260 pages).
* **Option C, cosmetic, not page-count driven:** remove the forced break before the Template 20 planner sheet (PDF 228). Tighten field spacing so Templates 11, 13, 17 and 18 fit one page each (PDF 212, 215, 221, 224). Fit "How to use this book" item 7 on p. x (PDF 11). These shift later pages, so the recto rule may add or remove blanks elsewhere; re-audit afterwards.
* **Not recommended:** removing the blank before Bonus B (PDF 198) on its own. Bonus C, D and the Appendix also follow the recto rule, so the saving would be lost or moved elsewhere, and the back matter would become inconsistent.

## 7. Integrity statement
No repository file was modified, regenerated, overwritten or deleted during this audit. All renders and intermediate data were written to /tmp. Before/after SHA-256 comparison of every file in the working tree: identical, except this new report (`production/reports/FINAL_BLANK_PAGE_AUDIT.md`). Nothing was committed or pushed.
