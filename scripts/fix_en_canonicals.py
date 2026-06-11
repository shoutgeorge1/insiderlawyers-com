# -*- coding: utf-8 -*-
"""Normalize English-page canonicals on the 10 pages that historically used a
trailing slash (mismatch with hreflang and with most other pages).

Idempotent and narrowly scoped: only rewrites the <link rel="canonical">
href when it is exactly the trailing-slash form of one of the affected pages.

Run-once-and-forget; safe to re-run.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.insiderlawyers.com"

# 10 EN pages flagged by qa_es_pages.py for trailing-slash canonical.
EN_PATHS = [
    "/settlements",
    "/motor-vehicle",
    "/premises-liability",
    "/parking-lot-accident-lawyer-los-angeles",
    "/t-bone-accident-lawyer-los-angeles",
    "/rear-end-accident-lawyer-los-angeles",
    "/hit-and-run-accident-lawyer-los-angeles",
    "/pedestrian-accident-lawyer-los-angeles",
    "/uber-accident-lawyer-los-angeles",
    "/uninsured-driver-accident-lawyer-los-angeles",
]


def fix_page(en_path: str) -> tuple[bool, str]:
    rel = en_path.strip("/")
    fp = ROOT / Path(rel) / "index.html"
    if not fp.is_file():
        return False, f"missing: {en_path}"
    raw = fp.read_text(encoding="utf-8", errors="replace")
    want_no_slash = f"{SITE}{en_path}"
    bad = f"{SITE}{en_path}/"
    pattern = re.compile(
        r'(<link[^>]+rel=["\']canonical["\'][^>]+href=["\'])' + re.escape(bad) + r'(["\'])',
        flags=re.I,
    )
    new = pattern.sub(r"\1" + want_no_slash + r"\2", raw, count=1)
    # Also normalise og:url if it has trailing slash for this same URL
    pattern_og = re.compile(
        r'(<meta[^>]+property=["\']og:url["\'][^>]+content=["\'])' + re.escape(bad) + r'(["\'])',
        flags=re.I,
    )
    new = pattern_og.sub(r"\1" + want_no_slash + r"\2", new, count=1)
    if new == raw:
        return False, f"no change: {en_path}"
    fp.write_text(new, encoding="utf-8")
    return True, f"fixed:    {en_path}"


def main() -> int:
    changed = 0
    for p in EN_PATHS:
        ok, msg = fix_page(p)
        print(msg)
        if ok:
            changed += 1
    print(f"Updated {changed} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
