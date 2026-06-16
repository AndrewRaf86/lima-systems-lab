"""
clean_company_names.py — Create casual_business_name for outreach.

Reads and updates: data/qualified_leads.csv

Rules:
- Remove legal suffixes (LLC, SAC, S.A., Ltd, Corp, etc.)
- Remove generic category suffixes only when shorter name still makes sense
- Preserve accents
- Never shorten to the point of ambiguity

Usage: python3 scripts/clean_company_names.py
"""

import csv
import pathlib
import re
import sys

BASE  = pathlib.Path(__file__).parent.parent
QUAL  = BASE / "data" / "qualified_leads.csv"

# ---------------------------------------------------------------------------
# Suffix stripping rules
# ---------------------------------------------------------------------------

# Legal suffixes — always remove (with optional punctuation around them)
LEGAL_SUFFIXES = [
    r"\bS\.A\.C\.?\b", r"\bSAC\b",
    r"\bS\.A\.?\b",    r"\bSA\b",
    r"\bS\.R\.L\.?\b", r"\bSRL\b",
    r"\bE\.I\.R\.L\.?\b",
    r"\bLLC\b",        r"\bL\.L\.C\.?\b",
    r"\bInc\.?\b",     r"\bIncorporated\b",
    r"\bCorp\.?\b",    r"\bCorporation\b",
    r"\bLtd\.?\b",     r"\bLimited\b",
    r"\bPLC\b",
    r"\bGmbH\b",
    r"\b& Asociados\b", r"\by Asociados\b",
    r"\b& Cia\b",       r"\by Cia\.?\b",
    r"\b& Co\.?\b",
]

# Generic category words — remove only if the name still makes sense without them
# Checked in order; only the last matching suffix that leaves a non-empty name is removed
GENERIC_SUFFIXES = [
    # Spanish
    r"\bClínica Dental\b",
    r"\bClínica Odontológica\b",
    r"\bConsultorio Dental\b",
    r"\bOdontología Especializada\b",
    r"\bOdontología\b",
    r"\bClínica Dermatológica\b",
    r"\bClínica Estética\b",
    r"\bCentro Médico\b",
    r"\bCentro de Salud\b",
    r"\bCentro Odontológico\b",
    r"\bCentro de Fisioterapia\b",
    r"\bCentro de Terapia Física\b",
    r"\bClínica de Fisioterapia\b",
    r"\bFisioterapia y Rehabilitación\b",
    r"\bCentro Estético\b",
    r"\bSalón de Belleza\b",
    r"\bGimnasio\b",
    r"\bEstudio de Pilates\b",
    r"\bAcademia de\b",
    r"\bAcademia\b(?! Jiu Jitsu| Judo| Karate| MMA| BJJ)",
    r"\bEscuela de\b",
    r"\bBuffet de Abogados\b",
    r"\bEstudio de Abogados\b",
    r"\bDespacho de Abogados\b",
    r"\bContadores Públicos\b",
    r"\bContadores\b",
    # English
    r"\bDental Clinic\b",
    r"\bDental Center\b",
    r"\bDental Office\b",
    r"\bDental Studio\b",
    r"\bDermatology Clinic\b",
    r"\bDermatology Center\b",
    r"\bAesthetic Clinic\b",
    r"\bAesthetic Center\b",
    r"\bMed Spa\b",
    r"\bMedSpa\b",
    r"\bSpa\b",
    r"\bPhysical Therapy Clinic\b",
    r"\bPhysical Therapy Center\b",
    r"\bRehabilitation Center\b",
    r"\bChiropractic Clinic\b",
    r"\bChiropractic Center\b",
    r"\bWellness Center\b",
    r"\bMedical Center\b",
    r"\bMedical Clinic\b",
    r"\bHealth Center\b",
    r"\bFitness Studio\b",
    r"\bMartial Arts Academy\b",
    r"\bMartial Arts\b",
    r"\bJiu Jitsu Academy\b",
    r"\bKarate Academy\b",
    r"\bMMA Academy\b",
    r"\bLaw Firm\b",
    r"\bLaw Office\b",
    r"\bLaw Group\b",
    r"\bAccounting Firm\b",
    r"\bAccounting Group\b",
    r"\bAccounting Services\b",
    r"\bLanguage School\b",
    r"\bSpanish School\b",
    r"\bMarketing Solutions\b",
    r"\bMarketing Agency\b",
    r"\bDigital Agency\b",
    r"\bSolutions\b",
    r"\bServices\b",
    r"\bGroup\b",
    r"\bAgency\b",
]

# Words to normalize casing (preserve all-caps brand names)
KNOWN_ALLCAPS_BRANDS = {"skincenter", "bodyhelp", "kami"}


def strip_legal(name: str) -> str:
    for pattern in LEGAL_SUFFIXES:
        name = re.sub(pattern, "", name, flags=re.IGNORECASE).strip()
    # Clean trailing punctuation left behind
    name = re.sub(r"[-–,. ]+$", "", name).strip()
    return name


def strip_generic(name: str) -> str:
    """Remove category suffixes, but only if leftover is ≥2 meaningful words or ≥10 chars."""
    for pattern in GENERIC_SUFFIXES:
        candidate = re.sub(pattern, "", name, flags=re.IGNORECASE).strip()
        candidate = re.sub(r"[-–,. ]+$", "", candidate).strip()
        # Only accept if the shorter name is still meaningful
        if candidate and len(candidate) >= 4 and candidate != name:
            name = candidate
    return name


def clean_name(raw_name: str) -> str:
    if not raw_name:
        return ""

    name = raw_name.strip()

    # Step 1: remove legal suffixes
    name = strip_legal(name)

    # Step 2: remove generic category suffixes
    candidate = strip_generic(name)

    # Reject if we stripped too much (less than 3 chars or empty)
    if len(candidate) < 3:
        candidate = name

    # Step 3: title-case only if fully uppercase and not a known brand
    if candidate == candidate.upper() and candidate.lower() not in KNOWN_ALLCAPS_BRANDS:
        candidate = candidate.title()

    return candidate


def main():
    if not QUAL.exists():
        sys.exit(f"ERROR: {QUAL} not found. Run qualify_leads.py first.")

    with open(QUAL, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        leads = list(reader)

    if "casual_business_name" not in fieldnames:
        fieldnames = list(fieldnames) + ["casual_business_name"]

    updated = 0
    for lead in leads:
        raw = lead.get("business_name", "")
        casual = clean_name(raw)
        if casual and casual != raw:
            lead["casual_business_name"] = casual
            updated += 1
        elif not lead.get("casual_business_name"):
            lead["casual_business_name"] = raw  # fallback: use original

    with open(QUAL, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(leads)

    print(f"clean_company_names: updated {updated}/{len(leads)} names in {QUAL}")

    # Show sample transformations
    samples = [(l["business_name"], l["casual_business_name"])
               for l in leads if l["business_name"] != l["casual_business_name"]][:15]
    if samples:
        print(f"\nSample transformations:")
        for orig, casual in samples:
            print(f"  {orig!r:50s} → {casual!r}")


if __name__ == "__main__":
    main()
