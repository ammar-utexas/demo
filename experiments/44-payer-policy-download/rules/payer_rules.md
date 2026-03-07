# Anti-VEGF Prior Authorization Rules

*Auto-generated from `payer_rules.json` — 2026-03-07 15:16 UTC*

**30 rules** extracted from downloaded payer policy documents.

## Summary

| Payer | Rules | PA Required | Step Therapy |
|-------|------:|------------:|-------------:|
| Aetna Medicare Advantage | 6 | 6 | 0 |
| UnitedHealthcare Medicare Advantage | 24 | 8 | 12 |

## Drug Coverage

| HCPCS | Drug | Payers | Rules | PA Required |
|-------|------|-------:|------:|------------:|
| J0178 | Eylea (aflibercept) | 2 | 6 | 2 |
| J0179 | Eylea HD (aflibercept 8mg) | 2 | 5 | 3 |
| J1442 | Syfovre (pegcetacoplan) | 2 | 5 | 3 |
| J2778 | Lucentis (ranibizumab) | 2 | 5 | 2 |
| J3490 | Vabysmo (faricimab) | 2 | 5 | 3 |
| J9035 | Avastin (bevacizumab) | 2 | 4 | 1 |

---

## Field Reference

Each rule represents one **payer × drug × diagnosis** combination extracted from a downloaded PDF.

| Field | Type | Description |
|-------|------|-------------|
| `payer_id` | string | Config key for the payer (e.g., `uhc`, `aetna`) |
| `payer_name` | string | Human-readable payer name |
| `drug_code` | string | HCPCS J-code (e.g., `J0178`). `GENERIC` if no specific drug named |
| `drug_name` | string | Brand and generic name, formatted as `Brand (generic)` |
| `procedure_code` | string | CPT `67028` if intravitreal injection is mentioned; empty otherwise |
| `diagnosis_group` | string | `wet_amd`, `dme`, `rvo`, `geographic_atrophy`, or `general_ophthalmology` (fallback) |
| `covered_icd10` | string[] | ICD-10 codes matching the diagnosis group's patterns |
| `pa_required` | bool | `true` if PA language was found (drives `pa_evidence`) |
| `pa_evidence` | string[] | Up to 5 text lines that matched PA patterns |
| `step_therapy_required` | bool | `true` if step therapy language was found |
| `step_therapy_evidence` | string[] | Up to 5 text lines that matched step therapy patterns |
| `required_documentation` | string[] | Up to 10 lines matching documentation patterns (OCT, visual acuity, etc.) |
| `auth_duration_months` | int/null | Authorization validity period in months, if stated |
| `auth_max_injections` | int/null | Max injections per approval period, if stated |
| `denial_triggers` | string[] | Up to 10 lines matching denial patterns |
| `hcpcs_codes_found` | string[] | All J-codes found anywhere in the source document |
| `policy_source_file` | string | Path to the PDF this rule was extracted from |
| `policy_last_downloaded` | string | ISO date of last download |
| `extraction_confidence` | string | See confidence levels below |

**Confidence levels:**
- **high** — 2+ PA pattern matches **and** 1+ step therapy match. Strong, drug-specific language about both PA and step therapy. Safe to build automation rules from.
- **medium** — 1+ PA pattern match, no step therapy match. Document mentions PA requirements but doesn't discuss step therapy. Likely accurate for PA status.
- **low** — Drug mentioned but no PA patterns matched. The rule exists because the document is relevant, but PA status is unconfirmed. Treat as informational only.

Most rules are currently medium or low because the downloaded PDFs are broad PA lists covering hundreds of drugs. Drug-specific clinical policy bulletins (Aetna CPBs, EviCore guidelines) require Playwright and would produce higher-confidence rules.

**Key interactions:**
- `pa_required` is `true` when `pa_evidence` is non-empty — the evidence lines are the proof
- `extraction_confidence` is derived from the count of `pa_evidence` and `step_therapy_evidence` matches
- `diagnosis_group` determines which ICD-10 patterns filter `covered_icd10`; `general_ophthalmology` is the fallback
- `drug_code` is the specific drug for this rule; `hcpcs_codes_found` is every J-code in the whole document
- `auth_duration_months` and `auth_max_injections` are independent limits (whichever comes first)

---

## Rules by Payer

### Aetna Medicare Advantage

#### Eylea (aflibercept) — J0178

- **Diagnosis Group:** general_ophthalmology
- **Status:** **PA Required**
- **Confidence:** medium

**PA Evidence:**
> Precertification is required for the Aetna Medicare
> Precertification required for transportation by T2007, S9960
> 19. Hyperbaric oxygen therapy G0277, 99183 — precertification required for

*Source: `Aetna_2026_Precertification_List.pdf` — Downloaded 2026-03-07*

---

#### Eylea HD (aflibercept 8mg) — J0179

- **Diagnosis Group:** general_ophthalmology
- **Status:** **PA Required**
- **Confidence:** medium

**PA Evidence:**
> Precertification is required for the Aetna Medicare
> Precertification required for transportation by T2007, S9960
> 19. Hyperbaric oxygen therapy G0277, 99183 — precertification required for

*Source: `Aetna_2026_Precertification_List.pdf` — Downloaded 2026-03-07*

---

#### Avastin (bevacizumab) — J9035

- **Diagnosis Group:** general_ophthalmology
- **Status:** **PA Required**
- **Confidence:** medium

**PA Evidence:**
> Precertification is required for the Aetna Medicare
> Precertification required for transportation by T2007, S9960
> 19. Hyperbaric oxygen therapy G0277, 99183 — precertification required for

*Source: `Aetna_2026_Precertification_List.pdf` — Downloaded 2026-03-07*

---

#### Lucentis (ranibizumab) — J2778

- **Diagnosis Group:** general_ophthalmology
- **Status:** **PA Required**
- **Confidence:** medium

**PA Evidence:**
> Precertification is required for the Aetna Medicare
> Precertification required for transportation by T2007, S9960
> 19. Hyperbaric oxygen therapy G0277, 99183 — precertification required for

*Source: `Aetna_2026_Precertification_List.pdf` — Downloaded 2026-03-07*

---

#### Vabysmo (faricimab) — J3490

- **Diagnosis Group:** general_ophthalmology
- **Status:** **PA Required**
- **Confidence:** medium

**PA Evidence:**
> Precertification is required for the Aetna Medicare
> Precertification required for transportation by T2007, S9960
> 19. Hyperbaric oxygen therapy G0277, 99183 — precertification required for

*Source: `Aetna_2026_Precertification_List.pdf` — Downloaded 2026-03-07*

---

#### Syfovre (pegcetacoplan) — J1442

- **Diagnosis Group:** general_ophthalmology
- **Status:** **PA Required**
- **Confidence:** medium

**PA Evidence:**
> Precertification is required for the Aetna Medicare
> Precertification required for transportation by T2007, S9960
> 19. Hyperbaric oxygen therapy G0277, 99183 — precertification required for

*Source: `Aetna_2026_Precertification_List.pdf` — Downloaded 2026-03-07*

---

### UnitedHealthcare Medicare Advantage

#### Eylea (aflibercept) — J0178

- **Diagnosis Group:** general_ophthalmology
- **Status:** No PA | **Step Therapy**
- **Confidence:** low

**Step Therapy Evidence:**
> Preferred Drug List
> The Empire Plan Advanced Flexible Formulary Preferred Drug List is a guide within select therapeutic
> preferred drug alternatives, and a list of excluded drugs along with covered preferred drug alternatives. This

**Required Documentation:**
- letter of medical necessity to CVS Caremark which details the enrollee’s formulary alternative trials and

*Source: `Empire_Plan_Advanced_Flexible_Formulary.pdf` — Downloaded 2026-03-07*

---

#### Avastin (bevacizumab) — J9035

- **Diagnosis Group:** general_ophthalmology
- **Status:** No PA | **Step Therapy**
- **Confidence:** low

**Step Therapy Evidence:**
> Preferred Drug List
> The Empire Plan Advanced Flexible Formulary Preferred Drug List is a guide within select therapeutic
> preferred drug alternatives, and a list of excluded drugs along with covered preferred drug alternatives. This

**Required Documentation:**
- letter of medical necessity to CVS Caremark which details the enrollee’s formulary alternative trials and

*Source: `Empire_Plan_Advanced_Flexible_Formulary.pdf` — Downloaded 2026-03-07*

---

#### Lucentis (ranibizumab) — J2778

- **Diagnosis Group:** general_ophthalmology
- **Status:** No PA | **Step Therapy**
- **Confidence:** low

**Step Therapy Evidence:**
> Preferred Drug List
> The Empire Plan Advanced Flexible Formulary Preferred Drug List is a guide within select therapeutic
> preferred drug alternatives, and a list of excluded drugs along with covered preferred drug alternatives. This

**Required Documentation:**
- letter of medical necessity to CVS Caremark which details the enrollee’s formulary alternative trials and

*Source: `Empire_Plan_Advanced_Flexible_Formulary.pdf` — Downloaded 2026-03-07*

---

#### Eylea (aflibercept) — J0178

- **Diagnosis Group:** general_ophthalmology
- **Status:** No PA | **Step Therapy**
- **Confidence:** low

**Step Therapy Evidence:**
> Preferred Drug List
> The Empire Plan Flexible Formulary Preferred Drug List is a guide within select therapeutic categories for
> prescribed non-preferred (Level 3) drugs along with covered preferred drug alternatives, and a list of

*Source: `Empire_Plan_Flexible_Formulary.pdf` — Downloaded 2026-03-07*

---

#### Avastin (bevacizumab) — J9035

- **Diagnosis Group:** general_ophthalmology
- **Status:** No PA | **Step Therapy**
- **Confidence:** low

**Step Therapy Evidence:**
> Preferred Drug List
> The Empire Plan Flexible Formulary Preferred Drug List is a guide within select therapeutic categories for
> prescribed non-preferred (Level 3) drugs along with covered preferred drug alternatives, and a list of

*Source: `Empire_Plan_Flexible_Formulary.pdf` — Downloaded 2026-03-07*

---

#### Lucentis (ranibizumab) — J2778

- **Diagnosis Group:** general_ophthalmology
- **Status:** No PA | **Step Therapy**
- **Confidence:** low

**Step Therapy Evidence:**
> Preferred Drug List
> The Empire Plan Flexible Formulary Preferred Drug List is a guide within select therapeutic categories for
> prescribed non-preferred (Level 3) drugs along with covered preferred drug alternatives, and a list of

*Source: `Empire_Plan_Flexible_Formulary.pdf` — Downloaded 2026-03-07*

---

#### Eylea (aflibercept) — J0178

- **Diagnosis Group:** wet_amd
- **Status:** No PA | **Step Therapy**
- **Confidence:** low

**Step Therapy Evidence:**
> Medicare Part B Step Therapy Programs
> Medicare Part B Step Therapy Programs Page 1 of 26
> switch to the preferred drug/product upon enrollment. Similarly, an existing UnitedHealthcare plan member with paid

*Source: `Medicare_Part_B_Step_Therapy_Programs.pdf` — Downloaded 2026-03-07*

---

#### Eylea HD (aflibercept 8mg) — J0179

- **Diagnosis Group:** wet_amd
- **Status:** No PA | **Step Therapy**
- **Confidence:** low

**Step Therapy Evidence:**
> Medicare Part B Step Therapy Programs
> Medicare Part B Step Therapy Programs Page 1 of 26
> switch to the preferred drug/product upon enrollment. Similarly, an existing UnitedHealthcare plan member with paid

*Source: `Medicare_Part_B_Step_Therapy_Programs.pdf` — Downloaded 2026-03-07*

---

#### Avastin (bevacizumab) — J9035

- **Diagnosis Group:** wet_amd
- **Status:** No PA | **Step Therapy**
- **Confidence:** low

**Step Therapy Evidence:**
> Medicare Part B Step Therapy Programs
> Medicare Part B Step Therapy Programs Page 1 of 26
> switch to the preferred drug/product upon enrollment. Similarly, an existing UnitedHealthcare plan member with paid

*Source: `Medicare_Part_B_Step_Therapy_Programs.pdf` — Downloaded 2026-03-07*

---

#### Lucentis (ranibizumab) — J2778

- **Diagnosis Group:** wet_amd
- **Status:** No PA | **Step Therapy**
- **Confidence:** low

**Step Therapy Evidence:**
> Medicare Part B Step Therapy Programs
> Medicare Part B Step Therapy Programs Page 1 of 26
> switch to the preferred drug/product upon enrollment. Similarly, an existing UnitedHealthcare plan member with paid

*Source: `Medicare_Part_B_Step_Therapy_Programs.pdf` — Downloaded 2026-03-07*

---

#### Vabysmo (faricimab) — J3490

- **Diagnosis Group:** wet_amd
- **Status:** No PA | **Step Therapy**
- **Confidence:** low

**Step Therapy Evidence:**
> Medicare Part B Step Therapy Programs
> Medicare Part B Step Therapy Programs Page 1 of 26
> switch to the preferred drug/product upon enrollment. Similarly, an existing UnitedHealthcare plan member with paid

*Source: `Medicare_Part_B_Step_Therapy_Programs.pdf` — Downloaded 2026-03-07*

---

#### Syfovre (pegcetacoplan) — J1442

- **Diagnosis Group:** wet_amd
- **Status:** No PA | **Step Therapy**
- **Confidence:** low

**Step Therapy Evidence:**
> Medicare Part B Step Therapy Programs
> Medicare Part B Step Therapy Programs Page 1 of 26
> switch to the preferred drug/product upon enrollment. Similarly, an existing UnitedHealthcare plan member with paid

*Source: `Medicare_Part_B_Step_Therapy_Programs.pdf` — Downloaded 2026-03-07*

---

#### Eylea (aflibercept) — J0178

- **Diagnosis Group:** general_ophthalmology
- **Status:** No PA
- **Confidence:** low

*Source: `UHC_2026_Summary_of_Changes_PA.pdf` — Downloaded 2026-03-07*

---

#### Eylea HD (aflibercept 8mg) — J0179

- **Diagnosis Group:** general_ophthalmology
- **Status:** No PA
- **Confidence:** low

*Source: `UHC_2026_Summary_of_Changes_PA.pdf` — Downloaded 2026-03-07*

---

#### Vabysmo (faricimab) — J3490

- **Diagnosis Group:** general_ophthalmology
- **Status:** No PA
- **Confidence:** low

*Source: `UHC_2026_Summary_of_Changes_PA.pdf` — Downloaded 2026-03-07*

---

#### Syfovre (pegcetacoplan) — J1442

- **Diagnosis Group:** general_ophthalmology
- **Status:** No PA
- **Confidence:** low

*Source: `UHC_2026_Summary_of_Changes_PA.pdf` — Downloaded 2026-03-07*

---

#### Eylea HD (aflibercept 8mg) — J0179

- **Diagnosis Group:** general_ophthalmology
- **Status:** **PA Required**
- **Confidence:** medium
- **Procedure Code:** CPT 67028

**PA Evidence:**
> Prior authorization required. 23470 23472 23473 23474
> Prior authorization required. Prior authorization is required for all states.
> Prior authorization is required for all states. In addition, site of service

*Source: `UHC_Commercial_PA_Requirements_Jan2026.pdf` — Downloaded 2026-03-07*

---

#### Vabysmo (faricimab) — J3490

- **Diagnosis Group:** general_ophthalmology
- **Status:** **PA Required**
- **Confidence:** medium
- **Procedure Code:** CPT 67028

**PA Evidence:**
> Prior authorization required. 23470 23472 23473 23474
> Prior authorization required. Prior authorization is required for all states.
> Prior authorization is required for all states. In addition, site of service

*Source: `UHC_Commercial_PA_Requirements_Jan2026.pdf` — Downloaded 2026-03-07*

---

#### Syfovre (pegcetacoplan) — J1442

- **Diagnosis Group:** general_ophthalmology
- **Status:** **PA Required**
- **Confidence:** medium
- **Procedure Code:** CPT 67028

**PA Evidence:**
> Prior authorization required. 23470 23472 23473 23474
> Prior authorization required. Prior authorization is required for all states.
> Prior authorization is required for all states. In addition, site of service

*Source: `UHC_Commercial_PA_Requirements_Jan2026.pdf` — Downloaded 2026-03-07*

---

#### Eylea (aflibercept) — J0178

- **Diagnosis Group:** general_ophthalmology
- **Status:** **PA Required**
- **Confidence:** medium

**PA Evidence:**
> Erickson Advantage: Prior authorization is required on the following select set of services:
> Cancer supportive Prior Anti-emetics tha t require prior authorization:
> Cancer supportive Bone-modifying agent that requires prior authorization:

*Source: `UHC_Medicare_Advantage_PA_Requirements_Mar2026.pdf` — Downloaded 2026-03-07*

---

#### Eylea HD (aflibercept 8mg) — J0179

- **Diagnosis Group:** general_ophthalmology
- **Status:** **PA Required**
- **Confidence:** medium

**PA Evidence:**
> Erickson Advantage: Prior authorization is required on the following select set of services:
> Cancer supportive Prior Anti-emetics tha t require prior authorization:
> Cancer supportive Bone-modifying agent that requires prior authorization:

*Source: `UHC_Medicare_Advantage_PA_Requirements_Mar2026.pdf` — Downloaded 2026-03-07*

---

#### Lucentis (ranibizumab) — J2778

- **Diagnosis Group:** general_ophthalmology
- **Status:** **PA Required**
- **Confidence:** medium

**PA Evidence:**
> Erickson Advantage: Prior authorization is required on the following select set of services:
> Cancer supportive Prior Anti-emetics tha t require prior authorization:
> Cancer supportive Bone-modifying agent that requires prior authorization:

*Source: `UHC_Medicare_Advantage_PA_Requirements_Mar2026.pdf` — Downloaded 2026-03-07*

---

#### Vabysmo (faricimab) — J3490

- **Diagnosis Group:** general_ophthalmology
- **Status:** **PA Required**
- **Confidence:** medium

**PA Evidence:**
> Erickson Advantage: Prior authorization is required on the following select set of services:
> Cancer supportive Prior Anti-emetics tha t require prior authorization:
> Cancer supportive Bone-modifying agent that requires prior authorization:

*Source: `UHC_Medicare_Advantage_PA_Requirements_Mar2026.pdf` — Downloaded 2026-03-07*

---

#### Syfovre (pegcetacoplan) — J1442

- **Diagnosis Group:** general_ophthalmology
- **Status:** **PA Required**
- **Confidence:** medium

**PA Evidence:**
> Erickson Advantage: Prior authorization is required on the following select set of services:
> Cancer supportive Prior Anti-emetics tha t require prior authorization:
> Cancer supportive Bone-modifying agent that requires prior authorization:

*Source: `UHC_Medicare_Advantage_PA_Requirements_Mar2026.pdf` — Downloaded 2026-03-07*

---

