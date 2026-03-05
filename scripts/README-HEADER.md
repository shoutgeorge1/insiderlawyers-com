# Unify header across the site

The home page header (`.header` + `mid-container` + `header__left` / `header__middle` / `header__right` + `header-nav-wrap` + tap-to-call bar) is the reference. All inner pages should use the same header.

## Already updated (by hand or subagent)

- `index.html` (home – reference)
- `personal-injury/index.html`
- `motor-vehicle/index.html`
- `premises-liability/index.html`
- `legal/*` (e.g. disclaimer)
- `brain-injury/index.html`
- `adjuster-claim-valuation/index.html`, `at-fault-driver-no-insurance/index.html`, `can-i-sue-uninsured-driver-personally/index.html`, `comparative-negligence-california-explained/index.html`, `delayed-pain-after-car-accident/index.html`, `california-comparative-negligence-personal-injury/index.html`
- `attorney-referrals/index.html`, `california-car-accident-lawyer/index.html` (header + CSS cleanup)
- `demand-letters-explained/index.html`

## Updating remaining pages

Two scripts handle the rest of the site:

1. **`unify-header-replacements.py`** – Exact-match replacement for the most common template (inline scroll script + specific CSS). Run first; it updates ~45 pages.
2. **`unify-header.py`** – Flexible replacement for all other pages: finds `<header class="sticky-header">`, swaps in the home-page header HTML, closing + tap-to-call, and fixes both minified and multi-line scroll scripts. Handles the remaining ~33 pages (e.g. settlements, lit-referral-core, personal-injury/*).

To update all remaining pages in one go (run from repo root):

```bash
cd insiderlawyers-com
python3 scripts/unify-header-replacements.py   # optional: already-run pages
python3 scripts/unify-header.py
```

On Windows, if `python` is not in PATH, try `py scripts/unify-header.py`.

What the scripts do:

1. Replace the old header block (sticky-header + header-content + three cols + nav wrap opening) with the new header bar + `header-nav-wrap` + same nav.
2. Replace `</nav> … </div> </div> </header>` with `</nav> … </div> </div>` + tap-to-call bar.
3. Update the scroll script to use `#header` and `#header-nav-wrap` and toggle `header--hidden` on both (handles both inline minified and multi-line `var header = document.querySelector('.sticky-header')` styles).

**After running:** Some pages may still contain dead inline CSS (e.g. `.sticky-header`, `.header-content`, `.header-col--*`) in their `<style>` block. That is harmless; `main.css` controls the header. You can optionally remove those rules for smaller HTML.
