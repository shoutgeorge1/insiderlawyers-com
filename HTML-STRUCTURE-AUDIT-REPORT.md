# HTML Structure Audit Report — insiderlawyers-com

**Scope:** `insiderlawyers-com/` (www.insiderlawyers.com)  
**Excluded:** `_old-site-extract`, `components`, `_dev`, `social-assets`  
**Date:** February 2025  
**Instruction:** Report only; no files were modified.

---

## 1. Header variations

### Pattern A — Main header (home-style, 97 pages)

- **Markup:**  
  `<header class="header" id="header">` → `<div class="mid-container">` → `.header__left` (logo), `.header__middle` (verdicts), `.header__right` (phone CTA).  
  Sibling `<div class="header-nav-wrap" id="header-nav-wrap">` → `.container` → `<button class="mobile-menu-toggle">` + `<nav class="header-nav-row" id="primary-nav">` with dropdowns (`.nav-item`, `.nav-dropdown`).
- **Used on:** Home (`index.html`), legal pages, and the vast majority of content pages (e.g. `personal-injury/*`, `motor-vehicle/index.html`, `premises-liability/index.html`, `what-to-do-after-car-accident-california`, `legal/disclaimer`, etc.).

### Pattern B — Sticky header (2 pages)

- **Markup:**  
  `<header class="sticky-header">` → `<div class="container">` → `.header-content` with `.header-col--logo`, `.header-col--proof`, `.header-col--call`.  
  `<nav class="header-nav-wrap">` is the nav element itself (flat links only). **No** `mobile-menu-toggle`, **no** dropdowns, **no** tap-to-call bar.
- **Files:**
  1. `premises-liability/negligent-security-lawyer-los-angeles/index.html`
  2. `motor-vehicle/bus-accident-lawyer-los-angeles/index.html`

**Summary:** Two header patterns. Pattern A is the canonical layout (logo, phone CTA, full nav with mobile menu). Pattern B is the legacy “sticky” layout (logo, proof, phone, flat nav, no mobile menu).

---

## 2. Footer variations

### Full footer (97 pages)

- **Markup:**  
  `<footer class="site-footer">` → `.container` → `<div class="footer-content">` → multiple `<div class="footer-section">` (e.g. Practice Areas, After Accident, Insurance & Claims, Referrals, LA by Accident Type, Legal) + `footer__disclaimer`.
- **Used on:** All pages that use Pattern A header (index, legal, and almost all content pages).

### Minimal footer (2 pages)

- **Markup:**  
  `<footer class="site-footer">` → `.container` → paragraphs only (disclaimer, address, copyright, privacy link). **No** `footer-content`, **no** `footer-section`.
- **Files:**
  1. `premises-liability/negligent-security-lawyer-los-angeles/index.html`
  2. `motor-vehicle/bus-accident-lawyer-los-angeles/index.html`

**Summary:** Full footer (with practice areas, locations, contact, resources) is used site-wide except on the two sticky-header silo pages, which use a minimal footer.

---

## 3. Mobile navigation and nav scripts

### Pages with mobile menu (97 pages)

- All pages using Pattern A header include `header-nav-wrap` and `mobile-menu-toggle` in the markup.

### Pages missing mobile navigation (2 pages)

- **Pattern B (sticky-header) pages:** No `mobile-menu-toggle`; nav is flat links only.  
  - `premises-liability/negligent-security-lawyer-los-angeles/index.html`  
  - `motor-vehicle/bus-accident-lawyer-los-angeles/index.html`

### Nav script usage

- **Reference `site-nav.js`:** 28 pages (e.g. `index.html`, `legal/disclaimer`, `legal/accessibility`, `legal/terms`, `legal/results-disclaimer`, plus a subset of content pages such as `settlements`, `los-angeles-*`, `motor-vehicle`, `premises-liability`, `california-comparative-negligence-personal-injury`, etc.).
- **Inline nav/scroll script only (no site-nav.js):** At least `what-to-do-after-car-accident-california/index.html` — inline script toggles `header-nav-wrap.is-open` and dropdowns via `mobile-menu-toggle` and `.nav-link--dropdown` (same behavior as `site-nav.js`, but in-page).
- **Pages with mobile menu markup but no script reference in audit:** Many content pages have `mobile-menu-toggle` and `header-nav-wrap` but were not individually checked for script; they may load `site-nav.js` or an inline equivalent. Recommendation: ensure every page that has the main header and mobile menu either includes `<script src="/scripts/site-nav.js?v=2" defer></script>` or a single shared inline equivalent, and remove duplicate inline nav logic.

**Summary:** Two pages lack mobile navigation entirely (sticky-header pages). Elsewhere, mobile menu behavior is implemented either by `site-nav.js` (28 pages confirmed) or by inline script (at least one page), which is an inconsistency to fix.

---

## 4. Breadcrumbs

### Pages that have breadcrumbs (7 pages)

- `electric-scooter-ebike-accident-lawyer-los-angeles/index.html`
- `motor-vehicle/index.html`
- `motor-vehicle/bus-accident-lawyer-los-angeles/index.html`
- `premises-liability/index.html`
- `premises-liability/negligent-security-lawyer-los-angeles/index.html`
- `uninsured-motorist-claims-california/index.html`
- `what-to-do-after-car-accident-california/index.html`

### Pages missing breadcrumbs

- **By design:** Home (`index.html`), thank-you pages, and utility/social pages do not require breadcrumbs.
- **Content/category/article pages:** All other inner pages (e.g. other `personal-injury/*`, `lit-referral-*`, `los-angeles-*`, `legal/*`, and the majority of topic pages) do **not** include breadcrumb markup. For a consistent UX and SEO, any content page that is not the homepage or a thank-you/utility page should include a breadcrumb trail (e.g. `Home > Category > Page`).

**Summary:** Only 7 pages have breadcrumbs; the rest of the content tree does not. Recommendation: add breadcrumbs to all content/category/article pages using a single pattern (e.g. `nav class="breadcrumb" aria-label="Breadcrumb"` with schema BreadcrumbList where appropriate).

---

## 5. Summary table

| Item | Finding |
|------|--------|
| **Header patterns** | Two: (A) `header` + `mid-container` + `header__left/middle/right` + separate `header-nav-wrap` with `mobile-menu-toggle` and dropdowns; (B) `sticky-header` + `header-content` + flat `<nav class="header-nav-wrap">` (no mobile menu). |
| **Footer patterns** | Two: full (`site-footer` + `footer-content` + `footer-section`); minimal (`site-footer` + container + paragraphs only). |
| **Pages with Pattern A header** | 97 (includes index, legal, and most content pages). |
| **Pages with Pattern B header** | 2: `premises-liability/negligent-security-lawyer-los-angeles`, `motor-vehicle/bus-accident-lawyer-los-angeles`. |
| **Pages missing mobile nav** | Same 2 as Pattern B. |
| **site-nav.js vs inline** | 28 pages reference `site-nav.js`; at least one page (`what-to-do-after-car-accident-california`) uses inline nav script only. |
| **Breadcrumbs** | 7 pages have breadcrumbs; all other content pages are missing them. |

---

## 6. Proposed standardized layout

Apply one layout across the site so every page shares the same header and footer structure and behavior.

### Header (single pattern)

- **Logo** — Links to homepage (`/`). Same logo asset and alt text site-wide.
- **Phone CTA** — Visible “Available 24/7” + click-to-call number (e.g. 844-467-4335), with optional “Hablamos Español.” Same markup/class for tracking (e.g. `data-callrail-phone`).
- **Main navigation** — Implemented as:
  - A **sibling** of the top bar: `<div class="header-nav-wrap" id="header-nav-wrap">` containing:
    - `<button class="mobile-menu-toggle" id="mobile-menu-toggle" ...>` for small screens.
    - `<nav class="header-nav-row" id="primary-nav" aria-label="Primary">` with:
      - Primary CTA link (e.g. Case Review → `/#case-evaluation`).
      - Home.
      - Dropdowns: Practice Areas, After Accident, Insurance & Claims, Referrals, LA by Accident Type (or equivalent), with same link set as on the home page.
  - One script for toggle and scroll: **always** load `site-nav.js` on every page that uses this header; remove duplicate inline nav/scroll logic from inner pages.
- **Tap-to-call bar** — Optional sticky bar below header on mobile (e.g. `class="tap-to-call-bar"`) for consistency.
- **Reference implementation:** Use `index.html` (or `legal/disclaimer/index.html`) as the single source of truth for header + nav markup and script.

**Recommendations:**

1. Replace Pattern B header on the two silo pages with Pattern A (same structure as home).
2. Ensure every page with the main header loads `site-nav.js` and remove inline nav/scroll scripts that duplicate it (e.g. on `what-to-do-after-car-accident-california`).

### Footer (single pattern)

- **Practice areas** — One `footer-section` with links to main practice areas (e.g. Personal Injury, Motor Vehicle, Premises Liability, and key sub-pages).
- **Locations** — One `footer-section` for LA / office or location-based links (e.g. LA by accident type, “Car Accident Lawyer Near Me LA”).
- **Contact** — Address, phone, and/or contact page link; keep disclaimer text (e.g. “Past verdicts and settlements…”) in a consistent block.
- **Resources** — One `footer-section` for Referrals, Legal (Disclaimer, Terms, Accessibility, Results Disclaimer), Privacy, and any other global links.

**Recommendations:**

1. Replace the minimal footer on the two sticky-header pages with the full footer (same `footer-content` + `footer-section` structure as the rest of the site).
2. Keep footer link sets in sync with the main nav (e.g. single source or documented list) so new sections don’t drift.

### Breadcrumbs

- **Rule:** Every content page (article, category, or silo) that is not the homepage or a thank-you/utility page should include a breadcrumb.
- **Markup:** e.g. `<nav class="breadcrumb" aria-label="Breadcrumb">` with “Home > [Category] > [Page]” and, where appropriate, BreadcrumbList JSON-LD.
- **Recommendation:** Add breadcrumbs to all content pages that currently lack them, using the same pattern as the 7 pages that already have them (and optionally a small shared snippet or build step to avoid drift).

---

## 7. Recommended fix order (no file changes in this audit)

1. **Unify header:** Replace the sticky-header (Pattern B) on the two silo pages with the main header (Pattern A) and add tap-to-call bar so layout and behavior match the rest of the site.
2. **Unify footer:** Replace the minimal footer on those same two pages with the full footer (footer-content + footer-section).
3. **Unify nav script:** Ensure every page with the main header loads `site-nav.js`; remove duplicate inline nav/scroll logic from any page (e.g. `what-to-do-after-car-accident-california`).
4. **Breadcrumbs:** Add breadcrumbs to all content pages that don’t have them, using the same markup and (where applicable) schema as the 7 existing pages.

After these steps, the site will have a single standardized layout: one header (logo, phone CTA, main nav with mobile menu), one footer (practice areas, locations, contact, resources), and consistent breadcrumbs on content pages.
