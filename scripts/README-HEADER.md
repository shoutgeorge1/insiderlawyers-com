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

## Remaining pages

About 70+ HTML files under `insiderlawyers-com/` (excluding `_old-site-extract/` and `components/`) still use the old `<header class="sticky-header">` and inline header/nav styles.

To update them all in one go (requires Python 3):

```bash
cd insiderlawyers-com
python scripts/unify-header.py
```

On Windows, if `python` is not in PATH, try:

```bash
py scripts/unify-header.py
```

The script will:

1. Replace the old header block (sticky-header + header-content + three cols + nav wrap opening) with the new header bar + `header-nav-wrap` + same nav.
2. Replace `</nav> … </div> </div> </header>` with `</nav> … </div> </div>` + tap-to-call bar.
3. Update the scroll script to use `#header` and `#header-nav-wrap` and toggle `header--hidden` on both.

After running, remove any remaining inline header/nav CSS (`.sticky-header`, `.header-content`, `.header-col--*`, `.header-proof-title`, `.header-call-*`, `.header-logo`, `.header-nav-row`, `.nav-link`, `.nav-item`, `.nav-dropdown`, `.mobile-menu-toggle`, and the `@media (max-width: 900px)` / `@media (max-width: 767px)` blocks that only target those) from pages that still have them, so `main.css` controls the header everywhere.
