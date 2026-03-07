"""
Experiment 43: CMS Prior Authorization ML Training Dataset Builder

Phase 1-2: Parse PA Required List, load DE-SynPUF claims, join to create labeled dataset.

Data sources:
  - CMS DE-SynPUF Sample 1 (2008-2010 synthetic Medicare claims)
  - CMS DMEPOS Required Prior Authorization List (Jan 2026)
"""

import re
import pandas as pd
import pdfplumber
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
RAW_DIR = DATA_DIR / "raw"
OUTPUT_DIR = DATA_DIR / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ── Step 1: Extract HCPCS codes from PA Required List PDF ──────────────────

def extract_pa_codes(pdf_path: str) -> pd.DataFrame:
    """Extract HCPCS codes requiring prior authorization from CMS PDF."""
    codes = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if row and row[0] and re.match(r'^[A-Z]\d{4}$', row[0].strip()):
                        code = row[0].strip()
                        desc = row[1].replace('\n', ' ').strip() if row[1] else ''
                        codes.append({
                            'hcpcs_code': code,
                            'description': desc,
                            'pa_source': 'DMEPOS_LIST',
                        })

    # Add Hospital OPD PA services (CMS PA program categories)
    # Source: https://www.cms.gov/.../prior-authorization-certain-hospital-outpatient-department-opd-services
    opd_pa_codes = {
        # Blepharoplasty
        '15820': 'Blepharoplasty, lower eyelid',
        '15821': 'Blepharoplasty, lower eyelid; with extensive herniated fat pad',
        '15822': 'Blepharoplasty, upper eyelid',
        '15823': 'Blepharoplasty, upper eyelid; with excessive skin weighting down lid',
        # Botulinum toxin
        '64612': 'Chemodenervation of muscle(s); muscle(s) innervated by facial nerve',
        '64615': 'Chemodenervation of muscle(s); muscle(s) innervated by facial, trigeminal, cervical spinal and accessory nerves, bilateral',
        '64616': 'Chemodenervation of muscle(s); neck muscle(s)',
        '64617': 'Chemodenervation of muscle(s); larynx',
        '64642': 'Chemodenervation of one extremity; 1-4 muscle(s)',
        '64643': 'Chemodenervation of one extremity; each additional extremity, 1-4 muscles',
        '64644': 'Chemodenervation of one extremity; 5 or more muscles',
        '64645': 'Chemodenervation of one extremity; each additional extremity, 5 or more muscles',
        '64646': 'Chemodenervation of trunk muscle(s); 1-5 muscle(s)',
        '64647': 'Chemodenervation of trunk muscle(s); 6 or more muscles',
        # Panniculectomy
        '15830': 'Excision, excessive skin and subcutaneous tissue (includes lipectomy); abdomen',
        # Rhinoplasty
        '30400': 'Rhinoplasty, primary; lateral and alar cartilages and/or elevation of nasal tip',
        '30410': 'Rhinoplasty, primary; complete, external parts including bony pyramid, lateral and alar cartilages',
        '30420': 'Rhinoplasty, primary; including major septal repair',
        '30430': 'Rhinoplasty, secondary; minor revision (small amount of nasal tip work)',
        '30435': 'Rhinoplasty, secondary; intermediate revision',
        '30450': 'Rhinoplasty, secondary; major revision',
        # Vein ablation
        '36473': 'Endovenous ablation therapy, mechanochemical; first vein treated',
        '36474': 'Endovenous ablation therapy, mechanochemical; subsequent vein(s) treated',
        '36475': 'Endovenous ablation therapy, radiofrequency; first vein treated',
        '36476': 'Endovenous ablation therapy, radiofrequency; subsequent vein(s) treated',
        '36478': 'Endovenous ablation therapy, laser; first vein treated',
        '36479': 'Endovenous ablation therapy, laser; subsequent vein(s) treated',
        '36482': 'Endovenous ablation therapy, non-thermal non-tumescent; first vein treated',
        '36483': 'Endovenous ablation therapy, non-thermal non-tumescent; subsequent vein(s) treated',
        # Spinal neurostimulators
        '63650': 'Percutaneous implantation of neurostimulator electrode array, epidural',
        '63685': 'Insertion or replacement of spinal neurostimulator pulse generator',
        '63688': 'Revision or removal of implanted spinal neurostimulator pulse generator',
        # Cervical fusion
        '22551': 'Arthrodesis, anterior interbody, including disc space preparation; cervical below C2',
        '22552': 'Arthrodesis, anterior interbody; cervical below C2, each additional interspace',
        '22554': 'Arthrodesis, anterior interbody technique; cervical below C2',
        # Facet joint interventions
        '64490': 'Injection(s), diagnostic or therapeutic agent; cervical or thoracic, single level',
        '64491': 'Injection(s), diagnostic or therapeutic agent; cervical or thoracic, second level',
        '64493': 'Injection(s), diagnostic or therapeutic agent; lumbar or sacral, single level',
        '64494': 'Injection(s), diagnostic or therapeutic agent; lumbar or sacral, second level',
    }
    for code, desc in opd_pa_codes.items():
        codes.append({
            'hcpcs_code': code,
            'description': desc,
            'pa_source': 'HOSPITAL_OPD',
        })

    # Add Repetitive Scheduled Non-Emergent Ambulance Transport (RSNAT)
    rsnat_codes = {
        'A0426': 'Ambulance service, advanced life support, non-emergency transport, level 1 (ALS 1)',
        'A0428': 'Ambulance service, basic life support, non-emergency transport (BLS)',
    }
    for code, desc in rsnat_codes.items():
        codes.append({
            'hcpcs_code': code,
            'description': desc,
            'pa_source': 'RSNAT',
        })

    df = pd.DataFrame(codes).drop_duplicates(subset='hcpcs_code')
    print(f"Extracted {len(df)} unique PA-required HCPCS codes")

    # Show categories
    by_source = df['pa_source'].value_counts()
    print(f"\nBy PA program:")
    for source, count in by_source.items():
        print(f"  {source}: {count} codes")

    prefixes = df['hcpcs_code'].str[0].value_counts()
    print(f"\nCode prefixes:")
    for prefix, count in prefixes.items():
        print(f"  {prefix}: {count} codes")

    return df


# ── Step 2: Load DE-SynPUF claims data ─────────────────────────────────────

def load_beneficiary(path: str) -> pd.DataFrame:
    """Load beneficiary summary file."""
    df = pd.read_csv(path)
    print(f"Beneficiary records: {len(df):,}")
    print(f"  Columns: {list(df.columns)}")
    return df


def load_carrier_claims(path: str) -> pd.DataFrame:
    """Load carrier claims (contains HCPCS codes)."""
    df = pd.read_csv(path, low_memory=False)
    print(f"Carrier claims: {len(df):,}")

    # Identify HCPCS columns
    hcpcs_cols = [c for c in df.columns if 'HCPCS' in c.upper()]
    print(f"  HCPCS columns: {hcpcs_cols}")

    return df


def load_outpatient_claims(path: str) -> pd.DataFrame:
    """Load outpatient claims (contains HCPCS codes)."""
    df = pd.read_csv(path, low_memory=False)
    print(f"Outpatient claims: {len(df):,}")

    hcpcs_cols = [c for c in df.columns if 'HCPCS' in c.upper()]
    print(f"  HCPCS columns: {hcpcs_cols}")

    return df


def load_inpatient_claims(path: str) -> pd.DataFrame:
    """Load inpatient claims."""
    df = pd.read_csv(path, low_memory=False)
    print(f"Inpatient claims: {len(df):,}")
    return df


# ── Step 3: Label claims with PA requirement ───────────────────────────────

def label_carrier_claims(carrier_df: pd.DataFrame, pa_codes: set) -> pd.DataFrame:
    """Label carrier claims: does any HCPCS code on the claim require PA?"""
    hcpcs_cols = [c for c in carrier_df.columns if 'HCPCS' in c.upper()]

    # Check if any HCPCS code on the claim matches a PA-required code
    pa_match = pd.DataFrame(False, index=carrier_df.index, columns=['pa_required'])
    for col in hcpcs_cols:
        pa_match['pa_required'] |= carrier_df[col].astype(str).str.strip().isin(pa_codes)

    carrier_df['pa_required'] = pa_match['pa_required'].astype(int)

    pa_count = carrier_df['pa_required'].sum()
    total = len(carrier_df)
    print(f"\nCarrier claims PA labeling:")
    print(f"  PA required: {pa_count:,} ({pa_count/total*100:.2f}%)")
    print(f"  No PA: {total - pa_count:,} ({(total-pa_count)/total*100:.2f}%)")

    return carrier_df


def label_outpatient_claims(outpatient_df: pd.DataFrame, pa_codes: set) -> pd.DataFrame:
    """Label outpatient claims: does any HCPCS code on the claim require PA?"""
    hcpcs_cols = [c for c in outpatient_df.columns if 'HCPCS' in c.upper()]

    pa_match = pd.DataFrame(False, index=outpatient_df.index, columns=['pa_required'])
    for col in hcpcs_cols:
        pa_match['pa_required'] |= outpatient_df[col].astype(str).str.strip().isin(pa_codes)

    outpatient_df['pa_required'] = pa_match['pa_required'].astype(int)

    pa_count = outpatient_df['pa_required'].sum()
    total = len(outpatient_df)
    print(f"\nOutpatient claims PA labeling:")
    print(f"  PA required: {pa_count:,} ({pa_count/total*100:.2f}%)")
    print(f"  No PA: {total - pa_count:,} ({(total-pa_count)/total*100:.2f}%)")

    return outpatient_df


# ── Step 4: Feature engineering ────────────────────────────────────────────

def engineer_features(claims_df: pd.DataFrame, beneficiary_df: pd.DataFrame,
                      claim_type: str) -> pd.DataFrame:
    """Create ML features from claims + beneficiary data."""

    # Merge beneficiary demographics into claims
    bene_cols = ['DESYNPUF_ID']
    demo_cols = [c for c in beneficiary_df.columns if c.startswith('BENE_') or c.startswith('SP_')]
    bene_cols.extend(demo_cols)
    bene_subset = beneficiary_df[bene_cols].copy()

    merged = claims_df.merge(bene_subset, on='DESYNPUF_ID', how='left')

    # Count diagnosis codes per claim
    diag_cols = [c for c in merged.columns if 'DGNS_CD' in c and 'DGNS_CD_' in c]
    merged['n_diagnosis_codes'] = merged[diag_cols].notna().sum(axis=1)

    # Count procedure codes per claim
    prcdr_cols = [c for c in merged.columns if 'PRCDR_CD' in c and 'PRCDR_CD_' in c]
    if prcdr_cols:
        merged['n_procedure_codes'] = merged[prcdr_cols].notna().sum(axis=1)

    # Count HCPCS codes per claim
    hcpcs_cols = [c for c in merged.columns if 'HCPCS' in c.upper()]
    if hcpcs_cols:
        merged['n_hcpcs_codes'] = merged[hcpcs_cols].notna().sum(axis=1)

    # Chronic condition count (comorbidity proxy)
    sp_cols = [c for c in merged.columns if c.startswith('SP_')]
    if sp_cols:
        # SP_ columns use 1=yes, 2=no in SynPUF
        for col in sp_cols:
            merged[col] = (merged[col] == 1).astype(int)
        merged['chronic_condition_count'] = merged[sp_cols].sum(axis=1)

    # Payment amount (if present)
    pmt_cols = [c for c in merged.columns if 'PMT_AMT' in c or 'PD_AMT' in c]
    if pmt_cols:
        merged['total_payment'] = merged[pmt_cols].sum(axis=1)

    merged['claim_type'] = claim_type

    print(f"\n{claim_type} features engineered: {merged.shape}")
    return merged


# ── Step 5: Build final dataset ────────────────────────────────────────────

def build_dataset():
    """Main pipeline: parse, load, label, engineer features, export."""

    print("=" * 60)
    print("CMS Prior Authorization Dataset Builder")
    print("=" * 60)

    # Step 1: Extract PA codes
    print("\n── Step 1: Extract PA-required HCPCS codes ──")
    pa_df = extract_pa_codes(RAW_DIR / "PA_Required_List.pdf")
    pa_codes = set(pa_df['hcpcs_code'].values)
    pa_df.to_csv(OUTPUT_DIR / "pa_required_codes.csv", index=False)
    print(f"Saved to {OUTPUT_DIR / 'pa_required_codes.csv'}")

    # Step 2: Load claims
    print("\n── Step 2: Load DE-SynPUF claims ──")
    beneficiary = load_beneficiary(
        DATA_DIR / "DE1_0_2008_Beneficiary_Summary_File_Sample_1.csv"
    )
    carrier = load_carrier_claims(
        DATA_DIR / "DE1_0_2008_to_2010_Carrier_Claims_Sample_1A.csv"
    )
    outpatient = load_outpatient_claims(
        DATA_DIR / "DE1_0_2008_to_2010_Outpatient_Claims_Sample_1.csv"
    )
    inpatient = load_inpatient_claims(
        DATA_DIR / "DE1_0_2008_to_2010_Inpatient_Claims_Sample_1.csv"
    )

    # Step 3: Label claims
    print("\n── Step 3: Label claims with PA requirement ──")
    carrier_labeled = label_carrier_claims(carrier, pa_codes)
    outpatient_labeled = label_outpatient_claims(outpatient, pa_codes)

    # Step 4: Engineer features
    print("\n── Step 4: Engineer features ──")
    carrier_features = engineer_features(carrier_labeled, beneficiary, 'carrier')
    outpatient_features = engineer_features(outpatient_labeled, beneficiary, 'outpatient')

    # Step 5: Combine and export
    print("\n── Step 5: Build final dataset ──")

    # Select common feature columns for the combined dataset
    common_features = [
        'DESYNPUF_ID', 'CLM_ID', 'claim_type', 'pa_required',
        'n_diagnosis_codes', 'chronic_condition_count',
    ]
    # Add demographic columns
    demo_features = [c for c in carrier_features.columns if c.startswith('BENE_')]
    sp_features = [c for c in carrier_features.columns if c.startswith('SP_')]

    # Carrier-specific
    carrier_export_cols = common_features + demo_features + sp_features
    carrier_export_cols += [c for c in ['n_hcpcs_codes', 'total_payment'] if c in carrier_features.columns]
    carrier_out = carrier_features[[c for c in carrier_export_cols if c in carrier_features.columns]]

    # Outpatient-specific
    outpatient_export_cols = common_features + demo_features + sp_features
    outpatient_export_cols += [c for c in ['n_hcpcs_codes', 'n_procedure_codes', 'total_payment'] if c in outpatient_features.columns]
    outpatient_out = outpatient_features[[c for c in outpatient_export_cols if c in outpatient_features.columns]]

    # Combine
    combined = pd.concat([carrier_out, outpatient_out], ignore_index=True)

    print(f"\nFinal dataset shape: {combined.shape}")
    print(f"PA required distribution:")
    print(combined['pa_required'].value_counts())
    print(f"\nPA rate: {combined['pa_required'].mean()*100:.2f}%")

    # Train/val/test split
    from sklearn.model_selection import train_test_split

    train, temp = train_test_split(combined, test_size=0.3, random_state=42,
                                   stratify=combined['pa_required'])
    val, test = train_test_split(temp, test_size=0.5, random_state=42,
                                 stratify=temp['pa_required'])

    print(f"\nSplits:")
    print(f"  Train: {len(train):,} (PA rate: {train['pa_required'].mean()*100:.2f}%)")
    print(f"  Val:   {len(val):,} (PA rate: {val['pa_required'].mean()*100:.2f}%)")
    print(f"  Test:  {len(test):,} (PA rate: {test['pa_required'].mean()*100:.2f}%)")

    # Export
    combined.to_parquet(OUTPUT_DIR / "cms_pa_dataset_full.parquet", index=False)
    train.to_parquet(OUTPUT_DIR / "cms_pa_dataset_train.parquet", index=False)
    val.to_parquet(OUTPUT_DIR / "cms_pa_dataset_val.parquet", index=False)
    test.to_parquet(OUTPUT_DIR / "cms_pa_dataset_test.parquet", index=False)

    print(f"\nDataset exported to {OUTPUT_DIR}/")
    print(f"  cms_pa_dataset_full.parquet   ({combined.shape})")
    print(f"  cms_pa_dataset_train.parquet  ({train.shape})")
    print(f"  cms_pa_dataset_val.parquet    ({val.shape})")
    print(f"  cms_pa_dataset_test.parquet   ({test.shape})")

    # Summary stats
    print("\n── Dataset Summary ──")
    print(combined.describe())

    return combined


if __name__ == "__main__":
    build_dataset()
