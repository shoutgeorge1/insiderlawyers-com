# Long-Form SEO Page Template

**Reference page:** `/personal-injury/`  
**Purpose:** Reusable structural template for long-form SEO pages. Content is not prescribed; only section order, heading levels, and wrapper classes are defined.

---

## Page wrapper (main content only)

- `<main>`
  - `<section class="section-content">`
    - `<div class="container">`
      - `<div class="content-body">`
        - *[All sections below live inside `.content-body`.]*

---

## Section structure (in order)

### 1. Hero / Title + Intro

| Element | Markup | Notes |
|--------|--------|-------|
| Page title | `<h1>` | One H1 per page; primary keyword. |
| Intro paragraph | `<p class="lead-text">` | 1–2 sentences; key terms + internal links. |
| Hero image | `<figure class="content-hero-img" style="…">` → `<img>` | Optional; full-width image below lead. |

---

### 2. Intro / Context (reinforce topic)

| Element | Markup | Notes |
|--------|--------|-------|
| Section heading | `<h2>` | E.g. “[Topic] in [Location]” or secondary angle. |
| Body | `<p>` | Short context; can include internal links. |

---

### 3. Key Takeaways

| Element | Markup | Notes |
|--------|--------|-------|
| Section heading | `<h2>` | “Key Takeaways” or equivalent. |
| Bullet list | `<ul>` | 3–6 bullets. |
| Highlight list | `<ul class="plus-list">` | Optional; checkmark-style bullets. |
| Quote (optional) | `<blockquote class="content-quote">` | Optional; one short quote. |
| Insight lines (optional) | `<p class="book-insight">` | Optional; 1–3 short lines after quote. |

---

### 4. Why Experience / Differentiator

| Element | Markup | Notes |
|--------|--------|-------|
| Section heading | `<h2>` | E.g. “Why Experience Matters” or differentiator. |
| Lead | `<p class="lead-text">` | One line. |
| Sub-sections | `<h3>` + `<ul>` and/or `<ul class="plus-list">` | Repeat as needed. |

---

### 5. Common Causes / Legal Issues (liability discussion)

| Element | Markup | Notes |
|--------|--------|-------|
| Section heading | `<h2>` | E.g. “Common Causes / Legal Issues”. |
| Lead | `<p class="lead-text">` | One line. |
| Sub-sections | `<h3>` + `<ul>` | One H3 per cause/category; bullets underneath. |

---

### 6. Injuries / Injury explanation

| Element | Markup | Notes |
|--------|--------|-------|
| Section heading | `<h2>` | E.g. “Injuries We Handle” or topic-specific. |
| Lead | `<p class="lead-text">` | One line. |
| Sub-sections | `<h3>` + `<ul>` and/or `<ul class="plus-list">` | One H3 per injury type/category. |

---

### 7. Compensation section

| Element | Markup | Notes |
|--------|--------|-------|
| Section heading | `<h2>` | E.g. “Compensation Available Under California Law”. |
| Lead | `<p class="lead-text">` | One line. |
| List | `<ul>` | Damage types. |
| Optional | `<ul class="plus-list">` | One line if needed. |

---

### 8. How We Help / Legal process

| Element | Markup | Notes |
|--------|--------|-------|
| Section heading | `<h2>` | E.g. “How We Help” or “Legal Process”. |
| Lead | `<p class="lead-text">` | One line. |
| Steps/list | `<ul>` | Process or service points. |
| Optional | `<ul class="plus-list">` | One line if needed. |

---

### 9. Evaluation framework / Methodology (optional)

| Element | Markup | Notes |
|--------|--------|-------|
| Section heading | `<h2>` | E.g. “Insider Case Evaluation Framework”. |
| Lead | `<p class="lead-text">` | One line. |
| Numbered sub-sections | `<h3>` (e.g. “1) Liability”) + `<ul><li>` | Short list per step. |
| Optional | `<ul class="plus-list">` | One closing line. |

---

### 10. FAQ

| Element | Markup | Notes |
|--------|--------|-------|
| Section heading | `<h2>` | “FAQs” or “Frequently Asked Questions”. |
| Lead | `<p class="lead-text">` | One line. |
| FAQ items | `<div class="faq-item">` → `<h4>` + `<p>` | Repeat per question; match FAQPage JSON-LD in `<head>` if used. |

---

### 11. Related / Additional service pages

| Element | Markup | Notes |
|--------|--------|-------|
| Section heading | `<h2>` | E.g. “Additional Service Pages” or “Related Pages”. |
| Lead | `<p class="lead-text">` | One line. |
| Links | `<ul>` → `<li><a href="…">` | Internal links only. |

---

### 12. Call to action (final CTA)

| Element | Markup | Notes |
|--------|--------|-------|
| Section heading | `<h2>` | E.g. “Speak With a [Topic] Attorney”. |
| Lead | `<p class="lead-text">` | One line. |
| Body | `<p>` | Short paragraph; can include internal links. |
| Buttons | `<p style="margin-top:32px">` → `<a href="/#case-evaluation" class="btn-primary">` + `<a href="tel:…" class="btn-secondary">` | Primary = Free Case Review; Secondary = phone. |

---

## Heading and list class reference

| Use | Class / element |
|-----|------------------|
| Section title (main content) | `<h2>` — styled via `.content-body h2` (gradient bar, left border). |
| Sub-section | `<h3>` — `.content-body h3`. |
| FAQ question | `<h4>` inside `.faq-item`. |
| Standard bullets | `<ul>`, `<li>`. |
| Checkmark-style bullets | `<ul class="plus-list">`. |
| Pull quote | `<blockquote class="content-quote">`. |
| Short insight line | `<p class="book-insight">`. |
| Intro-style paragraph | `<p class="lead-text">`. |
| Primary CTA button | `<a class="btn-primary">`. |
| Secondary CTA (phone) | `<a class="btn-secondary" href="tel:…" data-callrail-phone="…">`. |

---

## Optional / flexible sections

- **Hero image** — Section 1: include or omit per page.
- **Key Takeaways** — Quote and `book-insight` paragraphs are optional.
- **Evaluation framework** — Section 9 can be skipped or replaced with another “methodology” block.
- **Related pages** — Section 11 can be shortened or merged into the final CTA copy.

---

## Order summary (checklist)

1. Hero (H1 + lead + optional hero image)  
2. Intro / context (H2 + p)  
3. Key takeaways (H2 + ul [+ plus-list] [+ quote] [+ book-insight])  
4. Why experience / differentiator (H2 + lead + H3 blocks)  
5. Common causes / legal issues (H2 + lead + H3 + ul)  
6. Injuries (H2 + lead + H3 + ul)  
7. Compensation (H2 + lead + ul)  
8. How we help / legal process (H2 + lead + ul)  
9. Evaluation framework (optional) (H2 + lead + H3 + ul)  
10. FAQ (H2 + lead + .faq-item × N)  
11. Related / additional pages (H2 + lead + ul of links)  
12. Call to action (H2 + lead + p + buttons)

---

*Template derived from `/personal-injury/` structure. No existing content was rewritten.*
