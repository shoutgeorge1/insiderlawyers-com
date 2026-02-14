# PI Search – Car Accident LP (Insider Accident Lawyers)

**Canonical URL for this minim LP (once configured):** [https://call.insideraccidentlawyers.com/los-angeles-car-accident/](https://call.insideraccidentlawyers.com/los-angeles-car-accident/)  
The root **https://call.insideraccidentlawyers.com/** is the long-form site and is not changed or replaced.

**Getting 404 on that URL?** That path doesn’t exist on your server yet. To get a **working URL to use right now**:

1. **Deploy this repo to Vercel** (easiest): [vercel.com/new](https://vercel.com/new) → Import `shoutgeorge1/pi-search-caraccident-lp` → Deploy. You’ll get a live URL like **`https://pi-search-caraccident-lp.vercel.app`** (or your Vercel project name). Use that to work off of and share.
2. **To get this LP at https://call.insideraccidentlawyers.com/los-angeles-car-accident:** Open the repo that serves **call.insideraccidentlawyers.com** → merge the `rewrites` from **[vercel-rewrite-add-to-main-site.json](vercel-rewrite-add-to-main-site.json)** into that project’s `vercel.json` → deploy. Done. (Details: [SERVE-AT-CANONICAL-URL.md](SERVE-AT-CANONICAL-URL.md).)

This repo is the **source** for the minim LP. The live domain stays **call.insideraccidentlawyers.com**; this repository is not a replacement for it.

---

## URL structure (super-long keyword URLs for minim LPs)

| URL | Purpose |
|-----|--------|
| **https://call.insideraccidentlawyers.com/** | **Base** – long-form, authoritative main site. |
| **https://call.insideraccidentlawyers.com/los-angeles-car-accident/** | **This project** – minimal high-contrast car accident LP. |
| **https://call.insideraccidentlawyers.com/los-angeles-motorcycle-accident-lawyer/** | Next variant – same template. |
| **https://call.insideraccidentlawyers.com/los-angeles-truck-accident-lawyer/** | Another – full keyword slug per topic. |

**Minim = super-long paths:** One path per topic, full keyword (e.g. `los-angeles-car-accident`).  
**To add a variant:** See [VARIANTS.md](VARIANTS.md) (duplicate repo → new slug → deploy).

---

## What if long-form performs better?

You have **two template types**: (1) **Long-form** (authoritative base site), (2) **Minim** (this repo). You can run both and scale the winner.

| Approach | When to use |
|----------|-------------|
| **Same path, swap template** | You test minim at `/los-angeles-car-accident/`. If long-form wins, replace that path with the long-form car accident page and 301 or retire the minim. One canonical URL per topic. |
| **Separate paths so both exist** | Minim at `/los-angeles-car-accident/`, long-form at `/los-angeles-car-accident/full/` (or base `/` for “all topics”). Send traffic to whichever converts better; no conflict. |
| **Minim for paid, long-form for organic** | Keep long-form as main SEO/authority. Use minim LPs for PPC/ads only. Build minim variants per campaign (e.g. `/los-angeles-motorcycle-accident-lawyer/` for bike ads). |

**Building more variants (minim or long-form):** Same idea per template—new topic = new slug, new copy, same layout. See [VARIANTS.md](VARIANTS.md).

---

## What’s in this repo

| File | Purpose |
|------|--------|
| **`hero-section-snippet.html`** | Drop-in hero: two-column layout (content left, form right). Use on the live site. |
| **`styles/main.css`** | Hero + form card styles. Link from the live site. |
| **`HERO-INTEGRATION.md`** | Step-by-step: add CSS, replace hero, optional CTA section. |
| **`VARIANTS.md`** | How to build minim + long-form variants and what to do when long-form wins. |
| **`index.html`** | Standalone preview/demo page (e.g. for Vercel/deploys). Not the live site. |

---

## How to use it

1. **Keep the live site:** All production traffic stays at **https://call.insideraccidentlawyers.com/los-angeles-car-accident/**.
2. **Apply changes there:** On the codebase that deploys to that URL, follow [HERO-INTEGRATION.md](HERO-INTEGRATION.md) to add the new hero and styles.
3. **Optional:** Deploy this repo (e.g. Vercel) as a **preview** (different URL) to test the hero before pushing to the live site.

Form actions and thank-you redirect stay pointed at the live domain (e.g. `https://call.insideraccidentlawyers.com/los-angeles-car-accident/thank-you.html`).

---

## Getting a new URL for this project

- **Production (canonical):** Use **https://call.insideraccidentlawyers.com/los-angeles-car-accident/**  
  Set this up on your host (same server as call.insideraccidentlawyers.com): add a route or folder `/los-angeles-car-accident/` that serves this repo’s `index.html` (and `styles/`, etc.), or copy the built files into that path.

- **Preview / testing:** Deploy this repo to get a **free URL**:
  - **[Vercel](https://vercel.com)** – Connect the GitHub repo; you get `pi-search-caraccident-lp-*.vercel.app` (or a custom subdomain).
  - **[Netlify](https://netlify.com)** – Connect the repo; you get `*.netlify.app`.
  - **GitHub Pages** – In repo **Settings → Pages**, set source to this branch and root; you get `https://shoutgeorge1.github.io/pi-search-caraccident-lp/`.

Use the preview URL to test changes; point production traffic at **call.insideraccidentlawyers.com/los-angeles-car-accident/** when ready.

---

## Production lock-down (recommended for live PPC)

To reduce accidental breakage on a live campaign page, this repo includes:

- **Preflight validation** (`npm run preflight`) that checks:
  - canonical tags exist and stay on `https://www.insiderlawyers.com/...`
  - homepage canonical remains `https://www.insiderlawyers.com/`
  - homepage retains the primary click-to-call number
  - required GTM container remains present
  - lead form action/hidden fields are intact
- **Vercel hardening headers** in `vercel.json`:
  - `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`
  - conservative cache behavior for HTML, long cache for static assets

### Safe publish flow

1. Make copy/design edits.
2. Run: `npm run preflight`
3. Preview deploy and submit a test lead.
4. Publish to production only after checks pass.

---

## PPC + SEO scaling docs

- Launch structure and indexing rules: `PPC-SEO-LAUNCH-PLAN.md`
- Local page-by-page review board: `REVIEW-PAGES.html`
