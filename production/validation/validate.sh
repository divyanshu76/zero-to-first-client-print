#!/usr/bin/env bash
# Repository validation: source integrity + signature asset checks.
# Usage: bash production/validation/validate.sh   (from repo root)
set -u; cd "$(dirname "$0")/../.."; fail=0
ok(){ echo "PASS  $1"; }; bad(){ echo "FAIL  $1"; fail=1; }

sha256sum -c --quiet production/validation/originals.sha256 && ok "originals unchanged (manuscript, portrait, signature upload)" || bad "an original asset changed"

python3 - <<'EOF' || fail=1
import sys, numpy as np
from PIL import Image
p = "author-assets/DIVYANSHU_VERMA_AUTHOR_SIGNATURE.png"
im = Image.open(p); err = []
if im.mode != "RGBA": err.append(f"mode {im.mode} != RGBA")
a = np.asarray(im)[..., 3]
if not (a == 0).any(): err.append("no transparent pixels")
if (a[0, :] > 0).any() or (a[-1, :] > 0).any() or (a[:, 0] > 0).any() or (a[:, -1] > 0).any():
    err.append("ink touches the edge (cropped too tight)")
if im.width < 1500: err.append(f"width {im.width}px < 1500px")
dpi = round(im.info.get("dpi", (0, 0))[0])
if dpi < 300: err.append(f"dpi {dpi} < 300")
print(("FAIL  " + "; ".join(err)) if err else f"PASS  signature PNG {im.size[0]}x{im.size[1]} RGBA, {dpi} dpi, transparent")
sys.exit(1 if err else 0)
EOF

for f in production/SOURCE_AND_BUILD/build_author_mark.py production/SOURCE_AND_BUILD/DIVYANSHU_VERMA_AUTHOR_SIGNATURE.svg; do
  [ -e "$f" ] && bad "generated author mark still present: $f"
done; [ $fail -eq 0 ] && ok "no generated author mark in repo tree"

exit $fail
