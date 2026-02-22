# ADR-0019: Lesion Longitudinal Tracking

**Date:** 2026-02-21
**Status:** Accepted
**Deciders:** Development Team

---

## Context

Patients with multiple moles or prior skin cancer history require longitudinal monitoring of skin lesions over time (SUB-PR-0016). A lesion photographed during one encounter must be compared against prior photographs of the same lesion to detect changes in size, shape, color, and morphology. These changes are among the strongest indicators of malignant transformation.

The challenge is establishing **persistent lesion identity** — linking a dermoscopic image captured today to images of the same lesion from previous encounters — and **quantifying change** in a way that is clinically meaningful.

## Options Considered

1. **Persistent lesion identity with change detection via embedding cosine distance** — Assign each lesion a persistent ID linked to patient + anatomical site, compute change scores by comparing current and prior image embeddings.
   - Pros: Quantitative change metric, leverages existing embedding infrastructure (ADR-0011), works across model versions with normalization, no image registration needed.
   - Cons: Cosine distance measures overall visual similarity, not specific clinical features (border irregularity, color distribution).

2. **Pixel-level image registration and differencing** — Align current and prior images using geometric registration, compute pixel-level differences.
   - Pros: Precise spatial change detection, highlights specific regions of change.
   - Cons: Extremely sensitive to camera angle, zoom, lighting; requires advanced image registration; brittle with different cameras or conditions.

3. **Separate change detection model** — Train a dedicated model to compare pairs of dermoscopic images and output a change score.
   - Pros: Learns clinically relevant change patterns, potentially more accurate than cosine distance.
   - Cons: Requires paired training data (same lesion over time, annotated), which is very rare in public datasets; additional model to maintain.

4. **Manual clinician comparison** — Show prior and current images side-by-side, let clinicians assess change subjectively.
   - Pros: No algorithm needed, leverages clinical expertise.
   - Cons: Subjective, inconsistent between clinicians, doesn't scale, misses subtle changes.

## Decision

Use **persistent lesion identity** (patient + anatomical site + lesion index) with **change detection via embedding cosine distance**, supplemented by side-by-side visual comparison in the UI.

## Rationale

1. **Quantitative change metric** — Cosine distance between the current embedding and the most recent prior embedding provides a 0-1 change score. Higher scores indicate greater visual change, which correlates with clinical significance.
2. **Leverages existing infrastructure** — Image embeddings are already generated for similarity search (ADR-0011). Longitudinal tracking reuses the same embedding pipeline with zero additional model cost.
3. **Persistent lesion identity** — A lesion is identified by `(patient_id, anatomical_site, lesion_index)`. When a clinician captures an image at the same anatomical site, the system proposes matching it to an existing lesion or creating a new one.
4. **Robust to imaging variation** — Unlike pixel-level differencing, embedding cosine distance is robust to minor changes in camera angle, zoom, and lighting because the CNN model learns translation/scale-invariant features.
5. **Change threshold integration** — The change score feeds into the risk scoring engine (ADR-0015) as an additional factor. A lesion with change_score > 0.3 elevates the risk level by one tier.
6. **Visual timeline** — In addition to the computed change score, the frontend displays a chronological timeline of lesion images (SUB-PR-0016-WEB), enabling clinicians to visually compare lesions over time.

## Lesion Identity Model

```
lesion_records
┌──────────────────────────────────────────────────┐
│ id (UUID)                                         │
│ patient_id (UUID) ─── links to patients table     │
│ anatomical_site (VARCHAR) ─── e.g., "back_upper"  │
│ lesion_index (INT) ─── nth lesion at this site    │
│ created_at (TIMESTAMPTZ)                          │
│ status (VARCHAR) ─── active / resolved / excised  │
└──────────────────────────────────────────────────┘
         │ 1:N
         ▼
lesion_images + patient_lesion_embeddings
┌──────────────────────────────────────────────────┐
│ lesion_record_id (UUID) ─── links to lesion       │
│ image_data (BYTEA, encrypted)                     │
│ embedding (vector(512))                           │
│ captured_at (TIMESTAMPTZ)                         │
│ change_score (FLOAT) ─── vs prior embedding       │
└──────────────────────────────────────────────────┘

Change Score Computation:
  change_score = 1 - cosine_similarity(current_embedding, prior_embedding)
  Range: 0.0 (identical) to 2.0 (opposite), typically 0.0 - 0.5
  Threshold: > 0.3 → "significant change detected"
```

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| Pixel-level image registration | Brittle with camera variation, requires advanced registration algorithms, sensitive to lighting |
| Dedicated change detection model | Requires paired temporal training data that doesn't exist in public datasets |
| Manual clinician comparison only | Subjective, inconsistent, doesn't scale, misses subtle changes |
| No longitudinal tracking | Fails SUB-PR-0016, misses a key clinical value proposition |

## Trade-offs

- **Cosine distance limitations** — Measures overall visual similarity, not specific clinical features. A lesion that changes color but not shape may have a lower change score than one that changes angle but not morphology. Mitigated by combining with visual side-by-side comparison.
- **Lesion identity assignment** — Matching a new image to an existing lesion relies on the clinician selecting the correct anatomical site and lesion index. If misassigned, change detection is meaningless. Mitigated by showing thumbnails of existing lesions at the selected site for confirmation.
- **Cross-model change scores** — If the classification model changes (ADR-0013), prior embeddings were generated by a different model. Change scores across model versions are not directly comparable. Mitigated by flagging cross-version comparisons and optionally recomputing prior embeddings with the new model.

## Consequences

- A new `lesion_records` table establishes persistent lesion identity (patient + site + index).
- The `lesion_images` table gains a `lesion_record_id` foreign key linking images to persistent lesions.
- The `patient_lesion_embeddings` table stores per-image embeddings with `change_score` computed on insertion.
- The CDS service computes change_score by fetching the most recent prior embedding for the same lesion_record_id.
- The risk scoring engine (ADR-0015) incorporates change_score > 0.3 as a risk factor.
- The frontend Lesion Timeline component (SUB-PR-0016-WEB) displays chronological images with change scores.
- Cross-model-version comparisons are flagged with a warning in the UI.
- The lesion history API (`/api/lesions/history/{patient_id}`) returns timeline data with change scores.

## References

- Related PRD: docs/experiments/18-PRD-ISICArchive-PMS-Integration.md (Section 5.6)
- Related Requirements: SYS-REQ-0012, SUB-PR-0016, SUB-PR-0016-BE, SUB-PR-0016-WEB
- Related ADRs: ADR-0011 (Vector Database), ADR-0013 (AI Model Lifecycle), ADR-0015 (Risk Scoring Engine)
