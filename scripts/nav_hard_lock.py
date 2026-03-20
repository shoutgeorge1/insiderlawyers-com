# -*- coding: utf-8 -*-
"""Navigation hard lock: report fragmentation, replace chrome with global-chrome-before-main.html."""
from __future__ import annotations

import hashlib
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPONENT = ROOT / "components" / "global-chrome-before-main.html"
SKIP_PREFIX = ("_old-site-extract/", "_dev/", "social-assets/")
LA_REL = "los-angeles-car-accident-lawyer/index.html"
# Home has a long inline <style> and sections that confuse bounded regex tests; chrome is already unified in repo.
HOME_REL = "index.html"

# Canonical chrome: header--unified + tap bar (exact bytes from component file)
CANONICAL = COMPONENT.read_text(encoding="utf-8").rstrip() + "\n"

UNIFIED_FULL = re.compile(
    r'<header\s+class="header\s+header--unified"[^>]*>[\s\S]*?</header>\s*'
    r'<a\s+href="tel:844-467-4335"[^>]*class="tap-to-call-bar"[^>]*>[\s\S]*?</a>',
    re.I,
)
UNIFIED_SOLO = re.compile(
    r'<header\s+class="header\s+header--unified"[^>]*>[\s\S]*?</header>'
    r'(?!\s*<a\s+href="tel:844-467-4335")',
    re.I,
)
LEGACY_CHROME = re.compile(
    r'<header\s+class="header"(?![^>]*\bheader--unified\b)[^>]*>[\s\S]*?</header>\s*'
    r'<div\s+class="header-nav-wrap"[^>]*>[\s\S]*?</nav>\s*</div>\s*</div>',
    re.I,
)
SITE_NAV_RE = re.compile(
    r'<script\s+src="/scripts/site-nav\.js\?v=\d+"\s+defer>\s*</script>\s*',
    re.I,
)
# Hide-on-scroll helpers (obsolete once header is static site-wide)
RE_STICKY_HIDE_MEDIA = re.compile(
    r"@media\s*\(\s*max-width\s*:\s*767px\s*\)\s*\{\s*\.sticky-header\.header--hidden\s*\{[^}]*\}\s*\}\s*",
    re.I,
)
RE_STICKY_HEADER_OPEN = re.compile(r"\.sticky-header\s*\{", re.I)

# Only rewrite chrome inside the top of the document so regex can never affect hero/body copy.
CHROME_WINDOW_AFTER_BODY = 60_000


def norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())


def should_skip(rel: str) -> bool:
    r = rel.replace("\\", "/")
    return any(r.startswith(p) or p.strip("/") in r for p in SKIP_PREFIX)


def classify(html: str) -> str:
    if LEGACY_CHROME.search(html):
        return "legacy_split_header_plus_nav_wrap"
    if UNIFIED_FULL.search(html):
        return "unified_header_plus_tap_bar"
    if re.search(r'class="header\s+header--unified"', html):
        return "unified_header_missing_tap_anchor"
    if re.search(r"<header[^>]*class=\"header\"", html, re.I):
        return "other_header_markup"
    return "no_primary_header_detected"


def nav_fingerprint(html: str) -> str:
    m = re.search(
        r'<header\s+class="header\s+header--unified"[^>]*>([\s\S]*?)</header>',
        html,
        re.I,
    )
    if not m:
        m2 = LEGACY_CHROME.search(html)
        if m2:
            blob = norm_ws(m2.group(0)[:8000])
        else:
            h = re.search(r"<header[^>]*>([\s\S]{0,6000}?)</header>", html, re.I)
            blob = norm_ws(h.group(0)) if h else "none"
    else:
        blob = norm_ws(m.group(1))
    return hashlib.sha256(blob.encode("utf-8", errors="replace")).hexdigest()[:16]


def dedupe_site_nav(html: str) -> tuple[str, bool]:
    matches = list(SITE_NAV_RE.finditer(html))
    if len(matches) <= 1:
        return html, False
    last = matches[-1]
    out = []
    pos = 0
    for m in matches[:-1]:
        out.append(html[pos : m.start()])
        pos = m.end()
    out.append(html[pos:])
    return "".join(out), True


def chrome_apply_slice(html: str) -> tuple[int, int]:
    bi = html.lower().find("<body")
    lo = bi if bi >= 0 else 0
    hi = min(len(html), lo + CHROME_WINDOW_AFTER_BODY)
    return lo, hi


def _apply_chrome_chunk(html: str) -> tuple[str, list[str]]:
    """Run chrome substitutions on a substring (caller slices document)."""
    notes: list[str] = []
    html, c = LEGACY_CHROME.subn(CANONICAL, html)
    if c:
        notes.append(f"replaced_legacy_chrome×{c}")
    guard = 0
    while guard < 12:
        guard += 1
        m = UNIFIED_FULL.search(html)
        if not m:
            break
        if norm_ws(m.group(0)) == norm_ws(CANONICAL):
            break
        html2 = UNIFIED_FULL.sub(CANONICAL, html, count=1)
        if html2 == html:
            break
        html = html2
        notes.append("normalized_unified+taps")
    guard = 0
    while guard < 12:
        guard += 1
        if not UNIFIED_SOLO.search(html):
            break
        html2 = UNIFIED_SOLO.sub(CANONICAL, html, count=1)
        if html2 == html:
            break
        html = html2
        notes.append("added_tap_via_unified_solo")
    return html, notes


def apply_chrome(html: str) -> tuple[str, list[str]]:
    lo, hi = chrome_apply_slice(html)
    chunk = html[lo:hi]
    new_chunk, notes = _apply_chrome_chunk(chunk)
    if new_chunk == chunk:
        return html, notes
    return html[:lo] + new_chunk + html[hi:], notes


def _brace_consume(s: str, open_idx: int) -> int:
    """Return index after closing `}` matching `{` at open_idx, or len(s) if unbalanced."""
    depth = 0
    j = open_idx
    while j < len(s):
        c = s[j]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    return len(s)


def strip_legacy_nav_inline_css(html: str) -> tuple[str, list[str]]:
    """Remove per-page duplicated mobile-nav CSS and hide-on-scroll hooks (main.css + site-nav.js own this)."""
    notes: list[str] = []
    html2 = RE_STICKY_HIDE_MEDIA.sub("", html)
    if html2 != html:
        notes.append("removed_sticky_header_hide_media")
        html = html2

    needles = ("@media(max-width:900px){", "@media (max-width:900px){")
    stripped_media = False
    while True:
        removed = False
        for tok in needles:
            i = 0
            while True:
                i = html.find(tok, i)
                if i < 0:
                    break
                start_brace = html.find("{", i)
                if start_brace < 0:
                    i += len(tok)
                    continue
                j = _brace_consume(html, start_brace)
                block = html[i:j]
                if (
                    ".header-content" in block
                    and "grid-template-columns:1fr" in block
                    and (".header-nav-wrap" in block or ".header-nav-row" in block)
                ):
                    html = html[:i] + html[j:]
                    stripped_media = True
                    removed = True
                    break
                i += len(tok)
            if removed:
                break
        if not removed:
            break
    if stripped_media:
        notes.append("removed_legacy_mobile_nav_media900")

    html3 = html
    while True:
        m = RE_STICKY_HEADER_OPEN.search(html3)
        if not m:
            break
        start = m.start()
        open_b = m.end() - 1
        if open_b < 0 or html3[open_b] != "{":
            break
        end = _brace_consume(html3, open_b)
        block = html3[start:end]
        if "sticky" in block and "position" in block:
            html3 = html3[:start] + html3[end:]
            notes.append("removed_inline_sticky_header_rule")
            continue
        break
    html = html3

    html4, n_or = re.subn(
        r"\n\s*;transition:\s*transform\s*\.25s\s*ease(?:\s*;transition:\s*transform\s*\.25s\s*ease)?",
        "",
        html,
    )
    if n_or:
        notes.append("removed_orphan_transition_rules")
        html = html4

    return html, list(dict.fromkeys(notes))


def apply_nav_hard_lock(html: str, *, skip_chrome: bool = False) -> tuple[str, list[str]]:
    notes: list[str] = []
    if not skip_chrome:
        html, n = apply_chrome(html)
        notes.extend(n)
    html, n = strip_legacy_nav_inline_css(html)
    notes.extend(n)
    html2, ch = dedupe_site_nav(html)
    if ch:
        html = html2
        notes.append("deduped_site_nav_js")
    return html, list(dict.fromkeys(notes))


def main() -> None:
    if "--help" in sys.argv:
        print("Usage: nav_hard_lock.py   # writes report, applies changes")
        sys.exit(0)

    by_struct: dict[str, list[str]] = defaultdict(list)
    by_fp: dict[str, list[str]] = defaultdict(list)
    for p in sorted(ROOT.rglob("*.html")):
        rel = str(p.relative_to(ROOT)).replace("\\", "/")
        if should_skip(rel):
            continue
        raw = p.read_text(encoding="utf-8", errors="replace")
        cat = classify(raw)
        by_struct[cat].append(rel)
        by_fp[nav_fingerprint(raw)].append(rel)

    report = ROOT / "scripts" / "nav_fragmentation_report.md"
    lines = [
        "# Navigation fragmentation scan",
        "",
        f"**Canonical chrome file:** `components/global-chrome-before-main.html` ({len(CANONICAL)} bytes).",
        "",
        "## Unique header/nav fingerprints (pre-lock)",
        "",
        f"**Distinct fingerprints:** {len(by_fp)}",
        "",
    ]
    for fp in sorted(by_fp, key=lambda k: (-len(by_fp[k]), k)):
        pages = by_fp[fp]
        lines.append(f"### `{fp}` — {len(pages)} page(s)")
        for r in pages[:25]:
            lines.append(f"- `{r}`")
        if len(pages) > 25:
            lines.append(f"- … +{len(pages) - 25} more")
        lines.append("")

    lines.extend(
        [
            "## Structural categories",
            "",
        ]
    )
    for cat in sorted(by_struct, key=lambda c: (-len(by_struct[c]), c)):
        lines.append(f"### {cat} ({len(by_struct[cat])} files)")
        for r in sorted(by_struct[cat])[:40]:
            lines.append(f"- `{r}`")
        if len(by_struct[cat]) > 40:
            lines.append(f"- … +{len(by_struct[cat]) - 40} more")
        lines.append("")

    report.write_text("\n".join(lines), encoding="utf-8")

    changed_files: list[tuple[str, list[str]]] = []
    for p in sorted(ROOT.rglob("*.html")):
        rel = str(p.relative_to(ROOT)).replace("\\", "/")
        if should_skip(rel):
            continue
        if rel == LA_REL:
            continue
        raw = p.read_text(encoding="utf-8", errors="replace")
        new, notes = apply_nav_hard_lock(raw, skip_chrome=(rel == HOME_REL))
        if new != raw:
            p.write_text(new, encoding="utf-8")
            changed_files.append((rel, notes))

    summary = ROOT / "scripts" / "nav_hard_lock_summary.md"
    sum_lines = [
        "# Navigation hard lock — summary",
        "",
        f"- **Unmodified (locked):** `{LA_REL}`",
        f"- **Chrome regex replacement skipped:** `{HOME_REL}` (already unified; long inline styles/sections).",
        "- **Chrome source:** `components/global-chrome-before-main.html` only.",
        "- **Nav script:** `/scripts/site-nav.js` only (deduped if duplicate tags found).",
        "- **Legacy inline CSS:** hide-on-scroll + duplicate mobile `@media(900px)` nav blocks stripped where found.",
        f"- **HTML files updated:** {len(changed_files)}",
        "",
        "## Files touched",
        "",
    ]
    for rel, notes in changed_files[:200]:
        sum_lines.append(f"- `{rel}`: " + "; ".join(notes))
    if len(changed_files) > 200:
        sum_lines.append(f"\n… and {len(changed_files) - 200} more.")
    summary.write_text("\n".join(sum_lines), encoding="utf-8")
    print("Wrote", report.name, "and", summary.name, "; updated", len(changed_files), "html files")


if __name__ == "__main__":
    main()
