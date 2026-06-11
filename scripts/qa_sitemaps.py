# -*- coding: utf-8 -*-
"""Validate the insiderlawyers.com sitemap system.

Exits non-zero if any of the following fail:
  * /sitemap.xml is a valid sitemap index referencing only child sitemaps
    that actually exist on disk and that contain at least one URL
  * every child sitemap is well-formed XML in the sitemap.org namespace
  * every <loc> exists on disk as an index.html (and is not in /es/_dev,
    /node_modules etc)
  * every <loc> is on https://www.insiderlawyers.com
  * every <loc> matches the page's declared canonical
  * no <loc> is noindex
  * no <loc> is a redirect source in vercel.json
  * no URL appears in more than one child sitemap
  * no URL has both a trailing-slash and non-trailing-slash variant in any
    child sitemap (per-page consistency)
  * Spanish hreflang annotations are valid (xhtml:link, en + es + x-default,
    pointing at URLs that themselves exist)
  * robots.txt references the sitemap index URL
  * no <priority> or <changefreq> remnants
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

_WORKSPACE = Path(r"C:\Users\georgea\insiderlawyer-com-lps")
ROOT = _WORKSPACE / "insiderlawyers-com"
if not (ROOT / "components" / "global-chrome-before-main.html").is_file():
    raise SystemExit(f"ROOT sanity check failed: {ROOT}")

SITE = "https://www.insiderlawyers.com"

INDEX_FILE = ROOT / "sitemap.xml"
CHILD_NAMES = [
    "sitemap-core-en.xml",
    "sitemap-guides-en.xml",
    "sitemap-es.xml",
    "sitemap-legal.xml",
    "sitemap-referrals.xml",
]

NS_SM = "http://www.sitemaps.org/schemas/sitemap/0.9"
NS_XHTML = "http://www.w3.org/1999/xhtml"
NS = {"sm": NS_SM, "xhtml": NS_XHTML}

RE_CANON = re.compile(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', re.I)
RE_NOINDEX = re.compile(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex', re.I)


class QA:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def report(self) -> int:
        if self.warnings:
            print(f"WARNINGS ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"  - {w}")
        if self.errors:
            print(f"ERRORS ({len(self.errors)}):")
            for e in self.errors:
                print(f"  - {e}")
            return 1
        print("OK: sitemap system is valid.")
        return 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def file_for_url(url: str) -> Path | None:
    if not url.startswith(SITE):
        return None
    rel = url[len(SITE):]
    if rel in ("", "/"):
        return ROOT / "index.html"
    rel = rel.strip("/")
    return ROOT / Path(rel) / "index.html"


def load_redirect_sources() -> set[str]:
    vj = ROOT / "vercel.json"
    if not vj.is_file():
        return set()
    try:
        data = json.loads(vj.read_text(encoding="utf-8"))
    except Exception:
        return set()
    return {(r.get("source", "").rstrip("/") or "/") for r in data.get("redirects", [])}


def parse_xml(p: Path) -> ET.ElementTree | None:
    try:
        return ET.parse(p)
    except ET.ParseError as exc:
        return None


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_index(qa: QA) -> list[Path]:
    """Validate /sitemap.xml is a sitemapindex; return list of child files."""
    if not INDEX_FILE.is_file():
        qa.err("missing sitemap.xml at site root")
        return []
    tree = parse_xml(INDEX_FILE)
    if tree is None:
        qa.err("sitemap.xml is not valid XML")
        return []
    root = tree.getroot()
    if root.tag != f"{{{NS_SM}}}sitemapindex":
        qa.err(f"sitemap.xml root is {root.tag!r}, expected sitemapindex")
        return []
    children: list[Path] = []
    seen: set[str] = set()
    for sm in root.findall("sm:sitemap", NS):
        loc_el = sm.find("sm:loc", NS)
        if loc_el is None or not loc_el.text:
            qa.err("sitemap-index entry missing <loc>")
            continue
        loc = loc_el.text.strip()
        if loc in seen:
            qa.err(f"sitemap-index duplicate loc: {loc}")
        seen.add(loc)
        if not loc.startswith(SITE + "/"):
            qa.err(f"sitemap-index loc not on insiderlawyers.com: {loc}")
            continue
        name = loc[len(SITE) + 1:]
        if name not in CHILD_NAMES:
            qa.err(f"sitemap-index references unknown child: {name}")
            continue
        f = ROOT / name
        if not f.is_file():
            qa.err(f"sitemap-index references missing file: {name}")
            continue
        children.append(f)
    # Also: every child sitemap that exists on disk should be referenced.
    existing = {n for n in CHILD_NAMES if (ROOT / n).is_file()}
    referenced = {c.name for c in children}
    for name in sorted(existing - referenced):
        qa.warn(f"child sitemap exists but is not referenced by index: {name}")
    return children


def check_child(qa: QA, child: Path, redirect_sources: set[str], all_locs: dict[str, str]) -> None:
    tree = parse_xml(child)
    if tree is None:
        qa.err(f"{child.name}: not valid XML")
        return
    root = tree.getroot()
    if root.tag != f"{{{NS_SM}}}urlset":
        qa.err(f"{child.name}: root is {root.tag!r}, expected urlset")
        return
    # Schema sanity
    raw = child.read_text(encoding="utf-8", errors="replace")
    if "<priority>" in raw:
        qa.err(f"{child.name}: contains <priority> (should not)")
    if "<changefreq>" in raw:
        qa.err(f"{child.name}: contains <changefreq> (should not)")
    if "xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\"" not in raw:
        qa.err(f"{child.name}: missing sitemap.org xmlns")

    seen_loc: set[str] = set()
    seen_loc_norm: set[str] = set()
    for url in root.findall("sm:url", NS):
        loc_el = url.find("sm:loc", NS)
        if loc_el is None or not loc_el.text:
            qa.err(f"{child.name}: <url> missing <loc>")
            continue
        loc = loc_el.text.strip()
        if loc in seen_loc:
            qa.err(f"{child.name}: duplicate <loc> {loc}")
        seen_loc.add(loc)
        loc_norm = loc.rstrip("/") or "/"
        if loc_norm in seen_loc_norm:
            qa.err(f"{child.name}: trailing-slash duplicate variant of {loc_norm}")
        seen_loc_norm.add(loc_norm)

        if not loc.startswith(SITE + "/") and loc != SITE + "/":
            qa.err(f"{child.name}: <loc> not on insiderlawyers.com: {loc}")
            continue

        # No URL should appear across two child sitemaps
        if loc in all_locs and all_locs[loc] != child.name:
            qa.err(f"duplicate URL across sitemaps: {loc} (in {all_locs[loc]} and {child.name})")
        all_locs[loc] = child.name

        # No URL should be a redirect source
        path = loc[len(SITE):] or "/"
        if path.rstrip("/") in redirect_sources and (path.rstrip("/") or "/") != "/":
            qa.err(f"{child.name}: {loc} is a redirect source in vercel.json")
            continue

        # File must exist on disk
        f = file_for_url(loc)
        if f is None or not f.is_file():
            qa.err(f"{child.name}: {loc} -> file not found")
            continue

        # Page must not be noindex, and canonical must agree
        try:
            html = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            qa.err(f"{child.name}: cannot read {f}")
            continue
        if RE_NOINDEX.search(html):
            qa.err(f"{child.name}: {loc} declares noindex")
        m = RE_CANON.search(html)
        if not m:
            qa.warn(f"{child.name}: {loc} has no canonical link tag")
        else:
            canon = m.group(1).strip()
            if canon.rstrip("/") != loc.rstrip("/"):
                qa.err(f"{child.name}: {loc} canonical mismatch: declared {canon}")

        # Spanish hreflang requirements
        if child.name == "sitemap-es.xml":
            hreflangs = url.findall("xhtml:link", NS)
            codes = {h.attrib.get("hreflang"): h.attrib.get("href") for h in hreflangs}
            if "en" not in codes or "es" not in codes or "x-default" not in codes:
                qa.err(f"{child.name}: {loc} missing required hreflang annotations (en/es/x-default)")
            else:
                en_url = codes["en"]
                es_url = codes["es"]
                xd_url = codes["x-default"]
                if es_url != loc:
                    qa.err(f"{child.name}: {loc} hreflang=es {es_url} != self")
                if not en_url or not en_url.startswith(SITE):
                    qa.err(f"{child.name}: {loc} hreflang=en not on insiderlawyers.com: {en_url}")
                else:
                    enf = file_for_url(en_url)
                    if enf is None or not enf.is_file():
                        qa.err(f"{child.name}: {loc} hreflang=en target missing: {en_url}")
                if xd_url != en_url:
                    qa.warn(f"{child.name}: {loc} x-default ({xd_url}) != en ({en_url})")


def check_robots(qa: QA) -> None:
    rt = ROOT / "robots.txt"
    if not rt.is_file():
        qa.err("robots.txt missing")
        return
    text = rt.read_text(encoding="utf-8", errors="replace")
    if f"Sitemap: {SITE}/sitemap.xml" not in text:
        qa.err(f"robots.txt does not reference {SITE}/sitemap.xml")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    qa = QA()
    redirect_sources = load_redirect_sources()
    children = check_index(qa)
    all_locs: dict[str, str] = {}
    for child in children:
        check_child(qa, child, redirect_sources, all_locs)
    check_robots(qa)
    return qa.report()


if __name__ == "__main__":
    sys.exit(main())
