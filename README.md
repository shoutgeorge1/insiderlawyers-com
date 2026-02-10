# PI Search – Car Accident LP (Insider Accident Lawyers)

**Live page (canonical):** [https://call.insideraccidentlawyers.com/car-accident/](https://call.insideraccidentlawyers.com/car-accident/)

This repo is the **source for building off** that URL. Use the code here to enhance and update the live site (hero redesign, new sections, styles). The live domain stays **call.insideraccidentlawyers.com**; this repository is not a replacement for it.

---

## What’s in this repo

| File | Purpose |
|------|--------|
| **`hero-section-snippet.html`** | Drop-in hero: two-column layout (content left, form right). Use on the live site. |
| **`styles/main.css`** | Hero + form card styles. Link from the live site. |
| **`HERO-INTEGRATION.md`** | Step-by-step: add CSS, replace hero, optional CTA section. |
| **`index.html`** | Standalone preview/demo page (e.g. for Vercel/deploys). Not the live site. |

---

## How to use it

1. **Keep the live site:** All production traffic stays at **https://call.insideraccidentlawyers.com/car-accident/**.
2. **Apply changes there:** On the codebase that deploys to that URL, follow [HERO-INTEGRATION.md](HERO-INTEGRATION.md) to add the new hero and styles.
3. **Optional:** Deploy this repo (e.g. Vercel) as a **preview** (different URL) to test the hero before pushing to the live site.

Form actions and thank-you redirect stay pointed at the live domain (e.g. `https://call.insideraccidentlawyers.com/car-accident/thank-you.html`).

---

## Getting a new URL for this project

- **Production (canonical):** Use **https://call.insideraccidentlawyers.com/car-accident/**  
  Set this up on your host (same server as call.insideraccidentlawyers.com): add a route or folder `/car-accident/` that serves this repo’s `index.html` (and `styles/`, etc.), or copy the built files into that path.

- **Preview / testing:** Deploy this repo to get a **free URL**:
  - **[Vercel](https://vercel.com)** – Connect the GitHub repo; you get `pi-search-caraccident-lp-*.vercel.app` (or a custom subdomain).
  - **[Netlify](https://netlify.com)** – Connect the repo; you get `*.netlify.app`.
  - **GitHub Pages** – In repo **Settings → Pages**, set source to this branch and root; you get `https://shoutgeorge1.github.io/pi-search-caraccident-lp/`.

Use the preview URL to test changes; point production traffic at **call.insideraccidentlawyers.com/car-accident/** when ready.
