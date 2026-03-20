# Layout fix summary — global template unification

**Branch:** local (commit requested; **not pushed** per instructions)

## What changed

### Single global chrome (`components/global-chrome-before-main.html`)

- One **unified header**: logo + compact results tagline (desktop) + text phone link (desktop) + shared mega-menu + **mobile call block inside the menu** (not a second duplicate bar in the header).
- **One bottom tap-to-call** strip: text-only, `id="tap-to-call-bar"`, **hidden until scroll** on mobile (see `scripts/site-nav.js`), **max height ~64px**, no phone SVG icon.
- Replaced prior variants that used a separate top “billboard” phone block, hide-on-scroll header, and/or redundant inline menu scripts.

### Single global footer (`components/global-footer.html`)

- Normalized **firm block**, **Case help** (lifecycle cluster + key hubs), **Practice Areas**, **After accident**, **Insurance & claims**, **Referrals**, **LA by accident type**, **Legal**, plus disclaimer, copyright, SMS notice.
- Fixed mojibake **Â ·** → **·** where it appeared in the old template.
- Preserved all **href** targets (no URL changes).

### CSS (`styles/main.css`)

- New **`.header--unified`** / **`.header-unified__shell`** rules: controlled height on mobile, row layout, sticky only on desktop (no hide-on-scroll).
- **Tap bar** styles + **`body.has-tap-bar-visible`** padding to reduce content overlap.
- **`scroll-padding-top`** for anchor targets under the header.
- **Desktop hide** for `.mobile-nav-cta` so the in-menu CTA does not appear in the horizontal nav.

### JavaScript (`scripts/site-nav.js`)

- **Removed** hide-on-scroll / `header--scroll-hide` behavior entirely.
- **Added** tap-bar visibility tied to scroll threshold and viewport (single bar; respects `prefers-reduced-motion`).

### Automation

- `scripts/apply_global_layout.py` — applies global header+tap+footer, strips problematic inline header scripts, injects slim **GTM-friendly** phone + `engaged_30s` where missing, normalizes **`site-nav.js?v=3`** + **`utm-gclid-tracking.js`** before `</body>`.
- `scripts/layout_audit.md` — inventory of template divergence before/after remediation pass.

## Pages affected (approx.)

- **~120** article/silo pages: full chrome + footer swap + script normalization.
- **Homepage** (`index.html`): special-cased (no `<main>`): same chrome before hero + footer + scripts.
- **~138** additional passes in the second run: mostly **footer-only** for pages without `<header>`/`<main>` (archives, extracts, dev scratch).

**Excluded from chrome swap:** `_old-site-extract/`, most `_dev/scratch-html/`, fragments under `components/` (except footers on real pages still updated when applicable).

## Elements removed / risks resolved

| Issue | Mitigation |
|--------|------------|
| Hide-on-scroll header on mobile | Removed scripts + removed scroll-hide JS |
| Multiple sticky layers | One tap bar + sticky header desktop only |
| Oversized header phone treatment | Replaced with compact desktop text link + menu CTA on mobile |
| Inline duplicate menu handlers | Stripped where safe; `site-nav.js` is canonical |
| `</div>v>` typo | Global replace in apply script |
| Tap bar always visible / stacking | Bar off until scroll; desktop `display: none` |

## Not done / follow-ups (review)

- **Legal hub** (`legal/*`) and **`components/standard-header.html`** still use a smaller header fragment for non-silo tooling — consider aligning or documenting as “fragment only.”
- **Checkmark / star symbols** in page bodies (e.g. list bullets, rating rows) were **not** removed to avoid deleting substantive content; tune per page if CRO testing shows clutter.
- **Placeholder** copy in `_dev` / old extract trees not cleaned (not production targets).
- Optional: add `main` landmark to homepage for semantics (would simplify tooling).

## Commit

```
Global template unification + mobile usability repair
```

**Do not push** until design/SEO sign-off.
