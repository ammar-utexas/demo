#!/usr/bin/env python3
"""
Payer Rule Extractor — Parse downloaded PDFs into structured PA rule objects.

Reads PDF policy documents from the data/ directory and extracts structured
prior authorization rules for anti-VEGF intravitreal injections.

Usage:
    python extract_rules.py                    # Extract from all payers
    python extract_rules.py --payer uhc aetna  # Extract from specific payers
    python extract_rules.py --summary          # Show summary of extracted rules
"""

import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

import pdfplumber
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("rule_extractor")

# ---------------------------------------------------------------------------
# Drug and diagnosis reference data
# ---------------------------------------------------------------------------

DRUG_CODES = {
    "J0178": {"name": "aflibercept", "brand": "Eylea"},
    "J0179": {"name": "aflibercept 8mg", "brand": "Eylea HD"},
    "J9035": {"name": "bevacizumab", "brand": "Avastin"},
    "J2778": {"name": "ranibizumab", "brand": "Lucentis"},
    "J3490": {"name": "faricimab", "brand": "Vabysmo"},
    "J1442": {"name": "pegcetacoplan", "brand": "Syfovre"},
}

DIAGNOSIS_GROUPS = {
    "wet_amd": {
        "name": "Wet Age-Related Macular Degeneration",
        "icd10_patterns": [r"H35\.31", r"H35\.32"],
    },
    "dme": {
        "name": "Diabetic Macular Edema",
        "icd10_patterns": [r"H35\.81", r"E08\.3", r"E09\.3", r"E10\.3", r"E11\.3", r"E13\.3"],
    },
    "rvo": {
        "name": "Retinal Vein Occlusion",
        "icd10_patterns": [r"H34\.1", r"H34\.8", r"H34\.9"],
    },
    "geographic_atrophy": {
        "name": "Geographic Atrophy",
        "icd10_patterns": [r"H35\.31"],
    },
}

# ---------------------------------------------------------------------------
# Text extraction patterns
# ---------------------------------------------------------------------------

# Patterns to detect PA requirements in policy text
PA_REQUIRED_PATTERNS = [
    r"prior\s+auth(?:orization)?\s+(?:is\s+)?required",
    r"precertification\s+(?:is\s+)?required",
    r"requires?\s+prior\s+(?:auth|approval|certification)",
    r"must\s+(?:obtain|have)\s+(?:prior\s+)?auth(?:orization)?",
    r"PA\s+required",
]

STEP_THERAPY_PATTERNS = [
    r"step\s+therapy",
    r"must\s+(?:try|fail|use)\s+.*(?:first|before|prior)",
    r"(?:trial|failure)\s+of\s+.*(?:bevacizumab|avastin)",
    r"avastin[- ]first",
    r"preferred\s+(?:drug|agent|medication)",
    r"non[- ]preferred.*requires?\s+(?:documentation|justification)",
]

DOCUMENTATION_PATTERNS = [
    r"OCT\s+(?:within|dated|from)",
    r"visual\s+acuity",
    r"fundus\s+photograph",
    r"letter\s+of\s+(?:medical\s+)?necessity",
    r"clinical\s+notes?\s+(?:documenting|showing)",
    r"treatment\s+(?:history|record|documentation)",
    r"(?:diagnosis|diagnostic)\s+(?:report|documentation)",
]

AUTH_DURATION_PATTERNS = [
    r"(?:authorized?|approved?)\s+(?:for\s+)?(\d+)\s+months?",
    r"(?:valid|effective)\s+(?:for\s+)?(\d+)\s+months?",
    r"(\d+)[- ]month\s+(?:authorization|approval|period)",
    r"up\s+to\s+(\d+)\s+(?:injections?|treatments?)",
]

DENIAL_TRIGGER_PATTERNS = [
    r"(?:denied?|reject(?:ed)?)\s+(?:if|when|for)",
    r"(?:will|may)\s+(?:be\s+)?denied",
    r"(?:does\s+not|doesn't)\s+meet\s+(?:criteria|requirements?)",
    r"missing\s+(?:documentation|information)",
    r"(?:expired?|lapsed?)\s+(?:authorization|approval)",
    r"wrong\s+(?:diagnosis|code|laterality)",
]

ICD10_PATTERN = re.compile(r"[A-Z]\d{2}(?:\.\d{1,4})?")
HCPCS_PATTERN = re.compile(r"J\d{4}")
CPT_PATTERN = re.compile(r"6702[0-9]")


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract all text from a PDF file."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
            return "\n\n".join(pages)
    except Exception as e:
        log.warning(f"Failed to extract text from {pdf_path}: {e}")
        return ""


def search_patterns(text: str, patterns: list[str]) -> list[str]:
    """Search for regex patterns in text, return matching lines."""
    matches = []
    lines = text.split("\n")
    for line in lines:
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                matches.append(line.strip())
                break
    return matches


def extract_icd10_codes(text: str) -> list[str]:
    """Extract ICD-10 codes from text."""
    return sorted(set(ICD10_PATTERN.findall(text)))


def extract_hcpcs_codes(text: str) -> list[str]:
    """Extract HCPCS J-codes from text."""
    return sorted(set(HCPCS_PATTERN.findall(text)))


def extract_auth_duration(text: str) -> dict:
    """Extract authorization duration from text."""
    result = {"months": None, "max_injections": None}
    for pattern in AUTH_DURATION_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            num = int(match.group(1))
            if "injection" in match.group(0).lower() or "treatment" in match.group(0).lower():
                result["max_injections"] = num
            else:
                result["months"] = num
    return result


def determine_confidence(text: str, pa_matches: list, step_matches: list) -> str:
    """Determine extraction confidence based on match quality."""
    if len(pa_matches) >= 2 and len(step_matches) >= 1:
        return "high"
    elif len(pa_matches) >= 1:
        return "medium"
    else:
        return "low"


def extract_rules_from_pdf(pdf_path: Path, payer_id: str, payer_name: str) -> list[dict]:
    """Extract structured PA rules from a single PDF."""
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return []

    # Check if this document is relevant to our drugs/procedures
    text_lower = text.lower()
    relevant_terms = ["intravitreal", "anti-vegf", "vegf", "aflibercept", "bevacizumab",
                      "ranibizumab", "faricimab", "eylea", "avastin", "lucentis", "vabysmo",
                      "67028", "j0178", "j9035", "j2778"]
    if not any(term in text_lower for term in relevant_terms):
        log.debug(f"  Skipping irrelevant document: {pdf_path.name}")
        return []

    log.info(f"  Extracting rules from: {pdf_path.name}")

    # Extract evidence
    pa_matches = search_patterns(text, PA_REQUIRED_PATTERNS)
    step_matches = search_patterns(text, STEP_THERAPY_PATTERNS)
    doc_matches = search_patterns(text, DOCUMENTATION_PATTERNS)
    denial_matches = search_patterns(text, DENIAL_TRIGGER_PATTERNS)
    icd10_codes = extract_icd10_codes(text)
    hcpcs_codes = extract_hcpcs_codes(text)
    auth_duration = extract_auth_duration(text)
    confidence = determine_confidence(text, pa_matches, step_matches)

    # Determine which drugs are mentioned
    mentioned_drugs = {}
    for code, info in DRUG_CODES.items():
        if code.lower() in text_lower or info["name"] in text_lower or info["brand"].lower() in text_lower:
            mentioned_drugs[code] = info

    if not mentioned_drugs:
        # If no specific drugs found, create a generic rule
        mentioned_drugs = {"GENERIC": {"name": "anti-VEGF agents", "brand": "multiple"}}

    # Determine which diagnoses are mentioned
    mentioned_diagnoses = []
    for group_id, group_info in DIAGNOSIS_GROUPS.items():
        for pattern in group_info["icd10_patterns"]:
            if re.search(pattern, text):
                mentioned_diagnoses.append(group_id)
                break
    if not mentioned_diagnoses:
        mentioned_diagnoses = ["general_ophthalmology"]

    # Build rules
    rules = []
    for drug_code, drug_info in mentioned_drugs.items():
        for diag_group in mentioned_diagnoses:
            rule = {
                "payer_id": payer_id,
                "payer_name": payer_name,
                "drug_code": drug_code,
                "drug_name": f"{drug_info['brand']} ({drug_info['name']})",
                "procedure_code": "67028" if "67028" in text else "",
                "diagnosis_group": diag_group,
                "covered_icd10": [c for c in icd10_codes if any(
                    re.match(p, c) for p in DIAGNOSIS_GROUPS.get(diag_group, {}).get("icd10_patterns", [])
                )] if diag_group in DIAGNOSIS_GROUPS else icd10_codes[:20],
                "pa_required": len(pa_matches) > 0,
                "pa_evidence": pa_matches[:5],
                "step_therapy_required": len(step_matches) > 0,
                "step_therapy_evidence": step_matches[:5],
                "required_documentation": list(set(doc_matches))[:10],
                "auth_duration_months": auth_duration["months"],
                "auth_max_injections": auth_duration["max_injections"],
                "denial_triggers": list(set(denial_matches))[:10],
                "hcpcs_codes_found": hcpcs_codes,
                "policy_source_file": str(pdf_path),
                "policy_last_downloaded": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "extraction_confidence": confidence,
            }
            rules.append(rule)

    return rules


def extract_all_rules(base_dir: Path, target_payers: list[str], config: dict) -> list[dict]:
    """Extract rules from all downloaded PDFs for specified payers."""
    all_rules = []

    for payer_id in target_payers:
        payer_config = config["payers"].get(payer_id)
        if not payer_config:
            log.warning(f"Unknown payer: {payer_id}")
            continue

        payer_dir = base_dir / payer_id
        if not payer_dir.exists():
            log.warning(f"No downloads found for {payer_id} — run download_policies.py first")
            continue

        payer_name = payer_config["name"]
        log.info(f"\n=== {payer_name} ===")

        # Find all PDFs and HTML files
        pdf_files = sorted(payer_dir.glob("*.pdf"))
        html_files = sorted(payer_dir.glob("*.html"))

        log.info(f"  Found {len(pdf_files)} PDFs, {len(html_files)} HTML files")

        for pdf_path in pdf_files:
            rules = extract_rules_from_pdf(pdf_path, payer_id, payer_name)
            all_rules.extend(rules)
            if rules:
                log.info(f"    Extracted {len(rules)} rules from {pdf_path.name}")

    return all_rules


def print_summary(rules: list[dict]):
    """Print a summary of extracted rules."""
    print("\n" + "=" * 70)
    print("RULE EXTRACTION SUMMARY")
    print("=" * 70)

    # By payer
    payers = {}
    for r in rules:
        pid = r["payer_id"]
        if pid not in payers:
            payers[pid] = {"name": r["payer_name"], "rules": 0, "pa_required": 0, "step_therapy": 0}
        payers[pid]["rules"] += 1
        if r.get("pa_required"):
            payers[pid]["pa_required"] += 1
        if r.get("step_therapy_required"):
            payers[pid]["step_therapy"] += 1

    print(f"\n  Total rules extracted: {len(rules)}")
    print(f"\n  {'Payer':<30s}  {'Rules':>6s}  {'PA Req':>7s}  {'Step Tx':>8s}")
    print(f"  {'-'*30}  {'-'*6}  {'-'*7}  {'-'*8}")
    for pid, info in sorted(payers.items()):
        print(f"  {info['name']:<30s}  {info['rules']:>6d}  {info['pa_required']:>7d}  {info['step_therapy']:>8d}")

    # Confidence breakdown
    confidence_counts = {}
    for r in rules:
        c = r.get("extraction_confidence", "unknown")
        confidence_counts[c] = confidence_counts.get(c, 0) + 1

    print(f"\n  Confidence breakdown:")
    for c, count in sorted(confidence_counts.items()):
        print(f"    {c}: {count}")

    # Drug coverage
    drug_counts = {}
    for r in rules:
        dc = r.get("drug_code", "unknown")
        dn = r.get("drug_name", "unknown")
        drug_counts[dc] = {"name": dn, "count": drug_counts.get(dc, {}).get("count", 0) + 1}

    print(f"\n  Drug coverage:")
    for dc, info in sorted(drug_counts.items()):
        print(f"    {dc} ({info['name']}): {info['count']} rules")

    print()


def main():
    parser = argparse.ArgumentParser(description="Extract structured PA rules from downloaded policy PDFs")
    parser.add_argument("--payer", nargs="*", help="Specific payer(s) to extract from")
    parser.add_argument("--summary", action="store_true", help="Show summary of existing rules")
    parser.add_argument("--config", default="config.yaml", help="Config file path")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        log.error(f"Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    base_dir = Path(config["output"]["base_dir"])
    rules_path = Path(config["output"]["rules_file"])

    # Summary mode
    if args.summary:
        if not rules_path.exists():
            log.error(f"Rules file not found: {rules_path} — run extraction first")
            sys.exit(1)
        with open(rules_path) as f:
            rules = json.load(f)
        print_summary(rules)
        return

    # Extract mode
    target_payers = args.payer if args.payer else list(config["payers"].keys())

    log.info(f"Extracting rules for {len(target_payers)} payer(s): {', '.join(target_payers)}")

    all_rules = extract_all_rules(base_dir, target_payers, config)

    # Save rules
    rules_path.parent.mkdir(parents=True, exist_ok=True)
    with open(rules_path, "w") as f:
        json.dump(all_rules, f, indent=2)
    log.info(f"\nSaved {len(all_rules)} rules to {rules_path}")

    print_summary(all_rules)


if __name__ == "__main__":
    main()
