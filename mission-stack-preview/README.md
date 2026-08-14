# Mission Stack — preview directory

Three redesign directions for the Mission Stack rebrand, built for review before anything goes live. See `../DESIGN.md` and `../design-rationale.md` for the full brief. Rebuilt after initial feedback that the first pass read as generic AI-template SaaS design — these lean into current award-winning patterns (Linear/Attio-style kinetic type, editorial magazine layouts, console/product-UI framing) instead of a recolored card-grid template.

- `v1-signal/` — dark, high-contrast, oversized kinetic typography with a running problem-statement marquee, scroll-driven journey timeline, and an interactive hover-teardown. Closest to Linear/Attio.
- `v2-field-notes/` — warm-paper editorial magazine: sticky table-of-contents rail, serif masthead, drop-cap founder quote, hand-annotated "clipping" teardown.
- `v3-console/` — light product-console framing: window-chrome panels, a typed terminal intro line, a CLI-style journey status list that checks off stages as you scroll, terminal-styled offer deliverables.

Each is a self-contained static HTML file (open directly in a browser, no build step). `sitemap.xml`, `robots.txt`, and `llms.txt` in this directory are drafts for `missionstack.us` and are **not** wired to any live domain.

This directory does not affect production. The live site (`index.html`, `en/index.html`, `sitemap.xml`, `robots.txt` at the repo root) is untouched.
