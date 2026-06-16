"""
verify_websites.py — Generate a verification queue for top leads.

Reads:  data/qualified_leads.csv (preferred) or data/leads_matrix.csv
Writes: data/website_verification_queue.csv

For each lead, creates search queries to verify website, booking, and contact path.
Fill in the verified_* columns manually, then re-run the full pipeline.

Usage: python3 scripts/verify_websites.py
"""

import csv
import pathlib
import sys

BASE  = pathlib.Path(__file__).parent.parent
QUAL  = BASE / "data" / "qualified_leads.csv"
MAT   = BASE / "data" / "leads_matrix.csv"
QUEUE = BASE / "data" / "website_verification_queue.csv"

QUEUE_LIMIT = 30

NEEDS_SEARCH = {
    "website_not_listed_in_source",
    "needs_website_search",
    "needs_manual_check",
    "",
}
SOCIAL_ONLY = "instagram_or_facebook_only"


def clean(v) -> str:
    return str(v).strip() if v else ""


def to_float(v) -> float:
    try:
        return float(str(v).replace(",", ".").strip())
    except (ValueError, TypeError):
        return 0.0


def is_lima(lead: dict) -> bool:
    country = clean(lead.get("country", "")).upper()
    return country == "PE" or "PERU" in country


def build_lima_queries(lead: dict) -> list[str]:
    name = clean(lead.get("business_name", ""))
    neighborhood = clean(lead.get("neighborhood", ""))
    city = clean(lead.get("city", "")) or "Lima"

    q = [
        f'"{name}" {neighborhood} Lima sitio web',
        f'"{name}" {city} website',
        f'"{name}" Instagram',
        f'"{name}" WhatsApp',
        f'"{name}" Google Maps',
        f'"{name}" reseñas',
    ]
    return q


def build_usa_queries(lead: dict) -> list[str]:
    name = clean(lead.get("business_name", ""))
    city = clean(lead.get("city", ""))
    state = clean(lead.get("neighborhood", "")) or ""  # state sometimes in neighborhood field

    location = f"{city} {state}".strip() if state else city
    q = [
        f'"{name}" {location} website',
        f'"{name}" booking',
        f'"{name}" reviews',
        "", "", "",  # pad to 6 for consistent columns
    ]
    return q


QUEUE_COLUMNS = [
    "rank",
    "total_lead_score",
    "business_name",
    "niche",
    "neighborhood",
    "city",
    "country",
    "phone",
    "current_website_status",
    "website_in_source",
    "instagram_in_source",
    "search_query_1",
    "search_query_2",
    "search_query_3",
    "search_query_4",
    "search_query_5",
    "search_query_6",
    "verified_website_url",
    "verified_website_status",
    "booking_confirmed",
    "whatsapp_confirmed",
    "verification_notes",
    "verified_by",
    "verified_date",
]


def build_queue_row(rank: int, lead: dict) -> dict:
    lima = is_lima(lead)
    if lima:
        queries = build_lima_queries(lead)
    else:
        queries = build_usa_queries(lead)

    while len(queries) < 6:
        queries.append("")

    return {
        "rank": rank,
        "total_lead_score": lead.get("total_lead_score", ""),
        "business_name": lead.get("business_name", ""),
        "niche": lead.get("niche", ""),
        "neighborhood": lead.get("neighborhood", ""),
        "city": lead.get("city", ""),
        "country": lead.get("country", ""),
        "phone": lead.get("phone", ""),
        "current_website_status": lead.get("website_status", ""),
        "website_in_source": lead.get("website", ""),
        "instagram_in_source": lead.get("instagram", ""),
        "search_query_1": queries[0],
        "search_query_2": queries[1],
        "search_query_3": queries[2],
        "search_query_4": queries[3],
        "search_query_5": queries[4],
        "search_query_6": queries[5],
        "verified_website_url": lead.get("verified_website_url", ""),
        "verified_website_status": "",
        "booking_confirmed": "",
        "whatsapp_confirmed": "",
        "verification_notes": "",
        "verified_by": "",
        "verified_date": "",
    }


def main():
    # Prefer qualified_leads.csv, fall back to leads_matrix.csv
    source = QUAL if QUAL.exists() else MAT
    if not source.exists():
        sys.exit(f"ERROR: neither {QUAL} nor {MAT} found. Run score_leads.py first.")

    with open(source, newline="", encoding="utf-8") as f:
        leads = list(csv.DictReader(f))

    print(f"Loaded {len(leads)} leads from {source.name}")

    # Select leads needing verification (unverified or social-only to confirm)
    candidates = [
        l for l in leads
        if clean(l.get("website_status", "")) in NEEDS_SEARCH
        or clean(l.get("website_status", "")) == SOCIAL_ONLY
    ]

    # Sort by score descending
    candidates.sort(
        key=lambda r: float(r.get("total_lead_score", 0) or 0),
        reverse=True
    )
    candidates = candidates[:QUEUE_LIMIT]

    rows = [build_queue_row(i + 1, lead) for i, lead in enumerate(candidates)]

    with open(QUEUE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=QUEUE_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nVerification queue: {QUEUE}")
    print(f"Leads queued: {len(rows)}")
    print(f"\nTop 10:")
    for row in rows[:10]:
        print(
            f"  {row['rank']:>2}. [{row['total_lead_score']:>4}] "
            f"{row['business_name'][:38]:<38} | {row['current_website_status']}"
        )

    print(f"\nVerification checklist per lead:")
    print(f"  1. Run search_query_1 — look for official site or booking page")
    print(f"  2. Run search_query_2 — alternative search with city")
    print(f"  3. Open Google Maps profile directly — check website button")
    print(f"  4. Check Instagram / Facebook — any real site in bio?")
    print(f"  5. Try likely domain (businessname.com / businessname.pe)")
    print(f"  6. Set verified_website_status to one of:")
    print(f"       no_website_found_after_search")
    print(f"       instagram_or_facebook_only")
    print(f"       website_found_linked")
    print(f"       website_found_not_linked_on_google_profile")
    print(f"       website_found_but_weak")
    print(f"  7. Fill in booking_confirmed and whatsapp_confirmed (yes/no)")
    print(f"  8. Update data/leads_matrix.csv and re-run score_leads.py")


if __name__ == "__main__":
    main()
