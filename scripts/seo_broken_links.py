#!/usr/bin/env python3
"""Find internal /href targets that have no matching static file (heuristic)."""
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RE_HREF = re.compile(r'href=(["\'])([^"\']+)\1', re.I)
SKIP_PARTS = {"_old-site-extract", "_dev", "components", "node_modules", "social-assets"}


def build_valid_paths() -> set[str]:
    valid: set[str] = {"/", ""}
    for p in ROOT.rglob("index.html"):
        rel = p.relative_to(ROOT)
        if any(x in rel.parts for x in SKIP_PARTS):
            continue
        parts = rel.parts
        if len(parts) == 1:
            continue
        path = "/" + "/".join(parts[:-1]).replace("\\", "/")
        valid.add(path)
        valid.add(path + "/")
    for p in ROOT.glob("*.html"):
        valid.add("/" + p.name)
        valid.add("/" + p.name.replace(".html", ""))
    return valid


def target_exists(href: str, valid: set[str]) -> bool:
    h = href.strip()
    if not h.startswith("/") or h.startswith("//"):
        return True
    h = h.split("#")[0].split("?")[0]
    if not h or h == "/":
        return True
    if any(h.startswith(p) for p in ("/images/", "/styles/", "/scripts/", "/assets/")):
        return True
    if h.endswith((".css", ".js", ".ico", ".png", ".jpg", ".jpeg", ".webp", ".svg", ".pdf", ".xml")):
        return True
    key = h.rstrip("/")
    if key in valid or h in valid:
        return True
    if (key + "/") in valid:
        return True
    fs = ROOT / key.lstrip("/").replace("/", "\\")
    if (fs / "index.html").exists():
        return True
    if fs.with_suffix(".html").exists():
        return True
    return False


def main() -> None:
    valid = build_valid_paths()
    broken: list[tuple[str, str]] = []
    for p in ROOT.rglob("*.html"):
        rel = p.relative_to(ROOT)
        if any(x in rel.parts for x in SKIP_PARTS):
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for m in RE_HREF.finditer(text):
            h = m.group(2)
            if not target_exists(h, valid):
                broken.append((str(rel).replace("\\", "/"), h))
    c = Counter(b[1] for b in broken)
    print("Broken href count:", len(broken), "unique:", len(c))
    for u, n in c.most_common(40):
        print(f"  {n}x {u}")


if __name__ == "__main__":
    main()
