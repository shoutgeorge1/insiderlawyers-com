# Technical SEO audit — www.insiderlawyers.com (static HTML)

**Scope:** `insiderlawyers-com/` · **Audit date:** 2026-03-19 · **Method:** Automated crawl of 127 `.html` files (excluding `components/`, `_dev/`, `_old-site-extract/`, `social-assets/` utility HTML), link graph from `href`, comparison to `sitemap.xml`, manual review of `vercel.json` routing.

---

## Executive summary

The site is a **flat slug + silo** architecture (`/personal-injury/...`, `/premises-liability/...`, `/motor-vehicle/...`, `/legal/...`) with **Vercel `cleanUrls`** and an explicit **`rewrites` map**. **~125 indexable URLs** are listed in `sitemap.xml` (after fixes). Low indexation is consistent with **historically weak internal signals** (template-style duplicate meta, **dozens of broken internal hrefs** to non-existent slugs), **intentional 302 consolidation** of many LA URLs to the car-accident LP, and **Google quality thresholds**—not a single “smoking gun” like `robots.txt` blocking the site.

**Implemented in this pass:** broken link repair, legal-page canonicals + descriptions, deduped titles/meta on key PI subpages and referral cluster, **removed `thank-you` from sitemap** (page is `noindex`), **`Disallow: /social-assets/`** in `robots.txt`, footer link to `sitemap.xml`, reproducible audit scripts under `scripts/`.

---

## 1. Critical issues affecting indexation

| Issue | Evidence | Risk | Action taken |
|--------|-----------|------|----------------|
| **Broken internal links** (64 instances → **7 unique dead paths**) | Legacy slugs: `/personal-injury-lawyer-los-angeles/`, `/premises-liability-lawyer-los-angeles/`, `/slip-and-fall/`, `/los-angeles-personal-injury-lawyer`, `/insurance-claims/injuries-truck-accidents`, `/should-i-go-to-er-after-accident` | Crawlers and users hit **404**; PageRank/context lost | **Fixed** in 29 files → hubs: `/personal-injury`, `/premises-liability`, `/personal-injury/slip-and-fall`, `/injuries-truck-accidents`, `/delayed-pain-after-car-accident`; cleaned “Related Resources” anchor text where it echoed dead URLs |
| **`noindex` URL in sitemap** | `/thank-you` listed while `meta robots` = `noindex,follow` | Conflicting signals to Google | **Removed** `/thank-you` from `sitemap.xml` |
| **Duplicate `<title>` on money pages** | Same title on `/pedestrian-accident-lawyer-los-angeles` vs `/personal-injury/pedestrian-accidents`; same for premises | Near-duplicate SERP / consolidation risk | **Fixed** — PI subdirectory titles + meta now describe **guide/overview** vs **LA service** pages |
| **Mass duplicate meta descriptions** | Same paragraph on **5** attorney-referral pages | Weak differentiation | **Fixed** — unique `meta description` + matching `og:` / `twitter:` descriptions |

**Not “broken” but limits organic upside**

- **`vercel.json` 302 redirects** map many `/los-angeles-*-lawyer` URLs to **`/los-angeles-car-accident-lawyer`**. That is a **business/PPC choice** (do not remove without a strategy). It creates **many URLs that are not self-canonical** from a crawl perspective; Google generally consolidates on the target, but **topic pages do not stand alone** for those slugs.

---

## 2. Important issues affecting crawl efficiency

| Issue | Notes |
|--------|--------|
| **Utility HTML under `/social-assets/`** | Several `.html` previews; not in sitemap. **Now disallowed** in `robots.txt` to reduce accidental crawl waste. |
| **Two thank-you files** | `thank-you/index.html` and root `thank-you.html` — both `noindex`; forms may target one or the other. **Do not delete** without checking form actions. Optional later: **single canonical URL** + redirect (out of scope here). |
| **Large `vercel.json` rewrite list** | Maintenance-heavy; any new folder needs a rewrite pair. Consider generation from a manifest in a later phase (not implemented). |

---

## 3. Content / template quality signals (observed, minimal change this phase)

| Topic | Finding |
|--------|---------|
| **Thin body copy** | Heuristic (&lt;400 words in `<body>` after stripping tags): **one** page near threshold (`nursing-home-wrongful-death/index.html` ~396 words). Most pages are **not** thin by word count alone. |
| **Duplicate / near-duplicate intents** | Several LA “practice” URLs **302** to car accident — content duplication is **policy-driven**, not accidental. |
| **H1** | No pages with **0** or **&gt;1** H1 in automated scan (except GSC verification file). |
| **Legal pages** | Previously missing **canonical** and **meta description**; **fixed**. |

---

## 4. Internal linking issues

| Finding | Detail |
|---------|--------|
| **Orphan pages (href graph)** | Only **`/google0f074189c817401a.html`** (verification) and **`/thank-you.html`** had **zero** inbound `href` from other HTML files. Expected for verification; thank-you may still receive **form POST/redirect** traffic. |
| **Hub coverage** | Home **`index.html`** already includes a large **“Practice Areas & Topics”** block with many deep links. **Footer** now includes **`/sitemap.xml`** for discovery (primarily for crawlers). |
| **Nav** | `components/standard-header.html` links to hubs: Personal Injury, Car Accidents, Premises, key LPs. Many long-tail URLs rely on **home hub + in-content links** — still the main lever for phase 2. |

---

## 5. Sitemap / robots / canonical

| Asset | Status |
|--------|--------|
| **`robots.txt`** | `Allow: /` + **Sitemap** directive. **Added** `Disallow: /social-assets/`. |
| **`sitemap.xml`** | **124** URL entries after removing `thank-you`. Matches deployed indexable routes (extensionless). **GSC file** correctly **excluded** from sitemap. **Legal URLs** `lastmod` bumped for this release. |
| **Canonicals** | **Self-referencing** canonicals present on primary templates; **legal/** pages **completed** in this pass. |
| **`noindex`** | Only thank-you variants (intended). |

---

## 6. Quick wins implemented (safe)

1. Repair **broken internal links** (29 files).  
2. **Remove** `noindex` thank-you URL from **sitemap**.  
3. **`robots.txt`** — disallow **`/social-assets/`**.  
4. **Legal** — canonical + meta description on all four legal pages.  
5. **Unique titles + meta** for `/personal-injury/pedestrian-accidents` and `/personal-injury/premises-liability`.  
6. **Unique meta** (and OG/Twitter) for attorney referral cluster (5 pages).  
7. **Home footer** — link to **`/sitemap.xml`**.  
8. **`thank-you.html`** — distinct `<title>` to avoid duplicate title pairing with `/thank-you`.  
9. **Scripts** — `scripts/seo_technical_audit.py`, `scripts/seo_broken_links.py`, `scripts/seo_apply_link_fixes.py` (re-run after large edits).

---

## 7. Recommended next phase (not done here)

1. **Topic silo breadcrumbs** — consistent “Home → Silo → Page” links on long-tail URLs (template change, still no redesign).  
2. **302 vs 301** review on `vercel.json` — only where SEO should **permanently** consolidate; coordinate with PPC so **ad final URLs** stay valid.  
3. **Consolidate thank-you** — one public URL + redirect; verify all form `action` / thank-you paths.  
4. **Programmatic sitemap** — generate `sitemap.xml` from filesystem + rewrite rules to avoid drift.  
5. **GSC-driven** internal links from URLs that already get impressions.  
6. **Content differentiation** for URLs that 302 to car accident if those topics should rank on their own.

---

## 8. How to re-run checks

```bash
cd insiderlawyers-com
python scripts/seo_technical_audit.py   # writes docs/seo-audit-data.json
python scripts/seo_broken_links.py      # should report 0 broken after fixes
```

---

*This document is the audit deliverable; implementation details and file list are in the git commit / project changelog for this change set.*
