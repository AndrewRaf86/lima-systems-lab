"""
segment_leads.py — Assign outreach segments and draft messages. Build send-ready list.

Reads:  data/qualified_leads.csv
Writes: data/qualified_leads.csv (adds segment, outreach_draft, language)
        data/send_ready_leads.csv
        reports/send_ready_summary.md

Segments:
  A — High-trust clinic, unclear website or booking path
  B — Review-heavy business with weak follow-up
  C — Lima business with WhatsApp/contact friction
  D — Expat/tourist-facing Lima business with weak English path
  E — Fitness or martial arts business
  F — U.S. home service

Outreach draft is written in Peru Spanish for Lima leads,
English for U.S. leads. Lima drafts include English translation below.

Usage: python3 scripts/segment_leads.py
"""

import csv
import pathlib
import sys

BASE = pathlib.Path(__file__).parent.parent
QUAL    = BASE / "data" / "qualified_leads.csv"
SEND    = BASE / "data" / "send_ready_leads.csv"
REPORT  = BASE / "reports" / "send_ready_summary.md"

CONFIRMED_GAPS = {
    "no_website_found_after_search",
    "instagram_or_facebook_only",
    "website_found_but_weak",
    "website_found_not_linked_on_google_profile",
}
UNVERIFIED = {
    "website_not_listed_in_source",
    "needs_website_search",
    "needs_manual_check",
    "",
}


def clean(v) -> str:
    return str(v).strip() if v else ""


def to_int(v) -> int:
    try:
        return int(str(v).replace(",", "").strip())
    except (ValueError, TypeError):
        return 0


def to_float(v) -> float:
    try:
        return float(str(v).replace(",", ".").strip())
    except (ValueError, TypeError):
        return 0.0


def is_lima(lead: dict) -> bool:
    country = clean(lead.get("country", "")).upper()
    return country == "PE" or "PERU" in country


def is_usa(lead: dict) -> bool:
    country = clean(lead.get("country", "")).upper()
    return country in ("US", "USA", "UNITED STATES")


def niche_is(lead: dict, *keywords) -> bool:
    niche = clean(lead.get("niche", "")).lower()
    return any(kw in niche for kw in keywords)


# ---------------------------------------------------------------------------
# Segment assignment
# ---------------------------------------------------------------------------

def assign_segment(lead: dict) -> str:
    ws = clean(lead.get("website_status", "")).lower()
    review_resp = clean(lead.get("review_response_status", "")).lower()
    wa_flow = clean(lead.get("whatsapp_flow_status", "")).lower()
    english_page = clean(lead.get("english_page", "")).lower()
    niche = clean(lead.get("niche", "")).lower()
    lima = is_lima(lead)
    usa = is_usa(lead)

    high_trust = niche_is(lead,
        "dental", "dentist", "dermatol", "aesthetic", "med spa", "medspa",
        "physical therapy", "fisio", "chiropract", "private clinic", "wellness",
        "law", "immigration", "abogad"
    )
    fitness = niche_is(lead, "martial arts", "jiu jitsu", "bjj", "karate", "mma", "kickbox", "gym", "fitness")
    home_service = niche_is(lead, "home service", "plumb", "electric", "roofing", "hvac")
    tourist_facing = niche_is(lead, "hotel", "tour", "restaurant", "cafe", "school")

    # F — U.S. home service
    if usa and home_service:
        return "F"

    # E — Fitness / martial arts (any country)
    if fitness:
        return "E"

    # D — Lima tourist/expat-facing with weak English path
    if lima and tourist_facing and english_page in ("no", "none", "missing", "needs_manual_check", ""):
        return "D"

    # C — Lima business with WhatsApp/contact friction
    if lima and wa_flow in ("no", "none", "missing", "not found", "needs_manual_check"):
        return "C"

    # B — Review-heavy business with weak review follow-up
    reviews = to_int(lead.get("review_count", 0))
    if reviews >= 50 and review_resp in ("none", "poor", "no responses", "not responding"):
        return "B"

    # A — High-trust clinic with unclear website or booking path (default for clinics)
    if high_trust:
        return "A"

    return "A"  # default


# ---------------------------------------------------------------------------
# Outreach draft generation
# ---------------------------------------------------------------------------

PERU_TEMPLATE = (
    "Hola {name}, vi su perfil de Google y me llamó la atención que tienen {reviews_line}. "
    "También noté que {gap_line}. "
    "Puede que se me haya pasado algo, pero hice una mini auditoría de 3 puntos "
    "sobre cómo podrían estar perdiendo consultas por Google o WhatsApp. "
    "¿Se la puedo enviar?"
)

PERU_TEMPLATE_EN = (
    "Hi {name}, I saw your Google profile and noticed you have {reviews_line}. "
    "I also noticed that {gap_line_en}. "
    "I may have missed something, but I made a short 3-point audit "
    "showing where inquiries may be leaking from Google or WhatsApp. "
    "Can I send it over?"
)

USA_TEMPLATE = (
    "Hi {name}, I came across your profile and noticed you have {reviews_line}. "
    "I also noticed that {gap_line_en}. "
    "I may have missed something, but I put together a short audit "
    "showing where you may be missing leads from Google or calls. "
    "Mind if I send it over?"
)


def reviews_line(lead: dict) -> str:
    rating = to_float(lead.get("rating", 0))
    reviews = to_int(lead.get("review_count", 0))
    if reviews >= 100:
        return f"{reviews} reseñas con {rating}★"
    if reviews >= 20:
        return f"{reviews} reseñas"
    return "buenas reseñas"


def reviews_line_en(lead: dict) -> str:
    rating = to_float(lead.get("rating", 0))
    reviews = to_int(lead.get("review_count", 0))
    if reviews >= 100:
        return f"{reviews} reviews at {rating}★"
    if reviews >= 20:
        return f"{reviews} reviews"
    return "good reviews"


def gap_line_es(lead: dict) -> str:
    ws = clean(lead.get("website_status", "")).lower()
    booking = clean(lead.get("booking_link_status", "")).lower()
    wa_flow = clean(lead.get("whatsapp_flow_status", "")).lower()

    if ws == "no_website_found_after_search":
        return "no aparece un sitio web vinculado al perfil de Google"
    if ws == "instagram_or_facebook_only":
        return "el camino para contactarlos o reservar desde el perfil no está muy claro"
    if ws == "website_found_but_weak":
        return "el sitio web o el proceso de reserva puede tener algunos puntos de fricción"
    if ws == "website_found_not_linked_on_google_profile":
        return "el sitio web no aparece vinculado directamente en el perfil de Google"
    if booking in ("no", "none", "missing", "not found"):
        return "no aparece un botón para reservar o contactar fácilmente"
    if wa_flow in ("no", "none", "missing", "not found"):
        return "no aparece un flujo de WhatsApp o contacto activo desde el perfil"
    # Unverified — use careful language
    return "el sitio web o camino para reservar no aparece muy claro desde el perfil"


def gap_line_en(lead: dict) -> str:
    ws = clean(lead.get("website_status", "")).lower()
    booking = clean(lead.get("booking_link_status", "")).lower()
    wa_flow = clean(lead.get("whatsapp_flow_status", "")).lower()

    if ws == "no_website_found_after_search":
        return "no website appears to be linked on your Google profile"
    if ws == "instagram_or_facebook_only":
        return "the path to contact or book from the profile was not very clear"
    if ws == "website_found_but_weak":
        return "the website or booking process may have some friction points"
    if ws == "website_found_not_linked_on_google_profile":
        return "your website does not appear linked directly on your Google profile"
    if booking in ("no", "none", "missing", "not found"):
        return "there is no clear booking or contact button visible from the profile"
    if wa_flow in ("no", "none", "missing", "not found"):
        return "there does not appear to be an active WhatsApp or contact flow from the profile"
    # Unverified — careful
    return "the website or booking path was not very clear from the profile"


def build_outreach_draft(lead: dict) -> tuple[str, str]:
    """Returns (outreach_draft, language)."""
    name = clean(lead.get("casual_business_name", "")) or clean(lead.get("business_name", ""))
    lima = is_lima(lead)
    usa = is_usa(lead)

    if lima:
        es = PERU_TEMPLATE.format(
            name=name,
            reviews_line=reviews_line(lead),
            gap_line=gap_line_es(lead),
        )
        en = PERU_TEMPLATE_EN.format(
            name=name,
            reviews_line=reviews_line_en(lead),
            gap_line_en=gap_line_en(lead),
        )
        draft = f"[ES]\n{es}\n\n[EN]\n{en}"
        return draft, "es-PE"
    elif usa:
        en = USA_TEMPLATE.format(
            name=name,
            reviews_line=reviews_line_en(lead),
            gap_line_en=gap_line_en(lead),
        )
        return en, "en-US"
    else:
        # Default to Spanish for any other market
        es = PERU_TEMPLATE.format(
            name=name,
            reviews_line=reviews_line(lead),
            gap_line=gap_line_es(lead),
        )
        return es, "es"


# ---------------------------------------------------------------------------
# Send-ready filter
# ---------------------------------------------------------------------------

SEND_READY_COLUMNS = [
    "business_name", "casual_business_name", "niche", "industry",
    "city", "neighborhood", "country",
    "website", "verified_website_url", "google_maps_url",
    "phone", "email", "whatsapp", "instagram",
    "rating", "review_count",
    "qualification_status", "website_status",
    "booking_link_status", "contact_form_status",
    "whatsapp_flow_status", "review_response_status",
    "useful_data_point", "verified_gap_summary",
    "recommended_offer", "outreach_angle", "outreach_draft",
    "language", "segment", "priority", "verification_status",
    "next_action", "notes",
]


def is_send_ready(lead: dict) -> bool:
    qual = clean(lead.get("qualification_status", "")).lower()
    vs   = clean(lead.get("verification_status", "")).lower()
    name = clean(lead.get("casual_business_name", ""))
    dp   = clean(lead.get("useful_data_point", ""))
    offer = clean(lead.get("recommended_offer", ""))
    draft = clean(lead.get("outreach_draft", ""))
    phone = clean(lead.get("phone", ""))
    email = clean(lead.get("email", ""))
    wa    = clean(lead.get("whatsapp", ""))

    if qual != "qualified":
        return False
    if vs not in ("verified", "partially_verified"):
        return False
    if not name:
        return False
    if not dp or "needs_manual_check" in dp:
        return False
    if not offer:
        return False
    if not draft:
        return False
    if not phone and not email and not wa:
        return False
    return True


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def build_report(leads: list[dict], qualified: list[dict],
                 rejected_count: int, send_ready: list[dict]) -> str:
    lines = []
    a = lines.append

    a("# Send-Ready Lead Summary")
    a("")
    a("**Generated by:** scripts/segment_leads.py")
    a("")
    a("---")
    a("")
    a("## Pipeline Counts")
    a("")
    a(f"| Stage | Count |")
    a(f"|---|---|")
    a(f"| Raw leads (leads_matrix.csv) | {len(leads) + rejected_count} |")
    a(f"| After qualification | {len(leads)} |")
    a(f"| Rejected | {rejected_count} |")
    a(f"| Send-ready (verified + complete) | {len(send_ready)} |")
    a("")

    # Niche breakdown
    niches: dict[str, int] = {}
    for l in qualified:
        n = l.get("niche", "unknown")
        niches[n] = niches.get(n, 0) + 1
    a("## Qualified Leads by Niche")
    a("")
    a("| Niche | Count |")
    a("|---|---|")
    for n, c in sorted(niches.items(), key=lambda x: -x[1]):
        a(f"| {n} | {c} |")
    a("")

    # Verified pain niches
    pain_niches: dict[str, int] = {}
    for l in qualified:
        ws = clean(l.get("website_status", ""))
        if ws in ("no_website_found_after_search", "instagram_or_facebook_only",
                  "website_found_but_weak", "website_found_not_linked_on_google_profile"):
            n = l.get("niche", "unknown")
            pain_niches[n] = pain_niches.get(n, 0) + 1
    if pain_niches:
        a("## Top Niches by Verified Pain")
        a("")
        a("| Niche | Leads with confirmed gap |")
        a("|---|---|")
        for n, c in sorted(pain_niches.items(), key=lambda x: -x[1]):
            a(f"| {n} | {c} |")
        a("")

    # Top 10 by score
    top = sorted(qualified, key=lambda x: -float(x.get("total_lead_score", 0) or 0))[:10]
    a("## Top 10 Qualified Leads (by score)")
    a("")
    a("| # | Score | Business | Niche | City | Website Status | Verification |")
    a("|---|---|---|---|---|---|---|")
    for i, l in enumerate(top, 1):
        a(f"| {i} | {l.get('total_lead_score',0)} | {l.get('business_name','')} "
          f"| {l.get('niche','')} | {l.get('city','')} "
          f"| {l.get('website_status','')} | {l.get('verification_status','')} |")
    a("")

    # Top 5 Lima
    lima_leads = [l for l in qualified if l.get("country","").upper() in ("PE","PERU")]
    lima_leads.sort(key=lambda x: -float(x.get("total_lead_score", 0) or 0))
    a("## Top 5 Lima Leads")
    a("")
    a("| # | Score | Business | Niche | Neighborhood | Website Status |")
    a("|---|---|---|---|---|---|")
    for i, l in enumerate(lima_leads[:5], 1):
        a(f"| {i} | {l.get('total_lead_score',0)} | {l.get('business_name','')} "
          f"| {l.get('niche','')} | {l.get('neighborhood','')} "
          f"| {l.get('website_status','')} |")
    a("")

    # Top 5 USA
    usa_leads = [l for l in qualified if l.get("country","").upper() in ("US","USA","UNITED STATES")]
    usa_leads.sort(key=lambda x: -float(x.get("total_lead_score", 0) or 0))
    if usa_leads:
        a("## Top 5 U.S. Leads")
        a("")
        a("| # | Score | Business | Niche | City | Website Status |")
        a("|---|---|---|---|---|---|")
        for i, l in enumerate(usa_leads[:5], 1):
            a(f"| {i} | {l.get('total_lead_score',0)} | {l.get('business_name','')} "
              f"| {l.get('niche','')} | {l.get('city','')} "
              f"| {l.get('website_status','')} |")
        a("")

    # Segment breakdown
    segs: dict[str, int] = {}
    for l in qualified:
        s = l.get("segment", "?")
        segs[s] = segs.get(s, 0) + 1
    a("## Outreach Bucket Breakdown")
    a("")
    seg_descriptions = {
        "A": "High-trust clinic — unclear website or booking path",
        "B": "Review-heavy business with weak follow-up",
        "C": "Lima business with WhatsApp/contact friction",
        "D": "Expat/tourist-facing Lima with weak English path",
        "E": "Fitness or martial arts studio",
        "F": "U.S. home service",
    }
    a("| Bucket | Description | Count |")
    a("|---|---|---|")
    for s in sorted(segs):
        a(f"| {s} | {seg_descriptions.get(s, '')} | {segs[s]} |")
    a("")

    # Send-ready
    a("## Send-Ready Leads")
    a("")
    if not send_ready:
        a("**0 send-ready leads.** All leads require manual verification before outreach.")
        a("")
        a("No leads currently have `verification_status = verified` or `partially_verified`.")
        a("This is expected for raw Apify data — no manual verification has been done yet.")
    else:
        a(f"**{len(send_ready)} send-ready leads:**")
        a("")
        for i, l in enumerate(send_ready[:5], 1):
            a(f"### {i}. {l.get('business_name', '')} (score {l.get('total_lead_score', 0)})")
            a(f"- **Niche:** {l.get('niche', '')}")
            a(f"- **City:** {l.get('city', '')}, {l.get('country', '')}")
            a(f"- **Website status:** {l.get('website_status', '')}")
            a(f"- **Data point:** {l.get('useful_data_point', '')}")
            a(f"- **Offer:** {l.get('recommended_offer', '')}")
            a(f"- **Segment:** {l.get('segment', '')}")
            a("")
    a("")

    # Data quality problems
    a("## Data Quality Flags")
    a("")
    unverified_count = sum(1 for l in qualified
                           if l.get("verification_status", "") in
                           ("needs_website_search", "needs_manual_check", ""))
    social_only_count = sum(1 for l in qualified
                            if l.get("website_status", "") == "instagram_or_facebook_only")
    blank_count = sum(1 for l in qualified
                      if l.get("website_status", "") == "website_not_listed_in_source")

    a(f"- **{unverified_count}** leads have unverified website status (need manual search)")
    a(f"- **{social_only_count}** leads show Instagram/social as their only web presence — "
      f"no real booking path confirmed")
    a(f"- **{blank_count}** leads have blank website in source — "
      f"may have a real website that was simply not linked on GBP")
    a(f"- **0** email addresses recovered — Apify does not return email; "
      f"requires website scrape or manual lookup")
    a(f"- **0** owner/manager names — requires manual lookup or LinkedIn search")
    a("")

    # Verification priority
    needs_search = [l for l in qualified
                    if l.get("verification_status", "") == "needs_website_search"]
    if needs_search:
        a("## Leads Needing Website Verification")
        a("")
        a("These leads need a manual Google search before scoring is meaningful.")
        a("Use `data/website_verification_queue.csv` for search queries.")
        a("")
        a("| # | Business | Niche | City | Score |")
        a("|---|---|---|---|---|")
        for i, l in enumerate(needs_search[:15], 1):
            a(f"| {i} | {l.get('business_name','')} | {l.get('niche','')} "
              f"| {l.get('city','')} | {l.get('total_lead_score',0)} |")
        a("")

    # Decision
    a("## Decision")
    a("")
    if len(send_ready) >= 5:
        a("**≥5 send-ready leads available.** Do not scrape more. "
          "Prepare outreach assets and audit briefs for the send-ready list.")
    else:
        a(f"**Fewer than 5 send-ready leads ({len(send_ready)}).** "
          "Complete manual verification of top leads before scraping more.")
        a("")
        a("**Recommended next 5 Apify searches** (do not run without approval):")
        a("")
        a("| Query | Why |")
        a("|---|---|")
        a("| `dermatology clinic Miraflores Lima Peru` | Dermatology had 40% no-website rate in batch 2 |")
        a("| `physical therapy clinic San Isidro Lima Peru` | High volume, unverified gaps |")
        a("| `aesthetic clinic Surco Lima Peru` | Thin results in Surco so far |")
        a("| `med spa Garden City NY` | Only 20 results, all have phones |")
        a("| `chiropractor Garden City NY` | Untested U.S. niche, strong fit for intake offer |")
    a("")

    # Next 5 actions
    a("## Next 5 Actions for Andrew")
    a("")
    a("1. **Manually verify top 5 dental leads** — search each business name + neighborhood on Google.")
    a("   For each: find website (or confirm none), check GBP for booking button, check WhatsApp.")
    a("   Fill in `data/website_verification_queue.csv` with results.")
    a("")
    a("2. **Re-run scorer after verification** — `python3 scripts/score_leads.py` then")
    a("   `python3 scripts/qualify_leads.py` then `python3 scripts/segment_leads.py`.")
    a("   Verified leads with confirmed gaps will become HIGH priority.")
    a("")
    a("3. **Manually check top 3 Instagram-only leads** — open the Instagram profile,")
    a("   confirm there is no link in bio pointing to a real booking site.")
    a("   If confirmed social-only: update `website_status = instagram_or_facebook_only`.")
    a("")
    a("4. **Find owner/manager names for top 5 leads** — check Instagram, Google profile,")
    a("   or the business name on LinkedIn. Add to `custom_audit_note` as `owner: [name]`.")
    a("   This boosts contactability score and personalizes outreach.")
    a("")
    a("5. **Review segment A outreach draft** — check that the Spanish draft for the top")
    a("   dental lead sounds natural before first send. Adjust neighborhood reference if needed.")
    a("")

    return "\n".join(lines)


def main():
    if not QUAL.exists():
        sys.exit(f"ERROR: {QUAL} not found. Run qualify_leads.py first.")

    # Load all qualified leads (including low_priority)
    with open(QUAL, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        leads = list(reader)

    # Ensure segment/outreach_draft/language columns exist
    for col in ("segment", "outreach_draft", "language"):
        if col not in fieldnames:
            fieldnames = list(fieldnames) + [col]

    qualified = [l for l in leads if l.get("qualification_status") == "qualified"]
    rejected_count = len(leads) - len(qualified)  # low_priority treated separately

    print(f"Loaded {len(leads)} qualified/low-priority leads ({len(qualified)} qualified)")

    for lead in leads:
        if not lead.get("segment"):
            lead["segment"] = assign_segment(lead)
        if not lead.get("outreach_draft"):
            draft, lang = build_outreach_draft(lead)
            lead["outreach_draft"] = draft
            lead["language"] = lang

    # Write back enriched qualified_leads.csv
    with open(QUAL, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(leads)

    print(f"Updated {QUAL} with segments and outreach drafts")

    # Build send-ready list
    send_ready = [l for l in leads if is_send_ready(l)]
    send_ready.sort(key=lambda x: -float(x.get("total_lead_score", 0) or 0))

    with open(SEND, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SEND_READY_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(send_ready)

    print(f"Wrote {len(send_ready)} send-ready leads to {SEND}")

    # Build report
    report = build_report(leads, qualified, rejected_count, send_ready)
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(f"Report written to {REPORT}")

    # Summary
    print(f"\n{'='*50}")
    print(f"SEGMENT SUMMARY")
    print(f"{'='*50}")
    segs: dict[str, int] = {}
    for l in leads:
        s = l.get("segment", "?")
        segs[s] = segs.get(s, 0) + 1
    for s in sorted(segs):
        print(f"  Bucket {s}: {segs[s]} leads")
    print(f"\nSend-ready: {len(send_ready)}")
    if len(send_ready) < 5:
        print("  → Manual verification needed before outreach")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
