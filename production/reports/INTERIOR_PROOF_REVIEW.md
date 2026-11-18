# Interior proof — review stage

**Cover:** ✅ approved: Concept A "Editorial Ripple", locked (`cover/APPROVED_COVER_DIRECTION.md`).
**Interior:** ⏸ **five-page proof awaiting your separate approval.** Phase 6 does not start until then.

Proof file: `previews/proof/ZTFC_interior_proof_5pp_print.pdf` (paperback interior, 135 × 210 mm, black-and-white).
Page images (200 dpi): `previews/proof/proof_print_p-1.png` … `proof_print_p-5.png`.
Review sheet (all five side by side): `previews/proof/proof_review_sheet.png`.
For comparison only: the digital-edition rendering of the same pages, `proof_digital_p-*.png`.

All text is the actual manuscript content and all images are the actual author assets. **Folios are provisional.** They follow the original's convention (front matter in roman numerals, Chapter 1 = page 1) and the positions measured in a full trial typeset of the book.

## Verified on this proof (`validation/proof_print_pdf_check.json`)
Every page exactly 135.00 × 210.00 mm · all 10 font faces embedded and subset (Inter, Manrope, Noto Sans Devanagari) · no broken Devanagari glyphs · no doubled marks · 0 link annotations · portrait ≈ 918 ppi effective · no blank pages · body text and rules in DeviceCMYK K only (100% K text).

---

## Page 1 — Chapter opening (folio 1, recto)
**Shows:** chapter eyebrow, large numeral, title, Hindi subtitle with closing rule; Chapter introduction; start of Learning objectives as a printable checklist.
**Check:** generosity of the top white space (about 30 mm before the eyebrow); size of the numeral vs the title; the short rule above each section heading (the H2 motif used throughout).
**Notes:** no running head on chapter openers (by design); the folio stays.

## Page 2 — Body text (folio 4, verso)
**Shows:** the "दस realistic services" table continuing from the previous page (header row repeated automatically), **Figure 2 rebuilt as vector** (original label wording; Hindi labels correctly shaped), caption, section heading, intro line, start of the Skill assessment worksheet table.
**Check:** table readability at 7.8 pt; diagram clarity in greyscale; caption style.
**My observations (to fix in Phase 6 unless you prefer otherwise):**
- The Skill assessment worksheet shows only its example row. The original's blank writing rows were empty table cells, which carry no text, so they don't survive extraction. In-chapter worksheet tables will get blank write-in rows, like the templates.
- The header "Level (1 से 5)" wraps after "से"; Phase 6 will keep short parenthetical header ranges unbroken.
- About 20 mm stays empty at the foot because the next box (a TIP) is kept whole on the following page. This is intentional: boxes are not split.

## Page 3 — AI prompts (folio 20, verso)
**Shows:** the end of #C02 (EXAMPLE, VERIFY) carried over from the previous page, then complete #C03, #C04, #C05: ID, title, category, PURPOSE, the prompt in a framed white box with **[placeholders] in semibold**, OUTPUT, EXAMPLE, VERIFY.
**Check:** ease of copying the prompt text; label column; the card tint (K5) against natural-shade paper.
**Rule used:** a card may break between its fields, but the **prompt text itself is never split** and the title always stays with PURPOSE. This cut Chapter 2 from 22 to 19 pages without splitting any prompt.
**Option for you:** add a small "#C02 continued" tag at the top when a card continues from the previous page (recommended; costs no space).

## Page 4 — Printable template (folio 195, recto)
**Shows:** Template 10: Case Study, all 9 fields on one page. Field name and fictional example on the left; two ruled writing lines (6.6 mm spacing) on the right; instructions without the removed download link; Bonus B running head.
**Check:** writing space (practical handwriting size?); legibility of the grey "e.g." examples; whether any field needs 3 lines.

## Page 5 — About the Author (folio 243, recto; placed at the end of the book)
**Shows:** original portrait (greyscale, framing crop only, no retouching); name, Technology Entrepreneur, Founder of DeadCode Labs; **approved biography verbatim**; philosophy quote; **genuine handwritten signature** (cleaned black version, strokes unchanged); printed name, "Founder — DeadCode Labs", https://deadcode.space/.
**Check:** portrait size and crop; name breaking onto two lines; position of the signature.
**Option for you:** about 25 mm is free at the foot, so the portrait could be enlarged (31 → ~36 mm wide) if you want more presence.

---

## Interior decisions for your approval
(From `reports/PROOF_AND_DESIGN_REPORT.md`; D9 cover is approved.)

| # | Decision | Recommendation |
|---|---|---|
| D1 | Overall interior design of these five pages | Approve, or send revisions |
| D2 | Ragged-right text, no automatic hyphenation (Hinglish) | Keep |
| D3 | Chapters and Bonus sections open on a right-hand page | Keep |
| D4 | Template form style (label left, writing lines right) | Approve |
| D5 | Bonus C printed as 7 calculator worksheets using only formulas already in the book | Approve |
| D6 | 10 rewritten Hinglish passages marked `author_review: true` in `source/print_edits.yaml` | Read and approve or reword |
| D7 | Print-only greyscale conversion of the black signature file (strokes identical; supplied file unchanged) | Approve |
| D8 | About the Author at the end of the book | Approve, or move to front matter |
| D10 | Copyright line stays "© 2026 DEADCODE LABS"; author credited on cover, title page and About page | Confirm |
| D12 | "#C02 continued" tag on prompt cards that cross a page | Approve / decline |
| D13 | Larger portrait on the About page (31 → ~36 mm) | Approve / decline |
| D14 | Blank write-in rows for in-chapter worksheet tables (e.g. Skill assessment) | Approve |
