# Podcast Feature – Beyond the Gavel

Lightweight promo module for Donn Christensen's Beyond the Gavel podcast feature. Two options: **Banner** (inline) and **Modal** (popup).

## Assets Used

- Podcast art: `https://is1-ssl.mzstatic.com/image/thumb/Podcasts211/v4/0e/8f/ad/0e8fadd2-9d01-0edb-79a2-2a185f6d9be0/mza_7050964826481513520.jpg/1200x1200bf-60.jpg`
- LinkedIn event: `https://www.linkedin.com/events/7428108930947518464/`
- Video CTA: LinkedIn video URL (in components)

---

## Option 1: Banner (inline section)

Add the banner anywhere on a page (e.g. below hero, above footer).

### 1. Add CSS

In your page `<head>` or before the banner:

```html
<link rel="stylesheet" href="styles/podcast-feature.css">
```

### 2. Add the banner HTML

Copy the contents of `components/PodcastFeatureBanner.html` and paste where you want it. Or include it:

```html
<!-- Example: after hero, inside a container -->
<div class="container" style="margin-top: 2rem;">
  <!-- Paste contents of components/PodcastFeatureBanner.html here -->
</div>
```

---

## Option 2: Modal (popup)

The modal appears after **8 seconds** or on **exit intent** (desktop only: mouse leaving top of viewport). It respects:
- **7-day suppression** via `localStorage` when user closes, clicks CTA, or "No thanks"
- **prefers-reduced-motion** (no animations)
- **Accessibility**: focus trap, ESC to close, ARIA labels

### 1. Add CSS

```html
<link rel="stylesheet" href="styles/podcast-feature.css">
```

### 2. Add the script (before `</body>`)

```html
<script src="scripts/podcast-feature-modal.js" defer></script>
```

The script injects the modal into the page and handles timing, exit intent, and localStorage.

---

## Full page example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Example</title>
  <link rel="stylesheet" href="styles/main.css">
  <link rel="stylesheet" href="styles/podcast-feature.css">
</head>
<body>
  <!-- Your page content -->

  <!-- Optional: Banner (paste from components/PodcastFeatureBanner.html) -->
  <section class="podcast-feature-banner">
    <!-- ... -->
  </section>

  <!-- Modal: script only, no HTML needed -->
  <script src="scripts/podcast-feature-modal.js" defer></script>
</body>
</html>
```

---

## Social media

Open `components/PodcastFeatureSocial.html` in a browser to screenshot for LinkedIn, Facebook, etc. Or use the banner design as a reference. Link directly to the video URL in posts.

---

## Files

| File | Purpose |
|------|---------|
| `styles/podcast-feature.css` | Styles for banner + modal |
| `components/PodcastFeatureBanner.html` | Inline banner HTML snippet |
| `components/PodcastFeatureSocial.html` | Standalone social card (screenshot for LinkedIn, etc.) |
| `scripts/podcast-feature-modal.js` | Modal logic (injects modal, timing, localStorage) |
