# DESIGN.md — Mission Stack Visual System

Companion to `design-rationale.md` (why) and `migration-checklist.md` (what/when). This file defines the concrete design tokens for the three preview directions and the shared page-level conversion brief they all implement.

## Shared brand constraints (all 3 vibes)

- Palette family: dark navy/charcoal + warm white + **one** restrained amber/copper/muted-gold accent. No neon, no purple AI gradients, no additional accent colors.
- Typography: one display face (serif or high-contrast) for headlines + one grotesque/sans for body and UI — never more than 2 font families.
- Medium-radius cards (not sharp, not pill-everything), restrained borders/shadows, accessible contrast (WCAG AA minimum for body text).
- Mobile-first, subtle motion only (opacity/translate on scroll-into-view, no parallax gimmicks).
- Visual language: annotated screenshots, process diagrams, a sample spreadsheet — never stock photography, never robot/circuit imagery.

## Page-level conversion brief (shared by all 3 previews)

1. **Hero** — state the business problem in one sentence, primary CTA above the fold, no scroll required to see the offer.
2. **Revenue leaks** — 3-card breakdown of where inquiries die (weak site, unclear forms/slow response, no follow-up). Sets up the rest of the page as "here's what we fix," not "here's what we sell."
3. **Find → Understand → Inquire → Qualify → Follow Up → Book** — a 6-step horizontal journey diagram. This is the single most important visual on the page: it's the mental model for everything Mission Stack does, and it's diagram-first, not photo-first.
4. **Services organized by outcome** — not "web design / SEO / automation" as a feature list, but "get found," "get chosen," "get the booking" as outcome groupings.
5. **Systems Review offer** — the entry offer, with the 5 concrete deliverables listed explicitly (annotated screenshots, journey map, lead-capture/follow-up gap list, 30-day plan, prioritized spreadsheet).
6. **Demonstration teardown** — one annotated-screenshot mockup + one sample spreadsheet row set, **labeled "Illustrative example" in the UI itself**, not presented as a real client engagement.
7. **Process: Review → Prioritize → Build → Improve** — 4-step, matches the existing Lima Systems Lab process language (already validated copy, just re-branded).
8. **Founder section** — verified facts only: Andrew Rafaniello, founder, US Army veteran, direct communication, remote systems partner. No fabricated bio details.
9. **Final CTA** — repeat the Systems Review offer once more before the footer.

Primary CTA everywhere: **Request a Systems Review**. Secondary CTA: **See What Gets Fixed** (anchors to the revenue-leaks / demonstration sections).

---

## Vibe 1 — Editorial Warm (Stripe + Basecamp lean)

```
Typography
  Display:      "Newsreader" (serif), weight 400-600, tight letter-spacing (-0.04em)
  Body/UI:      "Inter", weight 400-700
  Scale:        h1 clamp(2.75rem, 6vw, 5rem) / h2 clamp(2.2rem, 4.5vw, 3.6rem) / body 1.05rem / small 0.85rem

Color
  --bg:         #FAF7F0   (warm parchment)
  --bg-soft:    #F2EADF
  --ink:        #14110C
  --muted:      #5E5646
  --dark:       #1C1810   (near-black warm charcoal, used for dark sections/footer)
  --accent:     #B8834A   (copper)
  --accent-soft:#DDB07C
  --line:       rgba(20,17,12,0.12)
  --white:      #FFFFFF

Spacing / Radius / Shadow
  Section pad:  96px vertical desktop / 64px mobile
  Card radius:  24px
  Card shadow:  0 20px 60px rgba(20,17,12,0.08)
  Border:       1px solid var(--line)

Layout
  Max width:    1180px
  Hero:         2-col (copy + founder card), collapses to 1-col < 1040px
  Buttons:      rounded-rect (14px radius), min-height 52px, no pill shapes
```

## Vibe 2 — Systems Dark (Linear lean)

```
Typography
  Display:      "Space Grotesk" or system fallback, weight 500-700, tight tracking
  Body/UI:      "Inter", weight 400-600
  Monospace accents on labels/numbers/step counters: "IBM Plex Mono" / ui-monospace
  Scale:        h1 clamp(2.6rem, 5.5vw, 4.6rem) / h2 clamp(2rem, 4vw, 3.2rem) / body 1rem

Color
  --bg:         #0B0F14   (charcoal, dominant background — dark-first design)
  --bg-soft:    #131922
  --ink:        #F4F6F8
  --muted:      #8A94A3
  --panel:      #161D27
  --accent:     #C98A3E   (muted gold, used only for CTAs / active states / step numbers)
  --line:       rgba(244,246,248,0.12)
  --white:      #FFFFFF

Spacing / Radius / Shadow
  Section pad:  88px vertical desktop / 56px mobile
  Card radius:  16px (tighter than Vibe 1 — more "systems," less "editorial")
  Card shadow:  none (flat panels + 1px border instead, Linear-style)
  Border:       1px solid var(--line)

Layout
  Max width:    1200px
  Hero:         2-col, journey diagram rendered as a horizontal connected-node strip directly under hero
  Buttons:      12px radius, monospace label caps for secondary buttons (e.g. "REQUEST_REVIEW")
  Grid motif:   faint 1px grid-line background texture behind hero only, opacity 0.04
```

## Vibe 3 — Modern Approachable (lighter Basecamp lean)

```
Typography
  Display:      "Newsreader" for H1 only (kept for brand consistency); "Inter" weight 700-800 for H2/H3
  Body/UI:      "Inter", weight 400-700
  Scale:        h1 clamp(2.6rem, 6vw, 4.6rem) / h2 clamp(1.9rem, 4vw, 2.8rem) / body 1.05rem, slightly larger line-height (1.65) for a friendlier feel

Color
  --bg:         #FFFDF9   (brightest of the three, near-white warm)
  --bg-soft:    #FBF3E7
  --ink:        #1E2430
  --muted:      #5B6472
  --dark:       #14202E   (used sparingly — footer + final CTA band only, NOT full sections)
  --accent:     #D89B4A   (warmer, slightly brighter gold than Vibe 1)
  --line:       rgba(30,36,48,0.10)
  --white:      #FFFFFF

Spacing / Radius / Shadow
  Section pad:  80px vertical desktop / 56px mobile
  Card radius:  28px (roundest of the three — friendliest feel, but still not pill-shaped)
  Card shadow:  0 16px 40px rgba(30,36,48,0.06) — softer/lighter than Vibe 1
  Border:       1px solid var(--line)

Layout
  Max width:    1160px
  Hero:         2-col, founder photo placeholder card is smaller/friendlier, more whitespace around CTA buttons
  Buttons:      16px radius, primary CTA in accent gold (not navy) — the only vibe where the primary button isn't dark/navy
  Dark sections: limited to footer + final CTA only, so the page reads "light B2B SaaS" rather than "consulting firm," per the design-rationale mapping to a less-corporate buyer
```

---

## Iteration log

- **v1 (this pass)**: all three vibes built as static, self-contained HTML previews implementing the full page-level conversion brief above, using only verified founder facts and the one real (Dreamglade) proof point, explicitly labeled where content is illustrative. No live screenshots exist yet for desktop/mobile QA since these are new artifacts, not a running app — visual QA notes captured directly in each preview file's structure (semantic HTML, real breakpoints at 1040px/760px matching the current production site's proven breakpoints) rather than from a screenshot audit.
- **Next iteration (pending Andrew's pick)**: once a direction is chosen, do a real desktop/mobile screenshot pass, tighten hierarchy/spacing per that audit, and move from static HTML to whatever stack Andrew wants for production (the current site is plain HTML/CSS with no framework, so continuing that way keeps the migration simple, but a Next.js rebuild is also reasonable given the `dreamglade-website` precedent).
