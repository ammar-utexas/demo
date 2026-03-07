# Experiment 44: Payer Policy Download — Anti-VEGF PA Rule Library

Downloads publicly available medical policy documents from 6 major payers to build a structured prior authorization rule library for anti-VEGF intravitreal injections.

## Payers

| Payer | Type | Key Documents |
|-------|------|---------------|
| CMS Medicare Traditional | FFS | LCDs, NCDs, ASP pricing |
| UnitedHealthcare | MA | Medical policies, PA list, formulary |
| Aetna | MA | Clinical Policy Bulletins, precertification |
| BCBS of Texas | Commercial + MA | Medical policies, PA requirements |
| Humana | MA | Coverage policies, PA lookup |
| Cigna | MA | Coverage policies, EviCore guidelines |

## Quick Start

```bash
# Install dependencies
pip install requests beautifulsoup4 pdfplumber pyyaml

# Download all payer policies
python download_policies.py

# Download specific payer(s)
python download_policies.py --payer cms_medicare uhc

# List configured payers
python download_policies.py --list

# Verify existing downloads
python download_policies.py --verify

# Extract structured rules from downloaded PDFs
python extract_rules.py

# View extraction summary
python extract_rules.py --summary
```

## Output Structure

```
data/
├── cms_medicare/     # CMS LCDs, NCDs, ASP pricing
├── uhc/              # UHC medical policies, PA requirements
├── aetna/            # Aetna CPBs, precertification
├── bcbstx/           # BCBSTX medical policies
├── humana/           # Humana coverage policies
├── cigna/            # Cigna + EviCore guidelines
└── manifest.json     # Download manifest (URLs, dates, SHA-256 checksums)

rules/
└── payer_rules.json  # Extracted structured PA rules
```

## Manifest

Every download is tracked in `data/manifest.json` with:
- Source URL
- Download timestamp
- File size
- SHA-256 checksum
- Content type
- Status (success/failed)

Run `python download_policies.py --verify` to validate all files against the manifest.

## Rule Schema

Each extracted rule follows this schema:

```json
{
  "payer_id": "uhc_ma",
  "drug_code": "J0178",
  "drug_name": "Eylea (aflibercept)",
  "diagnosis_group": "wet_amd",
  "pa_required": true,
  "step_therapy_required": true,
  "required_documentation": ["OCT within 30 days", "Visual acuity"],
  "auth_duration_months": 6,
  "extraction_confidence": "high"
}
```

## Rebuild on New Machine

```bash
cd experiments/44-payer-policy-download
pip install requests beautifulsoup4 pdfplumber pyyaml
python download_policies.py
python extract_rules.py
```

## Notes

- Some payer portals use JavaScript rendering — if pages download as empty HTML, use Playwright fallback
- Only publicly accessible documents are downloaded (no login-walled content)
- Policy documents should be re-downloaded monthly to catch updates
- The `data/` directory is gitignored; use `download_policies.py` to rebuild
