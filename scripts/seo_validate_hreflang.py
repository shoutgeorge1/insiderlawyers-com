# -*- coding: utf-8 -*-
# Hreflang and canonical reciprocity validator for insiderlawyers.com.
#
# Reports:
#   * en pages whose hreflang points to a Spanish URL that does not exist
#   * es pages whose hreflang points to an English URL that does not exist
#   * pages whose hreflang lacks a self-reference
#   * canonicals pointing at a redirect source
#   * Spanish pages canonicalized to English URLs
#
# Outputs reports/seo-hreflang.md and exits 0/1.
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from collections import defaultdict

_WORKSPACE = Path(r"C:\Users\georgea\insiderlawyer-com-lps")
ROOT = _WORKSPACE / "insiderlawyers-com"
SITE = "https://www.insiderlawyers.com"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

EXCLUDED_DIRS = {
    "_dev", "_old-site-extract", "scripts", "components", "social-assets",
    "docs", "node_modules", ".git", ".cursor", "reports", "assets",
}

RE_CANON = re.compile(
    r'<link\b[^>]*\brel=["\']canonical["\'][^>]*\bhref=(["\'])(.*?)\1',
    re.I | re.S,
)
RE_HREFLANG = re.compile(
    r'<link\b[^>]*\brel=["\']alternate["\'][^>]*\bhreflang=["\']([^"\']+)["\'][^>]*\bhref=(["\'])(.*?)\2',
    re.I | re.S,
)
RE_HTML_LANG = re.compile(r'<html[^>]+lang=["\']([^"\']+)["\']', re.I)


def discover():
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


def file_to_path(p: Path) -> str:
    rel = p.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("/index.html")]
    return "/" + rel


def url_for(path: str, language: str) -> str:
    if path == "/":
        return SITE + "/"
    if path == "/es":
        return SITE + "/es/"
    if language == "es":
        return SITE + (path if path.endswith("/") else path + "/")
    return SITE + path


def detect_lang(path: str, html: str) -> str:
    if path.startswith("/es/") or path == "/es":
        return "es"
    m = RE_HTML_LANG.search(html)
    if m and m.group(1).lower().startswith("es"):
        return "es"
    return "en"


def load_redirect_sources() -> set[str]:
    p = ROOT / "vercel.json"
    if not p.is_file():
        return set()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return set()
    out = set()
    for r in data.get("redirects", []):
        s = (r.get("source", "") or "").rstrip("/") or "/"
        if s and s != "/":
            out.add(s)
    return out


def main() -> int:
    redirect_sources = load_redirect_sources()
    pages = discover()
    catalog = {}  # url -> info
    by_path = {}
    for p in pages:
        html = p.read_bytes().decode("utf-8", errors="replace")
        path = file_to_path(p)
        lang = detect_lang(path, html)
        url = url_for(path, lang)
        m = RE_CANON.search(html)
        canonical = m.group(2) if m else ""
        hreflang = []
        for m_ in RE_HREFLANG.finditer(html):
            hreflang.append((m_.group(1).lower(), m_.group(3)))
        catalog[url] = {"path": path, "lang": lang, "canonical": canonical, "hreflang": hreflang}
        by_path[path.rstrip("/") or "/"] = url

    issues = []
    en_with_es_pair = 0
    es_with_en_pair = 0
    es_count = 0
    en_count = 0

    for url, info in catalog.items():
        path = info["path"]
        lang = info["lang"]
        canonical = info["canonical"]
        hreflang = info["hreflang"]

        if lang == "es":
            es_count += 1
        else:
            en_count += 1

        # Canonical sanity
        if canonical:
            canon_path = canonical.replace(SITE, "").split("?")[0].split("#")[0]
            canon_path = canon_path.rstrip("/") or "/"
            if canon_path in redirect_sources:
                issues.append(f"{url} canonical points to redirect source: {canonical}")
            if lang == "es" and not (canonical.startswith(SITE + "/es/") or canonical == SITE + "/es/"):
                issues.append(f"{url} (es) canonical is not a Spanish URL: {canonical}")
        else:
            issues.append(f"{url} missing canonical")

        # Hreflang reciprocity
        if hreflang:
            langs_present = {l for l, _ in hreflang}
            self_ref = any(href.rstrip("/") == url.rstrip("/") for _, href in hreflang)
            if not self_ref:
                issues.append(f"{url} hreflang lacks self-reference")
            for l, href in hreflang:
                if l in ("x-default",):
                    continue
                # Each href should resolve to an indexable page
                target = href.replace(SITE, "").split("?")[0].split("#")[0]
                target = target.rstrip("/") or "/"
                if target in redirect_sources:
                    issues.append(f"{url} hreflang {l!r} -> redirect source: {href}")
                if target not in by_path and href.rstrip("/") + "/" not in by_path:
                    if not (l == "x-default" and target == "/"):
                        if target not in by_path:
                            issues.append(f"{url} hreflang {l!r} -> unknown URL: {href}")
            if lang == "en" and "es" in langs_present:
                en_with_es_pair += 1
            if lang == "es" and "en" in langs_present:
                es_with_en_pair += 1

    summary_lines = [
        "# Hreflang & canonical validation",
        "",
        f"- English pages: {en_count}",
        f"- Spanish pages: {es_count}",
        f"- English pages with Spanish hreflang: {en_with_es_pair}",
        f"- Spanish pages with English hreflang: {es_with_en_pair}",
        f"- Issues: {len(issues)}",
        "",
    ]
    if issues:
        summary_lines.append("## Issues")
        summary_lines.append("")
        for i in issues:
            summary_lines.append(f"- {i}")
    else:
        summary_lines.append("(no issues detected)")
    out_path = REPORTS / "seo-hreflang.md"
    out_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    print("Hreflang validation:")
    print("  English:", en_count, "  Spanish:", es_count)
    print("  English w/ es hreflang:", en_with_es_pair)
    print("  Spanish w/ en hreflang:", es_with_en_pair)
    print("  Issues:", len(issues))
    print(f"  Report: {out_path}")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
