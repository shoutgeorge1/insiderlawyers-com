# UI normalization — second pass (March 2026)

**Site:** www.insiderlawyers.com (workspace: `pi-search-caraccident-lp/`, symlinked as `insiderlawyers-com/`).

## Constraints observed

- **Not modified:** `los-angeles-car-accident-lawyer/index.html` (primary PPC; still `body.home-ppc` + full `#call-bar` block).
- **Not changed:** phone numbers, marketing body copy, no `git push`.

## 1. Conversion vs informational chrome

- **`body.ppc-page`** added on the **home page** (`class="ppc-page landing-page"`) and on every **`index.html` that contains** `<section class="hero hero-section" id="case-evaluation">` **except** the LA car accident URL above (16 silo / near-me / nursing LP files total including home).
- **Fixed bottom `#tap-to-call-bar`:** `styles/main.css` only sets `display: flex` (mobile) for `body.home-ppc` and `body.ppc-page`. **All other pages** keep the element in the DOM for parity but it stays **hidden** and **`scripts/site-nav.js`** skips scroll/padding logic unless `home-ppc` or `ppc-page` is present — so informational pages do not get **extra bottom padding** or slide-up behavior.
- **`#call-bar` giant typography / gradient:** rules in `main.css` are scoped to  
  `body.home-ppc`, `body.ppc-page`, `body.landing-page`, `.hero-conversion` so they are not global. (Only LA currently ships a `.call-bar` block; other hero LPs use the in-flow **`.content-cta-strip`** already in templates.)

## 2. Breadcrumbs

- **Already present** on all `<main>`-based informational templates as **`nav.breadcrumb.breadcrumb--plain`** (text only, under header flow). **No change** this pass where already complete.
- **Skipped by design:** home, thank-you variants, LA car accident PPC, hero-form LPs without `<main>`.

## 3. Visual / motion normalization (`main.css`)

- **Header title:** `animation: none` by default; **zoom animation** only on `body.home-ppc` / `body.ppc-page`.
- **Mobile (≤767px):** heavy **3D yellow CTA shadow** on buttons applies only on `home-ppc` / `ppc-page`.
- **Mobile menu `.mobile-nav-cta`:** calm gray treatment by default; **bold gradient + large type** only on `home-ppc` / `ppc-page`.
- **New shared styles:** `.content-cta-strip` (mid-page strip), `.breadcrumb--plain` (lightweight hierarchy).

## 4. Automation

- `scripts/ui_normalize_pass2.py` — site root is **`Path(__file__).parent.parent`** (fixes mistaken walks to other monorepo folders). Safe to re-run; skips LA car accident path; idempotent for breadcrumbs / `call-bar` replacement if those patterns return on other URLs later.

## 5. Mobile sanity

- No animated title on informational headers; no fixed tap bar on SEOArticle-style pages; tap bar + padding behavior unchanged on **home-ppc** and **ppc-page** hero LPs.
