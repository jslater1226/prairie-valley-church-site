# Prairie Valley Church website

Static site for prairievalleychurch.com. Hosted on Netlify, which publishes the `dist/` folder.

- `dist/` is the finished site. This is what visitors see.
- `build/` holds the source. Run `cd build && python3 make.py` (needs Pillow and Playwright/Chrome only for previews) to rebuild `dist/`.
- `build/copyedit.txt` has most of the wording and layout edits. `build/make.py` holds times, phone, and links.
- Series buttons link to Church Center sermon pages. Add new ones in `build/copyedit.txt`.

Changes are made by asking Claude. It edits `build/`, rebuilds, checks the result, and pushes to `main`.
