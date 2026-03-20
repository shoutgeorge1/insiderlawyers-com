# -*- coding: utf-8 -*-
"""Second-pass UI: remove non-PPC call-bar, strip home-ppc, calm tap overrides, breadcrumbs."""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path


def site_root() -> Path:
    """This file lives in insiderlawyers-com/scripts/ — site root is that folder."""
    here = Path(__file__).resolve()
    base = here.parent.parent
    if (base / "styles" / "main.css").is_file():
        return base
    raise SystemExit(f"insiderlawyers-com root not found (expected {base})")


ROOT = site_root()
LA_REL = "los-angeles-car-accident-lawyer/index.html"

CALL_BAR_RE = re.compile(
    r'\s*<section class="call-bar"[\s\S]*?</section>\s*', re.I
)

BODY_PPC_RE = re.compile(r'<body\s+class="home-ppc">', re.I)

TAP_INLINE_FRAGMENT = re.compile(
    r"\.tap-to-call-bar\{[^}]{0,800}?\}", re.I
)

CTA_STRIP = (
    '<section class="content-cta-strip" aria-label="Contact options">\n'
    '  <div class="container">\n'
    '    <p class="content-cta-strip__inner"><a href="/#case-evaluation">Free case review</a>'
    '<span class="content-cta-strip__sep" aria-hidden="true"> · </span>'
    '<a href="tel:844-467-4335" data-callrail-phone="844-467-4335">844-467-4335</a></p>\n'
    "  </div>\n"
    "</section>\n\n"
)

BREADCRUMB_CLS = "breadcrumb breadcrumb--plain"


def should_skip_path(rel: str) -> bool:
    r = rel.replace("\\", "/")
    if r.startswith("_old-site-extract/") or r.startswith("_dev/"):
        return True
    if r.startswith("components/"):
        return True
    return False


def extract_h1_text(page: str) -> str:
    m = re.search(r"<h1\b[^>]*>([\s\S]*?)</h1>", page, re.I)
    if not m:
        return "Page"
    t = re.sub(r"<[^>]+>", " ", m.group(1))
    t = re.sub(r"\s+", " ", t).strip()
    return (t[:100] + "…") if len(t) > 100 else t


def should_skip_breadcrumb(rel: str, page: str) -> bool:
    r = rel.replace("\\", "/")
    if r == "index.html":
        return True
    if "thank-you" in r:
        return True
    if r == LA_REL:
        return True
    if '<main' not in page.lower():
        return True
    if "breadcrumb--plain" in page and 'aria-label="Breadcrumb"' in page:
        return True
    if re.search(
        r'<section class="hero hero-section"[^>]*id="case-evaluation"',
        page,
        re.I,
    ):
        return True
    return False


def breadcrumb_block(page: str) -> str:
    label = html.escape(extract_h1_text(page))
    return (
        f'<nav class="{BREADCRUMB_CLS}" aria-label="Breadcrumb">\n'
        f'  <div class="container"><a href="/">Home</a>'
        f' <span class="breadcrumb__sep">&gt;</span> '
        f'<span class="breadcrumb__current">{label}</span></div>\n'
        "</nav>\n"
    )


def insert_breadcrumb(page: str) -> str:
    if '<main' not in page.lower():
        return page
    low = page.lower()
    pos = low.find("<main")
    if pos == -1:
        return page
    # after <main> or <main ...>
    m = re.search(r"<main\b[^>]*>", page, re.I)
    if not m:
        return page
    ins_at = m.end()
    return page[:ins_at] + "\n" + breadcrumb_block(page) + page[ins_at:]


def process_file(path: Path) -> tuple[bool, list[str]]:
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    notes: list[str] = []
    if path.suffix.lower() != ".html":
        return False, notes
    if should_skip_path(rel):
        return False, notes
    if rel == LA_REL:
        return False, notes

    raw = path.read_text(encoding="utf-8", errors="replace")
    out = raw
    changed = False

    if CALL_BAR_RE.search(out):
        out = CALL_BAR_RE.sub("\n" + CTA_STRIP, out, count=1)
        notes.append("removed call-bar + cta strip")
        changed = True
    if BODY_PPC_RE.search(out):
        out = BODY_PPC_RE.sub("<body>", out, count=1)
        notes.append("stripped home-ppc")
        changed = True
    if "tap-to-call-bar{" in out and "<head" in out.lower():
        head_end = re.search(r"</head>", out, re.I)
        if head_end:
            head = out[: head_end.start()]
            rest = out[head_end.start() :]
            new_head, n = TAP_INLINE_FRAGMENT.subn("", head)
            if n:
                out = new_head + rest
                notes.append(f"removed {n} inline tap-to-call override(s)")
                changed = True

    if not should_skip_breadcrumb(rel, out):
        out2 = insert_breadcrumb(out)
        if out2 != out:
            out = out2
            notes.append("breadcrumb")
            changed = True

    if changed:
        path.write_text(out, encoding="utf-8")
    return changed, notes


def main() -> None:
    log: list[str] = []
    n = 0
    for path in sorted(ROOT.rglob("*.html")):
        ch, notes = process_file(path)
        if ch:
            n += 1
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            log.append(f"{rel}: " + "; ".join(notes))
    summary = ROOT / "scripts" / "ui_normalization_summary.md"
    body = (
        "# UI normalization — second pass\n\n"
        f"Files modified: **{n}**\n\n## Changes per file\n\n"
        + "\n".join(f"- `{line}`" for line in log[:200])
    )
    if len(log) > 200:
        body += f"\n\n… and {len(log) - 200} more.\n"
    summary.write_text(body, encoding="utf-8")
    print("Modified", n, "files; wrote", summary)


if __name__ == "__main__":
    main()
    sys.exit(0)
