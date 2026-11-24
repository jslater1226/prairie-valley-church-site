# Notes for Claude

This repo is the Prairie Valley Church website (owner: Josh Slater, jslater1226). GitHub Pages publishes `dist/` from `main` through `.github/workflows/pages.yml` (preview: https://jslater1226.github.io/prairie-valley-church-site/). Netlify was the first host but its credits ran out on 2026-11-23, so it is no longer used. The repo is public because GitHub Pages is free only for public repos on this plan.
- `NOINDEX=True` in `build/make.py` keeps the preview out of search engines. Set it to False at launch.
- Batch edits and push once per round. Every push triggers a deploy.

- Edit `build/` (mostly `build/copyedit.txt` and `build/make.py`), run `cd build && python3 make.py`, check the result, then commit `build/` and `dist/` together and push to `main`.
- Do not change DNS, Netlify settings, or repo visibility without Josh's yes.
- Do not commit under Josh's name or email. Commits are signed as Claude.

- Events are no longer in the page code. They live in `data/events.json` and are edited through Pages CMS (config in `.pages.yml`, flyer images in `data/media/`). The deploy workflow validates the JSON and copies `data/` into the published site. Do not move `data/` under `build/` or `dist/`, because `make.py` deletes `dist/` on every build.
- Sermon series buttons (`data/series.json`) and the ministries list (`data/ministries.json`) are also edited through Pages CMS (`.pages.yml`). `build/copyedit.txt` renders them into the page at build time as a fallback, and the page script re-renders them from the JSON at load. The workflow validates all three JSON files.
