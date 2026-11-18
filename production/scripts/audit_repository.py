#!/usr/bin/env python3
"""Repository and asset audit: sizes, SHA-256, image dimensions/modes/dpi,
PDF page count and page sizes, git state. Writes production/audit/asset_inventory.json.

Usage: audit_repository.py  (from anywhere)
"""
import hashlib
import json
import subprocess
from pathlib import Path

import pymupdf
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "production/audit/asset_inventory.json"

ROLES = {
    "manuscript/ZERO_TO_FIRST_CLIENT_2026.pdf": "Original manuscript (authoritative source, read-only)",
    "author-assets/divyanshu-portrait.jpg": "Original author portrait (read-only)",
    "author-assets/originals/DIVYANSHU_VERMA_SIGNATURE_ORIGINAL_UPLOAD.png": "Genuine handwritten signature, exactly as uploaded (read-only)",
    "author-assets/DIVYANSHU_VERMA_AUTHOR_SIGNATURE.png": "Genuine signature, cleaned, transparent, original blue ink (digital/colour use)",
    "production/SOURCE_AND_BUILD/DIVYANSHU_VERMA_AUTHOR_SIGNATURE_BLACK.png": "Genuine signature, cleaned, transparent, near-black (print interior)",
    "production/SOURCE_AND_BUILD/DIVYANSHU_VERMA_AUTHOR_SIGNATURE_WHITE.png": "Genuine signature, cleaned, transparent, white (dark backgrounds/cover)",
    "production/validation/signature_light_dark_check.png": "QA sheet from earlier signature cleanup",
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    recorded = {}
    rec = ROOT / "production/validation/originals.sha256"
    if rec.exists():
        for line in rec.read_text().splitlines():
            h, f = line.split()
            recorded[f] = h
    inv = []
    for f in files:
        p = ROOT / f
        e = {"path": f, "bytes": p.stat().st_size, "sha256": sha(p), "role": ROLES.get(f, "")}
        if f in recorded:
            e["matches_recorded_original_hash"] = recorded[f] == e["sha256"]
        if p.suffix.lower() in (".png", ".jpg", ".jpeg"):
            im = Image.open(p)
            e.update({"pixels": list(im.size), "mode": im.mode,
                      "dpi_metadata": [round(v) for v in im.info["dpi"]] if "dpi" in im.info else None})
            if im.mode == "RGB":
                import numpy as np
                a = np.asarray(im.convert("RGB")).astype(int)
                e["is_greyscale_content"] = bool((abs(a[..., 0] - a[..., 1]).max() <= 8) and (abs(a[..., 1] - a[..., 2]).max() <= 8))
        if p.suffix.lower() == ".pdf":
            d = pymupdf.open(p)
            sizes = {f"{round(pg.rect.width, 2)}x{round(pg.rect.height, 2)}" for pg in d}
            e.update({"pdf_pages": d.page_count, "pdf_page_sizes_pt": sorted(sizes),
                      "pdf_page_size_mm": [round(d[0].rect.width / 72 * 25.4, 1), round(d[0].rect.height / 72 * 25.4, 1)],
                      "pdf_metadata": {k: v for k, v in d.metadata.items() if v}})
        inv.append(e)
    git = {
        "branch": subprocess.run(["git", "branch", "--show-current"], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
        "log": subprocess.run(["git", "log", "--oneline"], cwd=ROOT, capture_output=True, text=True).stdout.strip().splitlines(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"git": git, "files": inv}, ensure_ascii=False, indent=1))
    for e in inv:
        extra = e.get("pixels") or e.get("pdf_pages") or ""
        print(f"{e['bytes']:>9}  {e['sha256'][:12]}  {f'{extra}':<14} {e['path']}")
    print("git:", git)


if __name__ == "__main__":
    main()
