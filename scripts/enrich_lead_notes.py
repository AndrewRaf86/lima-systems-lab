"""
enrich_lead_notes.py — Add useful_data_point and verified_gap_summary per lead.

Reads and updates: data/qualified_leads.csv

Rules:
- Extract the single most useful, honest data point per lead
- If not verified, label it possible_gap_needs_manual_check
- Do not make claims beyond what the data supports

Usage: python3 scripts/enrich_lead_notes.py
"""

import csv
import pathlib
import sys

BASE = pathlib.Path(__file__).parent.parent
QUAL = BASE / "data" / "qualified_leads.csv"

LIMA_COUNTRIES = {"PE", "Peru", "peru"}


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


# ---------------------------------------------------------------------------
# Useful data point logic
# ---------------------------------------------------------------------------

CONFIRMED_NO_WEBSITE = "no_website_found_after_search"
CONFIRMED_SOCIAL_ONLY = "instagram_or_facebook_only"
CONFIRMED_WEAK = "website_found_but_weak"
CONFIRMED_NOT_LINKED = "website_found_not_linked_on_google_profile"

UNVERIFIED = {
    "website_not_listed_in_source",
    "needs_website_search",
    "needs_manual_check",
    "",
}


def get_useful_data_point(lead: dict) -> str:
    name = clean(lead.get("casual_business_name", "")) or clean(lead.get("business_name", ""))
    ws = clean(lead.get("website_status", "")).lower()
    booking = clean(lead.get("booking_link_status", "")).lower()
    contact = clean(lead.get("contact_form_status", "")).lower()
    wa_flow = clean(lead.get("whatsapp_flow_status", "")).lower()
    review_resp = clean(lead.get("review_response_status", "")).lower()
    mobile = clean(lead.get("mobile_quality", "")).lower()
    rating = to_float(lead.get("rating", 0))
    reviews = to_int(lead.get("review_count", 0))
    niche = clean(lead.get("niche", "")).lower()
    lima = is_lima(lead)

    # Confirmed gaps — most valuable
    if ws == CONFIRMED_NO_WEBSITE:
        return f"{reviews} reviews at {rating}★ but no website confirmed — new clients searching online have nowhere to go"
    if ws == CONFIRMED_SOCIAL_ONLY:
        if reviews >= 50:
            return f"{reviews} reviews at {rating}★ but only Instagram/social linked — no booking path, no SEO, no trust page"
        return f"Instagram-only presence — no booking path or professional web presence"
    if ws == CONFIRMED_WEAK:
        return f"Website exists but appears weak — possible poor mobile experience or missing booking flow"
    if ws == CONFIRMED_NOT_LINKED:
        return f"Has website but it is not linked on Google profile — search traffic likely lost"

    # Booking confirmed absent
    if booking in ("no", "none", "missing", "not found"):
        if reviews >= 30:
            return f"{reviews} reviews at {rating}★ but no visible booking or contact path — possible inquiry leakage"
        return "No visible booking or appointment path found"

    # WhatsApp absent (Lima)
    if lima and wa_flow in ("no", "none", "missing", "not found"):
        return "No WhatsApp flow — likely missing after-hours inquiries in Lima market"

    # Review response gap
    if review_resp in ("none", "poor", "no responses", "not responding") and reviews >= 50:
        return f"{reviews} reviews but no visible response from owner — trust signal gap"

    # High reviews but digital presence unclear
    if reviews >= 100 and ws in UNVERIFIED:
        return f"possible_gap_needs_manual_check: {reviews} reviews at {rating}★ — website/booking status unknown from source"

    if reviews >= 30 and ws in UNVERIFIED:
        return f"possible_gap_needs_manual_check: {reviews} reviews at {rating}★ — website and booking path need verification"

    # Niche-specific context
    if "physical therapy" in niche or "fisio" in niche:
        return "possible_gap_needs_manual_check: physical therapy clinics often lack digital intake and appointment reminders"
    if "martial arts" in niche or "jiu jitsu" in niche or "karate" in niche:
        return "possible_gap_needs_manual_check: fitness/martial arts studios often lack trial-class funnel and WhatsApp follow-up"
    if "account" in niche or "contad" in niche:
        return "possible_gap_needs_manual_check: accounting firms often lack digital intake flow and appointment booking"
    if "law" in niche or "abogad" in niche or "immigration" in niche:
        return "possible_gap_needs_manual_check: law/immigration firms often lack online intake form and missed-call follow-up"

    return "possible_gap_needs_manual_check: needs manual profile check to identify specific gap"


def get_gap_summary(lead: dict) -> str:
    ws = clean(lead.get("website_status", "")).lower()
    booking = clean(lead.get("booking_link_status", "")).lower()
    contact = clean(lead.get("contact_form_status", "")).lower()
    wa_flow = clean(lead.get("whatsapp_flow_status", "")).lower()
    review_resp = clean(lead.get("review_response_status", "")).lower()
    mobile = clean(lead.get("mobile_quality", "")).lower()

    gaps = []

    # Website
    if ws == CONFIRMED_NO_WEBSITE:
        gaps.append("no website (confirmed)")
    elif ws == CONFIRMED_SOCIAL_ONLY:
        gaps.append("social-only presence (confirmed)")
    elif ws == CONFIRMED_WEAK:
        gaps.append("weak website (confirmed)")
    elif ws == CONFIRMED_NOT_LINKED:
        gaps.append("website not linked on GBP (confirmed)")
    elif ws in UNVERIFIED:
        gaps.append("website status unknown (needs search)")

    # Booking
    if booking in ("no", "none", "missing", "not found"):
        gaps.append("no booking link (confirmed)")
    elif booking in ("needs_manual_check", ""):
        gaps.append("booking status unknown")

    # Contact
    if contact in ("no", "none", "missing", "not found"):
        gaps.append("no contact form (confirmed)")
    elif contact in ("needs_manual_check", ""):
        gaps.append("contact form unknown")

    # WhatsApp (Lima)
    if is_lima(lead):
        if wa_flow in ("no", "none", "missing", "not found"):
            gaps.append("no WhatsApp flow (confirmed)")
        elif wa_flow in ("needs_manual_check", ""):
            gaps.append("WhatsApp flow unknown")

    # Review responses
    if review_resp in ("none", "poor", "no responses", "not responding"):
        gaps.append("no review responses (confirmed)")
    elif review_resp in ("needs_manual_check", ""):
        gaps.append("review response quality unknown")

    # Mobile
    if "poor" in mobile or "bad" in mobile:
        gaps.append("poor mobile experience (confirmed)")

    if not gaps:
        return "no gaps confirmed yet — needs manual check"

    return "; ".join(gaps)


def main():
    if not QUAL.exists():
        sys.exit(f"ERROR: {QUAL} not found. Run qualify_leads.py first.")

    with open(QUAL, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        leads = list(reader)

    for lead in leads:
        if not lead.get("useful_data_point"):
            lead["useful_data_point"] = get_useful_data_point(lead)
        if not lead.get("verified_gap_summary"):
            lead["verified_gap_summary"] = get_gap_summary(lead)

    with open(QUAL, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(leads)

    print(f"enrich_lead_notes: enriched {len(leads)} leads in {QUAL}")

    # Sample output
    samples = [(l.get("business_name", ""), l.get("useful_data_point", "")) for l in leads[:8]]
    print(f"\nSample data points:")
    for name, dp in samples:
        print(f"  {name[:40]:<40}  {dp[:80]}")


if __name__ == "__main__":
    main()
