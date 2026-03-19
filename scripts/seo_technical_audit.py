#!/usr/bin/env python3
"""One-off technical SEO audit for static HTML. Outputs JSON + markdown hints."""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.insiderlawyers.com"
SKIP_DIRS = {"_old-site-extract", "_dev", "node_modules", ".git", "social-assets", "docs"}

# Vercel cleanUrls: directory index.html maps to /slug and /slug/
RE_CANONICAL = re.compile(
    r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']',
    re.I,
)
RE_CANONICAL_ALT = re.compile(
    r'<link[^>]+href=["\']([^"\']+)["\'][^>]*rel=["\']canonical["\']',
    re.I,
)
RE_TITLE = re.compile(r"<title[^>]*>([^<]*)</title>", re.I | re.S)
RE_META_DESC = re.compile(
    r'<meta[^>]+name=["\']description["\'][^>]*content=["\']([^"\']*)["\']',
    re.I,
)
RE_META_DESC_ALT = re.compile(
    r'<meta[^>]+content=["\']([^"\']*)["\'][^>]*name=["\']description["\']',
    re.I,
)
RE_NOINDEX = re.compile(
    r'<meta[^>]+name=["\']robots["\'][^>]*content=["\'][^"\']*noindex',
    re.I,
)
RE_NOINDEX_ALT = re.compile(
    r'content=["\'][^"\']*noindex[^"\']*["\'][^>]*name=["\']robots["\']',
    re.I,
)
RE_H1 = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)
RE_HREF = re.compile(r'href=["\']([^"\']+)["\']', re.I)
STRIP_TAGS = re.compile(r"<[^>]+>")


def path_to_url_path(rel: Path) -> str:
    """Public URL path (no domain), extensionless for directory indexes."""
    parts = rel.parts
    if parts[-1].lower() == "index.html":
        if len(parts) == 1:
            return "/"
        return "/" + "/".join(parts[:-1]).replace("\\", "/") + "/"
    name = parts[-1]
    return "/" + "/".join(parts).replace("\\", "/")


def normalize_internal(href: str, from_path: str) -> str | None:
    href = href.strip()
    if not href or href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
        return None
    if href.startswith("javascript:"):
        return None
    if "insideraccidentlawyers.com" in href or "insiderlawyers.com" in href:
        if "insiderlawyers.com" not in href:
            return None
        href = href.split("insiderlawyers.com", 1)[-1] or "/"
    if href.startswith("http://") or href.startswith("https://"):
        return None
    if not href.startswith("/"):
        # relative — resolve from page directory
        base = from_path.rstrip("/")
        if base.endswith(".html"):
            base = str(Path(base).parent).replace("\\", "/")
        if not base.startswith("/"):
            base = "/" + base
        # crude join
        from urllib.parse import urljoin

        resolved = urljoin(BASE + (from_path if from_path.endswith("/") else from_path + "/"), href)
        p = resolved.replace(BASE, "")
        return p.split("#")[0].split("?")[0] or "/"
    return href.split("#")[0].split("?")[0] or "/"


def strip_h1(html: str) -> str:
    t = STRIP_TAGS.sub(" ", html)
    return re.sub(r"\s+", " ", t).strip()


def discover_html_files() -> list[Path]:
    out: list[Path] = []
    for p in ROOT.rglob("*.html"):
        rel = p.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if "components" in rel.parts:
            continue
        out.append(p)
    return sorted(out)


def parse_sitemap_locs() -> set[str]:
    sp = ROOT / "sitemap.xml"
    if not sp.exists():
        return set()
    tree = ET.parse(sp)
    locs = set()
    for loc in tree.iter():
        if loc.tag.endswith("loc") and loc.text:
            u = loc.text.strip()
            if u.startswith(BASE):
                path = u[len(BASE) :].split("#")[0]
                if not path.endswith("/") and path != "" and "/" in path:
                    pass
                locs.add(path.rstrip("/") or "/")
            else:
                locs.add(u)
    # normalize trailing slash for comparison
    norm = set()
    for p in locs:
        p = p.rstrip("/") or "/"
        norm.add(p)
    return norm


def main() -> int:
    files = discover_html_files()
    pages: list[dict] = []
    title_counts: dict[str, list[str]] = defaultdict(list)
    desc_counts: dict[str, list[str]] = defaultdict(list)
    h1_counts: dict[str, list[str]] = defaultdict(list)
    inbound: dict[str, set[str]] = defaultdict(set)
    nav_hrefs: set[str] = set()
    header_path = ROOT / "components" / "standard-header.html"
    if header_path.exists():
        htxt = header_path.read_text(encoding="utf-8", errors="replace")
        for m in RE_HREF.finditer(htxt):
            u = normalize_internal(m.group(1), "/")
            if u is not None:
                nav_hrefs.add(u.rstrip("/") or "/")

    for fp in files:
        rel = fp.relative_to(ROOT)
        url_path = path_to_url_path(rel)
        # normalize key for graph (no trailing slash except root)
        key = url_path.rstrip("/") or "/"
        text = fp.read_text(encoding="utf-8", errors="replace")
        canon_m = RE_CANONICAL.search(text) or RE_CANONICAL_ALT.search(text)
        canonical = canon_m.group(1).strip() if canon_m else None
        title_m = RE_TITLE.search(text)
        title = title_m.group(1).strip() if title_m else ""
        desc_m = RE_META_DESC.search(text) or RE_META_DESC_ALT.search(text)
        desc = desc_m.group(1).strip() if desc_m else ""
        noindex = bool(RE_NOINDEX.search(text) or RE_NOINDEX_ALT.search(text))
        h1s = [strip_h1(m.group(1)) for m in RE_H1.finditer(text)]
        h1 = h1s[0] if h1s else ""

        for m in RE_HREF.finditer(text):
            u = normalize_internal(m.group(1), url_path)
            if u is None:
                continue
            nk = u.rstrip("/") or "/"
            inbound[nk].add(key)

        pages.append(
            {
                "file": str(rel).replace("\\", "/"),
                "url_path": url_path,
                "key": key,
                "canonical": canonical,
                "title": title,
                "meta_description": desc,
                "h1": h1[:200],
                "h1_count": len(h1s),
                "noindex": noindex,
            }
        )
        if title:
            title_counts[title].append(key)
        if desc:
            desc_counts[desc].append(key)
        if h1:
            h1_counts[h1].append(key)

    keys = {p["key"] for p in pages}
    orphans = []
    for p in pages:
        k = p["key"]
        if k == "/":
            continue
        inc = inbound.get(k, set()) - {k}
        if not inc:
            orphans.append(k)
        elif not (inc & (nav_hrefs | {"/"})):
            # not linked from home or nav — soft orphan
            pass

    # orphans: no inbound from any page
    true_orphans = [p["key"] for p in pages if p["key"] != "/" and not inbound.get(p["key"], set())]

    sitemap_paths = parse_sitemap_locs()
    page_keys_norm = set()
    for p in pages:
        k = p["key"]
        page_keys_norm.add(k)
        if k != "/" and not k.endswith("/"):
            page_keys_norm.add(k + "/")

    missing_in_sitemap = []
    for p in pages:
        k = p["key"]
        if p["file"] == "thank-you.html":
            continue
        sk = k.rstrip("/") or "/"
        if sk not in sitemap_paths and (sk + "/") not in sitemap_paths and k not in sitemap_paths:
            # sitemap uses no trailing slash
            alt = k.rstrip("/")
            if alt == "":
                alt = "/"
            if alt not in sitemap_paths:
                missing_in_sitemap.append(k)

    extra_sitemap = []
    for sp in sitemap_paths:
        if sp == "/":
            continue
        found = False
        for p in pages:
            pk = p["key"].rstrip("/")
            sk = sp.rstrip("/")
            if pk == sk or p["url_path"].rstrip("/") == sk:
                found = True
                break
        if not found:
            extra_sitemap.append(sp)

    bad_canonical = []
    for p in pages:
        c = p["canonical"]
        if not c:
            bad_canonical.append((p["key"], "missing"))
            continue
        if not c.startswith(BASE):
            bad_canonical.append((p["key"], f"non-www or wrong host: {c[:60]}"))
            continue
        tail = c[len(BASE) :].split("?")[0].rstrip("/") or "/"
        my = p["key"].rstrip("/") or "/"
        if tail != my and tail + "/" != my + "/" and my != tail:
            # allow trailing slash mismatch
            if tail.rstrip("/") != my.rstrip("/"):
                bad_canonical.append((p["key"], f"mismatch page {my} vs canon {tail}"))

    report = {
        "counts": {
            "html_pages": len(pages),
            "sitemap_urls": len(sitemap_paths),
        },
        "true_orphans_no_inbound": true_orphans,
        "missing_title": [p["key"] for p in pages if not p["title"]],
        "missing_meta_description": [p["key"] for p in pages if not p["meta_description"]],
        "missing_h1": [p["key"] for p in pages if p["h1_count"] == 0],
        "multiple_h1": [p["key"] for p in pages if p["h1_count"] > 1],
        "noindex_pages": [p["key"] for p in pages if p["noindex"]],
        "duplicate_titles": {t: v for t, v in title_counts.items() if len(v) > 1},
        "duplicate_meta_descriptions": {d[:80]: v for d, v in desc_counts.items() if len(v) > 1},
        "missing_in_sitemap": missing_in_sitemap,
        "sitemap_without_html": extra_sitemap,
        "canonical_issues": bad_canonical,
    }

    out_json = ROOT / "docs" / "seo-audit-data.json"
    out_json.parent.mkdir(exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in report if k != "duplicate_meta_descriptions"}, indent=2))
    dup_md = len({k for k, v in report["duplicate_titles"].items()})
    print(f"\nDuplicate title groups: {dup_md}", file=sys.stderr)
    print(f"Duplicate meta desc groups: {len(report['duplicate_meta_descriptions'])}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
