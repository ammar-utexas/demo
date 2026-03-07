# Product Requirements Document: CMS Prior Authorization Dataset — ML Training Pipeline for PMS

**Document ID:** PRD-PMS-CMSPA-001
**Version:** 1.0
**Date:** 2026-03-07
**Author:** Ammar (CEO, MPS Inc.)
**Status:** Draft

---

## 1. Executive Summary

There are no publicly available, labeled prior authorization (PA) datasets on Hugging Face or elsewhere suitable for ML training. However, CMS provides several public data sources that, when combined, can produce a usable labeled dataset for training a PA decision-support model. This experiment constructs a **prior authorization ML training dataset** by joining CMS Synthetic Medicare Claims data with CMS's Required Prior Authorization List to generate binary labels (PA required / not required), enriched with aggregate approval/denial rates from CMS PA Program Statistics.

The resulting dataset enables the PMS to train a classifier that predicts whether a given clinical encounter will require prior authorization — reducing staff time spent on manual PA determination and accelerating the revenue cycle.

## 2. Problem Statement

Prior authorization is one of the most time-consuming administrative tasks in healthcare:

- **No training data exists**: Hugging Face has zero PA-specific datasets. Real PA data is PHI-protected under HIPAA and not publicly released.
- **Manual PA determination**: Clinical staff currently cross-reference procedure codes against payer PA lists manually — a process that takes 15-30 minutes per case.
- **Denial risk**: Submitting claims without required PA leads to denials. Submitting unnecessary PA requests wastes staff time and delays care.
- **No ML baseline**: Without a labeled dataset, the PMS cannot train or evaluate any PA prediction model.

## 3. Data Sources

### 3.1 CMS Synthetic Claims Data (Features)

| Source | URL | Format | Content |
|--------|-----|--------|---------|
| DE-SynPUF (2008-2010) | https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files/cms-2008-2010-data-entrepreneurs-synthetic-public-use-file-de-synpuf/de10-sample-1 | CSV | Beneficiary demographics, Inpatient claims, Outpatient claims, Carrier claims, Rx events |
| Synthetic Medicare FFS Claims (newer) | https://data.cms.gov/collection/synthetic-medicare-enrollment-fee-for-service-claims-and-prescription-drug-event | CSV/API | Updated synthetic enrollment + FFS claims + Prescription Drug Events |

**Key fields for features:**
- `ICD9_DGNS_CD_1` through `_10` — Diagnosis codes
- `ICD9_PRCDR_CD_1` through `_6` — Procedure codes
- `HCPCS_CD_1` through `_45` — HCPCS/CPT codes (Carrier claims)
- `BENE_SEX_IDENT_CD`, `BENE_AGE`, `SP_*` — Demographics and chronic conditions
- `CLM_PMT_AMT`, `NCH_PRMRY_PYR_CLM_PD_AMT` — Payment amounts
- `PRVDR_NUM`, `AT_PHYSN_NPI` — Provider identifiers
- `CLM_FROM_DT`, `CLM_THRU_DT` — Service dates

**Size:** 20 samples x ~100K-150K beneficiaries each. Total claims across all samples: millions of rows.

### 3.2 CMS Required Prior Authorization List (Labels)

| Source | URL | Format |
|--------|-----|--------|
| DMEPOS Required PA List (Jan 2026) | https://www.cms.gov/research-statistics-data-and-systems/monitoring-programs/medicare-ffs-compliance-programs/dmepos/downloads/dmepos_pa_required-prior-authorization-list.pdf | PDF |
| PA Program Service Categories | https://www.cms.gov/data-research/monitoring-programs/medicare-fee-service-compliance-programs/prior-authorization-and-pre-claim-review-initiatives | Web/PDF |

**PA-covered service categories (Medicare FFS):**
- DMEPOS items (power wheelchairs, negative pressure wound therapy, etc.)
- Certain Hospital Outpatient Department (OPD) services
- Repetitive Scheduled Non-Emergent Ambulance Transport (RSNAT)
- Certain Ambulatory Surgical Center (ASC) services
- Inpatient Rehabilitation Facility (IRF) services

**Labeling approach:** Extract HCPCS/CPT codes from the Required PA List PDF, then join against synthetic claims — claims with matching codes get `pa_required = 1`, others get `pa_required = 0`.

### 3.3 CMS PA Program Statistics (Calibration)

| Source | URL | Format |
|--------|-----|--------|
| FY 2024 PA Stats | https://www.cms.gov/files/document/pre-claim-review-program-statistics-document-fy-24.pdf | PDF |
| FY 2023 PA Stats | https://www.cms.gov/files/document/pre-claim-review-program-statistics-document-fy-23.pdf | PDF |

**Key metrics to extract:**
- Approval rates by service category
- Denial rates and top denial reasons
- Affirmed/overturned on appeal rates
- Volume by category

**Use:** Calibrate the label distribution and provide class weights for model training.

## 4. Proposed Pipeline

### 4.1 Architecture Overview

```
Phase 1: Data Acquisition
  ├── Download DE-SynPUF Sample 1 (CSV files)
  ├── Parse CMS Required PA List PDF → HCPCS code list
  └── Parse PA Program Stats PDFs → approval/denial rates

Phase 2: Data Processing
  ├── Load Inpatient, Outpatient, Carrier claims into DataFrames
  ├── Extract all HCPCS/CPT procedure codes per claim
  ├── Join against PA-required code list → binary label
  ├── Engineer features (demographics, chronic conditions, claim amounts)
  └── Apply class weights from PA Stats (expected ~5-15% PA-required rate)

Phase 3: Dataset Construction
  ├── Merge features + labels into single dataset
  ├── Train/validation/test split (70/15/15)
  ├── Export as Parquet + HuggingFace Dataset format
  └── Publish dataset card with schema documentation

Phase 4: Baseline Model Training
  ├── Train XGBoost/LightGBM classifier (PA required yes/no)
  ├── Evaluate: precision, recall, F1, AUC-ROC
  ├── Analyze feature importance (which codes/conditions drive PA)
  └── Compare against rule-based lookup baseline

Phase 5: PMS Integration
  ├── Serve model via FastAPI endpoint
  ├── On encounter save → predict PA likelihood
  ├── Surface PA alert in frontend when probability > threshold
  └── Log predictions for feedback loop
```

### 4.2 Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Data processing | Python, pandas | Standard for tabular data |
| PDF parsing | pdfplumber or camelot | Extract tables from CMS PDFs |
| ML training | scikit-learn, XGBoost | Tabular classification, interpretable |
| Dataset format | HuggingFace datasets, Parquet | Interoperable, versioned |
| Model serving | FastAPI | Consistent with PMS backend |
| Experiment tracking | MLflow (optional) | Reproducibility |

### 4.3 Feature Engineering Plan

**Demographic features:**
- Age, sex, race, state/county
- Chronic condition flags (Alzheimer's, CHF, COPD, diabetes, etc.)

**Claim-level features:**
- Primary and secondary diagnosis codes (ICD-9 → category)
- Procedure codes (HCPCS/CPT)
- Place of service
- Claim payment amount
- Length of stay (inpatient)
- Provider specialty (carrier claims)

**Derived features:**
- Number of distinct diagnosis codes per claim
- Number of distinct procedure codes per claim
- Claim cost relative to category median
- Whether provider is high-volume for this procedure
- Chronic condition count (comorbidity index proxy)

## 5. Known Limitations and Mitigations

| Limitation | Impact | Mitigation |
|-----------|--------|-----------|
| Synthetic data ≠ real data | Distribution may not match real-world PA patterns | Use as proof-of-concept; retrain on real claims when available |
| DE-SynPUF uses ICD-9 (2008-2010) | Modern claims use ICD-10 | Map ICD-9 → ICD-10 categories, or use newer synthetic dataset |
| PA list covers Medicare FFS only | Commercial payer PA rules differ significantly | Treat as Medicare-specific model; extend with payer-specific rules later |
| Label imbalance | Most claims do NOT require PA (~85-95%) | Apply SMOTE, class weights, or focal loss |
| PA rules change over time | Model trained on 2026 PA list applied to 2008-2010 claims | Acceptable for training; deploy with current PA list |
| PDF parsing fragility | CMS PDF format may change | Pin specific document versions; add parsing validation |

## 6. Success Criteria

| Metric | Target | Rationale |
|--------|--------|-----------|
| Dataset size | > 100K labeled claims | Sufficient for tabular ML |
| Label coverage | PA-required codes appear in synthetic claims | Validates join is meaningful |
| Baseline AUC-ROC | > 0.85 | Demonstrates signal in features |
| Precision (PA=yes) | > 0.80 | Avoid false PA alerts overwhelming staff |
| Recall (PA=yes) | > 0.90 | Missing a required PA causes denial — high cost |
| End-to-end pipeline | Reproducible from raw CMS downloads | Anyone can rebuild the dataset |

## 7. Implementation Phases

| Phase | Scope | Deliverable |
|-------|-------|-------------|
| **Phase 1** | Download and parse all CMS data sources | Raw CSVs + extracted PA code list |
| **Phase 2** | Feature engineering and labeling pipeline | Labeled DataFrame with train/val/test splits |
| **Phase 3** | Baseline model training and evaluation | Trained model + evaluation report |
| **Phase 4** | Dataset packaging and publication | HuggingFace dataset card + Parquet files |
| **Phase 5** | PMS API integration | `/api/v1/pa-predict` endpoint + frontend alert |

## 8. Future Extensions

- **CMS-0057-F FHIR API (Jan 2027)**: When payers implement the mandated Prior Authorization API, ingest real PA decision data for fine-tuning.
- **Part C UM Data (Apr 2026)**: Medicare Advantage organizations will submit internal PA criteria — incorporate as additional label source.
- **Commercial payer rules**: Integrate payer-specific PA lists (Aetna CPBs, UHC policies) to extend beyond Medicare FFS.
- **LLM-augmented PA**: Use Claude/GPT to extract medical necessity justifications from clinical notes and auto-populate PA request forms.
- **Appeal prediction**: Extend the model to predict appeal success probability for denied PAs.

## 9. References

- [CMS DE-SynPUF](https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files/cms-2008-2010-data-entrepreneurs-synthetic-public-use-file-de-synpuf)
- [CMS Synthetic Medicare FFS Claims Collection](https://data.cms.gov/collection/synthetic-medicare-enrollment-fee-for-service-claims-and-prescription-drug-event)
- [CMS Prior Authorization Initiatives](https://www.cms.gov/data-research/monitoring-programs/medicare-fee-service-compliance-programs/prior-authorization-and-pre-claim-review-initiatives)
- [CMS-0057-F Interoperability & Prior Authorization Rule](https://www.cms.gov/cms-interoperability-and-prior-authorization-final-rule-cms-0057-f)
- [CMS Part C UM Data Submission](https://www.cms.gov/medicare/audits-compliance/part-c-part-d-compliance-audits/part-c-utilization-management-um-annual-data-submission)
- [DE-SynPUF User Manual](https://www.cms.gov/Research-Statistics-Data-and-Systems/Downloadable-Public-Use-Files/SynPUFs/Downloads/SynPUF_DUG.pdf)
