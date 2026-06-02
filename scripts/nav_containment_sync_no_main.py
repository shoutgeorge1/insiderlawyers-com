# -*- coding: utf-8 -*-
"""Sync lean header/footer chrome into pages that have <header> but no <main>.

Companion to scripts/apply_global_layout.py for static PPC LPs and legal pages
that don't follow the <header>...<main>...</main>...<footer> pattern.

Replaces ONLY the header block (header through the tap-to-call-bar) and the
footer block. Does not touch forms, scripts, GTM, CallRail attributes, or
page body content.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def site_root() -> Path:
    here = Path(__file__).resolve()
    p = here.parent.parent
    if (p / "components" / "global-chrome-before-main.html").is_file():
        return p
    raise SystemExit("Could not find site root.")


ROOT = site_root()
COMP = ROOT / "components"
CHROME_PATH = COMP / "global-chrome-before-main.html"
FOOTER_PATH = COMP / "global-footer.html"

HEADER_BLOCK_RE = re.compile(
    r"<header\b[\s\S]*?</header>\s*<a\b[^>]*class=\"tap-to-call-bar\"[^>]*>[\s\S]*?</a>",
    flags=re.IGNORECASE,
)
FOOTER_BLOCK_RE = re.compile(r"<footer\b[\s\S]*?</footer>", flags=re.IGNORECASE)

TARGET_PAGES = [
    "car-accident-lawyer-near-me-los-angeles/index.html",
    "legal/accessibility/index.html",
    "legal/disclaimer/index.html",
    "legal/results-disclaimer/index.html",
    "legal/terms/index.html",
    "los-angeles-auto-accident-lawyer/index.html",
    "los-angeles-bicycle-accident-lawyer/index.html",
    "los-angeles-brain-injury-lawyer/index.html",
    "los-angeles-car-crash-lawyer/index.html",
    "los-angeles-catastrophic-injury-lawyer/index.html",
    "los-angeles-motorcycle-accident-lawyer/index.html",
    "los-angeles-nursing-home-neglect-lawyer/index.html",
    "los-angeles-pedestrian-accident-lawyer/index.html",
    "los-angeles-premises-liability-lawyer/index.html",
    "los-angeles-product-liability-lawyer/index.html",
    "los-angeles-slip-and-fall-lawyer/index.html",
    "los-angeles-spine-injury-lawyer/index.html",
    "los-angeles-truck-accident-lawyer/index.html",
    "los-angeles-uber-lyft-accident-lawyer/index.html",
    "los-angeles-wrongful-death-lawyer/index.html",
]


def main() -> None:
    chrome = CHROME_PATH.read_text(encoding="utf-8").strip()
    footer = FOOTER_PATH.read_text(encoding="utf-8").strip()
    changed = []
    for rel in TARGET_PAGES:
        path = ROOT / rel
        if not path.is_file():
            print(f"missing: {rel}")
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        out = raw
        new_out, n_header = HEADER_BLOCK_RE.subn(chrome, out, count=1)
        if n_header == 0:
            print(f"no header match: {rel}")
            continue
        new_out, n_footer = FOOTER_BLOCK_RE.subn(footer, new_out, count=1)
        if n_footer == 0:
            print(f"no footer match: {rel}")
            continue
        if new_out != raw:
            path.write_text(new_out, encoding="utf-8")
            changed.append(rel)
    print(f"Updated {len(changed)} files")


if __name__ == "__main__":
    main()
    sys.exit(0)
