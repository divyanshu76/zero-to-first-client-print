# Folio (page-number) correction report

**Reported:** some pages showed two overlapping page numbers at the bottom corner (Calculator 2, Bonus D Resource Directory, About the Author).

## Investigation

| Step | Finding |
|---|---|
| Text audit of the files merged in PR #1 | Every page of the print (258) and digital (257) PDF had exactly one folio text object in the folio band |
| Pixel audit (new `scripts/validate_folios.py`): render the 16 mm folio band at 200 dpi, mask the single expected number, look for any remaining ink | PR #1 files: **0 extra marks** on all 515 pages |
| Build history | The symptom was real in an intermediate build made during production, on exactly the reported pages: "233" over "213" (Calculator 2), "241/221" (Bonus D, Website builders), "257/237" (About the Author) |

## Root cause

**Two independent page-numbering systems:**
1. `design-system/book.css` set folios with CSS margin boxes (`@bottom-right` / `@bottom-left: counter(page)`), numbering pages physically (1, 2, 3 …).
2. `scripts/build_book.py` stamps the book's real folios (roman front matter, arabic from Chapter 1) as an overlay.

Where both printed, the physical page number (e.g. 233) overlapped the book folio (213). PR #1 hid the CSS folios with an override in the build. That made the merged files correct, but the override was fragile: any stylesheet change could bring the duplicates back.

A second, smaller defect turned up in the audit: the **digital edition stamped folios on 13 intentionally blank pages** (including "ii" on the blank verso behind the half-title). Its full-page ivory background was treated as content, so blank pages were not recognised as blank.

## Corrections

| File | Change |
|---|---|
| `design-system/book.css` | **Removed** both `counter(page)` folio rules. The stylesheet defines no page numbers at all |
| `design-system/proof-folios.css` (new) | The CSS folios, used **only** by the 5-page proof builder so the historical proof stays reproducible; the complete book never loads it |
| `scripts/build_proof.py` | Loads `proof-folios.css` |
| `scripts/build_book.py` | Override removed. **Guard added:** the build stops if the typeset pages contain any text in the folio band before stamping (single source of numbering). Blank-page detection now ignores a full-page background fill |
| `scripts/validate_folios.py` (new) + `run_checks.sh` step 10b | Per page: text equals the expected label as one object; pixel check finds no other ink; outer-corner position; roman/arabic sequence; raw build has no folio text |

No manuscript wording, edits, biography, signature, portrait or cover file changed (verified: `production/source`, `production/about-the-author`, `author-assets`, `manuscript`, `production/cover` have no diff).

## Result

| | Print | Digital |
|---|---|---|
| Pages | 258 | 257 |
| Pages with a folio | 237 | 237 (was 250) |
| Front matter | roman **v–xvii** (pages i–iv: half-title, blank, title, copyright; xviii–xx: blank / Stage 01 / blank, unnumbered) | identical |
| Main text | arabic **1–237** from Chapter 1 | identical |
| Unnumbered pages | half-title, title, copyright, 4 stage dividers, 14 blank versos (incl. the closing blank) | half-title, title, copyright, 4 stage dividers, 13 blank versos |
| Duplicate / extra marks in folio band (pixel audit) | **0** | **0** |
| Body text vs PR #1 | identical on all pages | identical on all pages |
| Folio text vs PR #1 | identical on all pages | 13 blank pages: folio removed |

Full suite (`run_checks.sh`, rebuild from the original PDF): **ALL CHECKS PASSED**. That covers 141/141 prompts, 20/20 templates, 7/7 calculators, 24/24 diagrams, every word present, Hinglish preserved, Devanagari glyphs and text layer, fonts embedded, trim 135 × 210 mm on every page, margins, Contents page numbers, 1,055 internal links resolved, K-only print ink, approved cover unchanged.

Cover: rebuilt by the suite and compared with the delivered artwork at **0 differing pixels**; the delivered cover files are kept byte-for-byte. Status unchanged: front and back final; **spine (13.4 mm) and full wrap provisional, not printer-ready**, pending the printer's paper caliper and wrap template.
