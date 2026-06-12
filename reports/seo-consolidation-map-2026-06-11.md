# SEO Consolidation Map - 2026-06-11

Site: https://www.insiderlawyers.com/
Pass: Controlled SEO Improvement & Consolidation (June 2026)
Max consolidations this pass: 4 (limit honored)

For each cluster: one winner, one or more losers, direct 301 (no chains), winner returns 200, winner is self-canonical and indexable, loser removed from every sitemap, internal links across the site rewritten to point to the winner.

---

## Cluster 1 - Changing personal injury lawyer

- Winner URL: `/changing-personal-injury-lawyer-california`
- Loser URLs:
  - `/can-i-change-my-personal-injury-lawyer-california`
  - `/what-happens-if-i-fire-my-accident-attorney`
- Reason: All three pages targeted the same intent ("can I switch / fire / change my California personal injury lawyer"). Winner had the cleanest URL slug, the strongest existing content, and was already in the sitemap.
- Content merged: Pulled four high-value FAQ items from `/what-happens-if-i-fire-my-accident-attorney` into the winner: (a) "Should I fire my current lawyer by email?" (b) "What if I have already accepted a settlement offer?" (c) "Does firing my lawyer reset the statute of limitations?" (d) "Can the old lawyer hold my file hostage?"
- Redirect added: `vercel.json` -> 301 from both loser slugs (with and without trailing slash) to the winner.
- Internal links updated: `.cursor/tmp/fix_inline_links_v2.py` rewrote every `href` to a loser URL across all English pages. 51 link rewrites across 32 files. Spanish pages skipped.
- Sitemap updated: Both losers added to `EXCLUDED` in `scripts/build_sitemaps.py`. Winner remains in `GUIDES_EN`. New sitemaps regenerated; QA passes.
- Hreflang impact: None. Losers had no Spanish counterparts. Winner has no Spanish counterpart either, so no hreflang block is required.
- QA result: PASS. Winner returns 200, self-canonical, indexable. Losers 301 directly to winner (no chain). No internal links to losers remain in body content. Loser HTML files left on disk so existing inbound links still resolve via 301.

---

## Cluster 2 - Stalled personal injury case

- Winner URL: `/personal-injury-case-feels-stalled-what-to-do`
- Loser URL: `/personal-injury-case-stalled-california`
- Reason: Same intent ("my California injury case feels stuck, what do I do?"). Winner slug was clearer for the action the user wants to take and had the better structural content.
- Content merged: Added the "Normal delays vs. warning signs" diagnostic section from the loser to the winner (helps the page actually answer the user's question instead of just describing the legal process).
- Redirect added: `vercel.json` -> 301 from loser (with and without trailing slash) to winner.
- Internal links updated: Site-wide via `fix_inline_links_v2.py`.
- Sitemap updated: Winner moved from `EXCLUDED` into `GUIDES_EN`; loser moved from `GUIDES_EN` into `EXCLUDED`.
- Hreflang impact: None. Neither page has a Spanish counterpart.
- QA result: PASS. Winner is sitemap-resident, self-canonical, indexable. Loser 301s directly.

---

## Cluster 3 - Adjuster / insurance settlement valuation

- Winner URL: `/how-adjusters-value-claims`
- Loser URLs:
  - `/adjuster-claim-valuation`
  - `/how-insurance-calculates-settlement-offers`
- Reason: All three pages explained how insurance adjusters value claims. GSC: winner was at position 39.23 (13 impressions); `/adjuster-claim-valuation` at 62.07 (14 impressions); `/how-insurance-calculates-settlement-offers` was already in the sitemap but ranked weaker for the same query set. Winner chosen on (a) best GSC position and (b) most natural URL.
- Content merged: Reviewed both losers - winner already covers the same substantive material. No unique sections needed to be merged (avoided length-for-length's-sake additions).
- Redirect added: `vercel.json` -> 301 from both loser slugs (with and without trailing slash) to the winner.
- Internal links updated: Global header `components/global-chrome-before-main.html` updated to point at the winner with the new anchor "How Adjusters Value Claims"; `apply_global_layout.py` propagated to all 151 content pages. Inline body links updated by `fix_inline_links_v2.py`.
- Sitemap updated: Winner moved from `EXCLUDED` into `GUIDES_EN`. Losers moved into `EXCLUDED`.
- Hreflang impact: None. Neither winner nor losers have Spanish counterparts.
- QA result: PASS. Winner 200, self-canonical, indexable. Losers 301 directly to winner. No remaining global navigation references to either loser.

---

## Cluster 4 - California comparative negligence

- Winner URL: `/california-comparative-negligence-personal-injury`
- Loser URL: `/comparative-negligence-california-explained`
- Reason: This is the one cluster where the initial direction was reversed. The slug `/comparative-negligence-california-explained` looked like the better winner on first audit (cleaner, "explained" suggests a guide), but reading the body revealed the page's content was corrupted - the title was about comparative negligence but the body was hit-and-run content. The other page had correct, substantive comparative-negligence content (pure comparative fault, percentage math, common insurer tactics). Reversed the redirect direction.
- Content merged: None needed - winner already had correct, deeper content. Improved the winner's `<title>` and `<meta description>` to clarify search intent and improve CTR.
- Redirect added: `vercel.json` -> 301 from loser (with and without trailing slash) to winner.
- Internal links updated: Site-wide rewrites via `fix_inline_links_v2.py` (including a duplicate inline link on `/personal-injury` that was corrected to point at the winner).
- Sitemap updated: Winner moved from `EXCLUDED` into `GUIDES_EN`. Loser kept in `EXCLUDED` with updated rationale noting the body corruption.
- Hreflang impact: None.
- QA result: PASS. Winner returns 200, self-canonical, indexable. Loser 301s directly.

---

## Consolidation Candidates Audited but NOT Consolidated This Pass

Per the prompt's "consolidate no more than 4 clusters" limit, these were evaluated and intentionally left for a future pass:

| Cluster | Pages | Decision | Reason |
|---|---|---|---|
| First settlement offer | `/should-i-accept-first-settlement-offer-california` (W) vs `/should-i-accept-insurance-first-offer` (L) | DEFER - loser already excluded from sitemap by prior pass; not adding the redirect to `vercel.json` this pass to keep the diff small. | Pre-existing partial consolidation; no harm done by deferring full redirect step. |
| Motorcycle | `/personal-injury/motorcycle-accidents` vs `/motorcycle-accident-case` | KEEP BOTH | Different intent: hub vs. informational case-process page. |
| Rideshare | `/personal-injury/uber-and-lyft-accidents` vs `/uber-accident-lawyer-los-angeles` vs `/uber-or-lyft-accident` | KEEP CURRENT STRUCTURE | First two have clearly different intent (informational hub vs. LA commercial). The third is only 5 impressions - too small to act on; no internal links currently point to it. |
| Parking lot | `/parking-lot-accident-lawyer-los-angeles` vs `/california-parking-lot-accident-claim-guide` | KEEP BOTH | Different intent: LA commercial vs. CA informational guide. Cross-linked. |
| Pedestrian | `/pedestrian-accident-lawyer-los-angeles` vs `/pedestrian-right-of-way` | KEEP BOTH | Different intent: LA commercial vs. statewide right-of-way guide. |
| T-bone | `/t-bone-accident-lawyer-los-angeles` vs `/t-bone-accident-claim-value-california` | KEEP BOTH | Different intent: LA commercial vs. CA claim-value guide. |

---

## Final Consolidation Tally

- Clusters consolidated: 4 / 4 (at limit)
- Total losers 301'd this pass: 6 distinct URLs (12 with-slash pairs)
- Sitemap entries added to `EXCLUDED`: 5 new this pass (1 was already excluded for unrelated reasons and stays)
- Sitemap entries added to `CORE_EN` / `GUIDES_EN`: 3 winners moved out of `EXCLUDED` + 1 net-new (`/los-angeles-construction-accident-lawyer`)
- Redirect chains created: 0
