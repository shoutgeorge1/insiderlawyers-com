# Step-by-step: Get https://call.insideraccidentlawyers.com/los-angeles-car-accident working

Do these steps in the **project that has the domain call.insideraccidentlawyers.com** (your long-form site). That project might be in a different folder on your computer, or you might edit it on GitHub.

---

## Step 1: Open that project

- **If you have it on your computer:** Open the folder in File Explorer, then open it in Cursor (or any editor).
- **If you only see it on GitHub:** Go to github.com → find the repo that deploys call.insideraccidentlawyers.com → click **Code** → **Open with GitHub Desktop** (or **Download ZIP** and unzip). Then open that folder in Cursor.

You need to be able to edit files in that repo. The repo might be named something like `insider-website`, `ial-lp`, or similar.

---

## Step 2: Find or create `vercel.json`

In the **root** of that project (same level as index.html or package.json or your main site files):

- **If you already have a file named `vercel.json`:** Open it and go to Step 3.
- **If you don’t have `vercel.json`:** Create a new file, name it exactly `vercel.json`, and put this in it (then save and go to Step 4):

```json
{
  "rewrites": [
    { "source": "/los-angeles-car-accident", "destination": "https://pi-search-caraccident-lp.vercel.app" },
    { "source": "/los-angeles-car-accident/", "destination": "https://pi-search-caraccident-lp.vercel.app/" },
    { "source": "/los-angeles-car-accident/:path*", "destination": "https://pi-search-caraccident-lp.vercel.app/:path*" }
  ]
}
```

---

## Step 3: If `vercel.json` already exists — add the rewrites

Open `vercel.json`. You’ll see something like `{ ... }`.

- **If there is no `"rewrites"` key:** Add a comma after the first `{`, then add this block (replace nothing, just add):

```json
  "rewrites": [
    { "source": "/los-angeles-car-accident", "destination": "https://pi-search-caraccident-lp.vercel.app" },
    { "source": "/los-angeles-car-accident/", "destination": "https://pi-search-caraccident-lp.vercel.app/" },
    { "source": "/los-angeles-car-accident/:path*", "destination": "https://pi-search-caraccident-lp.vercel.app/:path*" }
  ]
```

Example: if your file was `{ "buildCommand": "npm run build" }`, it becomes:

```json
{
  "buildCommand": "npm run build",
  "rewrites": [
    { "source": "/los-angeles-car-accident", "destination": "https://pi-search-caraccident-lp.vercel.app" },
    { "source": "/los-angeles-car-accident/", "destination": "https://pi-search-caraccident-lp.vercel.app/" },
    { "source": "/los-angeles-car-accident/:path*", "destination": "https://pi-search-caraccident-lp.vercel.app/:path*" }
  ]
}
```

- **If there is already a `"rewrites"` array:** Add the three `los-angeles-car-accident` lines inside that array (each line is one `{ "source": ..., "destination": ... },`). Don’t remove any existing rewrites.

Save the file.

---

## Step 4: Commit and push

- **In Cursor:** Open the Source Control view (Ctrl+Shift+G). You should see `vercel.json` as changed. Type a message like `Add /los-angeles-car-accident rewrite to LP`, click the checkmark to commit, then click **Sync** or **Push**.
- **In GitHub (if you edited on the website):** After editing the file, scroll down and click **Commit changes**.
- **In GitHub Desktop:** Commit the change, then click **Push origin**.

---

## Step 5: Wait for Vercel to redeploy

- Go to [vercel.com](https://vercel.com) → your account → find the **project that has the domain call.insideraccidentlawyers.com**.
- After the push, a new deployment should start. Wait until it shows **Ready** (usually 1–2 minutes).

---

## Step 6: Check the URL

Open in your browser:

**https://call.insideraccidentlawyers.com/los-angeles-car-accident**

You should see the minim LP (same as pi-search-caraccident-lp.vercel.app). The root **https://call.insideraccidentlawyers.com/** should still show the long-form site.

---

## If you can’t find the repo that has call.insideraccidentlawyers.com

- In Vercel: open the project that has that domain → **Settings** → **Git** — it will show which GitHub repo is connected. That’s the repo you need to edit.
- Then open that repo (clone it or open on GitHub) and do Steps 2–6 above.
