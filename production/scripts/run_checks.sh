#!/usr/bin/env bash
# Rebuild the content sources from the original PDF and run every validation.
# Usage (from anywhere): bash production/scripts/run_checks.sh
set -u
cd "$(dirname "$0")/.."            # production/
fail=0
step(){ echo; echo "== $1"; }
run(){ "$@" || fail=1; }

step "Original assets unchanged"
run bash validation/validate.sh

step "Extract tagged structure from the original manuscript"
run python3 scripts/extract_manuscript.py
step "Rebuild semantic source"
run python3 scripts/build_source.py
step "Content fidelity: extracted source vs original PDF (every word)"
run python3 scripts/validate_fidelity.py source/extracted.html validation/fidelity_extracted.json --allow validation/fidelity_allow_extracted.json
step "Apply documented print/digital edits + resource-removal scan"
run python3 scripts/apply_edits.py
step "Prompt validation (141 expected)"
for ed in print digital; do run python3 scripts/validate_prompts.py source/book_$ed.html validation/prompts_$ed.json --baseline source/extracted.html | tail -1; done
step "Content inventory"
run python3 scripts/content_inventory.py source/extracted.html audit/content_inventory.json
run python3 scripts/content_inventory.py source/book_print.html audit/content_inventory_print.json
run python3 scripts/write_inventory_reports.py
if [ -f previews/proof/ZTFC_interior_proof_5pp_print.pdf ]; then
  step "Proof PDF checks (trim, fonts, glyphs, links, images)"
  run python3 scripts/validate_pdf.py previews/proof/ZTFC_interior_proof_5pp_print.pdf validation/proof_print_pdf_check.json --expect-links 0
fi
echo; [ $fail -eq 0 ] && echo "ALL CHECKS PASSED" || echo "SOME CHECKS FAILED — see output above"
exit $fail
