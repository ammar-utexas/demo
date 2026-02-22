# ADR-0015: Risk Scoring Engine Design

**Date:** 2026-02-21
**Status:** Accepted
**Deciders:** Development Team

---

## Context

The Dermatology CDS module (SUB-PR-0015) must convert raw AI classification probabilities into clinically actionable risk assessments. Raw probability distributions (e.g., "melanoma: 35%, melanocytic nevus: 40%") are not directly useful to primary care clinicians — they need structured outputs: risk level (low/medium/high), referral urgency (routine/expedited/urgent), and contributing factors.

The risk scoring engine must be interpretable (clinicians need to understand why a score was given), configurable (clinical administrators can adjust thresholds), and consistent across server and mobile platforms.

## Options Considered

1. **Configurable threshold-based rules** — Deterministic rules with configurable thresholds for malignant probability, melanoma-specific probability, patient age, and anatomical site.
   - Pros: Fully interpretable, auditable, same logic on server and mobile, easy to adjust thresholds, no training data needed.
   - Cons: Cannot learn complex risk patterns, thresholds are somewhat arbitrary.

2. **ML-based scoring model** — Train a secondary model to predict risk level from classification output + patient features.
   - Pros: Can learn complex nonlinear risk patterns, potentially more accurate.
   - Cons: Requires labeled risk data (doesn't exist yet), black-box (hard to explain to clinicians), additional model to maintain.

3. **Clinical scoring system (e.g., Glasgow 7-point checklist)** — Implement established dermatology scoring rubric.
   - Pros: Evidence-based, clinically validated, familiar to dermatologists.
   - Cons: Requires structured clinical observations (asymmetry, border irregularity) that the AI model doesn't output — only classification probabilities.

4. **No risk scoring** — Return raw classification probabilities only.
   - Pros: Simplest implementation, no threshold decisions.
   - Cons: Clinicians must interpret probability distributions themselves, inconsistent triage decisions, no referral urgency guidance.

## Decision

Use **configurable threshold-based rules** for risk scoring, converting classification probabilities into structured risk levels with referral urgency recommendations.

## Rationale

1. **Full interpretability** — Every risk score comes with a list of contributing factors (e.g., "Malignant probability 65%", "Patient age 72 (elevated risk)", "High-risk site: scalp"). Clinicians understand exactly why a score was assigned.
2. **Auditability** — The rule set is deterministic: given the same inputs and thresholds, the same risk score is always produced. This is critical for medical device regulatory compliance.
3. **Cross-platform consistency** — The same threshold-based logic runs on the server (Python `RiskScorer` class) and Android (Kotlin `RiskScorer`), ensuring offline triage matches server-side scoring.
4. **Configurable thresholds** — Clinical administrators can adjust malignant probability thresholds (default: high ≥ 0.6, medium ≥ 0.3), melanoma sensitivity threshold (default: 0.2), and age risk threshold (default: 60). This supports the ISIC recommendation of high-sensitivity thresholds that over-refer rather than under-refer.
5. **No training data required** — ML-based scoring would require labeled outcomes data (which lesions were actually malignant) that we don't have yet. Rule-based scoring works from day one.
6. **Extensible** — Additional rules can be added (e.g., lesion change detection score from ADR-0019, family history) without retraining a model.

## Scoring Rules

```
Risk Level = HIGH when:
  - Sum of malignant class probabilities ≥ 0.6
  - OR melanoma probability ≥ 0.4

Risk Level = MEDIUM when:
  - Sum of malignant class probabilities ≥ 0.3
  - OR melanoma probability ≥ 0.2
  - OR patient age > 60 AND malignant probability ≥ 0.2
  - OR lesion change score > 0.3 (from longitudinal tracking)

Risk Level = LOW when:
  - None of the above criteria met

Referral Urgency:
  - HIGH risk → Urgent (within 2 weeks)
  - MEDIUM risk → Expedited (within 4 weeks)
  - LOW risk → Routine (next scheduled visit)

Malignant Classes:
  - melanoma, basal_cell_carcinoma, squamous_cell_carcinoma, actinic_keratosis

High-Risk Anatomical Sites:
  - scalp, back, trunk, lower_extremity, upper_extremity
```

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| ML-based scoring model | Requires labeled outcome data we don't have, black-box scoring unacceptable for clinical use |
| Glasgow 7-point checklist | Requires structured clinical observations the AI model doesn't output |
| Raw probabilities only | Clinicians must interpret distributions themselves, inconsistent triage |
| ABCDE criteria integration | Requires image segmentation model for asymmetry/border analysis, not available in current pipeline |

## Trade-offs

- **Threshold sensitivity** — Fixed thresholds may not account for all clinical nuances. Mitigation: thresholds are configurable per deployment, and the system explicitly states "Clinical Decision Support Only — does not replace clinical judgment."
- **No learning from outcomes** — Rule-based scoring doesn't improve from outcome data. If outcome labels become available in the future, an ML-based scorer can be added as an alternative scoring strategy.
- **Over-referral bias** — The default thresholds are intentionally set to over-refer rather than under-refer (high melanoma sensitivity). This is by design — missing a melanoma is worse than an unnecessary referral.

## Consequences

- `risk_scorer.py` in the CDS service implements the `RiskScorer` class with configurable thresholds.
- `RiskScorer.kt` on Android implements identical logic for offline triage.
- Risk scoring thresholds are loaded from environment variables or a configuration file.
- Every `lesion_classifications` row stores `risk_level`, `risk_factors` (JSONB), and `referral_urgency`.
- The frontend displays risk assessment as a color-coded banner (red/yellow/green) with contributing factors listed.
- Clinical disclaimer is always displayed alongside risk scores.
- Reporting dashboard (SUB-RA-0008) tracks risk level distribution and referral urgency trends over time.

## References

- Related PRD: docs/experiments/18-PRD-ISICArchive-PMS-Integration.md (Section 5.4)
- Related Requirements: SYS-REQ-0012, SUB-PR-0015, SUB-PR-0015-BE, SUB-PR-0015-WEB
- Related ADRs: ADR-0008 (CDS Microservice), ADR-0012 (Android On-Device Inference), ADR-0019 (Lesion Longitudinal Tracking), ADR-0020 (Feature Flags)
