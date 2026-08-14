# Design Rationale — Mission Stack

## Positioning, grounded in research

A background research pass (web search, US market, 2025-2026) informed the direction below. Summary:

1. **"AI agency" is now a crowded, low-trust category.** The number of self-described AI/automation agencies grew roughly 6x between 2024 and 2026, and a large share of them ship almost no real client work. Meanwhile most US small-business owners are skeptical of AI accuracy and worry it makes their business feel less personal. Leading with "AI" reads as noise, not credibility.
2. **What actually earns trust in this niche** (websites + lead capture + follow-up for local/service businesses): picking a specific business outcome and being concrete about it, transparent pricing, and real proof — not badges, not vague "trusted by" claims. Category players (Podium, Birdeye, GoHighLevel-based agencies) win by naming a vertical and quantifying one outcome, not by claiming broad AI capability.
3. **SEO/AI-crawler practice in 2025-2026**: `llms.txt` plus a deliberate robots.txt policy (allow AI *answer* crawlers, decide separately on *training* crawlers) is now a reasonable baseline. A fully remote, no-office business should use `Organization`/`Service` schema, not `LocalBusiness`/`ProfessionalService` — the latter implies a physical premises Mission Stack doesn't have.
4. **FTC / credibility guardrails**: don't imply a US office, team, or local presence that doesn't exist; don't use "as seen on"-style badges or unverifiable trust theater; every claim (express or implied) needs to be true and something Andrew could substantiate if asked.

This directly shaped the copy and structural decisions below: the previews say "remote systems partner," never imply a US office; the one piece of proof (the Dreamglade project) is kept honest and specific rather than dressed up as a "case study" with invented metrics; and the demonstration teardown is explicitly labeled as illustrative, not a real client engagement.

## Design benchmarks

Three real, well-known professional references, and specifically what's borrowed from each — not a wholesale copy of any one of them:

**1. Stripe (stripe.com)** — Editorial confidence through typography and content design, not decoration. Borrowed: pairing a serif or high-contrast display face for headlines against a clean grotesque for body copy; generous line-height and whitespace that lets a dense B2B pitch breathe; using real diagrams/screenshots instead of stock photography as the primary visual language.

**2. Linear (linear.app)** — Restraint and precision in a dark UI. Borrowed: a single accent color used sparingly against navy/charcoal so it actually means something when it appears (CTA, one highlight); tight, confident microcopy; subtle motion (fade/slide-in on scroll, not attention-grabbing animation); dark sections used structurally (to separate pricing/process from editorial sections), not just for mood.

**3. Basecamp / 37signals (37signals.com)** — Plainspoken, founder-voiced B2B writing with warm, human backgrounds instead of cold corporate blue. Borrowed: first-person, direct copy ("I review your site, I tell you what's broken"); warm off-white backgrounds instead of stark white; a willingness to be specific and slightly informal in a B2B context, which reads as more trustworthy than polished agency-speak — this maps directly onto Andrew being a solo, direct-contact founder rather than "an agency."

These three references also map onto the three preview "vibes" below — each preview leans harder into one benchmark while keeping the shared brand constraints (navy/charcoal + warm white + one amber/copper accent, no neon, no purple AI gradients, no stock photography, no circuit-board/robot imagery).

## The three previews

| # | Name | Leans toward | Feel |
|---|---|---|---|
| 1 | **Editorial Warm** | Stripe + Basecamp | Serif display headlines, warm parchment background, generous whitespace, the calmest and most "trustworthy consultant" of the three. Closest to the brief's literal design direction. |
| 2 | **Systems Dark** | Linear | Charcoal/navy-dominant, monospace accents on labels and numbers, grid/blueprint motifs suggesting "systems," more technical and precise. Best if Andrew wants to feel more like a tools/ops brand. |
| 3 | **Modern Approachable** | Basecamp, lighter touch | Brightest and friendliest of the three, rounded cards, navy used only for footer/CTA anchoring, reads closest to a friendly SMB-facing SaaS product rather than a consulting firm. Best if the target buyer skews less corporate (e.g. trades, home services, salons). |

All three share: identical copy/positioning/offer (only visual system differs), identical information architecture (see DESIGN.md → page-level brief), `Organization`+`Service`+`FAQPage` JSON-LD, no fabricated proof, and the same non-negotiable guardrails (no Lima/Peru mentions, no implied US office, no invented case studies/testimonials/results).

## What's deliberately NOT included

- No fabricated client logos, testimonials, or "results" — the only real proof point kept is the Dreamglade website (genuine, verifiable, live), described honestly as remote/international work rather than reframed as a US case study.
- No stock photography of generic "business people." Visual language is annotated screenshots, a sample spreadsheet, and a process diagram, per the brief.
- No claim of a US office, US team, or US address anywhere in metadata, structured data, or copy.
- No pill-shaped buttons everywhere / no purple gradients / no circuit-board or robot iconography, per the brief's explicit avoid-list.
