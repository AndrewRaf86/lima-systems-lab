# Migration Inventory — Lima Systems Lab → Mission Stack

Generated: 2026-08-14
Scope: full repository, case-insensitive search, excluding `.git`. Repo contains no `node_modules` or build output (static 2-page site).

This is a **read-only inventory**. Nothing listed here has been changed yet. See `migration-checklist.md` for the execution plan and `DESIGN.md` / `design-rationale.md` for the redesign itself.

## Files in repo

| File | Role | Contains old-brand content? |
|---|---|---|
| `index.html` | Production homepage, Spanish (`es_PE`), canonical for `/` | Yes |
| `en/index.html` | Production homepage, English, canonical for `/en/` | Yes |
| `sitemap.xml` | Sitemap, 2 URLs | Yes (URLs) |
| `robots.txt` | Crawler rules incl. GPTBot/ClaudeBot/PerplexityBot allow list | Yes (sitemap URL) |
| `README.md` | Repo description | Yes |
| `andrew-rafaniello-web-lima.jpg` | Founder photo, referenced by both HTML files | Filename only ("lima") |
| `proof-dreamglade.jpg` | Screenshot of real client project (Dreamglade retreat site) | No brand terms, but tied to a Lima-based project |

No `.env`, CI config, or deployment manifest exists in this repo — Vercel project settings (name, env vars) live outside the repo; see checklist.

## Category-by-category findings

### 1. Brand name ("Lima Systems Lab" / "LSL")
- `index.html`: title tag (L7), meta description (L11), OG title/description (L16, L19), JSON-LD `ProfessionalService.name` (L850), nav brand mark "LSL" (L942) and brand title (L944), founder strip copy (L1014), trust section copy (L1224), FAQ answers (L896, L1307), mailto subject (L1285), footer copyright (L1373).
- `en/index.html`: same pattern — title (L7), OG (L16), JSON-LD (L738), nav (L822, L824), hero copy (L860), founder strip (L897), FAQ answers (L784, L808, L1064, L1079), footer (L1124).
- `README.md`: L2, describes the repo as "Landing page for Lima Systems Lab."

### 2. Location language (Lima / Peru / Sudamérica / South America)
- Spanish hero eyebrow "· Lima" (index.html:971), hero copy "Sudamérica y Estados Unidos" (index.html:980), trust line "Servicios para negocios en Sudamérica y Estados Unidos" (index.html:997), problem/services copy referencing "el mercado de Lima" (index.html:1254), FAQ Q&A "¿Trabajas con negocios fuera de Lima?" (index.html:917, 1321), footer (index.html:1373).
- English hero eyebrow "Serving businesses across South America and the United States" (en/index.html:851), hero H1 subtitle (en/index.html:856), hero copy (en/index.html:860), FAQ "Where are you based?" answer explicitly naming Lima/South America (en/index.html:808, 1079), footer (en/index.html:1124).
- JSON-LD `areaServed` includes `Country: Peru` and `Place: South America` in both files (index.html:858-863; en/index.html:746-751).
- Work/portfolio copy describes the Dreamglade project as "un retiro de bienestar en la selva peruana" / "a wellness retreat in the Peruvian jungle" (index.html:1033, 1041; en/index.html:916, 924) and "Conozco el mercado de Lima" (index.html:1254).

### 3. Locale metadata
- `og:locale` = `es_PE` (index.html:23). English version correctly uses `en_US` (en/index.html:23) — only the Spanish locale tag needs to change.
- `hreflang="es-PE"` on both files' `<link rel="alternate">` tags (index.html:27, en/index.html:27) — used for the ES/EN alternate pair, independent of the brand migration but worth revisiting if the ES page is retired or kept.

### 4. Domain references (limasystems.digital)
- Canonical URLs: index.html:26, en/index.html:26.
- `hreflang` alternates: index.html:27-29, en/index.html:27-29.
- OG `url`/`image`: index.html:22,24; en/index.html:22,24.
- JSON-LD `@id`/`url`/`image`/founder `@id`: index.html:849-852,872,884; en/index.html:737-740,760,772.
- `sitemap.xml`: both `<loc>` entries (L4, L8).
- `robots.txt`: `Sitemap:` line (L19).

### 5. Structured data (JSON-LD)
- `ProfessionalService` block in both files names Peru/South America in `areaServed`, uses `priceRange` in PEN (index.html:854) vs USD (en/index.html:742) — inconsistent currency across locales, not just a brand issue.
- `FAQPage` entries in Spanish ask directly about Lima pricing/location (index.html:893-931); English FAQ includes "Where are you based?" naming Lima explicitly (en/index.html:805-809).
- `Person` (founder) schema itself is location-neutral and can carry over as-is (index.html:883-887; en/index.html:771-775).

### 6. Pricing / currency (PEN, S/, local pricing model)
- Spanish pricing grid entirely in Peruvian soles: `S/ 550`, `S/ 1,850` (index.html:1114,1138,1161 and JSON-LD `priceRange: "PEN 550 - 2990"` at L854). This is a full pricing-model migration question, not just a copy swap — see checklist.
- English pricing already in USD ($150 / $800 / $250), so the EN page's price *values* don't need currency conversion, only positioning/service-scope updates to match Mission Stack's Systems Review offer.

### 7. Contact / phone / WhatsApp
- Phone/WhatsApp number `+13475206792` appears as `tel:`-style JSON-LD (`telephone`) and multiple `wa.me` links with pre-filled Spanish/English messages throughout both files (index.html: L960,986,1057,1127,1151,1173,1344,1362; en/index.html: L840,866,960,984,1006,1095,1113). This is a real, working US-format WhatsApp number — not Lima-specific — but every prefilled message references "página web" / "business website" generically, none mention Lima by name, so these are reusable as-is once rebranded. Confirm with Andrew whether this number stays the primary contact channel for Mission Stack.
- Email `rafanielloandrew@gmail.com` used in `mailto:` links with brand-specific subject lines, e.g. `subject=Consulta%20Lima%20Systems%20Lab` (index.html:1285) and `subject=Website%20for%20my%20business` (en/index.html:1102). No branded email domain (`@missionstack.us`) exists yet — see checklist.
- No contact form exists on the site today — WhatsApp and mailto links are the only contact paths. No autoresponder, no CRM/spreadsheet integration, no thank-you page found in this repo.

### 8. Social / external links
- LinkedIn: `linkedin.com/in/andrewrafaniello/` (index.html:1276,1379; en/index.html:1130) — personal founder profile, brand-neutral, carries over.
- External portfolio link to `dreamglade.com` (index.html:1044; en/index.html:927) — a real, live client site. Not a Lima Systems Lab-branded asset; safe to keep as genuine proof of work once the surrounding copy drops the Peru/jungle framing (or reframes it as "hospitality client" without the geographic descriptor, since Mission Stack shouldn't spotlight Peru-based work as its lead proof point for a US audience — see design-rationale.md).

### 9. Images / filenames / alt text
- `andrew-rafaniello-web-lima.jpg` — filename contains "lima." Used as founder photo (index.html:1004,1232; en/index.html:887). Alt text: "Andrew Rafaniello, fundador de Lima Systems Lab" (index.html:1007) / "Andrew Rafaniello, founder of Lima Systems Lab" (en/index.html:890), and again at index.html:1236.
- `proof-dreamglade.jpg` — filename references the client, not Lima Systems; alt text explicitly says "selva peruana" / "Peruvian jungle" and "diseñado por Lima Systems Lab" (index.html:1041; en/index.html:924).
- No favicon, OG-image variant, or logo file exists in the repo beyond these two photos — Mission Stack will need a new brand mark/wordmark asset (see DESIGN.md).

### 10. SEO / AI-crawler configuration
- `robots.txt` explicitly allows GPTBot, ClaudeBot, Claude-Web, PerplexityBot, Google-Extended (L4-17) — a deliberate AI-visibility choice worth preserving and extending with an `llms.txt` file (none exists today).
- `sitemap.xml` lists exactly the 2 production URLs; will need Mission Stack URLs once the new domain goes live, and should stay as a **separate, non-activated file** until approval (see checklist).

### 11. Environment variables / project metadata / deployment
- No `.env`, `vercel.json`, or CI file exists in this repo. Hosting is **Vercel** — confirmed via the Vercel API: project `lima-systems-lab` (ID `prj_A2flIB49hmDTNrXi8fhTzxV3V3QB`) in team `andrewraf86's-projects`, framework `null` (static site), production domain `limasystems.digital` attached and `READY`, plus the default `*.vercel.app` domains.
- The Vercel **project name itself** ("lima-systems-lab") is old-brand and will need a decision: rename in place vs. create a new "mission-stack" project. Renaming is reversible and doesn't affect the live domain binding, but it is a change to shared infrastructure — do not do this until approval (see checklist).
- `missionstack.us` was checked against this Vercel account's domain registrar API and **is not registered through this Vercel team and not attached to any of its 21 projects** (confirmed by inspecting every project's domain list). Its actual registrar and DNS provider could not be determined from this session — outbound DNS/whois/HTTP lookups to arbitrary hosts are blocked by this sandbox's network egress policy (only github.com, npm, pypi, and a few other allowlisted hosts are reachable). **This needs to be resolved with Andrew directly** (which registrar was used to buy missionstack.us, and where the SSL certificate referenced in the request was issued) before any DNS work can be planned. See `migration-checklist.md` → "Domain & DNS" for the exact follow-up questions.

### 12. Terms not found in this repo
No occurrences of: old email-signature templates, form autoresponder text, CRM/spreadsheet destination references, thank-you page, or any additional documentation files (docs/, CHANGELOG, etc.) — this repo is just the two HTML pages plus SEO/asset files listed above. If Andrew has other Lima Systems Lab material (email signature, Google Business Profile, LinkedIn company page, Instagram, invoicing templates), those live outside this repo and are out of scope for a code search — flagged in the checklist as a manual inventory item.

## Note on repository scope

This session also had access to a second repository, **`dreamglade-website`**. That repo is a **separate, unrelated business** (a Next.js site for "Dreamglade," a wellness retreat — the same client referenced as portfolio proof above, not Lima Systems Lab itself). It contains no Lima Systems Lab branding and was not touched or included in this migration. All migration work in this document and the accompanying checklist applies only to the `lima-systems-lab` repository.
