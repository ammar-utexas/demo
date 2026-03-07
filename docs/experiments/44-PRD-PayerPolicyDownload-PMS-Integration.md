# PRD: Payer Policy Download — Anti-VEGF Prior Authorization Rule Library

**Document ID:** PMS-EXP-PPD-PRD-001
**Version:** 1.0
**Date:** 2026-03-07
**Applies To:** MarginLogic PA Outcome Intelligence (Experiment 44)
**Depends On:** Experiment 43 (CMS Prior Auth ML Dataset)

---

## 1. Problem Statement

MarginLogic's PA prediction model (Experiment 43) is trained on CMS synthetic claims data with binary PA-required labels. To make predictions actionable for Texas Retina Associates (TRA), the system needs payer-specific rules: which drugs require PA, what step therapy protocols apply, what documentation is needed, and what triggers denials.

These rules are publicly available in payer medical policy documents, coverage determination guidelines, formularies, and prior authorization requirement lists. Today, a PA coordinator manually looks up these rules across 6+ payer websites. This experiment automates the download, organizing all policy documents into a structured library that feeds the MarginLogic rule engine.

## 2. Objective

Build an automated pipeline that:

1. **Downloads** all publicly available anti-VEGF PA policy documents from 6 payers
2. **Organizes** them into a structured directory by payer, document type, and date
3. **Generates a manifest** tracking what was downloaded, when, and from where
4. **Extracts structured rule data** (JSON) from downloaded PDFs where possible
5. **Verifies** downloads are complete and uncorrupted

## 3. Payers in Scope

| # | Payer | Type | Why Included |
|---|-------|------|--------------|
| 1 | **CMS Medicare Traditional** | FFS | Baseline — LCDs/NCDs govern coverage without PA |
| 2 | **UnitedHealthcare** | Medicare Advantage | Largest MA payer nationally; requires PA for anti-VEGF |
| 3 | **Aetna** | Medicare Advantage | Major MA payer; detailed CPBs publicly available |
| 4 | **BCBS of Texas** | Commercial + MA | Dominant Texas payer; uses Availity for PA submission |
| 5 | **Humana** | Medicare Advantage | Significant MA market share in Texas |
| 6 | **Cigna** | Medicare Advantage | Delegates specialty PA to EviCore |

## 4. Document Types to Download

For each payer, the pipeline targets these document categories:

| Category | Description | Expected Format |
|----------|-------------|-----------------|
| **Medical Policy** | Coverage criteria for intravitreal injections / anti-VEGF agents | PDF |
| **Prior Auth Requirements List** | Which procedures/drugs require PA by plan type | PDF / HTML |
| **Drug Formulary** | Tier placement for each anti-VEGF drug | PDF / HTML |
| **Step Therapy Protocols** | Required drug sequencing (e.g., Avastin before Eylea) | PDF |
| **Billing/Coding Articles** | CPT/HCPCS/ICD-10 code requirements | PDF |
| **Clinical Guidelines** | EviCore or payer-specific clinical criteria | PDF |

## 5. Target Drug/Procedure Codes

| Drug | Brand | HCPCS | Indication |
|------|-------|-------|------------|
| Aflibercept | Eylea | J0178 | Wet AMD, DME, RVO |
| Aflibercept 8mg | Eylea HD | J0179 | Wet AMD, DME |
| Bevacizumab | Avastin | J9035 | Wet AMD (off-label, preferred) |
| Ranibizumab | Lucentis | J2778 | Wet AMD, DME, RVO |
| Faricimab | Vabysmo | J3490/J3590 | Wet AMD, DME |
| Pegcetacoplan | Syfovre | J1442 | Geographic Atrophy |
| Avacincaptad pegol | Izervay | J0ITZ | Geographic Atrophy |
| Intravitreal injection | (procedure) | CPT 67028 | All above |

## 6. Pipeline Architecture

```
download_policies.py
├── config.yaml              # Payer URLs, search terms, output paths
├── downloaders/
│   ├── cms_medicare.py      # CMS Medicare Coverage Database scraper
│   ├── uhc.py               # UnitedHealthcare policy downloader
│   ├── aetna.py             # Aetna CPB downloader
│   ├── bcbstx.py            # BCBS Texas policy downloader
│   ├── humana.py            # Humana coverage policy downloader
│   └── cigna.py             # Cigna + EviCore policy downloader
├── extractors/
│   └── pdf_rule_extractor.py  # Extract structured rules from PDFs
├── data/
│   ├── cms_medicare/        # Downloaded CMS documents
│   ├── uhc/                 # Downloaded UHC documents
│   ├── aetna/               # Downloaded Aetna documents
│   ├── bcbstx/              # Downloaded BCBSTX documents
│   ├── humana/              # Downloaded Humana documents
│   ├── cigna/               # Downloaded Cigna documents
│   └── manifest.json        # Download manifest with URLs, dates, checksums
└── rules/
    └── payer_rules.json     # Extracted structured rules (Phase 3 output)
```

## 7. Phases

### Phase 1: CMS Medicare Traditional (This Experiment)

Download from CMS Medicare Coverage Database:
- LCDs for intravitreal injections (Novitas Solutions, Jurisdiction H — Texas)
- LCD L33346 and associated LCA billing articles
- NCDs for ophthalmology
- ASP drug pricing file for Part B drugs
- ICD-10 code lists from LCD documents

### Phase 2: Top 5 MA Payers (This Experiment)

For each payer (UHC, Aetna, BCBSTX, Humana, Cigna):
- Medical policy for intravitreal injections / anti-VEGF agents
- Prior authorization requirements list (filtered for Texas / ophthalmology)
- Current drug formulary
- Step therapy protocols
- Clinical guidelines (EviCore for Cigna)

### Phase 3: Rule Extraction (This Experiment)

Parse downloaded PDFs to extract structured rule objects:
- PA required (yes/no) per payer × drug × diagnosis
- Step therapy requirements and exception paths
- Required documentation checklists
- Auth duration and renewal criteria
- Denial triggers
- Appeal process details

### Phase 4: Ongoing Monitoring (Future)

- Monthly re-download to detect policy changes
- Diff detection between current and previous versions
- Alert on formulary tier changes (especially biosimilar entry)

## 8. Output Schema

Each payer × drug × diagnosis combination produces a rule object:

```json
{
  "payer_id": "uhc_ma",
  "payer_name": "UnitedHealthcare Medicare Advantage",
  "drug_code": "J0178",
  "drug_name": "Eylea (aflibercept)",
  "procedure_code": "67028",
  "diagnosis_group": "wet_amd",
  "covered_icd10": ["H35.31", "H35.3110", "H35.3111"],
  "pa_required": true,
  "step_therapy_required": true,
  "step_therapy_detail": "Must document failure of 2+ bevacizumab injections",
  "step_therapy_exception_path": "Medical necessity letter for adverse reaction",
  "required_documentation": [
    "OCT within 30 days",
    "Visual acuity measurement",
    "Letter of medical necessity"
  ],
  "auth_duration_months": 6,
  "auth_max_injections": 6,
  "renewal_criteria": "Documented treatment response",
  "submission_method": "UHC provider portal or fax",
  "avg_turnaround_days": "5-7",
  "denial_triggers": [
    "Missing OCT date",
    "No Avastin trial documented"
  ],
  "appeal_process": "Written appeal within 60 days; peer-to-peer available",
  "policy_source_file": "uhc/medical_policy_intravitreal.pdf",
  "policy_source_url": "https://...",
  "policy_last_downloaded": "2026-03-07",
  "extraction_confidence": "high"
}
```

## 9. Success Criteria

| Metric | Target |
|--------|--------|
| Payers covered | 6/6 |
| Document types per payer | >= 3 |
| Total documents downloaded | >= 20 |
| Manifest completeness | 100% (every file has URL, date, checksum) |
| Rule extraction coverage | >= 1 rule per payer × drug combination |
| Download reproducibility | `download_policies.py` runs end-to-end on a clean machine |

## 10. Known Limitations

1. **Dynamic content:** Some payer portals load policies via JavaScript — may need Playwright for those pages
2. **Login walls:** Some formulary details require provider portal login — we only download publicly accessible documents
3. **PDF parsing accuracy:** Structured rule extraction from free-text PDFs is imperfect — confidence scores flag uncertain extractions
4. **Policy change frequency:** Documents become stale; monthly re-download recommended
5. **URL stability:** Payer URLs change without notice — the manifest tracks last-known-good URLs

## 11. Dependencies

| Dependency | Purpose |
|------------|---------|
| `requests` | HTTP downloads |
| `beautifulsoup4` | HTML parsing for search results |
| `pdfplumber` | PDF text extraction |
| `playwright` | JavaScript-rendered pages (fallback) |
| `hashlib` | SHA-256 checksums for integrity |
| `pyyaml` | Configuration file parsing |
