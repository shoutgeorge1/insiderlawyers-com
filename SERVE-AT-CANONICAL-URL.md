# Serve the LP at https://call.insideraccidentlawyers.com/los-angeles-car-accident

You want the minim LP to live at that exact URL. **The root URL (https://call.insideraccidentlawyers.com/) stays as-is** — that’s your long-form version. We’re only adding a *new* path for the minim LP; nothing is replaced or removed.

Do **one** of the following, depending on where **call.insideraccidentlawyers.com** is hosted.

---

## A. call.insideraccidentlawyers.com is on Vercel

You have a Vercel project that already has the domain **call.insideraccidentlawyers.com** attached. Use a **rewrite** so that path serves your LP deployment.

### 1. Get your LP’s Vercel URL

From the project **pi-search-caraccident-lp** in Vercel, copy the production URL, e.g.:

- `https://pi-search-caraccident-lp.vercel.app`  
  or  
- `https://pi-search-caraccident-lp-xxxx.vercel.app`

### 2. Edit the **main** site’s `vercel.json`

In the **repo/project that serves call.insideraccidentlawyers.com** (the long-form site), open or create `vercel.json` in the project root and add a `rewrites` section like this (replace `YOUR-LP-VERCEL-URL` with the URL from step 1):

```json
{
  "rewrites": [
    { "source": "/los-angeles-car-accident", "destination": "YOUR-LP-VERCEL-URL" },
    { "source": "/los-angeles-car-accident/", "destination": "YOUR-LP-VERCEL-URL/" },
    { "source": "/los-angeles-car-accident/:path*", "destination": "YOUR-LP-VERCEL-URL/:path*" }
  ]
}
```

Example if your LP URL is `https://pi-search-caraccident-lp.vercel.app`:

```json
{
  "rewrites": [
    { "source": "/los-angeles-car-accident", "destination": "https://pi-search-caraccident-lp.vercel.app" },
    { "source": "/los-angeles-car-accident/", "destination": "https://pi-search-caraccident-lp.vercel.app/" },
    { "source": "/los-angeles-car-accident/:path*", "destination": "https://pi-search-caraccident-lp.vercel.app/:path*" }
  ]
}
```

If that project already has a `vercel.json` with other settings, **merge** this `rewrites` array into it (don’t remove existing rewrites).

### 3. Deploy the main project

Commit, push, and let Vercel redeploy the project that has the domain **call.insideraccidentlawyers.com**. After deploy, **https://call.insideraccidentlawyers.com/los-angeles-car-accident** will serve the LP. The root **https://call.insideraccidentlawyers.com/** is unchanged and still serves your long-form site.

---

## B. call.insideraccidentlawyers.com is on another host (e.g. WordPress, Duda, cPanel, etc.)

You need that host to serve the LP at the path `/los-angeles-car-accident`.

**Option 1 – Upload files**

1. Create a folder on the server: **`los-angeles-car-accident`** (under the same place that serves the site root).
2. Upload into that folder:
   - **index.html** (from this repo)
   - **styles** folder (with **main.css** inside)

So the URL path `/los-angeles-car-accident/` (or `/los-angeles-car-accident/index.html`) is served by that folder.

**Option 2 – Reverse proxy**

If your host supports reverse proxy rules (e.g. Apache `ProxyPass`, Nginx `proxy_pass`), point:

- **Path:** `/los-angeles-car-accident`
- **Target:** your LP’s Vercel URL (e.g. `https://pi-search-caraccident-lp.vercel.app`)

Then the canonical URL will show the LP while the server fetches it from Vercel.

---

## Summary

| Host for call.insideraccidentlawyers.com | What to do |
|----------------------------------------|------------|
| **Vercel** | Add the rewrites above to that project’s `vercel.json`, then redeploy. |
| **Other** | Upload `index.html` + `styles/` into a `los-angeles-car-accident` folder, or set up a reverse proxy to your LP’s Vercel URL. |

After that, **https://call.insideraccidentlawyers.com/los-angeles-car-accident** is the URL for this LP.
