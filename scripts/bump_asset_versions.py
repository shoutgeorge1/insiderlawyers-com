"""One-off cache-buster.

/styles/* and /scripts/* are served with `Cache-Control: immutable` for a
year (see vercel.json), so changing a file under the same URL never reaches
returning visitors. Bump the query-string version on the assets we changed
so browsers fetch the new copies:

  - styles/main.css?v=2        -> ?v=3   (sticky mobile header, etc.)
  - scripts/privacy-choices.js -> ?v=2   (ApexChat killer removed)

Walks every processed .html file (same skip rules as apply_global_layout).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKIP_DIR_PREFIXES = (
    "components/",
    "scripts/",
    "_old-site-extract/",
    "_dev/",
    "node_modules/",
    "social-assets/",
)

REPLACEMENTS = [
    ("/styles/main.css?v=2", "/styles/main.css?v=3"),
    ('/scripts/privacy-choices.js"', '/scripts/privacy-choices.js?v=2"'),
]


def should_process(path: Path) -> bool:
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    if any(rel.startswith(p) for p in SKIP_DIR_PREFIXES):
        return False
    if rel == "google0f074189c817401a.html":
        return False
    return path.suffix.lower() == ".html"


def main() -> None:
    changed = 0
    for path in ROOT.rglob("*.html"):
        if not should_process(path):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        new = text
        for old, repl in REPLACEMENTS:
            new = new.replace(old, repl)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed += 1
    print(f"Bumped asset versions in {changed} files")


if __name__ == "__main__":
    main()
