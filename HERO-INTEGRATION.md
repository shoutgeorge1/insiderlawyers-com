# Hero Section Integration

**Target:** Update the live page [call.insideraccidentlawyers.com/car-accident/](https://call.insideraccidentlawyers.com/car-accident/) with the new hero. The live URL is not replaced; these files are applied to that site’s codebase.

## 1. Add the stylesheet
In your existing page `<head>` **on the live site**, add:
```html
<link rel="stylesheet" href="styles/main.css">
```

## 2. Replace the hero section
- **Remove** your current `<section class="hero hero-section">...</section>` (the whole hero block).
- **Paste in** the contents of `hero-section-snippet.html` in its place.

The new hero has **id="case-evaluation"**, so your nav link `#case-evaluation` will scroll to the hero (where the form now lives).

## 3. Replace the old form section
You currently have a separate section with `id="case-evaluation"` that contains only the form. **Remove that entire form section** (or replace it with the CTA below so long-scroll users still see a prompt).

Optional replacement for that section (keeps one form only, in the hero):

```html
<section class="case-form" style="padding: 3rem 0; background: linear-gradient(135deg, rgba(12,35,52,0.04), rgba(1,54,108,0.04));">
  <div class="container">
    <div style="text-align: center; max-width: 600px; margin: 0 auto;">
      <h2 style="font-size: 1.75rem; margin-bottom: 0.75rem;">Prefer to speak with someone?</h2>
      <p style="margin-bottom: 1.5rem; color: var(--brand-gray-700);">Call now for a free consultation. Available 24/7.</p>
      <a href="tel:844-467-4335" class="btn-primary" data-callrail-phone="844-467-4335" style="display: inline-block;">844-467-4335</a>
      <p style="margin-top: 1rem; font-size: 0.9rem;"><a href="#case-evaluation">Or fill out the form above</a></p>
    </div>
  </div>
</section>
```

## 4. Keep your existing scripts
Your form submit handler (FormSubmit / GTM) should still work: the form **id** remains `case-evaluation-form` and field **names** are unchanged (`full_name`, `phone`, `accident_reason`, `text_consent`). If your JS targets `#case-evaluation` for scroll, it now points at the hero.

## Branding preserved
- Phone: **844-467-4335**
- Colors: navy `#01366c`, blue `#01468a`, accent yellow `#fbba00`
- Same 3 fields + checkbox + “Get My Free Review” button
