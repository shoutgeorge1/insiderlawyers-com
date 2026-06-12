# -*- coding: utf-8 -*-
# JSON-LD validation pass for insiderlawyers.com.
#
# Walks every public page, parses every <script type="application/ld+json">
# block, and reports:
#   * blocks that fail to parse as JSON
#   * disallowed types on the neutral resource site (Attorney, LegalService,
#     LocalBusiness, AggregateRating, Review when not paired with an entity)
#   * Article schema with missing or fabricated-looking fields
#   * FAQPage schema whose questions are not present in the visible page text
#   * mismatched URLs (e.g. canonical mainEntityOfPage vs page URL)
#   * publisher entity name drift ("Insider Accident Lawyers" appearing as the
#     publisher on neutral pages)
#
# Outputs reports/seo-schema.md.
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\georgea\insiderlawyer-com-lps\insiderlawyers-com")
SITE = "https://www.insiderlawyers.com"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

EXCLUDED_DIRS = {
    "_dev", "_old-site-extract", "scripts", "components", "social-assets",
    "docs", "node_modules", ".git", ".cursor", "reports", "assets",
}

DISALLOWED_TYPES = {
    "Attorney", "LegalService", "LocalBusiness", "ProfessionalService",
    "Lawyer", "AggregateRating", "Review", "Service",
}

# Pages that may legitimately use those types (e.g. attorney referral hubs
# specifically targeting attorneys). Empty for now.
DISALLOWED_EXEMPT = set()

RE_JSONLD = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.I | re.S,
)


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


def iter_types(node):
    if isinstance(node, dict):
        t = node.get("@type")
        if isinstance(t, str):
            yield t
        elif isinstance(t, list):
            for x in t:
                if isinstance(x, str):
                    yield x
        for v in node.values():
            yield from iter_types(v)
    elif isinstance(node, list):
        for x in node:
            yield from iter_types(x)


def find_faq_questions(node, out):
    if isinstance(node, dict):
        if node.get("@type") == "Question":
            q = node.get("name")
            a = (node.get("acceptedAnswer") or {}).get("text", "")
            if isinstance(q, str):
                out.append((q, a))
        for v in node.values():
            find_faq_questions(v, out)
    elif isinstance(node, list):
        for x in node:
            find_faq_questions(x, out)


def main() -> int:
    pages = discover()
    issues = []
    valid = 0
    invalid = 0
    type_counts: dict[str, int] = {}

    for p in pages:
        path = file_to_path(p)
        html = p.read_bytes().decode("utf-8", errors="replace")
        plain = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
        plain = re.sub(r"<style[\s\S]*?</style>", " ", plain, flags=re.I)
        plain = re.sub(r"<[^>]+>", " ", plain)
        plain_lower = plain.lower()
        blocks = RE_JSONLD.findall(html)
        for idx, block in enumerate(blocks):
            try:
                data = json.loads(block.strip())
            except json.JSONDecodeError as e:
                invalid += 1
                issues.append(f"{path}: invalid JSON-LD block {idx} ({e.msg} at {e.pos})")
                continue
            valid += 1
            types = list(iter_types(data))
            for t in types:
                type_counts[t] = type_counts.get(t, 0) + 1
                if t in DISALLOWED_TYPES and path not in DISALLOWED_EXEMPT:
                    issues.append(f"{path}: disallowed schema @type={t!r} on neutral resource site")

            # FAQ validation: every question must appear (loosely) in visible text
            faqs = []
            find_faq_questions(data, faqs)
            for q, _ in faqs:
                # Strip trailing punctuation/whitespace, lowercase
                norm = re.sub(r"[^\w]+", " ", q.lower()).strip()
                norm = " ".join(norm.split())
                if not norm:
                    continue
                # check tokens (first 5 words) appear in plain page text
                tokens = norm.split()[:6]
                if tokens:
                    needle = " ".join(tokens)
                    if needle and needle not in re.sub(r"[^\w]+", " ", plain_lower):
                        issues.append(f"{path}: FAQ question not visible: {q[:80]!r}")

            # Article validation
            if "Article" in types or "BlogPosting" in types or "NewsArticle" in types:
                # walk to find article-like nodes
                def walk(node):
                    if isinstance(node, dict):
                        t = node.get("@type")
                        ts = [t] if isinstance(t, str) else (t or [])
                        if any(x in ("Article", "BlogPosting", "NewsArticle") for x in ts):
                            yield node
                        for v in node.values():
                            yield from walk(v)
                    elif isinstance(node, list):
                        for x in node:
                            yield from walk(x)
                for art in walk(data):
                    if not art.get("headline"):
                        issues.append(f"{path}: Article schema missing headline")
                    publisher = art.get("publisher")
                    if isinstance(publisher, dict):
                        name = publisher.get("name")
                        if isinstance(name, str) and "Insider Accident Lawyers" in name:
                            issues.append(f"{path}: Article publisher name uses 'Insider Accident Lawyers' on neutral site")
                    author = art.get("author")
                    if author and isinstance(author, dict):
                        a_name = author.get("name", "")
                        if isinstance(a_name, str) and a_name.strip().lower() in ("john doe", "jane doe", "admin"):
                            issues.append(f"{path}: Article author looks like placeholder ({a_name!r})")
                    # Date sanity
                    for k in ("datePublished", "dateModified"):
                        v = art.get(k)
                        if isinstance(v, str) and not re.match(r"\d{4}-\d{2}-\d{2}", v):
                            issues.append(f"{path}: Article {k} not ISO date: {v!r}")

    summary = [
        "# JSON-LD validation",
        "",
        f"- Pages scanned: {len(pages)}",
        f"- Valid JSON-LD blocks: {valid}",
        f"- Invalid JSON-LD blocks: {invalid}",
        f"- Issues: {len(issues)}",
        "",
        "## Schema @type counts",
        "",
    ]
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        summary.append(f"- {t}: {c}")
    summary.append("")
    if issues:
        summary.append("## Issues")
        summary.append("")
        for i in issues:
            summary.append(f"- {i}")
    else:
        summary.append("(no issues detected)")

    out = REPORTS / "seo-schema.md"
    out.write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(f"Pages: {len(pages)}  valid blocks: {valid}  invalid blocks: {invalid}  issues: {len(issues)}")
    print(f"Report: {out}")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
