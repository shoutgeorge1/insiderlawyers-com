# -*- coding: utf-8 -*-
# For every page that has FAQPage JSON-LD whose questions are NOT already
# visible on the page, render a visible <section class="seo-faq"> block
# from the existing schema. This makes the FAQ schema compliant with
# Google's policy without fabricating content — the Q&A copy is the same as
# what the schema already declares.
#
# Idempotent. Inserts a marker block and reuses it on subsequent runs.
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\georgea\insiderlawyer-com-lps\insiderlawyers-com")
EXCLUDED_DIRS = {
    "_dev", "_old-site-extract", "scripts", "components", "social-assets",
    "docs", "node_modules", ".git", ".cursor", "reports", "assets",
}

RE_JSONLD = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.I | re.S,
)
RE_BODY_END = re.compile(r"</main>|</body>", re.I)
RE_FAQ_BLOCK = re.compile(
    r"<!-- SEO_FAQ_START -->[\s\S]*?<!-- SEO_FAQ_END -->", re.I,
)


def discover() -> list[Path]:
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


def collect_faq_questions(node, out):
    if isinstance(node, dict):
        if node.get("@type") == "FAQPage":
            entities = node.get("mainEntity") or []
            if isinstance(entities, list):
                for e in entities:
                    if isinstance(e, dict) and e.get("@type") == "Question":
                        q = e.get("name", "")
                        a = ""
                        ans = e.get("acceptedAnswer")
                        if isinstance(ans, dict):
                            a = ans.get("text", "")
                        if isinstance(q, str) and isinstance(a, str) and q and a:
                            out.append((q, a))
        for v in node.values():
            collect_faq_questions(v, out)
    elif isinstance(node, list):
        for x in node:
            collect_faq_questions(x, out)


def html_escape(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def render_faq_block(faqs: list[tuple[str, str]], language: str) -> str:
    heading = "Preguntas frecuentes" if language == "es" else "Frequently Asked Questions"
    parts = ["<!-- SEO_FAQ_START -->",
             '<section class="seo-faq" aria-label="' + heading + '"'
             ' style="margin:2rem auto;max-width:920px;padding:1.5rem 1rem;">',
             f'  <h2 style="font-size:1.5rem;margin-bottom:1rem;color:#01366c;">{heading}</h2>']
    for q, a in faqs:
        parts.append('  <details style="border-top:1px solid #e5e7eb;padding:0.75rem 0;">')
        parts.append(
            f'    <summary style="font-weight:600;cursor:pointer;list-style:none;color:#01366c;">{html_escape(q)}</summary>'
        )
        parts.append(
            f'    <p style="margin-top:0.5rem;color:#374151;line-height:1.55;">{html_escape(a)}</p>'
        )
        parts.append('  </details>')
    parts.append('</section>')
    parts.append('<!-- SEO_FAQ_END -->')
    return "\n".join(parts)


def page_questions_already_visible(html_no_scripts: str, faqs: list[tuple[str, str]]) -> bool:
    """All questions appear in visible text? (loose check)"""
    plain = re.sub(r"<[^>]+>", " ", html_no_scripts)
    plain = re.sub(r"\s+", " ", plain).lower()
    for q, _ in faqs:
        norm = re.sub(r"[^\w]+", " ", q.lower()).strip()
        norm = " ".join(norm.split())
        tokens = norm.split()[:6]
        if not tokens:
            continue
        needle = " ".join(tokens)
        if needle and needle not in re.sub(r"[^\w]+", " ", plain):
            return False
    return True


def detect_lang(p: Path) -> str:
    rel = p.relative_to(ROOT).as_posix()
    return "es" if rel.startswith("es/") or rel == "es/index.html" else "en"


def process(p: Path) -> str | None:
    raw = p.read_bytes()
    html = raw.decode("utf-8", errors="replace")
    blocks = RE_JSONLD.findall(html)
    if not blocks:
        return None
    faqs: list[tuple[str, str]] = []
    for b in blocks:
        try:
            data = json.loads(b.strip())
        except json.JSONDecodeError:
            continue
        collect_faq_questions(data, faqs)
    if not faqs:
        return None
    # Strip <script> blocks before checking visibility
    html_no_scripts = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    html_no_scripts = re.sub(r"<style[\s\S]*?</style>", " ", html_no_scripts, flags=re.I)
    # Strip our SEO_FAQ section from the visibility check so re-runs don't
    # become trivially-visible-because-already-rendered.
    html_for_check = RE_FAQ_BLOCK.sub("", html_no_scripts)
    if page_questions_already_visible(html_for_check, faqs):
        return None
    language = detect_lang(p)
    block = render_faq_block(faqs, language)
    if RE_FAQ_BLOCK.search(html):
        new_html = RE_FAQ_BLOCK.sub(block, html, count=1)
        action = "updated"
    else:
        m = RE_BODY_END.search(html)
        if not m:
            return None
        new_html = html[: m.start()] + block + "\n\n" + html[m.start():]
        action = "added"
    if new_html != html:
        p.write_bytes(new_html.encode("utf-8"))
        return action
    return None


def main() -> int:
    pages = discover()
    added = 0
    updated = 0
    for p in pages:
        action = process(p)
        if action == "added":
            added += 1
            print(f"  + {p.relative_to(ROOT).as_posix()}")
        elif action == "updated":
            updated += 1
    print(f"\nFAQ blocks added: {added}, updated: {updated}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
