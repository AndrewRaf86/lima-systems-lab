# Migration Checklist — Lima Systems Lab → Mission Stack

Status legend: `[ ]` not started · `[~]` prepared, not activated · `[x]` done · `[BLOCKED]` needs info/access this session doesn't have

**Nothing below touches production.** `index.html`, `en/index.html`, `sitemap.xml`, `robots.txt`, and the live `limasystems.digital` Vercel domain binding are untouched. All new work lives under `mission-stack-preview/` in this repo plus the docs at repo root, on branch `claude/mission-stack-migration-hsldy8`.

## 0. Facts confirmed this session
- [x] Current hosting: **Vercel**, project `lima-systems-lab`, framework `null` (static export), production domain `limasystems.digital` attached, deployment state `READY`.
- [x] `missionstack.us` is registered (owned by someone) but **not attached to this Vercel team/account or any of its 21 projects**.
- [BLOCKED] Registrar and DNS provider for `missionstack.us` — could not be queried; this sandbox's network policy blocks outbound DNS/whois/HTTP to arbitrary domains (only github/npm/pypi/anthropic-style allowlisted hosts are reachable). **Need from Andrew:** where was `missionstack.us` purchased (Vercel Domains under a different account, GoDaddy, Namecheap, Cloudflare, Google Domains, etc.) and where was the SSL certificate issued?
- [BLOCKED] Same limitation applies to independently re-verifying `limasystems.digital`'s live DNS records (A/CNAME/MX/TXT) — the Vercel API confirms the *binding*, not the resolver-level records. A follow-up session with unrestricted egress, or Andrew pasting `dig`/registrar-panel output, can close this out.

## 1. Brand replacement (public + technical surfaces)
- [~] Logo/wordmark — no logo file exists today (founder photo only); new mark designed in `DESIGN.md`, not yet built as a production asset.
- [~] Navigation, footer, page titles, meta descriptions, OG/Twitter metadata, canonical URLs — rewritten in the 3 preview homepages under `mission-stack-preview/`.
- [~] JSON-LD (`Organization`/`Service`/`Person`/`FAQPage`) — rewritten for previews using `Organization` instead of `ProfessionalService`/`LocalBusiness` (a fully remote consultancy shouldn't claim a physical-premises schema type — see design-rationale.md).
- [~] Sitemap, robots, `llms.txt` — draft versions included in preview directory, **not wired to a live domain**.
- [ ] Image filenames/alt text — previews use new filenames without "lima"; production images (`andrew-rafaniello-web-lima.jpg`, `proof-dreamglade.jpg`) untouched until approval.
- [ ] Contact forms / thank-you pages / autoresponders — none exist today (WhatsApp + mailto only); no autoresponder to migrate. If Andrew wants a real form for Mission Stack, that's a new build, not a migration item.
- [ ] Email subject lines in `mailto:` links — updated in previews to drop "Lima Systems Lab."
- [ ] README, package/project metadata — README rewrite prepared as part of this branch; **Vercel project rename is NOT done** (shared infrastructure — needs explicit go-ahead since renaming affects dashboard links Andrew may have bookmarked).
- [ ] Hosting project name / deployment labels — decision needed: rename `lima-systems-lab` Vercel project vs. create a new `mission-stack` project and cut over. Recommendation in checklist §4.
- [ ] Environment variables — none exist in this static-site repo today; N/A unless Andrew adds server-side features later.
- [ ] Social links — LinkedIn stays as-is (personal, brand-neutral). No other social profiles found in the repo.
- [ ] Privacy policy / Terms of service — **none exist today** for Lima Systems Lab. Mission Stack should ship with real ones before launch (flag as new content to draft, not a migration).
- [ ] Copyright text — updated in previews to "© 2026 Mission Stack."

## 2. Domain & DNS (prepare only — do not activate)
- [BLOCKED] Confirm `missionstack.us` registrar/DNS provider (see §0).
- [ ] Once known: obtain exact DNS records the *hosting provider* (Vercel, if that's where Mission Stack ends up, or wherever Andrew prefers) requires for `missionstack.us` and `www.missionstack.us`.
- [ ] Choose canonical host between apex (`missionstack.us`) and `www` — **recommend apex as canonical** (matches current `limasystems.digital` convention, which uses the apex, not `www`), with `www` 301-redirecting to apex.
- [ ] Verify DNS resolution, HTTPS/SSL, correct deployment, no mixed content, canonical URL, sitemap URL, robots URL — all deferred until domain is actually connected to a project.
- [ ] Decide: attach `missionstack.us` to the **existing** `lima-systems-lab` Vercel project (simplest, one deploy target, but keeps old-brand project name until renamed) or a **new** Vercel project. Either way, `limasystems.digital` stays attached and serving production traffic throughout — Vercel supports multiple domains per project, so this is non-destructive by construction.
- [ ] Keep `limasystems.digital` registered and resolving after launch — do not let it lapse; plan the 301 redirect (§3) instead of a takedown.

## 3. SEO migration (prepare, do not activate)
- [~] Draft Mission Stack `sitemap.xml`, `robots.txt`, `llms.txt` — included in `mission-stack-preview/`.
- [~] Canonical URLs, OG URLs, structured-data URLs point at `missionstack.us` **inside the preview files only**.
- [ ] 301 redirect map, `limasystems.digital` → `missionstack.us`:
  | Old | New |
  |---|---|
  | `/` | `/` |
  | `/en/` | `/` (if Mission Stack ships English-only) or `/en/` (if the ES/EN split continues — decision needed) |
  Two production URLs total today, so the redirect map is small — the real decision is whether Mission Stack keeps a Spanish version at all, since the brief targets US small-business owners specifically. Flagging for Andrew's call rather than assuming.
- [ ] New Google Search Console property for `missionstack.us` (needs Andrew's Google account access — outside this session's scope).
- [ ] Analytics: no analytics snippet exists in the current `lima-systems-lab` repo at all (unlike `dreamglade-website`, which has `@vercel/analytics`). Decide whether Mission Stack adds Vercel Analytics or similar before/at launch.
- [ ] Internal links — trivial here since it's a 2-page site with no internal nav beyond anchors + the ES/EN toggle.

## 4. Contact & email systems
- [ ] Current contact paths verified from source: WhatsApp (`wa.me/13475206792`) and `mailto:rafanielloandrew@gmail.com`. No form, no CRM, no spreadsheet destination, no autoresponder exists — confirmed by full-repo search, not just assumption.
- [ ] Decide whether WhatsApp stays the primary CTA for a US audience — US service-business owners skew more toward "request a call" / email / form than WhatsApp; flagged as a positioning question for Andrew, addressed in `design-rationale.md`.
- [ ] Branded email (`hello@missionstack.us`, `andrew@missionstack.us`) — not yet provisioned; requires email hosting decision (Google Workspace, Zoho, etc.) tied to wherever `missionstack.us` DNS ends up. Do not delete `rafanielloandrew@gmail.com` until the new addresses are live and tested.
- [ ] If/when email DNS changes: verify SPF, DKIM, DMARC before go-live.

## 5. Quality control (run before requesting approval — see also DESIGN.md iteration log)
- [x] Full case-insensitive search for Lima/Peru/old-brand terms across the repo — see `migration-inventory.md`.
- [ ] Confirm remaining old-domain references exist only in migration/redirect/historical docs (true today: only in this checklist, the inventory, and the still-live production files, which is expected and correct pre-launch).
- [ ] No old public branding remains **in the Mission Stack previews** — verify per preview build.
- [ ] Desktop + mobile layout test for all 3 previews.
- [ ] Every CTA/link test (WhatsApp/mailto placeholders, nav anchors) in previews.
- [ ] Every route test — trivial (single-page previews), but confirm no dead anchors.
- [ ] Canonical URL test — previews point at `missionstack.us` (not live, informational only).
- [ ] Structured data validated (Organization/Service/FAQPage) — spot-check JSON-LD syntax.
- [ ] Sitemap/robots draft reviewed.
- [ ] HTTPS — N/A until a real deployment exists.
- [ ] Email delivery — N/A, no email system built yet.
- [ ] Production artifact build — N/A for these static previews; applies once a preview is chosen and Andrew wants a real Vercel preview deployment (can be done on request, still non-production).
- [ ] Migration report summarizing what changed vs. what needs manual approval — this checklist + inventory together serve as that report; update after Andrew picks a direction.

## Explicit stop point

Per the request: **do not** change production DNS, redirect `limasystems.digital`, delete anything, rename the live Vercel project, or deploy any Mission Stack content to a production domain. Everything above marked `[~]` or `[ ]` stays that way until Andrew reviews the 3 previews and explicitly approves a direction and a go-live plan.
