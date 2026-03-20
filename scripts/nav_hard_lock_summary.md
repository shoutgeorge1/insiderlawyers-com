# Navigation hard lock — summary

- **Unmodified (locked):** `los-angeles-car-accident-lawyer/index.html`
- **Chrome regex replacement skipped:** `index.html` (already unified; long inline styles/sections).
- **Chrome source:** `components/global-chrome-before-main.html` only.
- **Nav script:** `/scripts/site-nav.js` only (deduped if duplicate tags found).
- **Legacy inline CSS:** hide-on-scroll + duplicate mobile `@media(900px)` nav blocks stripped where found.
- **HTML files updated (last script run):** 0 — working tree already contained prior substitutions.

## Global CSS / home template (manual, in-repo)

- **`styles/main.css`:** Header is **not** sticky on desktop; `.sticky-header` is visual-only (`position: relative`). Desktop dropdown panels use `min-width` / `max-width` capped with `min(..., 100vw - …)` so mega-menus stay in the viewport. `html` / `body` use `overflow-x: clip` (with `@supports` fallback) to suppress horizontal scroll from nav. Mobile block tightens `.header--unified` / `.header-nav-wrap` to `max-width: 100%`.
- **`index.html`:** Removed duplicate **inline** nav rules (`.header-nav-wrap`, `.nav-dropdown`, mobile toggles) from the hero `<style>` block so navigation styles come only from `main.css`.
- **`scripts/nav_hard_lock.py`:** Chrome replacement runs only in the first ~60KB after `<body`>; `index.html` skips chrome regex entirely; legacy inline hide-on-scroll + duplicate `@media(900px)` nav blocks are stripped site-wide (except skipped paths + LA PPC lock).

## Files touched
