# Internal linking & topical clusters — March 2026

**Goal:** Strengthen crawl paths and topical clustering for five hub families **without** new URLs, redesign, or PPC redirect changes.

---

## 1. Hub candidates & cluster maps

### A. Personal injury (client hub)

| Hub URL | Role |
|---------|------|
| **`/personal-injury`** | Primary PI hub (indexed; strong organic in GSC notes). |

**Cluster (examples):** `/personal-injury/auto-accidents`, `/personal-injury/truck-accidents`, `/personal-injury/wrongful-death`, `/personal-injury/slip-and-fall`, `/personal-injury/premises-liability`, etc.

**Weak links addressed:** Hub now explicitly lists **`/premises-liability`**, **`/personal-injury/wrongful-death`**, and **`/lit-referral-core`** under “Additional Service Pages” so silo pages tie back to adjacent hubs.

---

### B. Car accidents

| Hub URL | Role |
|---------|------|
| **`/los-angeles-car-accident-lawyer`** | Primary PPC / high-intent LA car hub. |
| **`/personal-injury/auto-accidents`** | Long-form “auto accidents” guide within PI silo. |

**Cluster:** Parking lot, rear-end, T-bone, hit-and-run, uninsured, UM pages, `what-to-do-after-car-accident-california`, etc.

**Weak links addressed:**  
- **Home** practice grid → `/personal-injury/auto-accidents`.  
- **`/personal-injury/auto-accidents`** → contextual sentence to **`/los-angeles-car-accident-lawyer`** + **`/personal-injury`**; new **“Related car accident resources”** list (parking lot, rear-end, wrongful death, premises).  

---

### C. Wrongful death

| Hub URL | Role |
|---------|------|
| **`/personal-injury/wrongful-death`** | Canonical topical page for wrongful death (PI silo). |
| **`/lit-referral-wrongful-death`** | Attorney referral slice of the same topic. |

**Cluster:** Fatal car crashes, premises fatalities, **`/nursing-home-wrongful-death`**, comparative negligence.

**Weak links addressed:** New **“Related resources”** block on **`/personal-injury/wrongful-death`** linking to PI hub, LA car hub, auto-accidents guide, premises hub, nursing home WD, and attorney WD referrals.

**Nav / home:** **`/personal-injury/wrongful-death`** added to **Resources** dropdown (`standard-header.html` + **`index.html`** mirror) and to **home footer** practice list.

---

### D. Premises liability

| Hub URL | Role |
|---------|------|
| **`/premises-liability`** | Main premises LP (traction target). |

**Cluster:** `/personal-injury/slip-and-fall`, `/personal-injury/premises-liability`, `/premises-liability/negligent-security-lawyer-los-angeles`, parking lot LP, LA slip/fall LPs.

**Weak links addressed:** **Additional Service Pages** on **`/premises-liability`** now include **`/parking-lot-accident-lawyer-los-angeles`** and a **wrongful death** line where death occurs on unsafe property.

---

### E. Attorney referral / second opinion

| Hub URL | Role |
|---------|------|
| **`/attorney-referrals`** | Entry for referring counsel. |
| **`/lit-referral-core`** | Program overview / “second hub” for litigation co-counsel. |

**Cluster:** `lit-referral-process`, `lit-referral-criteria`, `lit-referral-economics`, `lit-referral-trial-ready-cocounsel`, case-type pages (catastrophic, truck, brain, wrongful death, coverage disputes).

**Weak links addressed:**  
- **Resources** nav → **`/lit-referral-core`** + wrongful death claims (victim path).  
- **Home** practice grid → **`/lit-referral-core`**; **home footer** → litigation co-counsel link.  
- **`/attorney-referrals`** + **`/lit-referral-core`** → new **related lists** cross-linking the cluster.  
- Six **`lit-referral-*`** pages: replaced thin **“See also: Personal Injury”** with **Related hubs** (core + attorney referrals + PI).

---

## 2. Crawl depth & priority (summary)

| Signal | Change |
|--------|--------|
| **Global nav** | `components/standard-header.html` + **`index.html`** header: Resources now surface **co-counsel overview** and **wrongful death** (2 extra links; not sitewide footer spam). |
| **Homepage** | Practice Areas grid + footer practice list tightened to **named hubs** (PI, car, auto guide, premises, wrongful death, parking lot, referrals). |
| **Hub ↔ spoke** | PI hub, premises hub, auto-accidents guide, wrongful death page, attorney/referral cores explicitly cross-link. |

**Note:** Most inner pages still use **duplicated footers** with many links (pre-existing). This pass **did not** expand those mega-footers; changes are **targeted** to hubs and cluster leaders.

---

## 3. Files updated (this pass)

| File | Change |
|------|--------|
| `components/standard-header.html` | Resources: `lit-referral-core`, `personal-injury/wrongful-death` |
| `index.html` | Same nav; practice grid; footer practice + resources |
| `personal-injury/index.html` | Extra hub links under Additional Service Pages |
| `personal-injury/auto-accidents/index.html` | Lead links + Related car accident resources |
| `personal-injury/wrongful-death/index.html` | Related resources block |
| `premises-liability/index.html` | Parking lot + wrongful death in service list |
| `attorney-referrals/index.html` | Related referral resources; closing paragraph |
| `lit-referral-core/index.html` | Referral cluster list; closing paragraph |
| `lit-referral-{process,criteria,economics,trial-ready-cocounsel,catastrophic-cases,coverage-disputes}/index.html` | “Related hubs” line |

---

## 4. Remaining indexation / authority risks

1. **Google quality bar:** Internal links help discovery and topical grouping; they do not replace **unique, substantive** copy and trust signals off-site.  
2. **302 consolidation:** Many `/los-angeles-*-lawyer` URLs still **302** to the car LP by policy; those URLs will not accumulate standalone topical authority.  
3. **Header drift:** Only **`index.html`** and **`standard-header.html`** share the new top nav; **other pages** embed their own headers. Sync **`standard-header.html`** into templates when those pages are next edited (per site rules).  
4. **Orphans:** Long-tail pages depend on **home grid**, **in-content links**, and **page footers**—continue GSC-based linking from URLs that get impressions.

---

## 5. Next recommendations (authority growth)

1. **GSC-led linking:** From queries/pages with impressions, add **1–2 contextual `<a href>`** in body copy on the ranking URL to the nearest hub.  
2. **Breadcrumb pattern:** Reusable “Home › Silo › Page” row above H1 (same CSS as today—no redesign).  
3. **Single header build:** Generate nav from **`standard-header.html`** in CI or a small build step to prevent drift.  
4. **Earned links & E-E-A-T:** Citations, bar/professional profiles, and **original** stats or case narratives on hub pages.

---

*Implemented: March 2026. Pair with `docs/TECHNICAL-SEO-AUDIT-2026-03.md` for crawl/sitemap context.*
