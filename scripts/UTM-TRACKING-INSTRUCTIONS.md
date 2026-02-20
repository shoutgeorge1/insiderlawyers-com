# UTM & Google Click ID Tracking — Implementation

## What’s included

- **Script:** `utm-gclid-tracking.js`  
  - Reads from URL: `gclid`, `gbraid`, `wbraid`, `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`
  - Saves them in `localStorage` (only overwrites when the param is present in the URL)
  - On DOMContentLoaded: adds/updates hidden inputs for these params on every form and includes them in submit
  - Adds a honeypot field `website_url` to every form; if it’s filled, submission is blocked (spam protection)

## Where to insert

Insert **once per page**, immediately **before** the closing `</body>` tag:

```html
<script src="/scripts/utm-gclid-tracking.js"></script>
</body>
```

- Use **root-relative** `/scripts/utm-gclid-tracking.js` so it works from any page path.
- If the site is not at domain root, change the path (e.g. `https://yoursite.com/scripts/utm-gclid-tracking.js` or the correct relative path).

## Deployment

Ensure the `scripts` folder is deployed so that `/scripts/utm-gclid-tracking.js` is served (e.g. copy `scripts/` to the site root or configure your server to serve it).

## Behavior summary

| Scenario | Result |
|----------|--------|
| User lands with `?gclid=...&utm_source=google` | Params stored in localStorage; forms get hidden inputs with those values. |
| User navigates to another page (no params) | Stored values kept; new page’s forms get the same values. |
| User refreshes | Same stored values; forms still populated. |
| User submits after multiple page views | Submit payload includes all stored attribution params. |
| Bot fills honeypot `website_url` | Form submit is prevented. |

No libraries required; script is vanilla JS and does not replace or remove existing form validation or submit handlers.
