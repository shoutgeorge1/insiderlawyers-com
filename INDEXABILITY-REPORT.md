# Indexability Analysis Report — insiderlawyers-com

**Scope:** All HTML pages in `insiderlawyers-com/` (excluded: `_old-site-extract`, `components`, `_dev`, `social-assets`).  
**Data source:** `INDEXABILITY-ANALYSIS.txt` (script-based crawl).  
**Purpose:** Identify why many pages may not be indexed and recommend fixes.

---

## Summary of checks

| Check | Result |
|-------|--------|
| **Pages with no internal links (to them)** | 1 orphan: `/thank-you/` (intentional — form confirmation). |
| **Duplicate / thin content** | 2 pages under ~700 words; 18+ LA lawyer pages with nearly identical word counts (~1,440) — template/duplicate content risk. |
| **Pages under ~700 words** | 3: `thank-you` (83), `motor-vehicle/bus-accident-lawyer-los-angeles` (676), `premises-liability/negligent-security-lawyer-los-angeles` (638). |
| **No canonical tag** | 4: all under `legal/` — `accessibility`, `disclaimer`, `results-disclaimer`, `terms`. |
| **No meta title** | 0 — every page has a `<title>`. |
| **Blocked by robots / meta noindex** | 2: `thank-you.html`, `thank-you/index.html` (intentional). |
| **Not reachable from main navigation** | 1: `/thank-you/` (only reached after form submit; not in nav by design). |

---

## 1. Likely indexable pages

Pages that have **canonical**, **title**, **no noindex**, **≥700 words**, and are **reachable from the main nav** (or linked from other content):

- **Home:** `/` (index.html)
- **Category hubs:** `/personal-injury/`, `/motor-vehicle/`, `/premises-liability/`, `/attorney-referrals/`, `/settlements/`
- **Practice-area pages:** All under `/personal-injury/*` (e.g. auto-accidents, truck-accidents, brain-injuries, wrongful-death, slip-and-fall, etc.) and the two silo sub-pages `/motor-vehicle/bus-accident-lawyer-los-angeles/`, `/premises-liability/negligent-security-lawyer-los-angeles/` (they are in nav and have canonical/title; thin word count is a separate risk)
- **After-accident / insurance / claims:** e.g. `/what-to-do-after-car-accident-california/`, `/uninsured-motorist-claims-california/`, `/insurance-company-playbook/`, `/demand-letter-negotiation/`, etc.
- **LA-by-type pages:** All `/los-angeles-*-lawyer/`, `/rear-end-accident-lawyer-los-angeles/`, `/hit-and-run-accident-lawyer-los-angeles/`, etc.
- **Lit-referral pages:** All `/lit-referral-*/`
- **Settlement/topic pages:** e.g. `/how-much-is-my-car-accident-worth-california/`, `/herniated-disc-car-accident-settlement-california/`, `/brain-injury/`, `/california-car-accident-lawyer/`, etc.

**Count:** 112 content pages (all HTML pages minus `thank-you`, minus the 4 legal pages that lack canonical — those 4 are still reachable and have title but are at higher risk of indexing issues).

**Note:** The 4 **legal** pages have **no canonical**; search engines may still index them but canonical is recommended for consistency and to avoid duplicate-URL issues.

---

## 2. Pages likely ignored or at risk

| Reason | Pages |
|--------|--------|
| **Explicit noindex (intentional)** | `thank-you.html`, `thank-you/index.html` — form confirmation; correctly blocked from indexing. |
| **No canonical** | `legal/accessibility/`, `legal/disclaimer/`, `legal/results-disclaimer/`, `legal/terms/` — may be indexed but are weaker without a self-referencing canonical. |
| **Under ~700 words (thin content)** | `motor-vehicle/bus-accident-lawyer-los-angeles/` (676), `premises-liability/negligent-security-lawyer-los-angeles/` (638). Risk of being treated as low-value or duplicate if template is similar to other silos. |
| **Template / duplicate content risk** | Many **Los Angeles lawyer** pages have almost identical word counts (~1,440): e.g. `los-angeles-car-accident-lawyer`, `los-angeles-auto-accident-lawyer`, `los-angeles-bicycle-accident-lawyer`, … (18+ pages). Same structure and similar copy can lead to filtering or consolidation in search results. |
| **Not reachable from main nav** | `/thank-you/` — only reached after form submit; not linked from nav (by design). |

---

## 3. Orphan pages (no internal links to them)

Only **one** URL is never linked to from any other page on the site:

- **`/thank-you/`** (and `thank-you.html`)

This is **intentional**: thank-you is the form confirmation page, reached only via redirect after submission. It is also noindex. No change needed unless you want it linked from footer (e.g. “Privacy” / “Contact” area) for transparency; even then, keeping it noindex is recommended.

---

## 4. Internal linking recommendations

### 4.1 Add canonical tags

- **Legal pages:** Add `<link rel="canonical" href="https://www.insiderlawyers.com/legal/accessibility/">` (and similarly for `disclaimer`, `results-disclaimer`, `terms`) so each legal page has a single canonical URL. Reduces risk of duplicate indexing with or without trailing slash.

### 4.2 Orphan / thank-you

- **Thank-you:** Keep as-is (noindex, no nav link). Optionally add a single footer link (e.g. “Contact” or “Form submitted”) if you want crawlers to see it for coverage; keep `noindex` so it doesn’t compete with main content.

### 4.3 Thin content (under ~700 words)

- **`/motor-vehicle/bus-accident-lawyer-los-angeles/`** and **`/premises-liability/negligent-security-lawyer-los-angeles/`**:  
  - Expand body copy (e.g. more FAQs, local examples, process steps) to reach 700+ words, **or**  
  - Add clear internal links from and to these pages (e.g. from `/motor-vehicle/` and `/premises-liability/` and from related “LA by accident type” and “After accident” pages) so they get more link equity and context.

### 4.4 Duplicate / template content (LA lawyer pages)

- **Differentiate** the 18+ LA lawyer pages: unique intros, local stats, case examples, or FAQs so they are not near-duplicates.  
- **Internal linking:** Ensure each LA lawyer page is linked from:  
  - The main nav (already done), and  
  - Relevant topic pages (e.g. truck accident page → LA truck accident lawyer; brain injury → LA brain injury lawyer).  
- Add **contextual links** from high-word-count pages (e.g. `/personal-injury/`, `/what-to-do-after-car-accident-california/`, `/uninsured-motorist-claims-california/`) to these LA and silo pages.

### 4.5 Hub-to-spoke linking

- **Category hubs** (`/personal-injury/`, `/motor-vehicle/`, `/premises-liability/`) should link to:  
  - All their sub-pages (e.g. bus-accident, negligent-security), and  
  - Key LA-by-type and topic pages.  
- **Settlement and “After accident” pages** should link to relevant LA lawyer and practice-area pages so crawlers and users can discover them from multiple paths.

### 4.6 Broken or non-existent targets

- The analysis listed some internal link targets (e.g. `/insurance-claims/injuries-truck-accidents/`, `/personal-injury-lawyer-los-angeles/`, `/premises-liability-lawyer-los-angeles/`, `/should-i-go-to-er-after-accident/`, `/slip-and-fall/`) that do not match existing HTML files. If any of these appear in your templates or content, fix or remove them so they either point to existing URLs (e.g. `/injuries-truck-accidents/`, `/personal-injury/`, `/premises-liability/`, `/personal-injury/slip-and-fall/`) or are removed.

---

## 5. Quick reference

| Category | Count | Action |
|----------|--------|--------|
| **Likely indexable** | 112 | Keep canonical, title, no noindex; maintain internal links. |
| **Ignored by choice** | 2 (thank-you) | Keep noindex. |
| **At risk (no canonical)** | 4 (legal) | Add canonical. |
| **Thin content (<700 words)** | 2 (bus-accident, negligent-security) | Expand or strengthen internal links. |
| **Duplicate/template risk** | 18+ (LA lawyer pages) | Differentiate content; add contextual internal links. |
| **Orphans** | 1 (thank-you) | No change required. |

---

*Report generated from INDEXABILITY-ANALYSIS.txt. No site files were modified.*
