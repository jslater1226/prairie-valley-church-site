# Notes for Claude

This repo is the Prairie Valley Church website (owner: Josh Slater, jslater1226). Netlify publishes `dist/` from `main`. The repo is public so Netlify's free plan accepts pushes from any contributor.

- Edit `build/` (mostly `build/copyedit.txt` and `build/make.py`), run `cd build && python3 make.py`, check the result, then commit `build/` and `dist/` together and push to `main`.
- Do not change DNS, Netlify settings, or repo visibility without Josh's yes.
- Do not commit under Josh's name or email. Commits are signed as Claude.
