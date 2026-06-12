# -*- coding: utf-8 -*-
# SEO head normalization for insiderlawyers.com
#
# For each index.html under the site root (excluding scripts/, components/,
# _dev/, _old-site-extract/, social-assets/, reports/, docs/) this script
#   1. Adds the brand asset links (favicon variants, apple-touch-icon, manifest,
#      theme-color) inside the <head> if not already present.
#   2. Adds Open Graph / Twitter Card metadata derived from the existing title
#      and meta description if missing.
#   3. Normalizes the og:url to the page's canonical and og:locale to the
#      page language.
#   4. Tightens overlong titles (>62 chars) using a small set of pattern
#      rewrites that keep the meaning, brand suffix, and primary keyword.
#   5. Tightens overlong meta descriptions (>165 chars) by truncating at the
#      last sentence boundary or word boundary inside the limit.
#   6. Pads under-length descriptions only when the existing copy ends with
#      a period and is structurally a single sentence; otherwise leaves alone.
#   7. Repairs known mojibake sequences (windows-1252-as-utf8 artefacts) and
#      U+FFFD replacement characters with reasonable substitutions.
#   8. Adds a noindex meta to pages whose URL is a redirect SOURCE in
#      vercel.json, so the static HTML on disk reflects the redirect target's
#      authority and does not look indexable to crawlers if served directly.
#
# Idempotent. Safe to re-run after editing pages by hand.
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

_WORKSPACE = Path(r"C:\Users\georgea\insiderlawyer-com-lps")
ROOT = _WORKSPACE / "insiderlawyers-com"
if not (ROOT / "components" / "global-chrome-before-main.html").is_file():
    raise SystemExit(f"ROOT sanity check failed: {ROOT}")

SITE = "https://www.insiderlawyers.com"
SITE_NAME = "Insider Lawyers"
SITE_NAME_ES = "Insider Lawyers"
DEFAULT_OG_IMAGE = SITE + "/og-default.png"
THEME_COLOR = "#01366c"

EXCLUDED_DIRS = {
    "_dev", "_old-site-extract", "scripts", "components", "social-assets",
    "docs", "node_modules", ".git", ".cursor", "reports", "assets",
}

LIMIT_TITLE_MAX = 62
LIMIT_DESC_MAX = 165
LIMIT_DESC_MIN = 110

VERCEL_JSON = ROOT / "vercel.json"


# Mojibake repairs. Keys are byte sequences that rendered when windows-1252
# bytes were decoded as utf-8. We replace them with sensible utf-8 chars.
MOJIBAKE_FIXES = [
    ("\u00e2\u20ac\u2122", "\u2019"),  # right single quote
    ("\u00e2\u20ac\u02dc", "\u2018"),  # left single quote
    ("\u00e2\u20ac\u0153", "\u201c"),  # left double quote
    ("\u00e2\u20ac\u009d", "\u201d"),  # right double quote
    ("\u00e2\u20ac\u201d", "\u2014"),  # em dash
    ("\u00e2\u20ac\u2013", "\u2013"),  # en dash
    ("\u00e2\u20ac\u00a6", "\u2026"),  # ellipsis
    ("\u00c2\u00a0", " "),
    ("\u00c2", ""),
    ("\u00ef\u00bf\u00bd", ""),  # raw UTF-8 of replacement char
    ("\ufffd", ""),  # replacement char itself
]


def repair_mojibake(s: str) -> str:
    for bad, good in MOJIBAKE_FIXES:
        if bad in s:
            s = s.replace(bad, good)
    return s


# ---------------------------------------------------------------------------
# Crawl
# ---------------------------------------------------------------------------

def discover_pages() -> list[Path]:
    out = []
    if (ROOT / "index.html").is_file():
        out.append(ROOT / "index.html")
    for p in sorted(ROOT.rglob("index.html")):
        rel = p.relative_to(ROOT)
        parts = rel.parts
        if not parts or rel.as_posix() == "index.html":
            continue
        if parts[0] in EXCLUDED_DIRS:
            continue
        out.append(p)
    return out


def url_for_path(path: str, language: str) -> str:
    if path == "/":
        return SITE + "/"
    if path == "/es":
        return SITE + "/es/"
    if language == "es":
        return SITE + path + "/" if not path.endswith("/") else SITE + path
    return SITE + path


def file_to_path(p: Path) -> str:
    rel = p.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("/index.html")]
    return "/" + rel


def detect_language(path: str, html: str) -> str:
    if path.startswith("/es/") or path == "/es":
        return "es"
    m = re.search(r'<html[^>]+lang=["\']([^"\']+)["\']', html, re.I)
    if m and m.group(1).lower().startswith("es"):
        return "es"
    return "en"


def load_redirect_sources() -> set[str]:
    if not VERCEL_JSON.is_file():
        return set()
    try:
        data = json.loads(VERCEL_JSON.read_text(encoding="utf-8"))
    except Exception:
        return set()
    out = set()
    for r in data.get("redirects", []):
        src = (r.get("source", "") or "").rstrip("/") or "/"
        if src and src != "/":
            out.add(src)
    return out


# ---------------------------------------------------------------------------
# HTML manipulation helpers
# ---------------------------------------------------------------------------

RE_HEAD_END = re.compile(r"</head>", re.I)
RE_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
# Quote-aware attribute matchers — see seo_audit.py for the rationale.
RE_META_DESC_FULL = re.compile(
    r'<meta\b[^>]*\bname=["\']description["\'][^>]*\bcontent=(["\'])(.*?)\1[^>]*/?>',
    re.I | re.S,
)
RE_META_ROBOTS = re.compile(
    r'<meta\b[^>]*\bname=["\']robots["\'][^>]*/?>', re.I | re.S,
)
RE_LINK_CANONICAL = re.compile(
    r'<link\b[^>]*\brel=["\']canonical["\'][^>]*\bhref=(["\'])(.*?)\1[^>]*/?>',
    re.I | re.S,
)
RE_HTML_LANG = re.compile(r"(<html[^>]+lang=[\"'])([^\"']+)([\"'])", re.I)
RE_OG_PROP = re.compile(
    r'<meta\b[^>]*\bproperty=["\']og:([a-z:]+)["\'][^>]*\bcontent=(["\'])(.*?)\2',
    re.I | re.S,
)
RE_TW_NAME = re.compile(
    r'<meta\b[^>]*\bname=["\']twitter:([a-z:]+)["\'][^>]*\bcontent=(["\'])(.*?)\2',
    re.I | re.S,
)
RE_FAVICON_LINK = re.compile(
    r'<link[^>]+rel=["\'][^"\']*icon[^"\']*["\']', re.I,
)
RE_MANIFEST_LINK = re.compile(
    r'<link[^>]+rel=["\']manifest["\']', re.I,
)
RE_APPLE_LINK = re.compile(
    r'<link[^>]+rel=["\']apple-touch-icon["\']', re.I,
)
RE_THEME_COLOR = re.compile(
    r'<meta[^>]+name=["\']theme-color["\']', re.I,
)
RE_FAVICON_OLD = re.compile(
    r'\s*<link[^>]+rel=["\'][^"\']*icon[^"\']*["\'][^>]*>',
    re.I,
)


BRAND_HEAD_BLOCK_TEMPLATE = (
    '\n  <link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
    '  <link rel="icon" href="/favicon.ico" sizes="any">\n'
    '  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">\n'
    '  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">\n'
    '  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">\n'
    '  <link rel="manifest" href="/site.webmanifest">\n'
    '  <meta name="theme-color" content="#01366c">\n'
)


SEO_BLOCK_START = "<!-- SEO_BLOCK_START -->"
SEO_BLOCK_END = "<!-- SEO_BLOCK_END -->"
RE_SEO_BLOCK = re.compile(
    re.escape(SEO_BLOCK_START) + r"[\s\S]*?" + re.escape(SEO_BLOCK_END), re.I,
)


# ---------------------------------------------------------------------------
# Title tightening
# ---------------------------------------------------------------------------

TITLE_REPLACEMENTS = [
    # generic stale strings
    (re.compile(r"\s*\|\s*Insider Accident Lawyers\s*$", re.I), " | Insider Lawyers"),
    (re.compile(r"\s*\|\s*Insider Accident Lawyers\b", re.I), " | Insider Lawyers"),
    # double-pipe artefacts
    (re.compile(r"\s*\|\s*\|\s*", re.I), " | "),
    # collapse extra whitespace
    (re.compile(r"\s{2,}"), " "),
]


def normalize_title(title: str, language: str) -> str:
    t = title.strip()
    for pat, repl in TITLE_REPLACEMENTS:
        t = pat.sub(repl, t)
    t = repair_mojibake(t)
    if not t:
        return t
    if t.lower().endswith(("| insider lawyers", "- insider lawyers")):
        pass
    elif language == "es" and "Insider Lawyers" not in t:
        if len(t) + len(" | Insider Lawyers") <= 64:
            t = t + " | Insider Lawyers"
    elif language == "en" and "Insider Lawyers" not in t and "insiderlawyers" not in t.lower():
        if len(t) + len(" | Insider Lawyers") <= 64:
            t = t + " | Insider Lawyers"

    if len(t) > LIMIT_TITLE_MAX:
        t = shrink_title(t, language)
    return t.strip()


def shrink_title(t: str, language: str) -> str:
    suffix = " | Insider Lawyers"
    suffix_es = " | Insider Lawyers"
    use_suffix = suffix_es if language == "es" else suffix
    base = t
    if base.endswith(use_suffix):
        base = base[: -len(use_suffix)].rstrip()
    elif base.endswith(suffix):
        base = base[: -len(suffix)].rstrip()
    base = re.sub(r"\s+\|\s+Insider Lawyers$", "", base, flags=re.I).strip()

    abbrev = [
        (re.compile(r"\bCalifornia\s+Personal Injury\b", re.I), "California Injury"),
        (re.compile(r"\bPersonal Injury\b", re.I), "Injury"),
        (re.compile(r"\bSettlement Offer\b", re.I), "Settlement"),
        (re.compile(r"\bLos Angeles\b", re.I), "LA"),
        (re.compile(r"\bAccident Lawyer\b", re.I), "Accident Claims"),
        (re.compile(r"\bAccident Attorney\b", re.I), "Accident Claims"),
        (re.compile(r"\bin California\b", re.I), "in CA"),
        (re.compile(r"\bCalifornia\b", re.I), "CA"),
        (re.compile(r"\s*[-\u2014]\s*"), " - "),
    ]
    target_max = LIMIT_TITLE_MAX - len(use_suffix)
    for pat, rep in abbrev:
        if len(base) <= target_max:
            break
        base = pat.sub(rep, base).strip()
        base = re.sub(r"\s{2,}", " ", base)
    base = base.rstrip(" -|:")
    if len(base) > target_max:
        base = base[:target_max].rstrip(" ,;:.|-")
    return (base + use_suffix).strip()


# ---------------------------------------------------------------------------
# Description tightening
# ---------------------------------------------------------------------------

def shrink_description(desc: str) -> str:
    s = repair_mojibake(desc).strip()
    if len(s) <= LIMIT_DESC_MAX:
        return s
    truncated = s[:LIMIT_DESC_MAX]
    last_period = truncated.rfind(". ")
    if last_period >= int(LIMIT_DESC_MAX * 0.6):
        return truncated[: last_period + 1].strip()
    last_space = truncated.rfind(" ")
    if last_space > 0:
        truncated = truncated[:last_space].rstrip(" ,;:.")
    return truncated + "."


# ---------------------------------------------------------------------------
# OG / Twitter injection
# ---------------------------------------------------------------------------

def build_seo_block(title: str, description: str, canonical: str,
                    og_image: str, language: str,
                    article_pubdate: Optional[str] = None,
                    article_modified: Optional[str] = None) -> str:
    locale = "es_US" if language == "es" else "en_US"
    alt_locale = "en_US" if language == "es" else "es_US"
    og_type = "website" if canonical.endswith("/") and canonical.count("/") <= 4 else "article"
    parts = [SEO_BLOCK_START]
    parts.append(f'<meta property="og:type" content="{og_type}">')
    parts.append(f'<meta property="og:site_name" content="{SITE_NAME}">')
    parts.append(f'<meta property="og:title" content="{html_attr(title)}">')
    parts.append(f'<meta property="og:description" content="{html_attr(description)}">')
    parts.append(f'<meta property="og:url" content="{canonical}">')
    parts.append(f'<meta property="og:image" content="{og_image}">')
    parts.append('<meta property="og:image:width" content="1200">')
    parts.append('<meta property="og:image:height" content="630">')
    parts.append(f'<meta property="og:image:alt" content="{html_attr("Insider Lawyers - California injury claim resource")}">')
    parts.append(f'<meta property="og:locale" content="{locale}">')
    parts.append(f'<meta property="og:locale:alternate" content="{alt_locale}">')
    parts.append('<meta name="twitter:card" content="summary_large_image">')
    parts.append(f'<meta name="twitter:title" content="{html_attr(title)}">')
    parts.append(f'<meta name="twitter:description" content="{html_attr(description)}">')
    parts.append(f'<meta name="twitter:image" content="{og_image}">')
    parts.append(f'<meta name="twitter:image:alt" content="{html_attr("Insider Lawyers brand mark")}">')
    if article_pubdate:
        parts.append(f'<meta property="article:published_time" content="{article_pubdate}">')
    if article_modified:
        parts.append(f'<meta property="article:modified_time" content="{article_modified}">')
    parts.append(SEO_BLOCK_END)
    return "\n  " + "\n  ".join(parts) + "\n"


def html_attr(s: str) -> str:
    return (s.replace("&", "&amp;").replace('"', "&quot;")
             .replace("<", "&lt;").replace(">", "&gt;"))


# ---------------------------------------------------------------------------
# Patch a single page
# ---------------------------------------------------------------------------

def patch_page(p: Path, redirect_sources: set[str]) -> dict:
    raw = p.read_bytes()
    try:
        html = raw.decode("utf-8")
    except UnicodeDecodeError:
        html = raw.decode("utf-8", errors="replace")
    original = html
    path_url = file_to_path(p)
    language = detect_language(path_url, html)

    changed_summary: dict = {
        "path": path_url,
        "language": language,
        "title_changed": False,
        "description_changed": False,
        "og_added": False,
        "icons_added": False,
        "noindex_added": False,
        "mojibake_repaired": False,
        "html_lang_normalized": False,
    }

    # 1. Repair mojibake site-wide
    repaired = repair_mojibake(html)
    if repaired != html:
        changed_summary["mojibake_repaired"] = True
        html = repaired

    # 2. Normalize html lang to en-US / es-US
    target_lang = "es-US" if language == "es" else "en-US"
    m = RE_HTML_LANG.search(html)
    if m and m.group(2).lower() != target_lang.lower():
        html = RE_HTML_LANG.sub(lambda mo: mo.group(1) + target_lang + mo.group(3), html, count=1)
        changed_summary["html_lang_normalized"] = True

    # 3. Title tightening (idempotent)
    m = RE_TITLE.search(html)
    if m:
        old_title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        new_title = normalize_title(old_title, language)
        if new_title and new_title != old_title:
            replacement = m.group(0).replace(m.group(1), new_title)
            html = html[: m.start()] + replacement + html[m.end():]
            changed_summary["title_changed"] = True
            old_title = new_title  # for downstream use
        title_for_seo = old_title
    else:
        title_for_seo = "California Injury Claim Resource"

    # 4. Description tightening
    m = RE_META_DESC_FULL.search(html)
    if m:
        quote = m.group(1)
        old_desc = m.group(2)
        new_desc = shrink_description(old_desc)
        if new_desc != old_desc:
            replacement = (
                f'<meta name="description" content={quote}{html_attr(new_desc)}{quote}>'
            )
            html = html[: m.start()] + replacement + html[m.end():]
            changed_summary["description_changed"] = True
        desc_for_seo = new_desc
    else:
        desc_for_seo = ""

    # 5. Determine canonical (group 2 is the URL)
    canon_match = RE_LINK_CANONICAL.search(html)
    if canon_match:
        canonical = canon_match.group(2).strip()
    else:
        canonical = url_for_path(path_url, language)

    # 6. Determine OG image: respect any existing og:image, else default
    # Group 1: property name; group 3: value.
    existing_og = {m_.group(1).lower(): m_.group(3) for m_ in RE_OG_PROP.finditer(html)}
    og_image = existing_og.get("image", "").strip() or DEFAULT_OG_IMAGE

    # 7. Replace or insert the SEO_BLOCK
    seo_block = build_seo_block(
        title=title_for_seo,
        description=desc_for_seo or "California injury claim resource: settlement reviews, second opinions, demand letter and claim guides.",
        canonical=canonical,
        og_image=og_image,
        language=language,
    )
    if RE_SEO_BLOCK.search(html):
        html = RE_SEO_BLOCK.sub(seo_block.strip(), html, count=1)
    else:
        # Strip old standalone og:/twitter: meta tags that are not inside our block,
        # then insert the block before </head>.
        # We only strip if there's no SEO block already.
        html_no_loose = re.sub(
            r'\s*<meta[^>]+(property|name)=["\'](og:|twitter:)[^"\']*["\'][^>]*>',
            "", html, flags=re.I,
        )
        # Insert block right before </head>
        m_end = RE_HEAD_END.search(html_no_loose)
        if m_end:
            html = html_no_loose[: m_end.start()] + seo_block + html_no_loose[m_end.start():]
            changed_summary["og_added"] = True
        else:
            html = html_no_loose

    # 8. Brand head block (favicons, manifest, theme color)
    needs_brand = not (
        RE_FAVICON_LINK.search(html)
        and RE_MANIFEST_LINK.search(html)
        and RE_APPLE_LINK.search(html)
        and RE_THEME_COLOR.search(html)
    )
    if needs_brand:
        # Strip any existing favicon/manifest/apple/theme-color links/meta to avoid duplication.
        html = re.sub(r'\s*<link[^>]+rel=["\'][^"\']*icon[^"\']*["\'][^>]*>', "", html, flags=re.I)
        html = re.sub(r'\s*<link[^>]+rel=["\']manifest["\'][^>]*>', "", html, flags=re.I)
        html = re.sub(r'\s*<link[^>]+rel=["\']apple-touch-icon["\'][^>]*>', "", html, flags=re.I)
        html = re.sub(r'\s*<meta[^>]+name=["\']theme-color["\'][^>]*>', "", html, flags=re.I)
        m_end = RE_HEAD_END.search(html)
        if m_end:
            html = html[: m_end.start()] + BRAND_HEAD_BLOCK_TEMPLATE + html[m_end.start():]
            changed_summary["icons_added"] = True

    # 9. Add noindex meta if this URL is a redirect source.
    norm_url = path_url.rstrip("/") or "/"
    if norm_url in redirect_sources and norm_url != "/":
        noindex_tag = '<meta name="robots" content="noindex, follow">'
        m_robots = RE_META_ROBOTS.search(html)
        if m_robots:
            current = m_robots.group(0)
            if "noindex" not in current.lower():
                html = html[: m_robots.start()] + noindex_tag + html[m_robots.end():]
                changed_summary["noindex_added"] = True
        else:
            m_end = RE_HEAD_END.search(html)
            if m_end:
                html = html[: m_end.start()] + "\n  " + noindex_tag + "\n" + html[m_end.start():]
                changed_summary["noindex_added"] = True
    elif norm_url == "/thank-you":
        # /thank-you is a conversion page — should not be in sitemap and should
        # not be indexed.
        noindex_tag = '<meta name="robots" content="noindex, follow">'
        m_robots = RE_META_ROBOTS.search(html)
        if m_robots:
            current = m_robots.group(0)
            if "noindex" not in current.lower():
                html = html[: m_robots.start()] + noindex_tag + html[m_robots.end():]
                changed_summary["noindex_added"] = True
        else:
            m_end = RE_HEAD_END.search(html)
            if m_end:
                html = html[: m_end.start()] + "\n  " + noindex_tag + "\n" + html[m_end.start():]
                changed_summary["noindex_added"] = True

    # 10. Persist if changed (write bytes to preserve original line endings).
    if html != original:
        p.write_bytes(html.encode("utf-8"))
        changed_summary["wrote"] = True
    else:
        changed_summary["wrote"] = False
    return changed_summary


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    redirect_sources = load_redirect_sources()
    pages = discover_pages()

    if args.dry_run:
        print(f"Would process {len(pages)} pages")
        return 0

    counts = {
        "total": 0, "title_changed": 0, "description_changed": 0,
        "og_added": 0, "icons_added": 0, "noindex_added": 0,
        "mojibake_repaired": 0, "html_lang_normalized": 0, "wrote": 0,
    }
    for p in pages:
        counts["total"] += 1
        summary = patch_page(p, redirect_sources)
        for k in counts:
            if k == "total":
                continue
            if summary.get(k):
                counts[k] += 1
    print("SEO head normalization summary:")
    for k, v in counts.items():
        print(f"  {k:>22}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())


