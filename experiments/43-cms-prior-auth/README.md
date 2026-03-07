# Experiment 43: CMS Prior Authorization ML Training Dataset

Builds a labeled ML dataset for prior authorization prediction by combining CMS synthetic Medicare claims with CMS PA-required HCPCS code lists.

## Prerequisites

```bash
pip install pandas pdfplumber pyarrow scikit-learn
```

## Rebuild Dataset from Scratch

The `data/` directory is gitignored (1.4GB+ of CSVs and parquet files). Run these steps to recreate it on a new machine.

### Step 1: Create directories

```bash
mkdir -p data/raw data/processed
```

### Step 2: Download CMS source files

```bash
cd data/raw

# DE-SynPUF Sample 1 — Beneficiary Summary (2008)
curl -L -o DE1_0_2008_Beneficiary_Summary_Sample_1.zip \
  "https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_beneficiary_summary_file_sample_1.zip"

# DE-SynPUF Sample 1 — Inpatient Claims (2008-2010)
curl -L -o DE1_0_Inpatient_Claims_Sample_1.zip \
  "https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_to_2010_inpatient_claims_sample_1.zip"

# DE-SynPUF Sample 1 — Outpatient Claims (2008-2010)
curl -L -o DE1_0_Outpatient_Claims_Sample_1.zip \
  "https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_to_2010_outpatient_claims_sample_1.zip"

# DE-SynPUF Sample 1 — Carrier Claims 1A (2008-2010)
curl -L -o DE1_0_Carrier_Claims_Sample_1A.zip \
  "http://downloads.cms.gov/files/DE1_0_2008_to_2010_Carrier_Claims_Sample_1A.zip"

# CMS Required Prior Authorization List (DMEPOS)
curl -L -o PA_Required_List.pdf \
  "https://www.cms.gov/research-statistics-data-and-systems/monitoring-programs/medicare-ffs-compliance-programs/dmepos/downloads/dmepos_pa_required-prior-authorization-list.pdf"

# CMS PA Program Statistics FY24
curl -L -o PA_Stats_FY24.pdf \
  "https://www.cms.gov/files/document/pre-claim-review-program-statistics-document-fy-24.pdf"
```

### Step 3: Extract CSVs

```bash
cd data/raw
for f in *.zip; do unzip -o "$f" -d ../; done
```

### Step 4: Build the labeled dataset

```bash
cd ../..   # back to experiments/43-cms-prior-auth/
python3 build_dataset.py
```

## Output

After running `build_dataset.py`, the following files are created in `data/processed/`:

| File | Description |
|------|-------------|
| `pa_required_codes.csv` | 115 HCPCS codes requiring PA (from 3 CMS programs) |
| `cms_pa_dataset_full.parquet` | Full labeled dataset (3.16M claims, 30 features) |
| `cms_pa_dataset_train.parquet` | Training split (70%) |
| `cms_pa_dataset_val.parquet` | Validation split (15%) |
| `cms_pa_dataset_test.parquet` | Test split (15%) |

## Dataset Stats

- **Total claims**: 3,161,457
- **PA-required claims**: 22,231 (0.70%)
- **PA code sources**: DMEPOS list (74), Hospital OPD (39), RSNAT ambulance (2)
- **Features**: demographics, chronic conditions, diagnosis/procedure counts, payment amounts

## Data Sources

| Source | URL |
|--------|-----|
| DE-SynPUF Overview | https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files |
| DE-SynPUF User Manual | https://www.cms.gov/Research-Statistics-Data-and-Systems/Downloadable-Public-Use-Files/SynPUFs/Downloads/SynPUF_DUG.pdf |
| CMS PA Initiatives | https://www.cms.gov/data-research/monitoring-programs/medicare-fee-service-compliance-programs/prior-authorization-and-pre-claim-review-initiatives |
| DMEPOS PA List | https://www.cms.gov/research-statistics-data-and-systems/monitoring-programs/medicare-ffs-compliance-programs/dmepos/downloads/dmepos_pa_required-prior-authorization-list.pdf |
