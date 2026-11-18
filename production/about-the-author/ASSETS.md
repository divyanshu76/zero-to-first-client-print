# About the Author — production assets

Status: **final.** Page source `production/about-the-author/about.html`; placed at the end of the book (paperback p. 237); exported to `production/final/about-the-author/`. Print uses `signature_black_print_gray.png` (K + alpha, alpha byte-identical to the supplied black version, made by `build_signature_print.py`); digital uses the original blue cleaned signature. Portrait print derivative `portrait_print_gray.jpg` (greyscale, framing crop only, `build_portrait.py`). The current manuscript (`manuscript/ZERO_TO_FIRST_CLIENT_2026.pdf`) has no About the Author page, so it needs to be added during the print build. Do not edit the manuscript PDF itself.

| Element | File | Notes |
|---|---|---|
| Portrait | `author-assets/divyanshu-portrait.jpg` | B&W, 1220×1707 px. About 2.0 in wide at 600 ppi, or about 4.1 in at 300 ppi. |
| Signature | `author-assets/DIVYANSHU_VERMA_AUTHOR_SIGNATURE.png` | **Genuine handwritten signature supplied by the author.** Original blue ink, transparent background. |
| Signature, 1-colour (K only) | `production/SOURCE_AND_BUILD/DIVYANSHU_VERMA_AUTHOR_SIGNATURE_BLACK.png` | For black-only interiors. Same strokes. |
| Signature, reversed | `production/SOURCE_AND_BUILD/DIVYANSHU_VERMA_AUTHOR_SIGNATURE_WHITE.png` | For dark backgrounds or cover. Same strokes. |

Byline: **Divyanshu Verma**. Imprint: DeadCode Labs.

Placement guidance: signature below the bio text, left-aligned with it, 1.6–2.4 in wide. It is 1796 px wide, so at 2 in it prints at about 900 ppi. Never scale it past 6 in (300 ppi floor).

Only the author-supplied signature may be used. The earlier generated calligraphic mark was removed in commit "Replace generated author mark with genuine handwritten signature" and must not be reintroduced.
