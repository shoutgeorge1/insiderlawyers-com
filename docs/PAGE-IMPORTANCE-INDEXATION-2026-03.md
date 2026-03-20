# Page importance, differentiation & indexation outlook — March 2026

**Site:** www.insiderlawyers.com · **Sitemap URLs:** 124 · **Constraints:** No URL changes, no redesign, no PPC LP rewrites in this analysis.

**Method:** Automated pass over `sitemap.xml` + local HTML: approximate **main body word count** (tags stripped), **cluster** tag (heuristic), **`vercel.json` 302** sources. Counts **undercount** pages with heavy content in repeated chrome; they are still useful **relative** signals. Re-run: `python scripts/page_importance_scan.py` (writes `docs/page-importance-data.json` when the file is not locked).

---

## 1. Executive read

| Finding | Implication |
|--------|----------------|
| **15 sitemap URLs** are **`302` → `/los-angeles-car-accident-lawyer`** | They share the **same ~1,224-word body footprint** as the car LP in our scan—**near-duplicates** for indexing. Expect **very low** probability of ranking as **separate** documents; crawlers consolidate on the target. |
| **~112** remaining URLs are **not** redirect-collapsed | Indexation is still gated by **quality, intent overlap, and backlinks**, not just crawl. |
| **Nursing-home long-tail** pages run **~400–660** words in the heuristic | **Salvageable** with expansion; intents are **more distinct** than the LA-lawyer clone set. |
| **`/what-to-do-after-car-accident-california`** ~**797** words | High **strategic** value (home + hub links) but **thinner** than peers—good **depth** target without touching the PPC LP. |
| **`/premises-liability/negligent-security-lawyer-los-angeles`** ~**660** words | Strong **premises** subtopic; worth deepening and tying to **`/premises-liability`**. |

---

## 2. Classification (A / B / C)

Legend: **A** = prioritize for authority & indexing potential · **B** = keep, improve or merge later · **C** = dilutive / low standalone value (do **not** noindex or delete per current directive).

### A — Strong candidates (unique intent, hub-linked, indexing upside)

| Path | Rationale |
|------|------------|
| `/` | Home; commercial + hub grid; GSC history. |
| `/personal-injury` | PI hub; thickest body in scan; organic clicks reported. |
| `/los-angeles-car-accident-lawyer` | Primary PPC/SEO LP; **do not rework** for “depth” here—support with satellites. |
| `/parking-lot-accident-lawyer-los-angeles` | Distinct scenario; traction target per site brief. |
| `/premises-liability` | Premises hub; strong word count; cluster anchor. |
| `/motor-vehicle` | Vehicle hub; breadth + internal links. |
| `/personal-injury/auto-accidents` | Bridges PI silo ↔ car cluster; recently strengthened links. |
| `/california-car-accident-lawyer` | Statewide guide; different scope from LA LP. |
| `/what-to-do-after-car-accident-california` | Classic informational intent; linked from home—**expand**, not replace. |
| `/rear-end-accident-lawyer-los-angeles`, `/t-bone-accident-lawyer-los-angeles`, `/hit-and-run-accident-lawyer-los-angeles`, `/uninsured-driver-accident-lawyer-los-angeles`, `/uber-accident-lawyer-los-angeles`, `/electric-scooter-ebike-accident-lawyer-los-angeles`, `/pedestrian-accident-lawyer-los-angeles` | **Standalone** accident-type LPs (**no 302** in `vercel.json`); differentiate with scenario-specific FAQs and internal links to hubs. |
| `/los-angeles-nursing-home-neglect-lawyer` | Clear vertical hub; supports bed-sore cluster. |
| `/personal-injury/wrongful-death` | WD intent within PI silo; linked from nav/hubs. |
| `/insurance-company-playbook`, `/proving-claim-value`, `/adjuster-claim-valuation`, `/insurance-company-tactics-personal-injury`, `/why-insurance-delays-claims` | **Insurance education** cluster; good for long-tail + E-E-A-T if examples stay concrete. |
| `/personal-injury/truck-accidents` + `/personal-injury/truck-accidents/*` | Truck **silo** with subpages (FMCSA, evidence, liability)—good for topical depth. |
| `/brain-injury` | Standalone guide; complements `/personal-injury/brain-injuries`. |
| `/attorney-referrals`, `/lit-referral-core` | B2B cluster entry points; recently interlinked. |

### B — Weak but salvageable (overlap, thin sections, or merge candidates later)

| Path / group | Issue | Salvage strategy |
|--------------|--------|------------------|
| **Nursing home long-tail** (`/pressure-ulcers-nursing-home-neglect`, `/stage-3-stage-4-bed-sore-lawsuit`, `/signs-of-nursing-home-neglect`, `/nursing-home-repositioning-standards`, `/nursing-home-wrongful-death`, `/nursing-home-neglect-vs-abuse`, `/nursing-home-understaffing-lawsuit`, `/what-causes-bed-sores`, `/can-you-sue-nursing-home-bed-sores`) | **Shorter** bodies vs site average; some **overlap** on bedsores/neglect. | Add **unique** checklists, statutes/citations, timelines, “when to call” sections; cross-link **up** to `/los-angeles-nursing-home-neglect-lawyer`. |
| `/premises-liability/negligent-security-lawyer-los-angeles` | Thinner vs `/premises-liability`. | Case patterns, duty factors, example fact patterns (hypothetical). |
| `/motor-vehicle/bus-accident-lawyer-los-angeles` | Moderate length; narrow audience. | Tie to `/motor-vehicle` + common carrier / carrier-insurance section. |
| **PI silo pages ~1,000 words** (`/personal-injury/animal-attacks`, `bicycle-accidents`, `motorcycle-accidents`, `pedestrian-accidents`, `catastrophic-injuries`, `product-liability`) | Template-style; **parallel** to many **LA “lawyer”** URLs (some 302’d). | Differentiate as **“California / PI overview”** vs local LP; add unique FAQs per mode. |
| `/demand-letter-negotiation` **vs** `/demand-letters-explained` | Overlapping topic. | Future **merge** into one pillar + 301 (when allowed) or clear **parent/child** roles. |
| `/california-comparative-negligence-personal-injury` **vs** `/comparative-negligence-california-explained` | Duplicate **intel**. | One **canonical** deep guide; other becomes **support** or redirect later. |
| **Settlement injury types:** `/herniated-disc-car-accident-settlement-california`, `/soft-tissue-injury-settlement-california`, `/spinal-fusion-surgery-car-accident-settlement-california`, `/traumatic-brain-injury-car-accident-settlement-california` | Same **template family**; risk of **similar** thin differentiation. | Optional future **mega-guide** “California car accident settlements by injury” with anchors; keep URLs as tabs later. |
| `/hit-and-run-accidents-los-angeles` **vs** `/hit-and-run-accident-lawyer-los-angeles` | Near **duplicate** intent; two URLs. | Pick a **primary** for internal links; consolidate later with 301. |
| `/personal-injury-court`, `/personal-injury-claim-process-california` | Adjacent **process** topics. | Cross-link tightly; consider chapter-style merge later. |
| `/lit-referral-process`, `criteria`, `economics`, `trial-ready-cocounsel`, vertical lit pages | Similar **chrome**; thin differentiation for Google. | Add **unique** paragraphs + FAQs per page; B2B queries may still justify separation. |

### C — Low-value / dilutive for *standalone* indexing (keep live; reduce emphasis)

| Path / group | Rationale |
|--------------|------------|
| **302 sources → car LP** (15 URLs): `/los-angeles-auto-accident-lawyer`, `/los-angeles-car-crash-lawyer`, `/car-accident-lawyer-near-me-los-angeles`, `/los-angeles-truck-accident-lawyer`, `/los-angeles-motorcycle-accident-lawyer`, `/los-angeles-pedestrian-accident-lawyer`, `/los-angeles-bicycle-accident-lawyer`, `/los-angeles-wrongful-death-lawyer`, `/los-angeles-brain-injury-lawyer`, `/los-angeles-spine-injury-lawyer`, `/los-angeles-catastrophic-injury-lawyer`, `/los-angeles-premises-liability-lawyer`, `/los-angeles-slip-and-fall-lawyer`, `/los-angeles-product-liability-lawyer`, `/los-angeles-uber-lyft-accident-lawyer` | **Redirect** to one money page; **not** independent SERP real estate. Indexation **unlikely** as distinct results. |
| `/legal/disclaimer`, `/legal/terms`, `/legal/accessibility`, `/legal/results-disclaimer` | **Compliance**; low organic upside. |
| **Scooter micro-cluster** (`/scooter-accident-driver-fled`, `no-license-plate`, `/recover-destroyed-scooter-ebike`) | **Narrow** volume; fine as **support** but low priority for new external links. |

---

## 3. Authority hierarchy (recommended)

```
                    [ Home / ]
                         │
     ┌───────────────────┼───────────────────┐
     ▼                   ▼                   ▼
/personal-injury   /los-angeles-car-    /premises-liability
                    accident-lawyer*            │
     │                   │                   ▼
     ├─ PI silos         ├─ Scenario LPs      └─ negligent-security,
     │  (auto, WD, …)    │  (rear-end, T,      slip/fall subtopics
     │                   │   parking, ped, …)
     └─ lit-referral-*   └─ edu: what-to-do,
        (B2B)               insurance playbooks

* PPC LP: support with links & content on **other** URLs, not risky LP surgery.
```

**Feed authority upward:** long-tail → **nearest hub** (PI, premises, motor-vehicle, nursing-home neglect, insurance cluster) → **home**.

---

## 4. Proposals (no implementation in this doc)

### Hubs that deserve more **depth** (safest wins)

1. **`/personal-injury`** — FAQs, local court/process color, stronger **unique** examples.  
2. **`/premises-liability`** — security + parking + slip subtopics as **clear** child sections (on-page or linked).  
3. **`/los-angeles-nursing-home-neglect-lawyer`** — anchor the **bed sore / neglect** cluster with a **table of contents** to long-tail pages.  
4. **`/what-to-do-after-car-accident-california`** — step depth, insurance timelines, “mistakes” list (no LP redesign needed).  
5. **Insurance cluster** — one **pillar** narrative across playbook ↔ proving value ↔ adjuster.

### Future **merge** candidates (when URL policy allows)

- Demand letter pair; comparative negligence pair; hit-and-run pair; optional **settlement-by-injury** consolidation.

### **Deprioritize** in *new* internal linking (existing footers can stay for now)

- **302 LA lawyer URLs** (avoid adding *new* prominent contextual links to URLs that always collapse to the car LP).  
- **Legal** footers beyond standard compliance.  
- **Hyper-niche scooter** URLs unless GSC shows impressions.

### **Expansion** for biggest authority gain

| Cluster | Why |
|---------|-----|
| **Nursing home neglect & bedsores** | Distinct intents; support pages are **short**; room for **unique** medical/legal framing. |
| **Insurance / claims education** | Matches “how does insurance work” queries; strengthens **trust**. |
| **Truck + FMCSA subpages** | Clear **entity** and regulatory differentiation vs generic car pages. |
| **Premises (security + parking)** | Ties **parking LP** and **premises hub** without touching PPC car LP. |

---

## 5. Indexation risk summary

| Risk | Severity | Mitigation (content / IA, not tech here) |
|------|-----------|------------------------------------------|
| **302 consolidation** | High for 15 URLs | Treat car LP as **single** ranking target; build **unique** pages on **non-302** URLs. |
| **Template similarity** across PI silo + LA LPs | Medium | Per-page **unique** H2s, FAQs, and **scenario** facts; avoid duplicate opening paragraphs. |
| **Intent overlap** (demand letters, comparative fault, hit-and-run) | Medium | Merge or **differentiate** roles when URLs are freed. |
| **Thin nursing / negligent-security** | Medium | Targeted **expansion** + hub links (already improved globally). |
| **Low external authority** | High (off-page) | Internal links alone won’t fix; **links + local trust** still needed. |
| **Discover → not indexed** (GSC) | Ongoing | After tech + linking fixes, **differentiation** and **signals of usefulness** remain the bottleneck. |

---

## 6. Full-page classification table (124 rows)

See **`docs/page-importance-data.json`** for `{ path, words, title, cluster, 302_to }` per sitemap URL. Assign **A/B/C** in a spreadsheet using the groups above; the JSON is the machine-readable baseline.

---

*This is an evaluation only—no `noindex`, deletes, or URL changes were applied.*
