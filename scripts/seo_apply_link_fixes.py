#!/usr/bin/env python3
"""Apply safe internal href fixes (broken legacy slugs). Idempotent."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {"components", "_dev", "_old-site-extract", "node_modules"}

REPLACEMENTS: list[tuple[str, str]] = [
    ('href="/personal-injury-lawyer-los-angeles/"', 'href="/personal-injury"'),
    ('href="/personal-injury-lawyer-los-angeles"', 'href="/personal-injury"'),
    ('href="/premises-liability-lawyer-los-angeles/"', 'href="/premises-liability"'),
    ('href="/premises-liability-lawyer-los-angeles"', 'href="/premises-liability"'),
    ('href="/slip-and-fall/"', 'href="/personal-injury/slip-and-fall"'),
    ('href="/slip-and-fall"', 'href="/personal-injury/slip-and-fall"'),
    ('href="/los-angeles-personal-injury-lawyer"', 'href="/personal-injury"'),
    ('href="/los-angeles-personal-injury"', 'href="/personal-injury"'),
    ('href="/should-i-go-to-er-after-accident"', 'href="/delayed-pain-after-car-accident"'),
    ('href="/insurance-claims/injuries-truck-accidents"', 'href="/injuries-truck-accidents"'),
]
# Fix visible link text that echoed broken paths (same line in Related Resources)
TEXT_FIXES: list[tuple[str, str]] = [
    ('>/personal-injury-lawyer-los-angeles/</a>', '>Personal injury overview</a>'),
    ('>/premises-liability-lawyer-los-angeles/</a>', '>Premises liability (Los Angeles)</a>'),
    ('>/slip-and-fall/</a>', '>Slip and fall claims</a>'),
]


def main() -> None:
    n = 0
    for p in ROOT.rglob("*.html"):
        if any(x in p.parts for x in SKIP):
            continue
        text = p.read_text(encoding="utf-8")
        orig = text
        for a, b in REPLACEMENTS + TEXT_FIXES:
            text = text.replace(a, b)
        if text != orig:
            p.write_text(text, encoding="utf-8")
            n += 1
            print("updated", p.relative_to(ROOT))
    print("files changed:", n)


if __name__ == "__main__":
    main()
