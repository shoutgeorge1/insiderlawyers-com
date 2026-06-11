"""Sweep remaining body-text 'Insider Accident Lawyers' references.

The first cleanup pass handled the most common patterns. This sweeps the long
tail of body sentences that still mention 'Insider Accident Lawyers' or use
firm-voice 'we' wording. It uses regex patterns to catch variant whitespace
and unicode dashes, and it preserves the required corporate disclosure
('operated in connection with Countrywide Trial Lawyers ... DBA Insider
Accident Lawyers') because that line is intentional.

Safe to re-run.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKIP_DIR_PARTS = {"_old-site-extract", "_dev", "node_modules", "components", "scripts", "styles"}


# Regex patterns and their replacements. Each tuple is (compiled regex, replacement).
# We deliberately keep the corporate "Countrywide Trial Lawyers ... DBA Insider
# Accident Lawyers" disclosure line untouched - that is the required operating
# entity disclosure in the global footer.
PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # "Insider Accident Lawyers handles X" - body sentence framing
    (
        re.compile(r"Insider Accident Lawyers handles ([^.]+?)\.", re.IGNORECASE),
        r"This guide covers \1 under California law.",
    ),
    # "Contact Insider Accident Lawyers to discuss your X" (anything)
    (
        re.compile(r"Contact Insider Accident Lawyers to discuss ([^.]+?)\.", re.IGNORECASE),
        r"Request a free claim review to discuss \1.",
    ),
    # "Call Insider Accident Lawyers now/today for X"
    (
        re.compile(r"Call Insider Accident Lawyers (?:now|today) for ([^.]+?)\.", re.IGNORECASE),
        r"Request a free claim review for \1.",
    ),
    # "Insider Accident Lawyers can help with X"
    (
        re.compile(r"Insider Accident Lawyers can help (?:with )?([^.]+?)\.", re.IGNORECASE),
        r"A free claim review can help with \1.",
    ),
    # "Insider Accident Lawyers is a / are a Los Angeles ... firm" generic
    (
        re.compile(r"Insider Accident Lawyers (?:is|are) a [^.]+?\.", re.IGNORECASE),
        r"This page is a neutral California injury claim resource.",
    ),
    # "Insider Accident Lawyers prepares ... cases ..."
    (
        re.compile(r"Insider Accident Lawyers prepares ([^.]+?)\.", re.IGNORECASE),
        "Strong California claims are prepared as if they could be tried in court \u2014 \\g<1> follows the same principle.",
    ),
    # "(no fee unless we win)" trailing sales tagline
    (
        re.compile(r"\s*[;.]?\s*[Nn]o fee unless we win\.?", re.IGNORECASE),
        r".",
    ),
    # "Free case review 24/7" sales tagline → neutral
    (
        re.compile(r"Free case review 24/7\.?", re.IGNORECASE),
        r"Free claim review available 24/7.",
    ),
    # "We focus on X, the same approach we use ..."
    (
        re.compile(
            r"We focus on ([^.]+?)[\u2014\u2013\-]+ ?the same (?:trial-ready )?approach we use ([^.]+?)\.",
            re.IGNORECASE,
        ),
        r"California claims of this kind turn on \1.",
    ),
    # "the same approach we use for every serious injury case"
    (
        re.compile("\u2014the same approach we use for every serious injury case", re.IGNORECASE),
        "\u2014the approach strong California injury claims usually take",
    ),
    # "Insider Accident Lawyers builds X cases with Y" - generic hero-note framing
    (
        re.compile(r"Insider Accident Lawyers builds ([^.]+?)\.", re.IGNORECASE),
        r"Strong California claims of this kind are built with \1.",
    ),
    # "Insider Accident Lawyers structures X cases around Y"
    (
        re.compile(r"Insider Accident Lawyers structures ([^.]+?)\.", re.IGNORECASE),
        r"Strong California claims of this kind are structured around \1.",
    ),
    # "Insider Accident Lawyers develops X files around Y"
    (
        re.compile(r"Insider Accident Lawyers develops ([^.]+?)\.", re.IGNORECASE),
        r"Strong California claims of this kind are developed around \1.",
    ),
    # "Insider Accident Lawyers treats X as Y"
    (
        re.compile(r"Insider Accident Lawyers treats ([^.]+?)\.", re.IGNORECASE),
        r"Strong California injury claims treat \1.",
    ),
    # "Insider Accident Lawyers approaches X as Y"
    (
        re.compile(r"Insider Accident Lawyers approaches ([^.]+?)\.", re.IGNORECASE),
        r"Strong California injury claims approach \1.",
    ),
    # "Insider Accident Lawyers focuses on X"
    (
        re.compile(r"Insider Accident Lawyers focuses on ([^.]+?)\.", re.IGNORECASE),
        r"Strong California injury claims focus on \1.",
    ),
    # "Insider Accident Lawyers represents X"
    (
        re.compile(r"Insider Accident Lawyers represents ([^.]+?)\.", re.IGNORECASE),
        r"California trial attorneys behind this resource handle \1.",
    ),
    # "Insider Accident Lawyers provides X" (sales)
    (
        re.compile(r"Insider Accident Lawyers provides ([^.]+?)\.", re.IGNORECASE),
        r"This resource supports \1.",
    ),
    # "Insider Accident Lawyers is available 24/7 ..."
    (
        re.compile(r"Insider Accident Lawyers is available 24/7\.?\s*", re.IGNORECASE),
        r"Free claim review is available 24/7. ",
    ),
    # "Insider Accident Lawyers works on contingency: no fee unless we recover."
    (
        re.compile(
            r"Insider Accident Lawyers works on contingency[:.,]?\s*no fee unless we recover\.?\s*",
            re.IGNORECASE,
        ),
        r"California injury attorneys often work on contingency, meaning no fee unless the case recovers. ",
    ),
    # "Insider Accident Lawyers is committed to making this website accessible ..."
    (
        re.compile(r"Insider Accident Lawyers is committed to making this website ([^.]+?)\.", re.IGNORECASE),
        r"Insider Lawyers is committed to making this website \1.",
    ),
    # "Call Insider Accident Lawyers for a free bilingual X." - common CTA in hero-note pages
    (
        re.compile(r"Call Insider Accident Lawyers for a free bilingual ([^.]+?)\.", re.IGNORECASE),
        r"Request a free claim review for \1.",
    ),
    # "Contact Insider Accident Lawyers (now/today)? for a free bilingual X."
    (
        re.compile(
            r"Contact Insider Accident Lawyers(?:\s+(?:now|today))? for a free bilingual ([^.]+?)\.",
            re.IGNORECASE,
        ),
        r"Request a free claim review for \1.",
    ),
    # "Contact Insider Accident Lawyers (now)? for X." (fallback)
    (
        re.compile(
            r"Contact Insider Accident Lawyers(?:\s+(?:now|today))? for ([^.]+?)\.",
            re.IGNORECASE,
        ),
        r"Request a free claim review for \1.",
    ),
    # "Speak with Insider Accident Lawyers now for X."
    (
        re.compile(r"Speak with Insider Accident Lawyers(?:\s+(?:now|today))? for ([^.]+?)\.", re.IGNORECASE),
        r"Request a free claim review for \1.",
    ),
    # "contact Insider Accident Lawyers. See ..." (referral-style links)
    (
        re.compile(r"contact Insider Accident Lawyers\.", re.IGNORECASE),
        r"request a free claim review.",
    ),
    # "For help proving your case, contact Insider Accident Lawyers" (lowercase entry)
    # already handled above by the "contact Insider Accident Lawyers." pattern
    # JSON-LD schema: "name": "Insider Accident Lawyers"  ->  "Insider Lawyers"
    (
        re.compile(r'"name"\s*:\s*"Insider Accident Lawyers"'),
        r'"name": "Insider Lawyers"',
    ),
    # Inline body refs: "with Insider Accident Lawyers" / "from Insider Accident Lawyers"
    (
        re.compile(r"\bwith Insider Accident Lawyers\b", re.IGNORECASE),
        r"with the California trial attorneys behind this resource",
    ),
    (
        re.compile(r"\bfrom Insider Accident Lawyers\b", re.IGNORECASE),
        r"from the California trial attorneys behind this resource",
    ),
    # Sales fragments: "no fee unless we recover" (independent)
    (
        re.compile(r"\s*[,;.:\-]?\s*no fee unless we recover\.?", re.IGNORECASE),
        r".",
    ),
    # Sales fragment: "As former insurance defense lawyers, we" - reframe
    (
        re.compile(r"As former insurance defense lawyers,\s*we ", re.IGNORECASE),
        r"The California trial attorneys behind this resource have insurance-defense experience, so they ",
    ),
]


# Replacements that don't need regex - just plain string swaps used for the
# title-section/og branding remnants on a few specific pages.
PLAIN_REPLACEMENTS: list[tuple[str, str]] = [
    # Footer trust-line / open-graph branding that was missed.
    ("\"og:site_name\" content=\"Insider Accident Lawyers\"", "\"og:site_name\" content=\"Insider Lawyers\""),
    # Inline meta references already mostly cleaned, but catch the legal disclosure-prefixed
    # alternate phrasing some pages still have inline in body text (not the footer disclosure).
    ("the law firm of Insider Accident Lawyers", "the California trial attorneys behind this resource"),
    ("the team at Insider Accident Lawyers", "the California trial attorneys behind this resource"),
]


def is_live_html(path: Path) -> bool:
    rel_parts = path.relative_to(ROOT).parts
    if path.suffix.lower() != ".html":
        return False
    for part in rel_parts:
        if part in SKIP_DIR_PARTS:
            return False
    return True


def is_corporate_disclosure_line(line: str) -> bool:
    """Return True if a line is the required corporate disclosure we keep."""
    lower = line.lower()
    return (
        "countrywide trial lawyers" in lower
        and "dba insider accident lawyers" in lower
    )


def apply_patterns_outside_disclosure(html: str) -> str:
    """Apply regex replacements but skip lines containing the corporate disclosure."""
    lines = html.splitlines(keepends=True)
    out_lines: list[str] = []
    for line in lines:
        if is_corporate_disclosure_line(line):
            out_lines.append(line)
            continue
        new_line = line
        for pat, repl in PATTERNS:
            new_line = pat.sub(repl, new_line)
        for old, new in PLAIN_REPLACEMENTS:
            new_line = new_line.replace(old, new)
        out_lines.append(new_line)
    return "".join(out_lines)


def main() -> int:
    changed: list[str] = []
    for path in sorted(ROOT.rglob("*.html")):
        if not is_live_html(path):
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        out = apply_patterns_outside_disclosure(raw)
        if out != raw:
            path.write_text(out, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)).replace("\\", "/"))
    print(f"Sweep cleaned {len(changed)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
