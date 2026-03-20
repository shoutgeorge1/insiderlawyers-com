# Baseline push summary — insiderlawyers.com

**Date:** 2026-03-19 (local)

## Commits

| Role | Hash | Message |
|------|------|---------|
| **Baseline stabilization** | `a54e8cf` | Baseline stabilization push — template SSOT, navigation hard lock, interaction reset, GTM hostname governance |
| **Docs (this file + follow-ups)** | `99b599c` … `1b6c699` | Add/update `push_baseline_summary.md` on `master` |

### Baseline commit stats

| Field | Value |
|--------|--------|
| **Files changed** | **137** |
| **Diffstat** | +4040 / −2189 lines (repository-wide; includes GTM guard injection + legacy inline nav CSS removal across HTML) |

## Remote & push

| Field | Value |
|--------|--------|
| **Remote** | `origin` → `https://github.com/shoutgeorge1/insiderlawyers-com.git` |
| **Branch** | `master` |
| **Push** | **Succeeded** — baseline `dd52d68..a54e8cf`; tip after docs `..1b6c699` → `origin/master` |

## Explicitly excluded from this commit (per safety rules)

- `los-angeles-car-accident-lawyer/index.html` — **not included** (working tree restored to `HEAD` before staging so PPC layout changes stay out of baseline).
- `scripts/clean_google_ads_exports_for_llm.py`, `scripts/process_google_ads_bulk_export_for_llm.py` — **untracked**, not staged.
- `**/__pycache__/**` — not staged.
- `_old-site-extract/` — not part of this commit workflow.

## Notes

- `scripts/site-nav.js`, `components/global-chrome-before-main.html`, and `components/global-footer.html` had **no local modifications** at commit time; they remain at the last committed baseline on `master`.
- Governance markdown (`scripts/layout_audit.md`, `scripts/layout_fix_summary.md`) had **no changes** to stage vs `HEAD`.

## Next recommended actions *(do not execute automatically)*

1. Deploy `origin/master` to production (e.g. Vercel/hosting) and smoke-test **www.insiderlawyers.com** + **staging/preview** to confirm GTM **does not** load off approved hostnames.
2. Repeat a similar baseline commit for **`pi-search-caraccident-lp`** if that tree should track the same GTM/nav/CSS governance (separate repo path / submodule).
3. Decide whether to **delete or `.gitignore`** the experimental `clean_google_ads_*` / `process_google_ads_*` scripts if they should never land in this repo.
4. Optional: run `python scripts/normalize_gtm_head.py` on any branch that still has old GTM snippets after merges.

---

*Generated as part of the baseline stabilization push.*
