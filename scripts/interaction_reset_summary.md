# Interaction hard reset — summary

## Goal

Stable mobile navigation (single interaction model) and conversion-only phone UI (`home-ppc` / `ppc-page` only). No duplicate nav logic outside `scripts/site-nav.js`.

---

## Step 1 — Conversion / phone UI trace

| Source | Role |
|--------|------|
| **`styles/main.css`** | `.call-bar` / `#call-bar` “giant type” strip; `.tap-to-call-bar` fixed bottom bar; `.mobile-nav-cta` in-header phone block; PPC-only accent rules. **Issue fixed:** `body.landing-page` and `.hero-conversion` were tied to `.call-bar` styling, so non-PPC pages with `landing-page` could inherit conversion sizing. **Removed** those selectors from `.call-bar` rules; added **`body:not(.home-ppc):not(.ppc-page) #call-bar { display: none !important; }`**. |
| **`scripts/site-nav.js`** | Only script that scrolls/shows **tap bar** (`#tap-to-call-bar`) and toggles **mobile menu**. **Tightened:** tap logic runs only when `body` has `home-ppc` or `ppc-page`; otherwise tap classes are cleared. |
| **Inline `DOMContentLoaded` in many `*.html`** | **GTM analytics only** (`phone_click`, `engaged_30s`, form events) — not nav/CTA injection. **Left in place** (no content/URL changes). |
| **`#call-bar` in `index.html`** | Static home section; visibility now CSS-gated to PPC classes (home has `ppc-page`). |
| **No** dedicated `#call-bar` injector script, **no** SVG phone injector, **no** `blink` class in live CSS for nav (only unrelated `header-title-zoom` animation elsewhere). |

---

## Step 2 — Legacy mobile nav JS

- **`insiderlawyers-com/scripts/`** contains **only** `site-nav.js` (no duplicate togglers, scroll-lock scripts, or focus-trap helpers in-repo).

---

## Step 3 — Hamburger behavior (`scripts/site-nav.js`)

- **Open state:** `body.nav-open` (+ `html.nav-open-lock` for scroll lock on small viewports).
- **Synced:** `#header-nav-wrap` keeps class `is-open` for backward-compatible CSS hooks.
- **Toggle:** `#mobile-menu-toggle` click flips `nav-open`.
- **Outside click:** closes when target is outside `#header-nav-wrap` and the toggle (informational pages, max-width ≤900px).
- **Escape:** closes menu.
- **Resize:** `≥901px` clears open state.
- **Dropdowns (mobile):** unchanged — `.nav-item` / `.nav-link--dropdown` accordion behavior only below 900px.

---

## Step 4 — CSS containment

- **`main.css`:** Mobile rules use `body.nav-open .header-nav-wrap` (replacing `.header-nav-wrap.is-open` only for the panel/hamburger block).
- **`#call-bar` / `.mobile-nav-cta`:** Hidden on non-PPC bodies as above.
- **`html.nav-open-lock` + `body.nav-open`:** `overflow: hidden` where menu is active (≤900px).
- **Nav row:** `max-width: 100%`, `overflow-x: hidden` when open.

---

## Step 5 — Runtime header mutation

- **No** JS appends links, phone icons, or resizes the header; nav remains server-rendered HTML only.

---

## Cache bust

- All live HTML under `insiderlawyers-com` (excluding `_old-site-extract/`) now reference **`/scripts/site-nav.js?v=4`**.

---

## Commit

Message: `Interaction hard reset — mobile nav rebuild + conversion injector purge`
