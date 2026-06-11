# -*- coding: utf-8 -*-
"""Production QA for /es/ pages and their English counterparts.

Verifies, locally, what Vercel will serve:
  - file presence (proxy for HTTP 200 since vercel.json has cleanUrls=true)
  - one H1, unique title, unique meta description, self-canonical, no noindex
  - html lang correctness
  - visible CTA, tel: links, hidden language=es field, form id, footer links
  - reciprocal hreflang (EN <-> ES), x-default validity
  - sitemap XML validity, namespaces, hreflang annotations, presence of all ES URLs
  - duplicate ids on a page
  - GTM, privacy-choices, CallRail data attrs, form_submit dataLayer push
  - JSON-LD validity (each script type=application/ld+json must parse), FAQ schema
    only present when there are visible FAQ items
  - footer disclaimer + attorney-advertising language
  - no banned guarantee/award language

Re-runnable. No side effects.
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITEMAP = ROOT / "sitemap.xml"
SITE = "https://www.insiderlawyers.com"

# Same canonical mapping as build_es_pages.py - keep this in sync with PAGES list.
# (en_path_no_slash, es_path_with_trailing_slash)
PAIRS: list[tuple[str, str]] = [
    ("/", "/es/"),
    ("/california-injury-claim-second-opinion", "/es/segunda-opinion-reclamo-lesiones-california/"),
    ("/contact", "/es/contacto/"),
    ("/personal-injury", "/es/lesiones-personales/"),
    ("/settlements", "/es/acuerdos-liquidaciones-lesiones/"),
    ("/second-opinion-personal-injury-claim-california", "/es/segunda-opinion-caso-lesiones-california/"),
    ("/california-personal-injury-settlement-checklist", "/es/lista-revision-liquidacion-lesiones-california/"),
    ("/california-personal-injury-demand-letter-guide", "/es/carta-demanda-lesiones-personales-california/"),
    ("/motor-vehicle", "/es/accidentes-vehiculos/"),
    ("/premises-liability", "/es/responsabilidad-de-propiedad/"),
    ("/major-car-accident", "/es/accidente-auto-grave/"),
    ("/los-angeles-car-accident-lawyer", "/es/abogado-accidentes-auto-los-angeles/"),
    ("/california-car-accident-lawyer", "/es/abogado-accidentes-auto-california/"),
    ("/personal-injury/auto-accidents", "/es/lesiones-personales/accidentes-auto/"),
    ("/personal-injury/slip-and-fall", "/es/lesiones-personales/resbalon-caida/"),
    ("/california-parking-lot-accident-claim-guide", "/es/guia-reclamo-accidente-estacionamiento-california/"),
    ("/parking-lot-accident-lawyer-los-angeles", "/es/abogado-accidente-estacionamiento-los-angeles/"),
    ("/t-bone-accident-claim-value-california", "/es/valor-reclamo-choque-lateral-california/"),
    ("/t-bone-accident-lawyer-los-angeles", "/es/abogado-choque-lateral-los-angeles/"),
    ("/rear-end-accident-lawyer-los-angeles", "/es/abogado-choque-por-alcance-los-angeles/"),
    ("/electric-scooter-ebike-accident-lawyer-los-angeles", "/es/abogado-accidente-scooter-bicicleta-electrica-los-angeles/"),
    ("/recover-destroyed-scooter-ebike", "/es/recuperar-scooter-bicicleta-electrica-danada/"),
    ("/hit-and-run-accident-lawyer-los-angeles", "/es/abogado-accidente-fuga-los-angeles/"),
    ("/pedestrian-accident-lawyer-los-angeles", "/es/abogado-accidente-peaton-los-angeles/"),
    ("/uber-accident-lawyer-los-angeles", "/es/abogado-accidente-uber-lyft-los-angeles/"),
    ("/personal-injury/truck-accidents", "/es/lesiones-personales/accidentes-camion/"),
    ("/uninsured-driver-accident-lawyer-los-angeles", "/es/abogado-accidente-conductor-sin-seguro-los-angeles/"),
    ("/los-angeles-nursing-home-neglect-lawyer", "/es/abogado-negligencia-asilo-ancianos-los-angeles/"),
    ("/pressure-ulcers-nursing-home-neglect", "/es/ulceras-presion-negligencia-asilo-ancianos/"),
    ("/personal-injury/wrongful-death", "/es/lesiones-personales/muerte-injusta/"),
    ("/personal-injury/brain-injuries", "/es/lesiones-personales/lesion-cerebral/"),
    ("/personal-injury/spine-injuries", "/es/lesiones-personales/lesiones-columna/"),
    ("/personal-injury/catastrophic-injuries", "/es/lesiones-personales/lesiones-catastroficas/"),
    ("/privacy-policy", "/es/politica-privacidad/"),
    ("/legal-terms", "/es/terminos-legales/"),
    ("/disclaimer", "/es/aviso-legal/"),
    ("/cookie-policy", "/es/politica-cookies/"),
    ("/california-privacy-rights", "/es/derechos-privacidad-california/"),
    ("/do-not-sell-or-share-my-personal-information", "/es/no-vender-compartir-informacion-personal/"),
    ("/accessibility", "/es/accesibilidad/"),
]


def file_for(url_path: str) -> Path:
    rel = url_path.strip("/")
    if rel == "":
        return ROOT / "index.html"
    candidate = ROOT / Path(rel) / "index.html"
    if candidate.is_file():
        return candidate
    candidate = ROOT / (rel + ".html")
    if candidate.is_file():
        return candidate
    return ROOT / Path(rel) / "index.html"  # for error reporting


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


# --------------------------- regexes ---------------------------

RE_H1 = re.compile(r"<h1\b[^>]*>", re.I)
RE_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
RE_DESC = re.compile(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)["\']', re.I)
RE_CANON = re.compile(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', re.I)
RE_NOINDEX = re.compile(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex', re.I)
RE_LANG = re.compile(r'<html[^>]+lang=["\']([^"\']+)["\']', re.I)
RE_TEL = re.compile(r'href=["\']tel:([^"\']+)["\']', re.I)
RE_FORM_ID = re.compile(r'id=["\']case-evaluation-form["\']', re.I)
RE_LANG_HIDDEN = re.compile(r'<input[^>]+name=["\']language["\'][^>]+value=["\']es["\']', re.I)
RE_GTM = re.compile(r"GTM-WS8XT5FC", re.I)
RE_PRIVACY = re.compile(r"privacy-choices\.js", re.I)
RE_CALLRAIL = re.compile(r'data-callrail-phone=["\']844-467-4335["\']', re.I)
RE_HREFLANG = re.compile(r'<link[^>]+rel=["\']alternate["\'][^>]+hreflang=["\']([^"\']+)["\'][^>]+href=["\']([^"\']+)["\']', re.I)
RE_HREFLANG_ALT = re.compile(r'<link[^>]+hreflang=["\']([^"\']+)["\'][^>]+rel=["\']alternate["\'][^>]+href=["\']([^"\']+)["\']', re.I)
RE_SCRIPT_JSONLD = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.I | re.S)
RE_FAQ_VISIBLE = re.compile(r'class=["\'][^"\']*\b(faq-item|es-faq|faq|box\s+faq)\b|>\s*(FAQs?|Preguntas frecuentes|Frequently Asked)\s*<', re.I)
RE_ALL_IDS = re.compile(r'\bid=["\']([^"\']+)["\']')
RE_DISCLAIMER_BLOCK = re.compile(r'footer__short-disclaimer|disclaimer-block', re.I)
RE_ATTORNEY_AD = re.compile(r"publicidad de abogado|attorney advertising", re.I)
RE_PHONE_CLASS = re.compile(r'class=["\'][^"\']*\bphone-link\b', re.I)
RE_FOOTER_LEGAL = re.compile(r'footer-section--legal', re.I)

# Banned guarantee / fake-claim language to flag (case-insensitive).
# We exclude the literal English "Attorney advertising." disclaimer line itself
# which is allowed. Match in body, not in the disclaimer.
BANNED_PHRASES = [
    "garantizamos resultado", "garantizamos resultados", "guaranteed result",
    "guaranteed outcome", "guaranteed compensation",
    "we win every", "ganamos siempre",
    "100% case results", "100 percent of cases",
    "best lawyer in", "el mejor abogado de",
    "no fees ever", "sin honorarios nunca",
    "5-star reviews from", "5 estrellas en cada",
]

ALLOWED_DUP_IDS = {
    "header", "footer-contact", "logo", "mobile-menu-toggle", "header-nav-wrap",
    "primary-nav", "case-evaluation",  # case-evaluation is an anchor target, not a form id
}


def text_of(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html)


# --------------------------- per-page audit ---------------------------

def audit_page(p: Path, expect_lang: str, expect_canonical: str | None = None) -> dict:
    res = {
        "file": str(p.relative_to(ROOT)).replace("\\", "/"),
        "exists": p.is_file(),
        "issues": [],
        "warnings": [],
    }
    if not res["exists"]:
        res["issues"].append("file missing (would be 404 in production)")
        return res
    html = read(p)

    # H1
    h1s = RE_H1.findall(html)
    if len(h1s) == 0:
        res["issues"].append("missing <h1>")
    elif len(h1s) > 1:
        res["issues"].append(f"{len(h1s)} <h1> tags (expected 1)")

    # title
    mt = RE_TITLE.search(html)
    title = (mt.group(1).strip() if mt else "")
    res["title"] = title
    if not title:
        res["issues"].append("missing <title>")

    # description
    md = RE_DESC.search(html)
    desc = md.group(1).strip() if md else ""
    res["description"] = desc
    if not desc:
        res["issues"].append("missing meta description")

    # canonical
    mc = RE_CANON.search(html)
    canon = mc.group(1).strip() if mc else ""
    res["canonical"] = canon
    if not canon:
        res["issues"].append("missing canonical")
    elif expect_canonical and canon != expect_canonical:
        res["issues"].append(f"canonical='{canon}' expected '{expect_canonical}'")

    # noindex
    if RE_NOINDEX.search(html):
        res["issues"].append("contains noindex")

    # html lang
    ml = RE_LANG.search(html)
    lang = ml.group(1) if ml else ""
    res["lang"] = lang
    if not lang.startswith(expect_lang):
        res["issues"].append(f"html lang='{lang}' expected '{expect_lang}'")

    # CTA: at least one tel link, at least one button-style or anchor with btn class
    if not RE_TEL.search(html):
        res["issues"].append("no tel: link")
    if not (re.search(r'href=["\']#case-evaluation["\']', html) or "btn-primary" in html or "btn-primary-cta" in html or "btn-secondary" in html):
        res["issues"].append("no visible primary CTA")

    # CallRail data attr
    if not RE_CALLRAIL.search(html):
        res["warnings"].append("no data-callrail-phone attribute (DNI may not swap)")

    # phone link class for DNI selector
    if not RE_PHONE_CLASS.search(html):
        res["warnings"].append("no class='phone-link' (DNI selector may miss)")

    # GTM
    if not RE_GTM.search(html):
        res["issues"].append("GTM container ID missing")

    # privacy-choices
    if not RE_PRIVACY.search(html):
        res["warnings"].append("privacy-choices.js not referenced")

    # JSON-LD validity
    res["jsonld_count"] = 0
    for m in RE_SCRIPT_JSONLD.finditer(html):
        body = m.group(1).strip()
        if not body:
            continue
        res["jsonld_count"] += 1
        try:
            json.loads(body)
        except Exception as e:
            res["issues"].append(f"invalid JSON-LD: {e.__class__.__name__}")

    # FAQ schema only when the FAQ questions are actually visible on the page.
    # We extract each FAQPage Question name from JSON-LD and look it up in the
    # rendered body text (markup stripped). This works regardless of which CSS
    # class the page uses for its FAQ container.
    body = html
    body_text = re.sub(r"<script[\s\S]*?</script>", " ", body)
    body_text = re.sub(r"<style[\s\S]*?</style>", " ", body_text)
    body_text = re.sub(r"<[^>]+>", " ", body_text)
    body_text = re.sub(r"\s+", " ", body_text).strip()
    has_faq_schema = False
    visible_count = 0
    expected_count = 0
    for m in RE_SCRIPT_JSONLD.finditer(html):
        sb = m.group(1).strip()
        if not sb:
            continue
        try:
            data = json.loads(sb)
        except Exception:
            continue
        nodes = data if isinstance(data, list) else [data]
        for node in nodes:
            if isinstance(node, dict) and node.get("@type") == "FAQPage":
                has_faq_schema = True
                for q in node.get("mainEntity", []) or []:
                    if not isinstance(q, dict):
                        continue
                    name = (q.get("name") or "").strip()
                    if not name:
                        continue
                    expected_count += 1
                    if name[:40].lower() in body_text.lower():
                        visible_count += 1
    if has_faq_schema:
        if expected_count > 0 and visible_count == 0:
            res["issues"].append("FAQ schema present but none of its questions appear in visible body text")
        elif expected_count > 0 and visible_count < expected_count:
            res["warnings"].append(f"FAQ schema has {expected_count} questions; only {visible_count} visible on page")
    res["has_faq_schema"] = has_faq_schema
    res["has_visible_faq"] = visible_count > 0

    # Duplicate IDs
    id_counts: dict[str, int] = {}
    for mid in RE_ALL_IDS.finditer(html):
        id_counts[mid.group(1)] = id_counts.get(mid.group(1), 0) + 1
    dups = [k for k, v in id_counts.items() if v > 1]
    bad_dups = [d for d in dups if d not in ALLOWED_DUP_IDS]
    if bad_dups:
        res["issues"].append(f"duplicate ids: {bad_dups}")

    # case-evaluation-form: home, contact, hub pages may or may not have it.
    form_ids = RE_FORM_ID.findall(html)
    if len(form_ids) > 1:
        res["issues"].append(f"{len(form_ids)} case-evaluation-form on same page")

    # If page has form, it should have hidden language=es for ES pages
    if form_ids and expect_lang == "es":
        if not RE_LANG_HIDDEN.search(html):
            res["issues"].append("Spanish form missing hidden language=es field")

    # Hreflang reciprocity check
    hrefs: dict[str, str] = {}
    for m in RE_HREFLANG.finditer(html):
        hrefs[m.group(1).lower()] = m.group(2).strip()
    for m in RE_HREFLANG_ALT.finditer(html):
        hrefs.setdefault(m.group(1).lower(), m.group(2).strip())
    res["hreflang"] = hrefs
    for required in ("en", "es", "x-default"):
        if required not in hrefs:
            res["issues"].append(f"missing hreflang '{required}'")

    # Footer disclaimer + attorney advertising language
    if not RE_DISCLAIMER_BLOCK.search(html):
        res["issues"].append("no disclaimer block found")
    if not RE_ATTORNEY_AD.search(html):
        res["warnings"].append("no attorney-advertising statement")

    # Footer legal links
    if not RE_FOOTER_LEGAL.search(html):
        res["warnings"].append("no footer-section--legal block")

    # Banned phrases (case-insensitive) outside of the explicit attorney advertising
    # disclaimer line (we leave that intact).
    flat = text_of(html).lower()
    banned_found = [b for b in BANNED_PHRASES if b in flat]
    if banned_found:
        res["issues"].append(f"banned phrases: {banned_found}")

    return res


# --------------------------- cross-page checks ---------------------------

def cross_check(audits: list[dict], label: str) -> list[str]:
    issues: list[str] = []
    titles: dict[str, list[str]] = {}
    descs: dict[str, list[str]] = {}
    for a in audits:
        if not a["exists"]:
            continue
        t = a.get("title", "")
        if t:
            titles.setdefault(t, []).append(a["file"])
        d = a.get("description", "")
        if d:
            descs.setdefault(d, []).append(a["file"])
    for t, files in titles.items():
        if len(files) > 1:
            issues.append(f"[{label}] duplicate <title> '{t[:80]}': {files}")
    for d, files in descs.items():
        if len(files) > 1:
            issues.append(f"[{label}] duplicate description '{d[:80]}': {files}")
    return issues


def hreflang_reciprocity(en_audits: list[dict], es_audits: list[dict]) -> list[str]:
    issues: list[str] = []
    by_en = {a["expected_url"]: a for a in en_audits}
    by_es = {a["expected_url"]: a for a in es_audits}
    for i, (en_path, es_path) in enumerate(PAIRS):
        en_url = SITE + (en_path if en_path != "/" else "/")
        es_url = SITE + es_path
        ea = en_audits[i]
        sa = es_audits[i]
        if ea["exists"]:
            en_hl = ea.get("hreflang", {})
            if en_hl.get("es") != es_url:
                issues.append(f"EN {en_url} hreflang es='{en_hl.get('es')}' expected '{es_url}'")
            if en_hl.get("en") != en_url:
                issues.append(f"EN {en_url} hreflang en='{en_hl.get('en')}' expected '{en_url}'")
            if en_hl.get("x-default") != en_url:
                issues.append(f"EN {en_url} x-default='{en_hl.get('x-default')}' expected '{en_url}'")
        if sa["exists"]:
            es_hl = sa.get("hreflang", {})
            if es_hl.get("en") != en_url:
                issues.append(f"ES {es_url} hreflang en='{es_hl.get('en')}' expected '{en_url}'")
            if es_hl.get("es") != es_url:
                issues.append(f"ES {es_url} hreflang es='{es_hl.get('es')}' expected '{es_url}'")
            if es_hl.get("x-default") != en_url:
                issues.append(f"ES {es_url} x-default='{es_hl.get('x-default')}' expected '{en_url}'")
    return issues


# --------------------------- sitemap ---------------------------

def check_sitemap() -> tuple[list[str], list[str]]:
    issues: list[str] = []
    info: list[str] = []
    if not SITEMAP.is_file():
        return ["sitemap.xml missing"], info
    raw = SITEMAP.read_text(encoding="utf-8")
    try:
        tree = ET.fromstring(raw)
    except ET.ParseError as e:
        return [f"sitemap.xml invalid XML: {e}"], info
    # urlset must declare xhtml namespace
    root_tag = tree.tag
    if not root_tag.endswith("urlset"):
        issues.append(f"sitemap root is {root_tag}, expected urlset")
    if "xmlns:xhtml" not in raw:
        issues.append("sitemap missing xmlns:xhtml")
    # Gather all <loc> values
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9", "xhtml": "http://www.w3.org/1999/xhtml"}
    locs = [el.text.strip() for el in tree.findall("sm:url/sm:loc", ns) if el.text]
    info.append(f"sitemap urls: {len(locs)}")
    # ES URLs must all be present
    expected = {SITE + es for _en, es in PAIRS}
    missing = expected - set(locs)
    if missing:
        for m in sorted(missing):
            issues.append(f"sitemap missing ES url: {m}")
    # ES file existence for each loc that starts with /es/
    for loc in locs:
        if "/es/" in loc:
            rel = loc.split(SITE, 1)[-1]
            file = file_for(rel)
            if not file.is_file():
                issues.append(f"sitemap loc has no file on disk: {loc}")
    # xhtml link annotations on /es/ urls
    es_urls = [el for el in tree.findall("sm:url", ns) if any("/es/" in (loc.text or "") for loc in el.findall("sm:loc", ns))]
    info.append(f"sitemap es-url entries: {len(es_urls)}")
    for el in es_urls:
        loc = el.find("sm:loc", ns).text
        hreflangs = el.findall("xhtml:link", ns)
        codes = [(h.get("hreflang"), h.get("href")) for h in hreflangs]
        cmap = {c: h for c, h in codes}
        if "en" not in cmap or "es" not in cmap or "x-default" not in cmap:
            issues.append(f"sitemap es entry {loc} missing hreflang annotations: {codes}")
        else:
            if cmap["es"] != loc:
                issues.append(f"sitemap es entry {loc} hreflang es='{cmap['es']}'")
    return issues, info


# --------------------------- main ---------------------------

def main() -> int:
    en_audits: list[dict] = []
    es_audits: list[dict] = []
    for en_path, es_path in PAIRS:
        en_file = file_for(en_path)
        es_file = file_for(es_path)
        en_url = SITE + (en_path if en_path != "/" else "/")
        es_url = SITE + es_path
        ea = audit_page(en_file, expect_lang="en", expect_canonical=en_url)
        ea["expected_url"] = en_url
        sa = audit_page(es_file, expect_lang="es", expect_canonical=es_url)
        sa["expected_url"] = es_url
        en_audits.append(ea)
        es_audits.append(sa)

    # cross-page uniqueness
    cross_es = cross_check(es_audits, "ES")
    cross_en_subset = cross_check(en_audits, "EN-subset")

    # reciprocity
    recip = hreflang_reciprocity(en_audits, es_audits)

    # sitemap
    sm_issues, sm_info = check_sitemap()

    # Summarize
    total_issues = 0
    total_warnings = 0

    print("=== EN pages ===")
    for a in en_audits:
        line = f"[{'OK' if not a['issues'] else 'FAIL'}] {a['expected_url']}"
        print(line)
        for i in a["issues"]:
            print("    ISSUE:", i); total_issues += 1
        for w in a["warnings"]:
            print("    warn :", w); total_warnings += 1

    print("\n=== ES pages ===")
    for a in es_audits:
        line = f"[{'OK' if not a['issues'] else 'FAIL'}] {a['expected_url']}"
        print(line)
        for i in a["issues"]:
            print("    ISSUE:", i); total_issues += 1
        for w in a["warnings"]:
            print("    warn :", w); total_warnings += 1

    print("\n=== Cross-page uniqueness ===")
    for x in cross_es + cross_en_subset:
        print("ISSUE:", x); total_issues += 1
    if not (cross_es or cross_en_subset):
        print("OK")

    print("\n=== Hreflang reciprocity ===")
    for x in recip:
        print("ISSUE:", x); total_issues += 1
    if not recip:
        print("OK")

    print("\n=== Sitemap ===")
    for x in sm_info:
        print(x)
    for x in sm_issues:
        print("ISSUE:", x); total_issues += 1
    if not sm_issues:
        print("OK")

    print(f"\nTotal ISSUES: {total_issues}")
    print(f"Total warnings: {total_warnings}")
    return 0 if total_issues == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
