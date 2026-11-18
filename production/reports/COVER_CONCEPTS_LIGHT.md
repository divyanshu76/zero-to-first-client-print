# Cover — revised LIGHT editorial concepts A and B

**Status: Concept A "Editorial Ripple" APPROVED by the author and LOCKED** (see `cover/APPROVED_COVER_DIRECTION.md`). Concept B was not selected. The cover is still not print-ready: the spine stays provisional until the final page count and printer specs are confirmed. Phase 6 (full book) waits for separate approval of the five-page interior proof.

The first concept (dark navy) is **superseded but preserved**: `cover/cover_concept.html` and `cover/ZTFC_cover_CONCEPT_not_for_print.pdf` are unchanged in the working tree and in Git history (commit `91fd426`).

## Files
| | Concept A · "Editorial Ripple" | Concept B · "Thirty-Day Dial" |
|---|---|---|
| Source | `cover/cover_concept_light_A.html` | `cover/cover_concept_light_B.html` |
| PDF (full wrap, 289 × 232 mm incl. 16 mm review slug) | `cover/ZTFC_cover_CONCEPT_light_A_not_for_print.pdf` | `cover/ZTFC_cover_CONCEPT_light_B_not_for_print.pdf` |
| Full wrap preview | `previews/cover/cover_A_full.png` | `previews/cover/cover_B_full.png` |
| Front / spine / back (at trim) | `cover_A_front.png`, `cover_A_spine.png`, `cover_A_back.png` | `cover_B_front.png`, `cover_B_spine.png`, `cover_B_back.png` |
| Side-by-side | `previews/cover/cover_light_A_vs_B_fronts.png`, `…_backs.png` | |

Rebuild: `python3 production/cover/build_cover_concepts.py` (shared styles in `cover/cover_light_base.css`).

## Shared foundation (both concepts)
- Warm ivory ground `#F7F4EE`; deep navy type `#14213D`; electric violet `#6D28D9` used only as accents (one rule, one point, one statistic).
- Manrope ExtraBold for the title; Inter for everything else. All fonts embedded.
- The title **ZERO TO FIRST CLIENT** is the largest, heaviest element on the front.
- Front: title, subtitle, 2026 Edition, Divyanshu Verma, DeadCode Labs. No price, no ISBN.
- Back: statistics exactly as specified (**10 Chapters · 141 AI Prompts · 20 Practical Templates · 7 Practical Calculators · 30-Day Action Plan**); "Written in **Hinglish**"; short author line; DEADCODE LABS + https://deadcode.space/; **empty barcode placeholder** (no ISBN allocated, no barcode invented).
- Spine: **13 mm provisional, NOT FINAL.** Marked on the artwork guides and in the slug; to be recalculated from the final page count and the printer's caliper.
- Back-cover copy only restates what the manuscript contains: no testimonials, no claims of results.

## How they differ

| | A · Editorial Ripple | B · Thirty-Day Dial |
|---|---|---|
| Front layout | Left-aligned, asymmetric; title stacked in 3 lines at 60 pt across the upper half; imprint and edition on a ruled top line | Centred, symmetrical; motif in the upper third, title in 2 lines at 36 pt below, author and edition centred at the foot |
| Growth motif | Concentric **growth rings** widening from one point (zero), bleeding off the right and bottom edges; the outermost ring is violet and carries a violet point (the first client). Reads as reach that widens step by step | **30 radial marks** (the book's 30 days) that lengthen and darken clockwise from a centre point; the 30th mark and its point are violet. Ties directly to the 30-Day Action Plan |
| Character | Bold, confident, modern business-book | Calm, precise, more literary and minimal |
| Back layout | One editorial column: eyebrow, headline, copy, statistics as a **ruled vertical list**, closing line, author line, publisher and barcode | Centred headline with violet rule, copy in a narrower measure, statistics in a **tonal band** across the page, centred closing line, author block, publisher and barcode |
| Spine | Title, violet point, author, imprint in one reading line | Stacked: year at head, title with violet "FIRST CLIENT", author, stacked imprint at foot |
| Bookstore read at distance | Strongest: the title is very large | Elegant; the title is still dominant, but the dial draws the eye first |

## Checks (`validation/cover_concept_light_{A,B}_pdf_check.json`)
Size 289 × 232 mm (3 + 135 + 13 + 135 + 3 by 3 + 210 + 3, plus 16 mm slug) ✅ · all fonts embedded ✅ · no broken glyphs ✅ · every required wording element present; no "Hindi and English", no ISBN number, no price ✅.

## Prepress notes for the final wrap (after approval)
- Build in CMYK to the printer's template. Navy and violet will be specified as CMYK builds and proofed for matte lamination, which darkens and slightly flattens colour.
- Ivory ground: printed as a light CMYK tint (or left as paper if a cream board is used). Confirm with the printer's stock.
- Concept B's statistics band stops 5 mm before the spine fold, so spine-width variation cannot misregister a tone across the fold. Both spines are ivory for the same reason.
- Barcode box stays white and empty until a legitimate ISBN and barcode are supplied.

## Your decision
1. Choose **A** or **B**, or ask for a combination (e.g. A's layout with B's dial).
2. Comments on the motif, title size, back copy or spine.
3. Approve, or send revisions for, the five-page interior proof (`reports/PROOF_AND_DESIGN_REPORT.md`, D1–D11).
