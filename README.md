# ZERO TO FIRST CLIENT — Print Production

Private print-production repo for *ZERO TO FIRST CLIENT: The AI-Powered Business Starter Kit* (2026) by **Divyanshu Verma** · CRAFT & CODE / DEADCODE LABS.

## Structure

| Path | Contents |
|---|---|
| `manuscript/ZERO_TO_FIRST_CLIENT_2026.pdf` | **Source manuscript — read-only. Never overwrite.** 142 pp, A4. |
| `author-assets/divyanshu-portrait.jpg` | Author portrait (original, unmodified, 1220×1707). |
| `author-assets/DIVYANSHU_VERMA_AUTHOR_SIGNATURE.png` | Calligraphic author mark, ink on transparent, 4361×1041 @ 600 dpi. |
| `production/SOURCE_AND_BUILD/` | Author-mark SVG masters, reversed-white PNG, and the build script. |

## Author mark

A typographic calligraphic mark (TeX Gyre Chorus + generated pressure-modulated flourish) for covers, title page and author bio. It is a design element, not a scan of a pen-and-paper signature. Don't use it to sign contracts, KYC or legal documents.

Rebuild: `python3 production/SOURCE_AND_BUILD/build_author_mark.py production/SOURCE_AND_BUILD`

## Checksums (originals)

```
04d4405eac9a3e03284be3931e74027e855809ed865d50202f0258a3c7f36875  manuscript/ZERO_TO_FIRST_CLIENT_2026.pdf
62e67e8d0bfa32fa0c4d09f46ef8b3720fa929046997d3b0a9006b6b3b341794  author-assets/divyanshu-portrait.jpg
```

Production outputs (interior, cover, proofs) go in `production/`, never in `manuscript/`.
