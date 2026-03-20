# -*- coding: utf-8 -*-
"""Apply global header/footer chrome and normalize body scripts (static HTML)."""
from __future__ import annotations

import re
import sys
from pathlib import Path


def site_root() -> Path:
    here = Path(__file__).resolve()
    candidates = [here.parent.parent, Path.cwd(), *here.parents]
    for base in candidates:
        p = Path(base).resolve()
        for _ in range(24):
            if (
                (p / "sitemap.xml").is_file()
                and (p / "styles" / "main.css").is_file()
                and (p / "index.html").is_file()
            ):
                return p
            if p.parent == p:
                break
            p = p.parent
    raise SystemExit("Could not find site root.")


ROOT = site_root()
COMP = ROOT / "components"
CHROME_PATH = COMP / "global-chrome-before-main.html"
FOOTER_PATH = COMP / "global-footer.html"

SLIM_TRACK_SCRIPT = """
<script>
document.addEventListener("DOMContentLoaded", function () {
  window.dataLayer = window.dataLayer || [];
  document.querySelectorAll('a[href^="tel:"]').forEach(function (el) {
    el.addEventListener("click", function () {
      window.dataLayer.push({
        event: "phone_click",
        phone_number: (this.getAttribute("href") || "").replace("tel:", ""),
        page_path: location.pathname,
      });
    });
  });
  setTimeout(function () {
    window.dataLayer.push({ event: "engaged_30s" });
  }, 30000);
});
</script>
""".strip()


def clean_prefix_scripts(prefix: str) -> str:
    def repl(m: re.Match[str]) -> str:
        s = m.group(0)
        if "header--hidden" in s:
            return ""
        if (
            "mobile-menu-toggle" in s
            and "header-nav-wrap" in s
            and "case-evaluation-form" not in s
            and "form_next" not in s.lower()
            and "hero-phone" not in s
        ):
            return ""
        return s

    return re.sub(r"<script[\s\S]*?</script>", repl, prefix, flags=re.I)


def inject_slim_tracking(prefix: str) -> str:
    if "engaged_30s" in prefix and "phone_click" in prefix:
        return prefix
    slim = SLIM_TRACK_SCRIPT + "\n"
    m = re.search(r"</noscript>", prefix, flags=re.I)
    if m:
        return prefix[: m.end()] + "\n" + slim + prefix[m.end() :]
    m2 = re.search(r"<body[^>]*>", prefix, flags=re.I)
    if m2:
        return prefix[: m2.end()] + "\n" + slim + prefix[m2.end() :]
    return slim + prefix


def replace_chrome(html: str, chrome: str) -> str | None:
    lower = html.lower()
    if "<main" not in lower:
        return None
    pre, post = html.split("<main", 1)
    hi = lower.rfind("<header")
    if hi == -1:
        return None
    prefix = pre[:hi]
    prefix = clean_prefix_scripts(prefix)
    prefix = inject_slim_tracking(prefix)
    return prefix + chrome + "\n<main" + post


def replace_chrome_home(html: str, chrome: str) -> str | None:
    marker = '<section class="hero hero-section"'
    if marker not in html:
        return None
    pre, post = html.split(marker, 1)
    lower = pre.lower()
    hi = lower.rfind("<header")
    if hi == -1:
        return None
    prefix = pre[:hi]
    prefix = clean_prefix_scripts(prefix)
    prefix = inject_slim_tracking(prefix)
    return prefix + chrome + "\n" + marker + post


def replace_footer(html: str, footer: str) -> str:
    if "<footer" not in html.lower():
        return html
    return re.sub(r"<footer\b[\s\S]*?</footer>\s*", footer + "\n", html, count=1, flags=re.I)


def normalize_body_end(html: str) -> str:
    html = re.sub(
        r'<script\s+src="/scripts/site-nav\.js[^"]*"\s*defer>\s*</script>\s*',
        "",
        html,
        flags=re.I,
    )
    html = re.sub(
        r'<script\s+src="/scripts/utm-gclid-tracking\.js">\s*</script>\s*',
        "",
        html,
        flags=re.I,
    )
    html = re.sub(r"</div>v>\s*", "</div>\n", html, flags=re.I)
    needle = "</body>"
    idx = html.lower().rfind(needle)
    if idx == -1:
        return html
    insert = (
        '<script src="/scripts/site-nav.js?v=3" defer></script>\n'
        '<script src="/scripts/utm-gclid-tracking.js"></script>\n'
    )
    return html[:idx] + insert + html[idx:]


def should_process(path: Path) -> bool:
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    if rel.startswith("components/"):
        return False
    if "/legal/" in "/" + rel + "/":
        pass
    return path.suffix.lower() == ".html"


def main() -> None:
    chrome = CHROME_PATH.read_text(encoding="utf-8")
    footer = FOOTER_PATH.read_text(encoding="utf-8")
    changed: list[str] = []
    skipped: list[str] = []
    for path in sorted(ROOT.rglob("*.html")):
        if not should_process(path):
            continue
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        raw = path.read_text(encoding="utf-8", errors="replace")
        out = raw
        out = replace_footer(out, footer)
        new = replace_chrome(out, chrome)
        if new is None:
            new = replace_chrome_home(out, chrome)
        if new is None:
            skipped.append(rel)
            out = normalize_body_end(out)
            if out != raw:
                path.write_text(out, encoding="utf-8")
                changed.append(rel + " (footer/scripts only)")
            continue
        out = new
        out = normalize_body_end(out)
        if out != raw:
            path.write_text(out, encoding="utf-8")
            changed.append(rel)
    print("Updated", len(changed), "files")
    if skipped:
        print("Skipped (no <header>/<main>):", len(skipped))
        for s in skipped[:15]:
            print(" ", s)


if __name__ == "__main__":
    main()
    sys.exit(0)
