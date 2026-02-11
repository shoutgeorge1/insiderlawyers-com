# Building variants (minim + long-form)

How to spin up new LPs and what to do when long-form outperforms minim.

---

## Two template types

| Type | URL example | Use case |
|------|-------------|----------|
| **Long-form** | `call.insideraccidentlawyers.com/` or `…/los-angeles-car-accident/` (full page) | Authority, SEO, “main” experience. |
| **Minim** (this repo) | `call.insideraccidentlawyers.com/los-angeles-car-accident/` (high-contrast, super-long keyword URL) | Paid, testing, or dedicated campaign LPs. |

You can run both. Build variants of each template by topic (car, motorcycle, truck, etc.).

---

## How to build a new **minim** variant (this repo)

1. **Duplicate or branch this repo**  
   New repo (e.g. `pi-search-motorcycle-accident-lp`) or a branch.

2. **Pick the slug**  
   Super-long keyword per topic: `los-angeles-motorcycle-accident-lawyer`, `los-angeles-truck-accident-lawyer`, `los-angeles-wrongful-death-lawyer`, etc.

3. **Find/replace in the codebase**  
   Replace `los-angeles-car-accident` with your new slug in:
   - `index.html` (canonical, logo link, form `_next`)
   - `hero-section-snippet.html` (logo link, form `_next`)
   - Any copy (H1, meta description, etc.) to match the topic.

4. **Deploy that path**  
   On your host, serve the built files at `https://call.insideraccidentlawyers.com/<slug>/` (e.g. `/los-angeles-motorcycle-accident-lawyer/`).

5. **Thank-you page**  
   Add or point to `https://call.insideraccidentlawyers.com/<slug>/thank-you.html` so the form redirect works.

Result: super-long keyword URLs like `…/los-angeles-car-accident/`, `…/los-angeles-motorcycle-accident-lawyer/`, one minim LP per path.

---

## How to build a new **long-form** variant

Same idea, but in the codebase that powers your long-form site (the main site):

1. **In that codebase**  
   Add a new route/page for the topic (e.g. `/motorcycle-accident/` or a new template + slug).

2. **Content**  
   Reuse your long-form layout; change headline, body, and meta to the new topic.

3. **Deploy**  
   New URL live (e.g. `…/motorcycle-accident/` if that’s where long-form lives).

You can have long-form and minim on the **same** path only if you choose one as canonical (e.g. long-form at `/los-angeles-car-accident/`, minim at `/los-angeles-car-accident/min/` or vice versa). See README “What if long-form performs better?” for options.

---

## If long-form performs better

- **Option A – One URL per topic**  
  Make the winning template the only one on that path.  
  Example: long-form wins for car accident → serve long-form at `…/los-angeles-car-accident/`, 301 the old minim URL to it (or remove minim from that path).

- **Option B – Keep both, send traffic to the winner**  
  e.g. Minim at `…/los-angeles-car-accident/`, long-form at `…/los-angeles-car-accident/full/`.  
  Use the better-performing URL in ads and links; leave the other for tests or backup.

- **Option C – Minim for paid only**  
  Keep long-form as the main site and SEO. Use minim variants only for PPC/campaigns so you get clean, focused LPs without touching the authoritative long-form URLs.

---

## Quick reference: slugs and paths

| Topic (example) | Minim path | Long-form (example) |
|-----------------|------------|----------------------|
| Car accident | `/los-angeles-car-accident/` | `/` or `/los-angeles-car-accident/` |
| Motorcycle | `/los-angeles-motorcycle-accident-lawyer/` | `/los-angeles-motorcycle-accident-lawyer/` |
| Truck | `/los-angeles-truck-accident-lawyer/` | `/los-angeles-truck-accident-lawyer/` |
| Wrongful death | `/los-angeles-wrongful-death-lawyer/` | `/los-angeles-wrongful-death-lawyer/` |

Use the same slug on both templates if you want topic parity; use a subpath (e.g. `/los-angeles-car-accident/full/`) when you need both templates for the same topic.
