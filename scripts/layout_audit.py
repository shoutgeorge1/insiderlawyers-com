# -*- coding: utf-8 -*-
"""Audit layout variants across static HTML; write scripts/layout_audit.md."""
from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from pathlib import Path

def site_root() -> Path:
    """Resolve insiderlawyers-com root even if this file is symlinked."""
    here = Path(__file__).resolve()
    candidates = [here.parent.parent, Path.cwd(), *here.parents]
    for base in candidates:
        p = Path(base).resolve()
        for _ in range(24):
            if (
                (p / "sitemap.xml").is_file()
                and (p / "styles" / "main.css").is_file()
                and (p / "index.html").is_file()
            ):
                return p
            if p.parent == p:
                break
            p = p.parent
    raise SystemExit("Could not find site root (sitemap.xml + styles/main.css + index.html).")


ROOT = site_root()
OUT = ROOT / "scripts" / "layout_audit.md"


def norm(s: str) -> str:
    s = re.sub(r"\s+", " ", s)
    return s.strip()[:12000]


def extract_pre_main(html: str) -> tuple[str, str | None]:
    """Return (before <main>, main_tag) or full if no main."""
    m = re.search(r"<main\b", html, re.I)
    if not m:
        return html, None
    return html[: m.start()], html[m.start() : m.start() + 20]


def header_signature(html: str) -> str | None:
    m = re.search(r"<header\b[\s\S]*?</header>", html, re.I)
    if not m:
        return None
    h = hashlib.sha256(norm(m.group(0)).encode()).hexdigest()[:16]
    return h


def footer_signature(html: str) -> str | None:
    m = re.search(r"<footer\b[\s\S]*?</footer>", html, re.I)
    if not m:
        return None
    return hashlib.sha256(norm(m.group(0)).encode()).hexdigest()[:16]


def has_viewport(html: str) -> bool:
    return bool(re.search(r'name=["\']viewport["\']', html, re.I))


def main():
    html_files = sorted(ROOT.rglob("*.html"))
    by_header: dict[str, list[str]] = defaultdict(list)
    by_footer: dict[str, list[str]] = defaultdict(list)
    tap_pages: list[str] = []
    hide_pages: list[str] = []
    no_main: list[str] = []
    no_viewport: list[str] = []
    nav_impl = {"site_nav_js": 0, "inline_menu_only": 0, "both": 0, "neither": 0}
    sticky_risk: list[str] = []

    for p in html_files:
        rel = str(p.relative_to(ROOT)).replace("\\", "/")
        t = p.read_text(encoding="utf-8", errors="replace")
        pre, _ = extract_pre_main(t)
        if "<main" not in t.lower():
            no_main.append(rel)

        hs = header_signature(t)
        if hs:
            by_header[hs].append(rel)
        else:
            by_header["__missing__"].append(rel)

        fs = footer_signature(t)
        if fs:
            by_footer[fs].append(rel)
        else:
            by_footer["__missing__"].append(rel)

        if "tap-to-call-bar" in t:
            tap_pages.append(rel)
        if "header--hidden" in t or "header--scroll-hide" in t:
            hide_pages.append(rel)
        if not has_viewport(t):
            no_viewport.append(rel)

        sn = "site-nav.js" in t
        inl = bool(re.search(r"mobile-menu-toggle[\s\S]{0,2000}header-nav-wrap", t)) and (
            "addEventListener('click'" in t or "addEventListener(\"click\"" in t
        )
        if sn and inl:
            nav_impl["both"] += 1
        elif sn:
            nav_impl["site_nav_js"] += 1
        elif inl:
            nav_impl["inline_menu_only"] += 1
        else:
            nav_impl["neither"] += 1

        if "tap-to-call-bar" in t and ("position:fixed" in t or "header--hidden" in t):
            sticky_risk.append(rel)

    lines = [
        "# Layout audit — insiderlawyers.com",
        "",
        f"**Generated:** automated scan of `{len(html_files)}` HTML files under repo root.",
        "",
        "## Summary",
        "",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Total HTML files | {len(html_files)} |",
        f"| Unique header signatures (SHA256 prefix) | {len([k for k in by_header if k != '__missing__'])} |",
        f"| Files missing `<header>` block | {len(by_header.get('__missing__', []))} |",
        f"| Unique footer signatures | {len([k for k in by_footer if k != '__missing__'])} |",
        f"| Files missing `<footer>` block | {len(by_footer.get('__missing__', []))} |",
        f"| Pages with `tap-to-call-bar` | {len(tap_pages)} |",
        f"| Pages with hide-on-scroll header scripts/classes | {len(hide_pages)} |",
        f"| Pages missing viewport meta | {len(no_viewport)} |",
        f"| Pages missing `<main>` | {len(no_main)} |",
        "",
        "## Nav / script patterns (heuristic)",
        "",
        f"- `site-nav.js` only: {nav_impl['site_nav_js']}",
        f"- Inline menu handlers only: {nav_impl['inline_menu_only']}",
        f"- Both: {nav_impl['both']}",
        f"- Neither detected: {nav_impl['neither']}",
        "",
        "## Unique headers (by hash) → files",
        "",
    ]

    for h in sorted(by_header.keys()):
        pages = sorted(by_header[h])
        lines.append(f"### `{h}` — {len(pages)} page(s)")
        lines.append("")
        for rel in pages[:35]:
            lines.append(f"- `{rel}`")
        if len(pages) > 35:
            lines.append(f"- … and {len(pages) - 35} more")
        lines.append("")

    lines.extend(
        [
            "## Unique footers (by hash) → files",
            "",
        ]
    )
    for h in sorted(by_footer.keys()):
        pages = sorted(by_footer[h])
        lines.append(f"### `{h}` — {len(pages)} page(s)")
        lines.append("")
        for rel in pages[:25]:
            lines.append(f"- `{rel}`")
        if len(pages) > 25:
            lines.append(f"- … and {len(pages) - 25} more")
        lines.append("")

    lines.extend(
        [
            "## Pages with tap-to-call bottom bar",
            "",
            f"{len(tap_pages)} files (mobile bottom bar pattern).",
            "",
            "## Pages with sticky / hide-on-scroll risk",
            "",
            "Pages that reference `tap-to-call-bar` **and** hide-on-scroll or fixed positioning in markup/scripts "
            "(stacking / overlap risk before remediation):",
            "",
        ]
    )
    for rel in sorted(set(sticky_risk))[:60]:
        lines.append(f"- `{rel}`")
    if len(set(sticky_risk)) > 60:
        lines.append(f"- … and {len(set(sticky_risk)) - 60} more")

    lines.extend(["", "## Mobile viewport meta gaps", ""])
    for rel in sorted(no_viewport)[:40]:
        lines.append(f"- `{rel}`")
    if len(no_viewport) > 40:
        lines.append(f"- … and {len(no_viewport) - 40} more")

    lines.extend(["", "## Pages without `<main>` (landmarks)", ""])
    for rel in sorted(no_main)[:30]:
        lines.append(f"- `{rel}`")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
