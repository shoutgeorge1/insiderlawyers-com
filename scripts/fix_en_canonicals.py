# -*- coding: utf-8 -*-
"""Normalize English-page canonicals to the no-trailing-slash form.

The site convention is no trailing slash for English URLs (matching Vercel
cleanUrls). A handful of historical pages still declare a canonical with a
trailing slash. This script auto-detects them and rewrites:

    <link rel="canonical" href="https://www.insiderlawyers.com/foo/">
    <meta property="og:url"  content="https://www.insiderlawyers.com/foo/">

to the no-trailing-slash form. Spanish /es/ pages are left untouched (they
use a trailing-slash convention).

Idempotent and safe to re-run.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_WORKSPACE = Path(r"C:\Users\georgea\insiderlawyer-com-lps")
ROOT = _WORKSPACE / "insiderlawyers-com"
if not (ROOT / "components" / "global-chrome-before-main.html").is_file():
    raise SystemExit(f"ROOT sanity check failed: {ROOT}")
SITE = "https://www.insiderlawyers.com"

SKIP_DIRS = {"components", "scripts", "styles", "images", "fonts", "social-assets", "_dev", "_old-site-extract", "node_modules"}

RE_CANON = re.compile(
    r'(<link[^>]+rel=["\']canonical["\'][^>]+href=["\'])([^"\']+)(["\'])',
    re.I,
)
RE_OGURL = re.compile(
    r'(<meta[^>]+property=["\']og:url["\'][^>]+content=["\'])([^"\']+)(["\'])',
    re.I,
)


def url_path_for(p: Path) -> str:
    rel = str(p.relative_to(ROOT)).replace("\\", "/")
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("/index.html")]
    if rel.endswith(".html"):
        return "/" + rel[: -len(".html")]
    return "/" + rel


def is_skip(rel: str) -> bool:
    return any(rel.startswith(d + "/") for d in SKIP_DIRS) or rel.startswith("es/") or rel == "es/index.html"


def fix_file(p: Path) -> bool:
    rel = str(p.relative_to(ROOT)).replace("\\", "/")
    if is_skip(rel):
        return False
    if not (rel == "index.html" or rel.endswith("/index.html")):
        return False
    expected_path = url_path_for(p)
    if expected_path == "/":
        expected_canon = SITE + "/"
    else:
        expected_canon = SITE + expected_path
    raw = p.read_text(encoding="utf-8", errors="replace")
    new = raw

    def fix_canon(m: re.Match[str]) -> str:
        href = m.group(2).strip()
        if href.rstrip("/") == expected_canon.rstrip("/") and href != expected_canon:
            return m.group(1) + expected_canon + m.group(3)
        return m.group(0)

    def fix_og(m: re.Match[str]) -> str:
        content = m.group(2).strip()
        if content.rstrip("/") == expected_canon.rstrip("/") and content != expected_canon:
            return m.group(1) + expected_canon + m.group(3)
        return m.group(0)

    new = RE_CANON.sub(fix_canon, new, count=1)
    new = RE_OGURL.sub(fix_og, new, count=1)
    if new == raw:
        return False
    p.write_text(new, encoding="utf-8")
    return True


def main() -> int:
    changed = 0
    scanned = 0
    for p in sorted(ROOT.rglob("*.html")):
        scanned += 1
        if fix_file(p):
            rel = str(p.relative_to(ROOT)).replace("\\", "/")
            print(f"fixed: /{rel}")
            changed += 1
    print(f"Scanned {scanned} files, normalized {changed} canonicals")
    return 0


if __name__ == "__main__":
    sys.exit(main())
