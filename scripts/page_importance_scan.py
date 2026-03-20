#!/usr/bin/env python3
"""Scan sitemap URLs: word count, title, redirect target (vercel), cluster tag."""
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

def _find_site_root() -> Path:
    """Resolve repo root even if this folder is a junction/symlink."""
    p = Path(__file__).resolve().parent
    for _ in range(8):
        if (p / "sitemap.xml").exists() and (p / "index.html").exists():
            ix = (p / "index.html").read_text(encoding="utf-8", errors="replace")[:2500]
            if "www.insiderlawyers.com" in ix and "Insider Accident" in ix:
                return p
        p = p.parent
    return Path(__file__).resolve().parents[1]


ROOT = _find_site_root()
BASE = "https://www.insiderlawyers.com"
RE_TITLE = re.compile(r"<title[^>]*>([^<]*)</title>", re.I | re.S)
TAG_STRIP = re.compile(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>|<[^>]+>")


def load_redirect_sources() -> dict[str, str]:
    import json as j

    vj = ROOT / "vercel.json"
    data = j.loads(vj.read_text(encoding="utf-8"))
    out = {}
    for r in data.get("redirects", []):
        src = r["source"].rstrip("/")
        out[src] = r["destination"]
    return out


def url_to_relpath(url_path: str) -> Path | None:
    p = url_path.strip("/")
    if not p:
        return ROOT / "index.html"
    d = ROOT / p.replace("/", "\\")
    if (d / "index.html").exists():
        return d / "index.html"
    if d.suffix == ".html" and d.exists():
        return d
    f = ROOT / (p + ".html")
    if f.exists():
        return f
    return None


def body_word_count(html: str) -> int:
    low = html.lower()
    if "<body" not in low:
        return 0
    body = low.split("<body", 1)[1].rsplit("</body>", 1)[0]
    text = TAG_STRIP.sub(" ", body)
    return len([w for w in re.split(r"\s+", text) if len(w) > 2])


def cluster(path: str) -> str:
    if path in ("/",):
        return "home"
    if path.startswith("/legal/"):
        return "legal"
    if path.startswith("/lit-referral"):
        return "referral"
    if path.startswith("/personal-injury/"):
        return "pi-silo"
    if path == "/personal-injury":
        return "pi-hub"
    if "nursing-home" in path or "bed-sore" in path or "bed-sores" in path or "pressure-ulcer" in path:
        return "nursing-home"
    if "premises" in path or "slip" in path or "negligent-security" in path:
        return "premises"
    if (
        "car-accident" in path
        or "motorcycle" in path
        or "truck" in path
        or "pedestrian" in path
        or "bicycle" in path
        or "uber" in path
        or "lyft" in path
        or "rear-end" in path
        or "t-bone" in path
        or "hit-and-run" in path
        or "uninsured" in path
        or "motor-vehicle" in path
        or "parking-lot" in path
        or "scooter" in path
        or "ebike" in path
        or path.startswith("/los-angeles-")
    ):
        return "motor-auto"
    if "insurance" in path or "adjuster" in path or "settlement" in path or "demand-letter" in path or "lowball" in path:
        return "insurance-claims"
    if "wrongful-death" in path:
        return "wrongful-death"
    return "general-pi"


def main() -> None:
    redir = load_redirect_sources()
    tree = ET.parse(ROOT / "sitemap.xml")
    rows = []
    for el in tree.iter():
        if not el.tag.endswith("loc") or not el.text:
            continue
        loc = el.text.strip()
        path = loc.replace(BASE, "").split("?")[0].rstrip("/") or "/"
        fp = url_to_relpath(path)
        wc = title = ""
        if fp and fp.exists():
            html = fp.read_text(encoding="utf-8", errors="replace")
            wc = body_word_count(html)
            m = RE_TITLE.search(html)
            title = (m.group(1).strip() if m else "")[:70]
        rkey = path.rstrip("/") or "/"
        redirect_to = redir.get(rkey) or redir.get(path + "/")
        rows.append(
            {
                "path": path,
                "words": wc,
                "title": title,
                "cluster": cluster(path),
                "302_to": redirect_to or "",
            }
        )

    out = ROOT / "docs" / "page-importance-data.json"
    out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    # summary stats
    thin = [r for r in rows if r["words"] and r["words"] < 900]
    with302 = [r for r in rows if r["302_to"]]
    print("URLs in sitemap:", len(rows))
    print("With 302 redirect:", len(with302))
    print("Body words < 900:", len(thin))
    print("wrote", out)


if __name__ == "__main__":
    main()
