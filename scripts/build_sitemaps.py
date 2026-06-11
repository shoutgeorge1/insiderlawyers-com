# -*- coding: utf-8 -*-
"""Single source of truth for the insiderlawyers.com sitemap system.

Emits a sitemap index plus five categorized child sitemaps:

    /sitemap.xml             sitemap index (only references child sitemaps)
    /sitemap-core-en.xml     primary English conversion / hub pages
    /sitemap-guides-en.xml   supporting English informational pages
    /sitemap-es.xml          Spanish content pages (excluding ES legal)
    /sitemap-legal.xml       English + Spanish legal / compliance pages
    /sitemap-referrals.xml   B2B / attorney referral pages

Design notes:
  * The categorization is hard-coded below (CORE_EN / GUIDES_EN / REFERRALS_EN
    / LEGAL_EN_PATHS / LEGAL_ES_PATHS plus auto-discovered Spanish content).
  * Spanish content pages are auto-discovered from /es/ on disk so the
    generator stays in sync with build_es_pages.py.
  * `vercel.json` is parsed and every redirect SOURCE is collected as a
    hard-exclude set, so a redirect URL can never appear in any sitemap.
  * `<priority>` and `<changefreq>` are never emitted.
  * `<lastmod>` is the git-tracked mtime of the actual HTML file (the last
    commit that touched it). A sitemap-only rebuild that does not change
    any HTML therefore does NOT stamp every page with today's date.
  * Every emitted URL is validated:
        - file exists on disk
        - canonical link tag points to the URL we are emitting
        - page is not noindex
        - URL is not a redirect source
        - URL is not in the explicit EXCLUDED dict (consolidation targets,
          conversion-only thank-you page, etc.)
  * Spanish URLs include reciprocal xhtml:link hreflang annotations.
  * Anything that fails validation is reported in the summary so a human
    can decide whether to fix the page or update the manifest.

Run:
    python insiderlawyers-com/scripts/build_sitemaps.py

Idempotent.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths / constants
# ---------------------------------------------------------------------------

# Path(__file__).resolve() on Windows follows the hardlink and lands in
# pi-search-caraccident-lp, which contains extra files we never want in the
# insiderlawyers.com sitemap. Anchor on a stable workspace-relative path.
_WORKSPACE = Path(r"C:\Users\georgea\insiderlawyer-com-lps")
ROOT = _WORKSPACE / "insiderlawyers-com"
if not (ROOT / "components" / "global-chrome-before-main.html").is_file():
    raise SystemExit(f"ROOT sanity check failed: {ROOT}")

SITE = "https://www.insiderlawyers.com"

INDEX_FILE = ROOT / "sitemap.xml"
CHILD_FILES = {
    "core-en":  ROOT / "sitemap-core-en.xml",
    "guides-en": ROOT / "sitemap-guides-en.xml",
    "es":       ROOT / "sitemap-es.xml",
    "legal":    ROOT / "sitemap-legal.xml",
    "referrals": ROOT / "sitemap-referrals.xml",
}

VERCEL_JSON = ROOT / "vercel.json"

# ---------------------------------------------------------------------------
# CATEGORIZATION (single source of truth)
# ---------------------------------------------------------------------------

# Core English pages: homepage, contact, hubs, primary LA accident pages,
# settlement / second-opinion / claim-review hubs, the two main nursing-home
# pages. Order is intentional and is preserved in the emitted sitemap.
CORE_EN: list[str] = [
    "/",
    "/contact",
    # Personal injury hub + category pages
    "/personal-injury",
    "/personal-injury/auto-accidents",
    "/personal-injury/truck-accidents",
    "/personal-injury/truck-accidents/fmcsa-hours-of-service",
    "/personal-injury/truck-accidents/truck-accident-evidence",
    "/personal-injury/truck-accidents/truck-accident-liability",
    "/personal-injury/motorcycle-accidents",
    "/personal-injury/bicycle-accidents",
    "/personal-injury/pedestrian-accidents",
    "/personal-injury/uber-and-lyft-accidents",
    "/personal-injury/slip-and-fall",
    "/personal-injury/premises-liability",
    "/personal-injury/animal-attacks",
    "/personal-injury/brain-injuries",
    "/personal-injury/spine-injuries",
    "/personal-injury/catastrophic-injuries",
    "/personal-injury/wrongful-death",
    "/personal-injury/product-liability",
    # Settlement / claim-review / second-opinion hubs
    "/settlements",
    "/california-injury-claim-second-opinion",
    "/second-opinion-personal-injury-claim-california",
    "/second-opinion-before-signing-release-california",
    "/california-personal-injury-settlement-checklist",
    "/california-personal-injury-demand-letter-guide",
    "/california-parking-lot-accident-claim-guide",
    "/t-bone-accident-claim-value-california",
    # Motor vehicle silo
    "/motor-vehicle",
    "/motor-vehicle/bus-accident-lawyer-los-angeles",
    # Premises liability silo
    "/premises-liability",
    "/premises-liability/negligent-security-lawyer-los-angeles",
    # Major / California accident hubs
    "/major-car-accident",
    "/california-car-accident-lawyer",
    # Primary live LA-lawyer landing pages (all the legacy
    # /los-angeles-*-lawyer URLs in vercel.json redirect to PI sub-hubs
    # except for the two listed here)
    "/los-angeles-car-accident-lawyer",
    "/los-angeles-nursing-home-neglect-lawyer",
    # LA -lawyer-los-angeles suffix pages (live, not redirected)
    "/parking-lot-accident-lawyer-los-angeles",
    "/t-bone-accident-lawyer-los-angeles",
    "/rear-end-accident-lawyer-los-angeles",
    "/hit-and-run-accident-lawyer-los-angeles",
    "/pedestrian-accident-lawyer-los-angeles",
    "/uber-accident-lawyer-los-angeles",
    "/electric-scooter-ebike-accident-lawyer-los-angeles",
    "/uninsured-driver-accident-lawyer-los-angeles",
    # Other conversion-focused pages
    "/recover-destroyed-scooter-ebike",
    "/pressure-ulcers-nursing-home-neglect",
]

# Supporting informational pages. Listed alphabetically for editability.
# Consolidation losers and the two explicit user exclusions are deliberately
# NOT in this list (see EXCLUDED below for the rationale).
GUIDES_EN: list[str] = [
    "/at-fault-driver-no-insurance",
    "/brain-injury",
    "/can-i-sue-uninsured-driver-personally",
    "/can-new-lawyer-increase-injury-settlement",
    "/can-you-sue-nursing-home-bed-sores",
    "/changing-personal-injury-lawyer-california",
    "/contingency-fee-when-switching-lawyers-injury-case",
    "/delayed-pain-after-car-accident",
    "/demand-letter-negotiation",
    "/demand-letters-explained",
    "/do-i-need-police-report-accident",
    "/does-filing-um-claim-raise-rates",
    "/evidence-preservation-car-accident-california",
    "/herniated-disc-car-accident-settlement-california",
    "/how-insurance-calculates-settlement-offers",
    "/how-long-does-a-car-accident-settlement-take-california",
    "/how-long-personal-injury-case-takes-california",
    "/how-much-is-my-car-accident-worth-california",
    "/injuries-truck-accidents",
    "/insurance-company-playbook",
    "/insurance-company-tactics-personal-injury",
    "/insurance-says-injury-is-minor-california",
    "/insurance-says-low-impact-car-accident-california",
    "/lawyer-pushing-settlement-too-fast-california",
    "/lowball-offer-response",
    "/motorcycle-accident-case",
    "/nursing-home-neglect-vs-abuse",
    "/nursing-home-repositioning-standards",
    "/nursing-home-understaffing-lawsuit",
    "/nursing-home-wrongful-death",
    "/passenger-in-uninsured-car",
    "/pedestrian-right-of-way",
    "/personal-injury-case-stalled-california",
    "/personal-injury-claim-process-california",
    "/personal-injury-court",
    "/personal-injury-lawyer-not-responding-california",
    "/post-dog-bite",
    "/proving-claim-value",
    "/proving-truck-accident-case",
    "/recorded-statement-should-you-give-one",
    "/scooter-accident-driver-fled",
    "/scooter-accident-no-license-plate",
    "/should-i-accept-first-settlement-offer-california",
    "/signs-of-nursing-home-neglect",
    "/signs-personal-injury-lawyer-not-maximizing-case",
    "/soft-tissue-injury-settlement-california",
    "/spinal-fusion-surgery-car-accident-settlement-california",
    "/stage-3-stage-4-bed-sore-lawsuit",
    "/traumatic-brain-injury-car-accident-settlement-california",
    "/truck-accident-legal-rights",
    "/uber-or-lyft-accident",
    "/underinsured-motorist-claims-explained",
    "/uninsured-motorist-claims-california",
    "/what-causes-bed-sores",
    "/what-if-i-cant-afford-deductible",
    "/what-if-liability-disputed",
    "/what-is-uninsured-motorist-coverage",
    "/what-to-do-after-car-accident-california",
    "/when-should-i-call-lawyer-accident",
    "/who-is-liable-scooter-accident",
    "/why-insurance-delays-claims",
]

# Referral / B2B pages. Stay separate so Google sees these target attorneys.
REFERRALS_EN: list[str] = [
    "/attorney-referrals",
    "/lit-referral-core",
    "/lit-referral-process",
    "/lit-referral-criteria",
    "/lit-referral-economics",
    "/lit-referral-trial-ready-cocounsel",
    "/lit-referral-catastrophic-cases",
    "/lit-referral-truck-litigation",
    "/lit-referral-brain-injury",
    "/lit-referral-wrongful-death",
    "/lit-referral-coverage-disputes",
]

# Legal pages, English.
LEGAL_EN_PATHS: list[str] = [
    "/privacy-policy",
    "/legal-terms",
    "/disclaimer",
    "/cookie-policy",
    "/california-privacy-rights",
    "/do-not-sell-or-share-my-personal-information",
    "/accessibility",
]

# Legal pages, Spanish. These are part of the 40 Spanish Tier 1 pages but
# belong in /sitemap-legal.xml, not in /sitemap-es.xml.
LEGAL_ES_PATHS: list[str] = [
    "/es/politica-privacidad",
    "/es/terminos-legales",
    "/es/aviso-legal",
    "/es/politica-cookies",
    "/es/derechos-privacidad-california",
    "/es/no-vender-compartir-informacion-personal",
    "/es/accesibilidad",
]

# Explicit exclusions with rationale. Pages still live on disk so existing
# inbound links and Google-discovered URLs do not 404, but Google should
# not be invited to re-discover them via sitemap.
EXCLUDED: dict[str, str] = {
    # User-specified
    "/comparative-negligence-california-explained":
        "user-specified exclusion (consolidation candidate)",
    "/what-happens-if-i-fire-my-accident-attorney":
        "user-specified exclusion (consolidation candidate)",
    # Conversion-only
    "/thank-you":
        "form thank-you / conversion landing page; no SEO value",
    # Consolidation losers — keep the strongest canonical of each cluster
    "/california-comparative-negligence-personal-injury":
        "consolidation: weak duplicate; primary is /comparative-negligence-california-explained (also excluded), neither is sitemap-worthy",
    "/adjuster-claim-valuation":
        "consolidation: keep /how-insurance-calculates-settlement-offers",
    "/how-adjusters-value-claims":
        "consolidation: keep /how-insurance-calculates-settlement-offers",
    "/can-i-change-my-personal-injury-lawyer-california":
        "consolidation: keep /changing-personal-injury-lawyer-california",
    "/personal-injury-case-feels-stalled-what-to-do":
        "consolidation: keep /personal-injury-case-stalled-california",
    "/should-i-accept-insurance-first-offer":
        "consolidation: keep /should-i-accept-first-settlement-offer-california",
    "/hit-and-run-accidents-los-angeles":
        "consolidation: keep /hit-and-run-accident-lawyer-los-angeles",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

RE_CANON = re.compile(
    r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', re.I,
)
RE_NOINDEX = re.compile(
    r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex', re.I,
)


def url_for_path(path: str) -> str:
    """Build a fully-qualified URL from a site-relative path.

    Convention used on this site:
      * English pages: no trailing slash (e.g. https://.../foo)
      * Spanish pages: trailing slash (e.g. https://.../es/foo/)
      * Homepage: https://.../
    """
    if path == "/":
        return SITE + "/"
    if path == "/es":
        return SITE + "/es/"
    if path.startswith("/es/") and not path.endswith("/"):
        return SITE + path + "/"
    return SITE + path


def file_for_path(path: str) -> Path:
    """Map a URL path to the on-disk HTML file."""
    if path == "/":
        return ROOT / "index.html"
    rel = path.strip("/")
    return ROOT / Path(rel) / "index.html"


def load_redirect_sources() -> set[str]:
    """Return every URL listed as a redirect source in vercel.json."""
    if not VERCEL_JSON.is_file():
        return set()
    try:
        data = json.loads(VERCEL_JSON.read_text(encoding="utf-8"))
    except Exception:
        return set()
    out: set[str] = set()
    for r in data.get("redirects", []):
        src = r.get("source", "").rstrip("/") or "/"
        if src:
            out.add(src)
    return out


def get_git_mtime(p: Path) -> str | None:
    """Return YYYY-MM-DD for the last git commit that touched this file."""
    try:
        rel = str(p.relative_to(ROOT)).replace("\\", "/")
        # %cs = committer date in YYYY-MM-DD; honours the working tree at
        # the file's last touching commit.
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", rel],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        s = (out.stdout or "").strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
            return s
    except Exception:
        pass
    return None


def extract_canonical(p: Path) -> tuple[str, bool]:
    """Return (canonical_href, is_noindex)."""
    try:
        html = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "", False
    m = RE_CANON.search(html)
    canon = m.group(1).strip() if m else ""
    return canon, bool(RE_NOINDEX.search(html))


# ---------------------------------------------------------------------------
# Spanish content auto-discovery
# ---------------------------------------------------------------------------

def discover_es_content_paths(legal_paths: set[str]) -> list[str]:
    """All /es/ index.html URLs except the ones in legal_paths.

    Returns deterministic, sorted list. Homepage /es/ first.
    """
    paths: list[str] = []
    es_root = ROOT / "es"
    if not es_root.is_dir():
        return paths
    for p in sorted(es_root.rglob("index.html")):
        rel = p.relative_to(ROOT).as_posix()
        if rel == "es/index.html":
            url = "/es"
        else:
            url = "/" + rel[: -len("/index.html")]
        if url in legal_paths:
            continue
        paths.append(url)
    # Move /es to the front
    paths = sorted(paths, key=lambda u: (0 if u == "/es" else 1, u))
    return paths


# Mapping of ES path -> EN path, used to generate hreflang on ES entries.
# Pulled from build_es_pages.py at runtime so the two stay in sync.
def load_es_to_en_map() -> dict[str, str]:
    """Parse build_es_pages.py to extract (es_path, en_path) pairs."""
    src = (ROOT / "scripts" / "build_es_pages.py").read_text(encoding="utf-8", errors="replace")
    # Look for blocks of the form:
    #   en_path="/foo",
    #   es_path="/es/bar",
    out: dict[str, str] = {}
    # Iterate over every PageSpec call by regex pairing.
    pattern = re.compile(
        r'en_path\s*=\s*"([^"]+)"[\s\S]{0,400}?es_path\s*=\s*"([^"]+)"',
    )
    for m in pattern.finditer(src):
        en, es = m.group(1), m.group(2)
        out[es.rstrip("/")] = en.rstrip("/") or "/"
    return out


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class Issue:
    __slots__ = ("path", "category", "code", "detail")

    def __init__(self, path: str, category: str, code: str, detail: str) -> None:
        self.path = path
        self.category = category
        self.code = code
        self.detail = detail

    def __repr__(self) -> str:
        return f"[{self.category}] {self.path} {self.code}: {self.detail}"


def validate_path(path: str, category: str, redirect_sources: set[str]) -> tuple[bool, list[Issue], str | None]:
    """Return (ok, issues, declared_canonical)."""
    issues: list[Issue] = []
    norm = path.rstrip("/") or "/"
    if norm != "/" and norm in redirect_sources:
        issues.append(Issue(path, category, "REDIRECT", "URL is a redirect source in vercel.json"))
    if norm in EXCLUDED:
        issues.append(Issue(path, category, "EXCLUDED", f"explicit exclusion: {EXCLUDED[norm]}"))
    f = file_for_path(path)
    if not f.is_file():
        issues.append(Issue(path, category, "MISSING", f"no index.html at {f.relative_to(ROOT)}"))
        return False, issues, None
    canon, noindex = extract_canonical(f)
    if noindex:
        issues.append(Issue(path, category, "NOINDEX", "page declares noindex"))
    expected = url_for_path(path)
    # Accept either trailing-slash or non-trailing-slash version of the
    # expected canonical, since cleanUrls makes them equivalent.
    if canon.rstrip("/") != expected.rstrip("/"):
        issues.append(Issue(
            path, category, "CANON_MISMATCH",
            f"declared canonical {canon!r} != expected {expected!r}",
        ))
    return (not any(i.code in ("REDIRECT", "EXCLUDED", "MISSING", "NOINDEX") for i in issues),
            issues, canon or None)


# ---------------------------------------------------------------------------
# XML emission
# ---------------------------------------------------------------------------

URLSET_HEAD = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
URLSET_HEAD_HREFLANG = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
URLSET_TAIL = "</urlset>\n"
INDEX_HEAD = '<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
INDEX_TAIL = "</sitemapindex>\n"


def emit_url(loc: str, lastmod: str | None, hreflangs: list[tuple[str, str]] | None = None) -> str:
    lines = ["  <url>", f"    <loc>{loc}</loc>"]
    if lastmod:
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
    if hreflangs:
        for code, href in hreflangs:
            lines.append(f'    <xhtml:link rel="alternate" hreflang="{code}" href="{href}" />')
    lines.append("  </url>")
    return "\n".join(lines) + "\n"


def render_urlset(entries: list[str], hreflang: bool = False) -> str:
    head = URLSET_HEAD_HREFLANG if hreflang else URLSET_HEAD
    return head + "\n" + "".join(entries) + URLSET_TAIL


def render_index(child_urls: list[tuple[str, str | None]]) -> str:
    lines = [INDEX_HEAD]
    for url, lm in child_urls:
        lines.append("  <sitemap>")
        lines.append(f"    <loc>{url}</loc>")
        if lm:
            lines.append(f"    <lastmod>{lm}</lastmod>")
        lines.append("  </sitemap>")
    lines.append(INDEX_TAIL.rstrip("\n"))
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build() -> dict:
    redirect_sources = load_redirect_sources()
    legal_es = list(LEGAL_ES_PATHS)
    es_content = discover_es_content_paths(set(legal_es))
    es_to_en = load_es_to_en_map()

    summary: dict = {
        "redirect_sources": sorted(redirect_sources),
        "buckets": OrderedDict(),
        "excluded": [],
        "issues": [],
        "files_written": [],
    }

    def emit_bucket(name: str, paths: list[str], hreflang: bool = False) -> int:
        entries: list[str] = []
        sitemap_lastmods: list[str] = []
        included: list[str] = []
        for path in paths:
            ok, issues, _canon = validate_path(path, name, redirect_sources)
            for i in issues:
                # canonical mismatch is a warning, not a skip
                if i.code == "CANON_MISMATCH":
                    summary["issues"].append(repr(i))
                else:
                    summary["issues"].append(repr(i))
            if not ok:
                continue
            f = file_for_path(path)
            lastmod = get_git_mtime(f)
            if lastmod:
                sitemap_lastmods.append(lastmod)
            loc = url_for_path(path)
            hrefs = None
            if hreflang and path.startswith("/es"):
                en_path = es_to_en.get(path.rstrip("/")) or es_to_en.get(path) or "/"
                en_url = url_for_path(en_path)
                hrefs = [
                    ("en", en_url),
                    ("es", loc),
                    ("x-default", en_url),
                ]
            entries.append(emit_url(loc, lastmod, hrefs))
            included.append(loc)
        out_path = CHILD_FILES[name]
        if entries:
            out_path.write_text(render_urlset(entries, hreflang=hreflang), encoding="utf-8")
            summary["files_written"].append(out_path.name)
        else:
            # If a child sitemap would be empty, do not write it (and do not
            # include it in the index).
            if out_path.is_file():
                out_path.unlink()
        summary["buckets"][name] = {
            "count": len(included),
            "urls": included,
            "max_lastmod": max(sitemap_lastmods) if sitemap_lastmods else None,
        }
        return len(included)

    # CORE EN
    emit_bucket("core-en", CORE_EN, hreflang=False)

    # GUIDES EN
    emit_bucket("guides-en", GUIDES_EN, hreflang=False)

    # REFERRALS
    emit_bucket("referrals", REFERRALS_EN, hreflang=False)

    # SPANISH content
    emit_bucket("es", es_content, hreflang=True)

    # LEGAL (EN + ES merged)
    legal_paths = LEGAL_EN_PATHS + legal_es
    emit_bucket("legal", legal_paths, hreflang=False)

    # Build the sitemap index, referencing only child sitemaps that were
    # written (i.e. that contain at least one URL).
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    child_index: list[tuple[str, str | None]] = []
    for name, file in CHILD_FILES.items():
        if not file.is_file():
            continue
        lm = summary["buckets"].get(name, {}).get("max_lastmod") or today
        url = f"{SITE}/{file.name}"
        child_index.append((url, lm))
    INDEX_FILE.write_text(render_index(child_index), encoding="utf-8")
    summary["files_written"].insert(0, INDEX_FILE.name)

    # Annotate explicit exclusions in summary for the final report.
    for path, reason in EXCLUDED.items():
        summary["excluded"].append({"path": path, "reason": reason, "kind": "explicit"})
    for src in sorted(redirect_sources):
        summary["excluded"].append({"path": src, "reason": "redirect source in vercel.json", "kind": "redirect"})

    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    summary = build()
    print("Sitemap files written:")
    for f in summary["files_written"]:
        print(f"  - {f}")
    print()
    print("URL counts per child sitemap:")
    for name, info in summary["buckets"].items():
        print(f"  - {name}: {info['count']} URLs  (max lastmod {info['max_lastmod']})")
    print()
    if summary["issues"]:
        print(f"Warnings / skipped: {len(summary['issues'])}")
        for line in summary["issues"]:
            print(f"  {line}")
    else:
        print("No validation warnings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
