#!/usr/bin/env bash
# Rebuild the complete book from the original manuscript PDF and run every validation.
# Usage (from anywhere): bash production/scripts/run_checks.sh
set -u
cd "$(dirname "$0")/.."            # production/
fail=0
step(){ echo; echo "== $1"; }
run(){ "$@" || fail=1; }
P=final/ZTFC_2026_paperback_interior_135x210_PRINT.pdf
D=final/ZTFC_2026_digital_edition.pdf

step "Original assets unchanged (manuscript, portrait, signature upload)"
run bash validation/validate.sh

step "Approved cover direction (Concept A) unchanged since approval"
if sha256sum -c --quiet cover/approved_cover_A.sha256; then echo "PASS  approved cover source unchanged (cover_concept_light_A.html, cover_light_base.css)"
else echo "FAIL  approved cover source changed: any change must be a documented technical refinement (see cover/APPROVED_COVER_DIRECTION.md), then re-record the hash"; fail=1; fi

step "1. Extract tagged structure from the original manuscript"
run python3 scripts/extract_manuscript.py
step "2. Rebuild semantic source"
run python3 scripts/build_source.py
step "3. Content fidelity: extracted source vs original PDF (every word)"
run python3 scripts/validate_fidelity.py source/extracted.html validation/fidelity_extracted.json --allow validation/fidelity_allow_extracted.json
step "4. Apply documented print/digital edits + resource-removal scan"
run python3 scripts/apply_edits.py
step "5. Content inventory"
run python3 scripts/content_inventory.py source/extracted.html audit/content_inventory.json
run python3 scripts/content_inventory.py source/book_print.html audit/content_inventory_print.json
step "6. Diagrams (24 vector rebuilds, original wording)"
run python3 scripts/build_diagrams.py
run python3 scripts/validate_diagrams.py source/book_print.html validation/diagrams_print.json
step "7. Typeset complete book (paperback + digital)"
run python3 about-the-author/build_portrait.py
run python3 about-the-author/build_signature_print.py
run python3 scripts/build_book.py print
run python3 scripts/build_book.py digital
step "8. Prompt validation on the typeset books (141 expected)"
for ed in print digital; do run python3 scripts/validate_prompts.py interior/build/book_$ed.html validation/prompts_final_$ed.json --baseline source/extracted.html | tail -1; done
run python3 scripts/write_inventory_reports.py
step "9. PDF checks: trim, fonts, glyphs, Devanagari, links, images, blanks"
run python3 scripts/validate_pdf.py $P validation/interior_print_pdf_check.json --expect-links 0 --page-map validation/page_map_print.json
run python3 scripts/validate_pdf.py $D validation/digital_pdf_check.json --page-map validation/page_map_digital.json
step "10. Book QA: folios, Contents, every word, language, margins, templates, calculators, assets"
run python3 scripts/validate_book.py print
run python3 scripts/validate_book.py digital
step "10b. Folio audit: one correct page number per page (text + pixels), single numbering source"
run python3 scripts/validate_folios.py $P validation/page_map_print.json validation/folios_print.json --raw interior/build/raw_print.pdf
run python3 scripts/validate_folios.py $D validation/page_map_digital.json validation/folios_digital.json --raw interior/build/raw_digital.pdf
step "11. Print interior ink: black only (no CMY on any page)"
cmy=$(gs -q -o - -sDEVICE=inkcov $P | awk '{t+=$1+$2+$3} END {printf "%.6f", t}')
if [ "$cmy" = "0.000000" ]; then echo "PASS  print interior is K-only on all pages"; else echo "FAIL  CMY ink found: $cmy"; fail=1; fi
step "12. Final cover artwork (approved Concept A; provisional spine from final page count)"
pages=$(pdfinfo $P | awk '/^Pages/ {print $2}')
run python3 cover/build_cover_final.py "$pages" > /dev/null
for f in final/cover/ZTFC_cover_*.pdf; do
  if pdffonts "$f" | awk 'NR>2 && $(NF-4)!="yes" {bad=1} END {exit bad}' && ! grep -qa " rg$\| RG$" <(qpdf --qdf --object-streams=disable "$f" - 2>/dev/null || cat "$f"); then
    echo "PASS  $(basename "$f"): fonts embedded"; else echo "CHECK $(basename "$f")"; fi
done
sha256sum -c --quiet cover/approved_cover_A.sha256 && echo "PASS  approved cover source still unchanged after final build" || { echo "FAIL  approved cover source changed"; fail=1; }

echo; [ $fail -eq 0 ] && echo "ALL CHECKS PASSED" || echo "SOME CHECKS FAILED — see output above"
exit $fail
