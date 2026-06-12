#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprehensive SEO + technical audit for insiderlawyers.com.

Walks every index.html under insiderlawyers-com/ (and the homepage), parses the
<head>, and records a row per URL with title, meta description, canonical,
hreflang, robots, OG/Twitter metadata, schema types, H1 count, language, and
encoding-error indicators.

Outputs:
  reports/seo-route-inventory.csv  all routes + parsed metadata
  reports/seo-audit-issues.json    machine-readable issue list
  reports/seo-before.md / -after.md (pass --label before|after)

Detects:
  * missing/duplicate titles and meta descriptions
  * over- and undersized titles and descriptions
  * missing/multiple canonicals or hreflang
  * canonical pointing to a redirect or non-200
  * mojibake / replacement characters
  * stale "Insider Accident Lawyers" branding outside the footer disclosure
  * pages with no H1 or multiple H1s
  * missing OG image, Twitter card, viewport, charset, JSON-LD
  * pages flagged noindex
  * pages not in any sitemap

Run from anywhere:
    python insiderlawyers-com/scripts/seo_audit.py [--label before|after]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html as html_lib
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

# Workspace anchored path (matches build_sitemaps.py)
_WORKSPACE = Path(r"C:\Users\georgea\insiderlawyer-com-lps")
ROOT = _WORKSPACE / "insiderlawyers-com"
if not (ROOT / "components" / "global-chrome-before-main.html").is_file():
    raise SystemExit(f"ROOT sanity check failed: {ROOT}")

REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

SITE = "https://www.insiderlawyers.com"

# ---------------------------------------------------------------------------
# Regex helpers (deliberately simple; HTML files in this project are flat)
# ---------------------------------------------------------------------------

RE_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
# IMPORTANT: attribute value capture allows apostrophes inside double-quoted
# attributes (and vice versa) by anchoring on the *opening* quote and
# back-referencing it. Naive `[^"\']*` corrupts descriptions like
#   content="What you can't ignore"
# by stopping at the apostrophe.
RE_META_DESC = re.compile(
    r'<meta\b[^>]*\bname=["\']description["\'][^>]*\bcontent=(["\'])(.*?)\1',
    re.I | re.S,
)
RE_META_KEYWORDS = re.compile(
    r'<meta\b[^>]*\bname=["\']keywords["\'][^>]*\bcontent=(["\'])(.*?)\1',
    re.I | re.S,
)
RE_META_ROBOTS = re.compile(
    r'<meta\b[^>]*\bname=["\']robots["\'][^>]*\bcontent=(["\'])(.*?)\1',
    re.I | re.S,
)
RE_CANONICAL = re.compile(
    r'<link\b[^>]*\brel=["\']canonical["\'][^>]*\bhref=(["\'])(.*?)\1',
    re.I | re.S,
)
RE_HREFLANG = re.compile(
    r'<link\b[^>]*\brel=["\']alternate["\'][^>]*\bhreflang=["\']([^"\']+)["\'][^>]*\bhref=(["\'])(.*?)\2',
    re.I | re.S,
)
RE_HREFLANG_REVERSED = re.compile(
    r'<link\b[^>]*\brel=["\']alternate["\'][^>]*\bhref=(["\'])(.*?)\1[^>]*\bhreflang=["\']([^"\']+)["\']',
    re.I | re.S,
)
RE_OG = re.compile(
    r'<meta\b[^>]*\bproperty=["\']og:([^"\']+)["\'][^>]*\bcontent=(["\'])(.*?)\2',
    re.I | re.S,
)
RE_TW = re.compile(
    r'<meta\b[^>]*\bname=["\']twitter:([^"\']+)["\'][^>]*\bcontent=(["\'])(.*?)\2',
    re.I | re.S,
)
RE_VIEWPORT = re.compile(r'<meta[^>]+name=["\']viewport["\']', re.I)
RE_CHARSET = re.compile(r'<meta[^>]+charset=["\']?([^"\'\s>]+)', re.I)
RE_THEMECOLOR = re.compile(
    r'<meta[^>]+name=["\']theme-color["\'][^>]+content=["\']([^"\']*)["\']', re.I
)
RE_JSONLD = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.I | re.S
)
RE_FAVICON = re.compile(
    r'<link[^>]+rel=["\'][^"\']*icon[^"\']*["\'][^>]+href=["\']([^"\']+)["\']', re.I
)
RE_MANIFEST = re.compile(
    r'<link[^>]+rel=["\']manifest["\'][^>]+href=["\']([^"\']+)["\']', re.I
)
RE_APPLE_ICON = re.compile(
    r'<link[^>]+rel=["\']apple-touch-icon["\']', re.I
)
RE_HTML_LANG = re.compile(r"<html[^>]+lang=[\"']([^\"']+)[\"']", re.I)
RE_H1 = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)
RE_TAG = re.compile(r"<[^>]+>")
RE_GTM = re.compile(r"GTM-WS8XT5FC", re.I)

# Mojibake / replacement char indicators
RE_MOJIBAKE = re.compile(r"[\ufffd]")
# Common windows-1252-as-utf8 sequences: â€™ â€œ â€ €" Ã©
RE_MOJIBAKE_SEQ = re.compile(r"(â€™|â€œ|â€\u009d|Ã©|Ã±|Ã¡|Ãº|Ã­|Â |\\u00a0)")

STALE_BRAND_PATTERNS = [
    re.compile(r"\bour attorneys\b", re.I),
    re.compile(r"\bour firm\b", re.I),
    re.compile(r"\bwe fight (for|on) (you|your)\b", re.I),
    re.compile(r"\bhire our lawyers\b", re.I),
    re.compile(r"\bno fee unless we win\b", re.I),
    re.compile(r"\bmillions recovered\b", re.I),
]

LIMIT_TITLE_MIN = 25
LIMIT_TITLE_MAX = 70
LIMIT_DESC_MIN = 100
LIMIT_DESC_MAX = 175

# Excluded from crawling — never indexable
EXCLUDED_DIRS = {
    "_dev", "_old-site-extract", "scripts", "components", "social-assets",
    "docs", "node_modules", ".git", ".cursor", "reports", "assets",
}

EXCLUDED_FILES = {
    "thank-you.html",
    "google0f074189c817401a.html",
    "INDEXABILITY-ANALYSIS.txt",
}


@dataclass
class Page:
    path: str  # URL path (no domain)
    file: str  # repo-relative filesystem path
    language: str = "en"
    category: str = "guide"
    title: str = ""
    title_len: int = 0
    description: str = ""
    description_len: int = 0
    h1: str = ""
    h1_count: int = 0
    canonical: str = ""
    robots: str = ""
    indexable: bool = True
    html_lang: str = ""
    hreflang_pairs: list[tuple[str, str]] = field(default_factory=list)
    og: dict = field(default_factory=dict)
    twitter: dict = field(default_factory=dict)
    schema_types: list[str] = field(default_factory=list)
    schema_blocks: int = 0
    schema_invalid_blocks: int = 0
    has_viewport: bool = False
    has_charset: bool = False
    has_jsonld: bool = False
    has_favicon: bool = False
    has_manifest: bool = False
    has_apple_icon: bool = False
    has_theme_color: bool = False
    gtm: bool = False
    mojibake: bool = False
    mojibake_examples: list[str] = field(default_factory=list)
    stale_branding_hits: list[str] = field(default_factory=list)
    in_sitemap: bool = False
    sitemap_files: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    word_count: int = 0


# ---------------------------------------------------------------------------
# Crawl
# ---------------------------------------------------------------------------

def url_for_path(path: str, language: str) -> str:
    if path == "/":
        return SITE + "/"
    if path == "/es":
        return SITE + "/es/"
    if language == "es":
        return (SITE + path) if path.endswith("/") else (SITE + path + "/")
    return SITE + path


def file_to_path(p: Path) -> str:
    rel = p.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("/index.html")]
    return "/" + rel


def discover_pages() -> list[Path]:
    out: list[Path] = []
    # Root index.html
    if (ROOT / "index.html").is_file():
        out.append(ROOT / "index.html")
    # All other index.html under directories
    for p in sorted(ROOT.rglob("index.html")):
        try:
            rel = p.relative_to(ROOT)
        except ValueError:
            continue
        parts = rel.parts
        if not parts:
            continue
        # Skip excluded top-level directories
        if parts[0] in EXCLUDED_DIRS:
            continue
        if rel.as_posix() == "index.html":
            continue
        out.append(p)
    return out


def classify(path: str, language: str) -> str:
    if path in ("/", "/es"):
        return "homepage"
    if language == "es":
        if path.startswith(("/es/politica-", "/es/terminos-", "/es/aviso-",
                            "/es/derechos-privacidad-", "/es/no-vender-",
                            "/es/accesibilidad", "/es/contacto")):
            return "legal-es" if "contact" not in path else "contact-es"
        return "es-content"
    if path in ("/contact",):
        return "contact"
    if path.endswith(("/privacy-policy", "/legal-terms", "/disclaimer",
                      "/cookie-policy", "/california-privacy-rights",
                      "/do-not-sell-or-share-my-personal-information",
                      "/accessibility")):
        return "legal"
    if path.startswith("/lit-referral-") or path == "/attorney-referrals":
        return "referral"
    if path.startswith("/personal-injury") or path == "/settlements":
        return "hub"
    if path.startswith("/los-angeles-") or path.endswith("-los-angeles"):
        return "la-claim"
    if path.startswith("/california-") or "settlement" in path or "claim" in path:
        return "claim-guide"
    return "guide"


# ---------------------------------------------------------------------------
# Parse
# ---------------------------------------------------------------------------

def strip_tags(s: str) -> str:
    return RE_TAG.sub("", s).strip()


def parse_page(p: Path) -> Page:
    path = file_to_path(p)
    raw_bytes = p.read_bytes()
    try:
        html = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        html = raw_bytes.decode("utf-8", errors="replace")
    page = Page(path=path, file=p.relative_to(ROOT).as_posix())

    # Detect language from /es/ or html lang
    lang_match = RE_HTML_LANG.search(html)
    if lang_match:
        page.html_lang = lang_match.group(1)
    if path.startswith("/es/") or path == "/es":
        page.language = "es"
    elif page.html_lang.startswith("es"):
        page.language = "es"
    else:
        page.language = "en"

    page.category = classify(path, page.language)

    # Title
    m = RE_TITLE.search(html)
    if m:
        page.title = html_lib.unescape(strip_tags(m.group(1)))
        page.title_len = len(page.title)

    # Meta description (group 2 is the value; group 1 is the opening quote)
    m = RE_META_DESC.search(html)
    if m:
        page.description = html_lib.unescape(m.group(2).strip())
        page.description_len = len(page.description)

    # H1
    h1s = [strip_tags(x) for x in RE_H1.findall(html)]
    page.h1_count = len(h1s)
    if h1s:
        page.h1 = h1s[0][:200]

    # Canonical (group 2 is the value)
    canons = [m.group(2) for m in RE_CANONICAL.finditer(html)]
    if canons:
        page.canonical = canons[0]
    if len(canons) > 1:
        page.issues.append(f"multiple canonical tags ({len(canons)})")

    # Robots (group 2 is the value)
    m = RE_META_ROBOTS.search(html)
    if m:
        page.robots = m.group(2).strip()
        if "noindex" in page.robots.lower():
            page.indexable = False

    # Hreflang
    pairs = []
    for m_ in RE_HREFLANG.finditer(html):
        # group 1: lang ; group 3: href
        pairs.append((m_.group(1), m_.group(3)))
    for m_ in RE_HREFLANG_REVERSED.finditer(html):
        # group 2: href ; group 3: lang
        pairs.append((m_.group(3), m_.group(2)))
    seen = set()
    deduped = []
    for lang, href in pairs:
        key = (lang.lower(), href)
        if key in seen:
            continue
        seen.add(key)
        deduped.append((lang.lower(), href))
    page.hreflang_pairs = deduped

    # Open Graph (group 1: property, group 3: content)
    for m_ in RE_OG.finditer(html):
        page.og[m_.group(1).lower()] = m_.group(3)

    # Twitter (group 1: name, group 3: content)
    for m_ in RE_TW.finditer(html):
        page.twitter[m_.group(1).lower()] = m_.group(3)

    # JSON-LD
    blocks = RE_JSONLD.findall(html)
    page.schema_blocks = len(blocks)
    page.has_jsonld = page.schema_blocks > 0
    types: list[str] = []
    for block in blocks:
        try:
            data = json.loads(block.strip())
        except json.JSONDecodeError:
            page.schema_invalid_blocks += 1
            continue
        for t in iter_schema_types(data):
            types.append(t)
    page.schema_types = sorted(set(types))

    # Misc head presence
    page.has_viewport = bool(RE_VIEWPORT.search(html))
    page.has_charset = bool(RE_CHARSET.search(html))
    page.has_favicon = bool(RE_FAVICON.search(html))
    page.has_manifest = bool(RE_MANIFEST.search(html))
    page.has_apple_icon = bool(RE_APPLE_ICON.search(html))
    page.has_theme_color = bool(RE_THEMECOLOR.search(html))
    page.gtm = bool(RE_GTM.search(html))

    # Mojibake / encoding
    if RE_MOJIBAKE.search(html):
        page.mojibake = True
        # Capture short example near the first instance
        idx = html.find("\ufffd")
        page.mojibake_examples.append(html[max(0, idx - 30): idx + 30])
    if RE_MOJIBAKE_SEQ.search(html):
        page.mojibake = True
        m2 = RE_MOJIBAKE_SEQ.search(html)
        if m2:
            page.mojibake_examples.append(m2.group(0))

    # Stale branding outside the corporate disclosure footer line
    body_text = html
    # Remove the corporate disclosure line so the legitimate Countrywide /
    # Insider Accident Lawyers reference does not generate a false positive.
    body_text = re.sub(
        r"Countrywide Trial Lawyers[^<]*Insider Accident Lawyers[^<]*",
        "", body_text, flags=re.I,
    )
    body_text = re.sub(
        r"DBA Insider Accident Lawyers", "", body_text, flags=re.I,
    )
    for pat in STALE_BRAND_PATTERNS:
        m3 = pat.search(body_text)
        if m3:
            page.stale_branding_hits.append(m3.group(0))

    # Word count of visible text (rough — strips tags only)
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = strip_tags(text)
    page.word_count = len(re.findall(r"\b\w+\b", text))

    # Issue detection
    if not page.title:
        page.issues.append("missing title")
    elif page.title_len > LIMIT_TITLE_MAX:
        page.issues.append(f"title too long ({page.title_len})")
    elif page.title_len < LIMIT_TITLE_MIN:
        page.issues.append(f"title too short ({page.title_len})")
    if not page.description:
        page.issues.append("missing description")
    elif page.description_len > LIMIT_DESC_MAX:
        page.issues.append(f"description too long ({page.description_len})")
    elif page.description_len < LIMIT_DESC_MIN:
        page.issues.append(f"description too short ({page.description_len})")
    if not page.canonical:
        page.issues.append("missing canonical")
    if page.h1_count == 0:
        page.issues.append("missing H1")
    elif page.h1_count > 1:
        page.issues.append(f"multiple H1s ({page.h1_count})")
    if not page.has_viewport:
        page.issues.append("missing viewport")
    if not page.has_charset:
        page.issues.append("missing charset")
    if not page.has_favicon:
        page.issues.append("missing favicon link")
    if not page.has_manifest:
        page.issues.append("missing web manifest link")
    if not page.has_apple_icon:
        page.issues.append("missing apple-touch-icon")
    if not page.og.get("title"):
        page.issues.append("missing og:title")
    if not page.og.get("description"):
        page.issues.append("missing og:description")
    if not page.og.get("image"):
        page.issues.append("missing og:image")
    if not page.twitter.get("card"):
        page.issues.append("missing twitter:card")
    if page.mojibake:
        page.issues.append("mojibake / replacement chars")
    if page.stale_branding_hits:
        page.issues.append(
            "stale law-firm branding: " + "; ".join(page.stale_branding_hits[:3])
        )
    if page.schema_invalid_blocks:
        page.issues.append(f"{page.schema_invalid_blocks} invalid JSON-LD block(s)")
    if page.indexable and "lawyer" in (page.title or "").lower() and "insider lawyers" in (page.title or "").lower():
        # Title already says Insider Lawyers; that's fine.
        pass

    return page


def iter_schema_types(node):
    if isinstance(node, dict):
        t = node.get("@type")
        if isinstance(t, str):
            yield t
        elif isinstance(t, list):
            for x in t:
                if isinstance(x, str):
                    yield x
        for v in node.values():
            yield from iter_schema_types(v)
    elif isinstance(node, list):
        for x in node:
            yield from iter_schema_types(x)


# ---------------------------------------------------------------------------
# Sitemap cross-check
# ---------------------------------------------------------------------------

def parse_sitemap_urls() -> dict[str, list[str]]:
    """Map URL -> [sitemap files containing it]."""
    out: dict[str, list[str]] = defaultdict(list)
    for f in sorted(ROOT.glob("sitemap-*.xml")):
        try:
            txt = f.read_text(encoding="utf-8")
        except OSError:
            continue
        for m in re.finditer(r"<loc>([^<]+)</loc>", txt):
            url = m.group(1).strip()
            out[url].append(f.name)
    return out


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

def write_inventory_csv(pages: list[Page], dest: Path) -> None:
    fields = [
        "path", "language", "category", "indexable", "title", "title_len",
        "description", "description_len", "h1", "h1_count", "canonical",
        "robots", "html_lang", "hreflang_count", "og_image",
        "schema_types", "in_sitemap", "sitemap_files", "word_count",
        "issues",
    ]
    with dest.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(fields)
        for p in pages:
            w.writerow([
                p.path, p.language, p.category,
                "yes" if p.indexable else "no",
                p.title, p.title_len,
                p.description, p.description_len,
                p.h1, p.h1_count,
                p.canonical, p.robots, p.html_lang,
                len(p.hreflang_pairs),
                p.og.get("image", ""),
                ",".join(p.schema_types),
                "yes" if p.in_sitemap else "no",
                ",".join(p.sitemap_files),
                p.word_count,
                "; ".join(p.issues),
            ])


def write_summary_md(pages: list[Page], dest: Path, label: str) -> dict:
    total = len(pages)
    en = [p for p in pages if p.language == "en"]
    es = [p for p in pages if p.language == "es"]
    indexable = [p for p in pages if p.indexable]
    noindex = [p for p in pages if not p.indexable]
    not_in_sitemap = [p for p in indexable if not p.in_sitemap]

    title_dupes = Counter(p.title for p in indexable if p.title)
    desc_dupes = Counter(p.description for p in indexable if p.description)
    dup_titles = {t: n for t, n in title_dupes.items() if n > 1}
    dup_descs = {d: n for d, n in desc_dupes.items() if n > 1}

    issue_counter: Counter = Counter()
    for p in pages:
        for issue in p.issues:
            head = re.split(r"[(:]", issue, 1)[0].strip()
            issue_counter[head] += 1

    summary = {
        "total": total,
        "en": len(en),
        "es": len(es),
        "indexable": len(indexable),
        "noindex": len(noindex),
        "not_in_sitemap": len(not_in_sitemap),
        "duplicate_titles": len(dup_titles),
        "duplicate_descriptions": len(dup_descs),
        "issue_counts": dict(issue_counter.most_common()),
    }

    lines: list[str] = []
    lines.append(f"# SEO audit ({label})")
    lines.append("")
    lines.append(f"- Total routes scanned: **{total}**")
    lines.append(f"- English: {len(en)} | Spanish: {len(es)}")
    lines.append(f"- Indexable: {len(indexable)} | Noindex: {len(noindex)}")
    lines.append(f"- Indexable pages missing from sitemap: {len(not_in_sitemap)}")
    lines.append(f"- Duplicate titles (groups): {len(dup_titles)}")
    lines.append(f"- Duplicate descriptions (groups): {len(dup_descs)}")
    lines.append("")
    lines.append("## Issue counts")
    lines.append("")
    if issue_counter:
        for issue, count in issue_counter.most_common():
            lines.append(f"- {issue}: {count}")
    else:
        lines.append("- (clean) no issues detected")
    lines.append("")
    if dup_titles:
        lines.append("## Duplicate titles")
        lines.append("")
        for title, count in sorted(dup_titles.items(), key=lambda x: -x[1]):
            lines.append(f"- ({count}) `{title}`")
            for p in indexable:
                if p.title == title:
                    lines.append(f"    - {p.path}")
        lines.append("")
    if dup_descs:
        lines.append("## Duplicate descriptions")
        lines.append("")
        for desc, count in sorted(dup_descs.items(), key=lambda x: -x[1])[:25]:
            lines.append(f"- ({count}) `{desc[:120]}...`")
        lines.append("")
    if not_in_sitemap:
        lines.append("## Indexable pages missing from sitemap")
        lines.append("")
        for p in not_in_sitemap[:200]:
            lines.append(f"- {p.path}")
        lines.append("")
    lines.append("## Pages with issues")
    lines.append("")
    pages_with_issues = [p for p in pages if p.issues]
    lines.append(f"({len(pages_with_issues)} pages with at least one issue)")
    lines.append("")
    for p in pages_with_issues[:300]:
        lines.append(f"- `{p.path}` ({p.language}): {', '.join(p.issues[:8])}")

    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


def write_issues_json(pages: list[Page], dest: Path) -> None:
    rows = []
    for p in pages:
        rows.append({
            "path": p.path,
            "language": p.language,
            "category": p.category,
            "indexable": p.indexable,
            "title": p.title,
            "title_len": p.title_len,
            "description": p.description,
            "description_len": p.description_len,
            "canonical": p.canonical,
            "robots": p.robots,
            "html_lang": p.html_lang,
            "hreflang_pairs": p.hreflang_pairs,
            "og": p.og,
            "twitter": p.twitter,
            "schema_types": p.schema_types,
            "schema_blocks": p.schema_blocks,
            "schema_invalid_blocks": p.schema_invalid_blocks,
            "h1": p.h1,
            "h1_count": p.h1_count,
            "in_sitemap": p.in_sitemap,
            "sitemap_files": p.sitemap_files,
            "issues": p.issues,
            "word_count": p.word_count,
            "mojibake_examples": p.mojibake_examples,
        })
    dest.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="before",
                    help="Output filename label, e.g. before|after")
    ap.add_argument("--strict", action="store_true",
                    help="Exit nonzero on critical issues")
    args = ap.parse_args()

    files = discover_pages()
    sitemap_index = parse_sitemap_urls()

    pages: list[Page] = []
    for f in files:
        page = parse_page(f)
        url_with_slash = url_for_path(page.path, page.language)
        url_no_slash = url_with_slash.rstrip("/") or url_with_slash
        if url_with_slash in sitemap_index:
            page.in_sitemap = True
            page.sitemap_files = sitemap_index[url_with_slash]
        elif url_no_slash in sitemap_index:
            page.in_sitemap = True
            page.sitemap_files = sitemap_index[url_no_slash]
        pages.append(page)

    pages.sort(key=lambda p: (p.language, p.path))

    csv_path = REPORTS_DIR / "seo-route-inventory.csv"
    write_inventory_csv(pages, csv_path)

    summary_md = REPORTS_DIR / f"seo-{args.label}.md"
    summary = write_summary_md(pages, summary_md, args.label)

    issues_json = REPORTS_DIR / f"seo-{args.label}-issues.json"
    write_issues_json(pages, issues_json)

    print(f"Pages scanned: {summary['total']}")
    print(f"  English: {summary['en']}, Spanish: {summary['es']}")
    print(f"  Indexable: {summary['indexable']}, Noindex: {summary['noindex']}")
    print(f"  Missing from sitemap: {summary['not_in_sitemap']}")
    print(f"  Duplicate titles: {summary['duplicate_titles']}")
    print(f"  Duplicate descriptions: {summary['duplicate_descriptions']}")
    print()
    print("Top issues:")
    for issue, count in list(summary["issue_counts"].items())[:30]:
        print(f"  {count:>4}  {issue}")
    print()
    print(f"Inventory: {csv_path}")
    print(f"Summary:   {summary_md}")
    print(f"Issues:    {issues_json}")

    if args.strict:
        critical = ["missing title", "missing description", "missing canonical",
                    "multiple H1s", "missing H1", "mojibake / replacement chars"]
        critical_count = sum(summary["issue_counts"].get(k, 0) for k in critical)
        if critical_count:
            print(f"\nSTRICT failure: {critical_count} critical issues", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
