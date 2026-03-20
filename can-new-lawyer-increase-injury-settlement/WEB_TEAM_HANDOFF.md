# Web team handoff: “Can a new lawyer increase injury settlement?” page

## Live URL (canonical)

`https://www.insiderlawyers.com/can-new-lawyer-increase-injury-settlement`

## Repo paths

| Asset | Path |
|--------|------|
| **Full page HTML** | `pi-search-caraccident-lp/can-new-lawyer-increase-injury-settlement/index.html` |
| **Vercel rewrites** | `pi-search-caraccident-lp/vercel.json` — routes `/can-new-lawyer-increase-injury-settlement` and trailing slash to this `index.html` |
| **Sitemap** | `pi-search-caraccident-lp/sitemap.xml` — includes the canonical `<loc>` above |

## What shipped

- Late-funnel “switching / second opinion” content for California PI (no settlement guarantees).
- **One H1**, **H2** section structure, on-page FAQ + **FAQPage** JSON-LD (5 Q&As).
- **LegalService** + **WebPage** JSON-LD in `<head>`.
- CTAs: `/#case-evaluation`, `tel:844-467-4335` (with `data-callrail-phone` where used elsewhere on the template).
- Internal links in body: `/changing-personal-injury-lawyer-california`, `/second-opinion-personal-injury-claim-california`, `/lit-referral-core`, `/los-angeles-car-accident-lawyer`, `/personal-injury`.
- Same global header/nav/footer/GTM shell as sibling LP pages in this project.

## Deploy notes

- If production is built from a **different** directory than `pi-search-caraccident-lp/`, copy `can-new-lawyer-increase-injury-settlement/index.html` into the deployed tree and mirror the **rewrite rules** + **sitemap** entry (or equivalent server config).

## Attach the HTML

Send **`index.html`** from this folder as the single-file deliverable, or deploy from git at the path above.
