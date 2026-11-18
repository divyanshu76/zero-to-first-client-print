# ZERO TO FIRST CLIENT — Print Production

Private print-production repo for *ZERO TO FIRST CLIENT: The AI-Powered Business Starter Kit* (2026) by **Divyanshu Verma** · DeadCode Labs (imprint as locked in the production brief; the manuscript itself credits DEADCODE LABS).

## Structure

| Path | Contents |
|---|---|
| `manuscript/ZERO_TO_FIRST_CLIENT_2026.pdf` | **Source manuscript. Read-only, never overwrite.** 142 pp, A4. |
| `author-assets/divyanshu-portrait.jpg` | Author portrait (original, unmodified, 1220×1707). |
| `author-assets/DIVYANSHU_VERMA_AUTHOR_SIGNATURE.png` | **Author-supplied genuine handwritten signature**, background removed. Transparent RGBA, 1796×668 px, 600 dpi, original blue ink. |
| `author-assets/originals/DIVYANSHU_VERMA_SIGNATURE_ORIGINAL_UPLOAD.png` | The signature image exactly as the author supplied it (backup, read-only). |
| `production/SOURCE_AND_BUILD/` | `process_signature.py` (cleanup script), plus black (K-only) and white (reversed) versions of the same signature. |
| `production/about-the-author/ASSETS.md` | Asset spec for the About the Author page (portrait + signature). |
| `production/validation/` | `validate.sh`, original-asset checksums, and the light/dark transparency check sheet. |

## Signature

The only signature in this book is the author's own handwritten signature, supplied by Divyanshu Verma. Processing (`production/SOURCE_AND_BUILD/process_signature.py`):

- The supplied file was flat RGB with a grey/white checkerboard painted in. Ink opacity is taken per pixel from colour saturation and darkness, so the checkerboard drops out.
- A contrast curve is applied to opacity only. Stroke shapes, widths, pen skips and proportions are untouched, and nothing is redrawn or traced.
- 56 isolated dust pixels that touched no stroke were removed.
- The image is cropped to the ink with a 40 px transparent margin. It stays at the native pixel resolution and is not upscaled.

An earlier generated calligraphic author mark has been **removed** and must not be used.

## Validate

```
bash production/validation/validate.sh
```

This checks that the manuscript, portrait and original signature upload are byte-identical to the recorded checksums. It also checks that the signature PNG is valid, transparent and high-resolution, and that no generated mark remains.

Production outputs (interior, cover, proofs) go in `production/`, never in `manuscript/`.

## Paperback production (135 × 210 mm)

| Path | Contents |
|---|---|
| `production/audit/` | Phase 1 audit report, asset inventory, content inventory, Devanagari text-layer fix log |
| `production/source/` | `extracted.html` (faithful reconstruction of the PDF), `print_edits.yaml` (every documented change), `book_print.html`, `book_digital.html` |
| `production/design-system/` | `book.css`, colour tokens (print K-only / digital), bundled OFL fonts, rebuilt vector diagrams |
| `production/about-the-author/` | About page content (approved bio), portrait print derivative + script |
| `production/scripts/` | Extraction, edits, typesetting, proof builder, all validators, `run_checks.sh` |
| `production/previews/` | 5-page interior proof (PDF + PNG) and cover concept preview |
| `production/cover/` | Cover concept (not print-ready) |
| `production/validation/` | Machine-readable validation reports |
| `production/reports/` | Proof & design report, production plan, prompt / template / calculator / figure inventories |

Run all checks: `bash production/scripts/run_checks.sh` · Rebuild the proof: `python3 production/scripts/build_proof.py print`

Status: **proof stage, awaiting approval** (see `production/reports/PROOF_AND_DESIGN_REPORT.md`).
