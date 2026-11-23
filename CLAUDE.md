# Notes for Claude

This repo is the Prairie Valley Church website (owner: Josh Slater, jslater1226). GitHub Pages publishes `dist/` from `main` through `.github/workflows/pages.yml` (preview: https://jslater1226.github.io/prairie-valley-church-site/). Netlify was the first host but its credits ran out on 2026-11-23, so it is no longer used. The repo is public because GitHub Pages is free only for public repos on this plan.
- `NOINDEX=True` in `build/make.py` keeps the preview out of search engines. Set it to False at launch.
- Batch edits and push once per round. Every push triggers a deploy.

- Edit `build/` (mostly `build/copyedit.txt` and `build/make.py`), run `cd build && python3 make.py`, check the result, then commit `build/` and `dist/` together and push to `main`.
- Do not change DNS, Netlify settings, or repo visibility without Josh's yes.
- Do not commit under Josh's name or email. Commits are signed as Claude.
