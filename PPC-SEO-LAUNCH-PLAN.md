# PPC + SEO Launch Plan (Phase 1)

This plan keeps the homepage stable for paid traffic while scaling supporting pages safely.

## 1) Locked Homepage Rule

- `index.html` is the primary PPC money page.
- Do not change core conversion sections unless intentional:
  - hero
  - case review form
  - phone CTA links
  - case results
  - attorneys section
  - footer contact
- Preflight script now checks required homepage snippets to reduce accidental breakage.

## 2) Page Types

### PPC pages (conversion-first)

- Layout should resemble homepage closely.
- Minimal header/footer navigation.
- Strong call + form CTAs.
- Cross-link to tightly related PPC pages only.

### SEO pages (authority/article style)

- Keep educational structure with strong internal linking.
- Link to relevant PPC pages where user intent becomes high.
- Maintain same brand colors, typography, and button system.

## 3) Initial URL Map

### Live now

- `/` -> PPC homepage (indexed)
- `/personal-injury` -> SEO hub (indexed)
- `/personal-injury/auto-accidents` -> SEO service page (indexed)
- `/personal-injury/brain-injuries` -> SEO service page (indexed)
- `/personal-injury/truck-accidents` -> SEO service page (indexed)
- `/personal-injury/wrongful-death` -> SEO service page (indexed)
- `/insurance-company-playbook` -> SEO authority page (indexed)

### Next PPC pages to build

- `/car-wreck-lawyer-los-angeles` -> PPC variant (start noindex)
- `/car-crash-lawyer-los-angeles` -> PPC variant (start noindex)
- `/rear-end-accident-lawyer-los-angeles` -> PPC variant (index candidate)
- `/truck-accident-lawyer-los-angeles` -> PPC variant (index candidate)

## 4) Indexing Decision Rules

Use `index,follow` when ALL are true:

- The page has unique intent and materially unique copy.
- It is not just a near-duplicate synonym of another indexed page.
- Internal links support it as a destination page.

Use `noindex,follow` when ANY are true:

- It is a paid ad-variant with near-duplicate body copy.
- The URL exists primarily for ad relevance/quality score testing.
- You have another canonical indexed page for the same intent cluster.

## 5) Practical Launch Sequence

1. Keep homepage untouched except intentional updates.
2. Launch current SEO pages (already drafted).
3. Build first 2 PPC variants.
4. Run ads + track CVR/CPL + engagement.
5. Promote winning unique PPC variants from `noindex` to `index`.

## 6) Content Reference Sources

- `https://ial-rewrite.vercel.app/` for structure/content mapping.
- Local draft pages in this repo for PPC + SEO buildout.

