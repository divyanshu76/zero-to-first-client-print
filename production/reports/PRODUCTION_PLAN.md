# Production Plan and Execution Status

## Phase status
| Phase | Status | Output |
|---|---|---|
| 1 Repository and manuscript audit | ✅ done | `audit/PHASE1_AUDIT_REPORT.md` |
| 2 Content cleanup, resource removal | ✅ done | `source/print_edits.yaml`, `reports/HINGLISH_EDITS_BEFORE_AFTER.md` |
| 3 Design system and typography | ✅ done | `design-system/` |
| 4 Five-page proof + cover concepts | ✅ done | `previews/` |
| 5 Approval gate | ✅ cover Concept A approved and locked; full production authorised | `cover/APPROVED_COVER_DIRECTION.md` |
| 6 Complete interior | ✅ done: 258-page paperback, 257-page digital | `final/` |
| 7 Cover production | ✅ front/back final; ⚠️ spine/wrap provisional pending printer caliper and template | `final/cover/` |
| 8 Automated + visual QA | ✅ all checks pass; every page rendered and inspected | `validation/`, `final/previews/` |
| 9 Final deliverables + report | ✅ | `reports/FINAL_PRODUCTION_REPORT.md` |

## Pipeline (reproducible, from the original PDF)
```
manuscript PDF ──extract_manuscript.py──▶ source/manuscript_tree.json  (tag tree, correct Unicode, 135 logged fixes)
              ──build_source.py────────▶ source/extracted.html          (faithful; fidelity-checked word by word)
              ──apply_edits.py + print_edits.yaml ─▶ source/book_print.html / book_digital.html
              ──typeset.py (design-system CSS, diagrams, About page) ─▶ WeasyPrint ─▶ PDF
checks: run_checks.sh → validate.sh · validate_fidelity.py · validate_prompts.py · content_inventory.py · validate_pdf.py
```
Run everything: `bash production/scripts/run_checks.sh` · Proof: `python3 production/scripts/build_proof.py print`
Requirements: Python 3.11+, `pymupdf`, `weasyprint` (v70), `beautifulsoup4`, `lxml`, `pyyaml`, `pypdf`, `pikepdf`, `Pillow`; Poppler and Ghostscript for previews and ink checks. Fonts are bundled in `design-system/fonts` (all SIL OFL).

## Phase 6 work list (after approval)
1. Front matter: half-title, title page (title, subtitle, 2026 Edition — First Edition, Divyanshu Verma, DeadCode Labs), copyright page (original wording, plus pending fields: ISBN / printer / printing date as clearly marked placeholders), then the existing front matter without the resource pages.
2. TOC rebuilt with `target-counter()` from final pagination; PDF bookmarks for chapters, stages, Bonus A–D, Appendix, Glossary, About the Author.
3. Rebuild the remaining 23 diagrams (SVG shapes + HTML labels, original wording) and add a diagram-label fidelity check.
4. Per-template layouts for all 20 (blank cells and rows, tick boxes, tracker sheets for 17–19, 30-day planner for 20).
5. Bonus C: 7 calculator worksheets from the manuscript's own formulas.
6. Narrow-table treatment for Bonus D and the Appendix (6-column tables at 102 mm).
7. Digital edition: resolve internal `#page=` links to real anchors, keep external links, bookmarks, ivory palette, blue signature.
8. Revalidate 141 prompts, 20 templates, 7 calculators, fidelity of the final PDF text against `book_print.html`, then render and inspect every page.

## Printer questionnaire (needed before Phase 7 can be final)
1. Exact trim 135 × 210 mm confirmed for perfect binding? Minimum and maximum page count, and page-count multiple?
2. Paper: 70 or 80 gsm natural shade? **Caliper per leaf** or spine-width calculator?
3. Minimum inner margin / gutter allowance for perfect binding at ~264 pp?
4. Interior: can selected colour pages be printed at per-page colour pricing on a 20-copy digital run, or is the book all-mono / all-colour?
5. Required PDF standard (PDF/X-1a, PDF/X-4, or plain PDF), colour profile (e.g. FOGRA39 / GRACoL), black-text handling, total ink limit.
6. Interior bleed required even if nothing prints to the edge?
7. Cover: board/card GSM, matte lamination, bleed (3 mm or 5 mm?), spine safe zone, their cover template for the final page count.
8. Barcode: will an ISBN be allocated (and by whom)? Until then the barcode box stays an empty placeholder.
9. Proof copy available before the 20-copy run?

## Not invented, still pending
ISBN · barcode · MRP · printer name/location · printing date · legal-deposit or registration details · final spine width · final PDF/X profile.
