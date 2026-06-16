"""
qualify_leads.py — Split scored leads into qualified and rejected.

Reads:  data/leads_matrix.csv
Writes: data/qualified_leads.csv
        data/rejected_leads.csv

Usage: python3 scripts/qualify_leads.py
"""

import csv
import pathlib
import sys

BASE = pathlib.Path(__file__).parent.parent
MATRIX  = BASE / "data" / "leads_matrix.csv"
QUAL    = BASE / "data" / "qualified_leads.csv"
REJECT  = BASE / "data" / "rejected_leads.csv"

# ---------------------------------------------------------------------------
# Niche targeting
# ---------------------------------------------------------------------------

TARGET_NICHES = {
    # Healthcare
    "dental clinic", "dental clinics", "dentist", "dentist office",
    "dermatology", "dermatology clinic", "dermatologist", "dermatología",
    "physical therapy", "physical therapy clinic", "physiotherapy",
    "fisioterapia", "rehabilitation", "rehab clinic",
    "chiropractor", "chiropractic clinic",
    "private clinic", "clinica privada", "wellness clinic",
    "aesthetic clinic", "clinica estetica",
    # Beauty / Med
    "med spa", "medspa", "med spas",
    # Fitness
    "martial arts", "martial arts gym", "karate", "jiu jitsu",
    "jiu-jitsu", "bjj", "mma", "kickboxing", "taekwondo", "fitness studio",
    # Services
    "immigration services", "immigration lawyer", "immigration attorney",
    "relocation services",
    "spanish school", "language school", "english school",
    "law firm", "law office", "attorney", "abogado",
    "accounting firm", "accountant", "cpa", "contador", "tax firm",
    # U.S. home services
    "home services", "plumber", "plumbing", "electrician",
    "roofing", "roofing contractor", "hvac", "hvac contractor",
}

# Niche keywords for partial match
TARGET_KEYWORDS = [
    "dental", "dentist", "dermatol", "aesthetic", "med spa", "medspa",
    "physical therapy", "fisio", "rehab", "chiropract",
    "martial arts", "jiu jitsu", "jiu-jitsu", "bjj", "karate",
    "mma", "kickbox",
    "immigration", "relocation", "law firm", "abogad", "attorney",
    "account", "contad", "cpa", "tax",
    "spanish school", "language school",
    "home service", "plumb", "electric", "roofing", "hvac",
]

# Niche → industry bucket
INDUSTRY_MAP = [
    (["dental", "dentist", "dermatol", "physical therapy", "fisio",
      "rehab", "chiropract", "private clinic", "wellness", "clinica"],   "healthcare"),
    (["aesthetic", "med spa", "medspa", "skin care", "beauty"],           "beauty & wellness"),
    (["martial arts", "jiu jitsu", "bjj", "karate", "mma", "kickbox",
      "fitness", "gym"],                                                  "fitness"),
    (["immigration", "relocation", "law firm", "abogad", "attorney"],     "legal & immigration"),
    (["account", "contad", "cpa", "tax"],                                 "professional services"),
    (["spanish school", "language school", "english school"],             "education"),
    (["home service", "plumb", "electric", "roofing", "hvac"],           "home services"),
]

# Chain / franchise indicators
CHAIN_SIGNALS = [
    "corporativo", "corporate", "cadena", "nationwide", "national",
    "headquarters", "hq", "group", "holdings", "franchise",
]

# Closed indicators
CLOSED_SIGNALS = ["permanently closed", "cerrado permanentemente", "closed permanently"]

MIN_RATING = 4.0
MIN_REVIEWS_DEFAULT = 10   # lowered — some premium niches are new
MIN_REVIEWS_PREMIUM = 5    # dental/aesthetic can be considered with fewer if premium signals

PREMIUM_NICHES = {"dental", "dentist", "aesthetic", "med spa", "medspa", "dermatol"}


def clean(v) -> str:
    return str(v).strip() if v else ""


def to_float(v) -> float:
    try:
        return float(str(v).replace(",", ".").strip())
    except (ValueError, TypeError):
        return 0.0


def to_int(v) -> int:
    try:
        return int(str(v).replace(",", "").strip())
    except (ValueError, TypeError):
        return 0


def get_industry(niche: str) -> str:
    niche_lc = niche.lower()
    for keywords, industry in INDUSTRY_MAP:
        if any(k in niche_lc for k in keywords):
            return industry
    return "other"


def niche_matches_target(niche: str) -> bool:
    niche_lc = niche.lower()
    if niche_lc in TARGET_NICHES:
        return True
    return any(kw in niche_lc for kw in TARGET_KEYWORDS)


def is_likely_chain(lead: dict) -> bool:
    name = clean(lead.get("business_name", "")).lower()
    notes = clean(lead.get("notes", "")).lower()
    return any(s in name or s in notes for s in CHAIN_SIGNALS)


def is_closed(lead: dict) -> bool:
    name = clean(lead.get("business_name", "")).lower()
    notes = clean(lead.get("notes", "")).lower()
    return any(s in name or s in notes for s in CLOSED_SIGNALS)


def has_contact_path(lead: dict) -> bool:
    return bool(
        clean(lead.get("phone", ""))
        or clean(lead.get("email", ""))
        or clean(lead.get("whatsapp", ""))
        or clean(lead.get("instagram", ""))
        or clean(lead.get("google_maps_url", ""))
    )


def already_fully_served(lead: dict) -> bool:
    """Reject if the lead has a strong site, booking, reviews, and no gap to solve."""
    ws = clean(lead.get("website_status", "")).lower()
    booking = clean(lead.get("booking_link", "")).lower()
    contact = clean(lead.get("contact_form", "")).lower()
    whatsapp_flow = clean(lead.get("whatsapp_flow", "")).lower()
    review_resp = clean(lead.get("review_response_quality", "")).lower()

    strong_site = ws == "website_found_linked"
    has_booking = booking not in ("", "no", "none", "missing", "not found", "needs_manual_check")
    has_contact = contact not in ("", "no", "none", "missing", "not found", "needs_manual_check")
    has_wa = whatsapp_flow not in ("", "no", "none", "missing", "not found", "needs_manual_check")
    strong_reviews = review_resp in ("good", "excellent", "responding", "active")

    return strong_site and has_booking and has_contact and has_wa and strong_reviews


def qualify(lead: dict) -> tuple[str, str]:
    """
    Returns (status, rejection_reason).
    status: "qualified" | "rejected" | "low_priority"
    """
    niche = clean(lead.get("niche", ""))
    rating = to_float(lead.get("rating", 0))
    reviews = to_int(lead.get("review_count", 0))
    name_lc = clean(lead.get("business_name", "")).lower()
    niche_lc = niche.lower()

    # Hard rejects
    if is_closed(lead):
        return "rejected", "appears closed"
    if is_likely_chain(lead):
        return "rejected", "likely chain or franchise"
    if rating > 0 and rating < MIN_RATING:
        return "rejected", f"rating {rating} below minimum {MIN_RATING}"
    if not has_contact_path(lead):
        return "rejected", "no usable contact path"

    # Niche check
    if not niche_matches_target(niche):
        return "rejected", f"niche '{niche}' not in target list"

    # Minimum reviews — relax for premium niches
    is_premium = any(kw in niche_lc for kw in PREMIUM_NICHES)
    min_rev = MIN_REVIEWS_PREMIUM if is_premium else MIN_REVIEWS_DEFAULT
    if reviews > 0 and reviews < min_rev:
        return "low_priority", f"only {reviews} reviews (min {min_rev} for {niche})"

    # Already fully served — deprioritize, don't reject (gap may emerge on verification)
    if already_fully_served(lead):
        return "low_priority", "appears to have strong digital presence — verify for specific gap"

    return "qualified", ""


def build_output_row(lead: dict, qual_status: str, rejection_reason: str) -> dict:
    niche = clean(lead.get("niche", ""))
    return {
        **lead,
        "industry": get_industry(niche),
        "qualification_status": qual_status,
        "rejection_reason": rejection_reason,
        # Fields that will be filled later
        "casual_business_name": "",
        "useful_data_point": "",
        "verified_gap_summary": "",
        "segment": "",
        "language": "",
        "booking_link_status": clean(lead.get("booking_link", "")) or "needs_manual_check",
        "contact_form_status": clean(lead.get("contact_form", "")) or "needs_manual_check",
        "whatsapp_flow_status": clean(lead.get("whatsapp_flow", "")) or "needs_manual_check",
        "review_response_status": clean(lead.get("review_response_quality", "")) or "needs_manual_check",
    }


QUAL_COLUMNS = [
    "business_name", "casual_business_name", "niche", "industry",
    "city", "neighborhood", "country",
    "website", "verified_website_url", "google_maps_url",
    "phone", "email", "whatsapp", "instagram",
    "rating", "review_count",
    "qualification_status", "rejection_reason",
    "website_status", "booking_link_status", "contact_form_status",
    "whatsapp_flow_status", "review_response_status",
    "useful_data_point", "verified_gap_summary",
    "recommended_offer", "outreach_angle", "outreach_draft",
    "language", "segment", "priority", "verification_status", "verified_gap_count",
    "total_lead_score", "next_action", "notes", "disqualifier",
    "address",
]

REJECT_COLUMNS = [
    "business_name", "niche", "industry", "city", "country",
    "rating", "review_count", "phone", "website_status",
    "qualification_status", "rejection_reason",
    "total_lead_score", "notes",
]


def main():
    if not MATRIX.exists():
        sys.exit(f"ERROR: {MATRIX} not found. Run score_leads.py first.")

    with open(MATRIX, newline="", encoding="utf-8") as f:
        leads = list(csv.DictReader(f))

    print(f"Loaded {len(leads)} leads from {MATRIX}")

    qualified, rejected, low = [], [], []

    for lead in leads:
        status, reason = qualify(lead)
        row = build_output_row(lead, status, reason)
        if status == "qualified":
            qualified.append(row)
        elif status == "low_priority":
            low.append(row)
        else:
            rejected.append(row)

    # Low priority goes into qualified file but flagged
    all_qualified = qualified + low
    all_qualified.sort(key=lambda r: -float(r.get("total_lead_score", 0) or 0))

    with open(QUAL, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=QUAL_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_qualified)

    with open(REJECT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REJECT_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rejected)

    print(f"\nQualification results:")
    print(f"  Qualified:    {len(qualified)}")
    print(f"  Low priority: {len(low)}")
    print(f"  Rejected:     {len(rejected)}")
    print(f"\nFiles written:")
    print(f"  {QUAL}  ({len(all_qualified)} rows)")
    print(f"  {REJECT}  ({len(rejected)} rows)")

    # Breakdown by rejection reason
    if rejected:
        reasons: dict[str, int] = {}
        for r in rejected:
            rr = r.get("rejection_reason", "unknown")
            reasons[rr] = reasons.get(rr, 0) + 1
        print(f"\nRejection reasons:")
        for reason, count in sorted(reasons.items(), key=lambda x: -x[1]):
            print(f"  {count:>3}  {reason}")

    # Niche breakdown of qualified
    niches: dict[str, int] = {}
    for r in all_qualified:
        n = r.get("niche", "unknown")
        niches[n] = niches.get(n, 0) + 1
    print(f"\nQualified by niche:")
    for niche, count in sorted(niches.items(), key=lambda x: -x[1]):
        print(f"  {count:>3}  {niche}")


if __name__ == "__main__":
    main()
