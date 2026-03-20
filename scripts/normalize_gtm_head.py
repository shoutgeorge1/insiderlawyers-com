# -*- coding: utf-8 -*-
"""Replace legacy GTM head loaders with hostname-guarded snippet; inject if missing."""
from __future__ import annotations

import re
import sys
from pathlib import Path

SKIP_PARTS = ("_old-site-extract/", "/_old-site-extract/", "\\_old-site-extract\\")

GTM_HEAD = Path(__file__).resolve().parent.parent / "components" / "gtm-head-snippet.html"
INSERT_SCRIPT = GTM_HEAD.read_text(encoding="utf-8")
INSERT_SCRIPT = re.sub(r"^<!--.*?-->\s*", "", INSERT_SCRIPT, flags=re.S).strip() + "\n"

OLD_GTM_HEAD = re.compile(
    r"(?:<!--\s*Google Tag Manager(?:\s*\([^)]*\))?\s*-->\s*)?"
    r"<script>\s*"
    r"\(\s*function\s*\(\s*w\s*,\s*d\s*,\s*s\s*,\s*l\s*,\s*i\s*\)"
    r"[\s\S]*?"
    r"GTM-WS8XT5FC"
    r"[\s\S]*?"
    r"</script>\s*"
    r"(?:<!--\s*End Google Tag Manager\s*-->\s*)?",
    re.I,
)

LEGACY_NAV_IN_STYLE = re.compile(
    r"\n[ \t]*\.header-content\{[\s\S]*?"
    r"\.content-body a\.btn-secondary:hover\{[^}]*\}\s*",
    re.M,
)


def should_skip(path: Path) -> bool:
    s = str(path).replace("\\", "/")
    if any(p in s for p in SKIP_PARTS):
        return True
    if "/components/" in "/" + s.lower() + "/":
        return True
    return False


def normalize_gtm(html: str) -> tuple[str, bool]:
    if "GTM-WS8XT5FC" not in html and not OLD_GTM_HEAD.search(html):
        return html, False
    il = html.lower().find("<head")
    ic = html.lower().find("</head>")
    if il == -1 or ic == -1:
        return html, False
    head = html[il:ic]
    if "allowedhosts.includes(window.location.hostname)" in head.lower().replace(" ", ""):
        return html, False

    new_head, n_rm = OLD_GTM_HEAD.subn("", head)
    changed = bool(n_rm)

    if "GTM-WS8XT5FC" in html:
        if "allowedhosts.includes" not in new_head.lower().replace(" ", ""):
            new_head = new_head.rstrip() + "\n" + INSERT_SCRIPT
            changed = True

    if not changed:
        return html, False
    return html[:il] + new_head + html[ic:], True


def strip_legacy_nav_css(html: str) -> tuple[str, bool]:
    if "header--unified" not in html:
        return html, False
    if ".header-content{" not in html:
        return html, False
    new_html, n = LEGACY_NAV_IN_STYLE.subn("\n", html, count=1)
    return new_html, bool(n)


def process_file(path: Path) -> list[str]:
    notes: list[str] = []
    raw = path.read_text(encoding="utf-8", errors="replace")
    out, g = normalize_gtm(raw)
    out, s = strip_legacy_nav_css(out)
    if out != raw:
        path.write_text(out, encoding="utf-8")
        if g:
            notes.append("gtm")
        if s:
            notes.append("legacy-nav-css")
    return notes


def main() -> None:
    here = Path(__file__).resolve().parent.parent
    roots = [here]
    pi = here.parent / "pi-search-caraccident-lp"
    if pi.is_dir():
        roots.append(pi)
    touched = 0
    for root in roots:
        for path in sorted(root.rglob("*.html")):
            if should_skip(path):
                continue
            n = process_file(path)
            if n:
                touched += 1
                print(path.relative_to(root), ":", ",".join(n))
    print("Updated", touched, "files")


if __name__ == "__main__":
    main()
    sys.exit(0)
