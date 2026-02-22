# ADR-0014: Image Preprocessing & Quality Validation

**Date:** 2026-02-21
**Status:** Accepted
**Deciders:** Development Team

---

## Context

The Dermatology CDS module accepts dermoscopic images from multiple sources: the Next.js frontend (file upload), the Android app (camera capture), and potentially USB dermoscopes. Image quality varies significantly — clinicians may upload blurry photos, poorly lit images, or non-dermoscopic photographs (e.g., screenshots, document scans). Poor image quality degrades classification accuracy and produces unreliable risk scores.

The classification model (EfficientNet-B4) expects a specific input format: 380x380 pixel RGB tensor, normalized with ImageNet mean/std. The embedding model for similarity search uses the same preprocessing. Consistent preprocessing is critical for reproducible results across platforms.

## Options Considered

1. **Resize/normalize pipeline with blur/exposure quality gates** — A multi-stage pipeline that validates image quality, then preprocesses for model input.
   - Pros: Catches bad images before wasting inference compute, consistent preprocessing, quality feedback to clinicians.
   - Cons: Quality gates may reject valid images, adds latency.

2. **Preprocessing only (no quality gates)** — Resize and normalize all uploaded images without quality checks.
   - Pros: Simpler pipeline, no false rejections.
   - Cons: Garbage-in-garbage-out; blurry or non-dermoscopic images produce misleading classifications with high confidence.

3. **AI-based quality assessment** — Train a separate model to assess dermoscopic image quality.
   - Pros: More sophisticated quality detection, can learn domain-specific quality criteria.
   - Cons: Additional model to maintain, additional inference latency, training data for quality assessment not readily available.

## Decision

Implement a **multi-stage image preprocessing pipeline** with configurable quality gates (blur detection, exposure assessment, resolution check) followed by deterministic resize/normalize for model input.

## Rationale

1. **Patient safety** — An AI classification of a blurry or overexposed image is clinically meaningless and could lead to false reassurance (low risk score on an actually malignant lesion). Quality gates prevent this.
2. **Clinician feedback** — When an image is rejected, the system provides actionable feedback ("Image too blurry — hold the dermoscope steady and recapture") rather than returning unreliable results.
3. **Deterministic preprocessing** — The same resize/normalize pipeline runs on server (Python/Pillow/torchvision), Jetson (same Python stack), and Android (TFLite preprocessing), ensuring the same image produces the same tensor regardless of platform.
4. **Configurable thresholds** — Quality gate thresholds are configurable per deployment to account for different camera hardware and clinical environments.
5. **Lightweight checks** — Blur detection (Laplacian variance), exposure assessment (histogram analysis), and resolution check are all <10ms operations, adding negligible latency to the pipeline.

## Pipeline Stages

```
Input Image (JPEG/PNG)
    │
    ▼
┌─────────────────────────────┐
│ 1. Format Validation        │  Verify JPEG/PNG, reject corrupted files
│    - MIME type check        │  Reject non-image files
│    - Pillow.open() verify   │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ 2. Resolution Check         │  Minimum 224x224 pixels
│    - Reject if too small    │  Warn if < 380x380 (model input size)
│    - Cap at 4096x4096       │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ 3. Blur Detection           │  Laplacian variance < threshold → reject
│    - cv2.Laplacian()        │  Default threshold: 100.0
│    - Variance of Laplacian  │  Configurable per deployment
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ 4. Exposure Assessment      │  Histogram analysis
│    - Underexposed: mean < 40│  Overexposed: mean > 220
│    - Warn (don't reject)    │  Clinician sees quality warning
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ 5. Resize & Center Crop     │  Resize to 380x380 (server)
│    - Maintain aspect ratio  │  or 224x224 (Android/TFLite)
│    - Center crop to square  │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ 6. Normalize                │  ImageNet normalization
│    - mean=[0.485,0.456,0.406]│ std=[0.229,0.224,0.225]
│    - Convert to float32     │  Output: [1, 3, H, W] tensor
└─────────────────────────────┘
    │
    ▼
Model Input Tensor
```

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| No quality gates | Blurry/bad images produce misleading classifications, patient safety risk |
| AI-based quality model | Additional model to train/maintain, quality training data unavailable, added latency |
| Client-side only validation | Inconsistent across platforms, can be bypassed, server must be authoritative |
| Reject on exposure issues | Too aggressive; slightly over/underexposed images can still produce valid classifications |

## Trade-offs

- **False rejections** — Quality gates may reject valid but unusual images (e.g., heavily pigmented lesions appear dark). Mitigation: exposure check issues a warning rather than a rejection; blur threshold is configurable.
- **Additional latency** — Quality checks add ~15ms total. Acceptable given the 5s total pipeline budget.
- **Platform consistency** — Android preprocessing must exactly match server preprocessing. Any divergence causes the same image to produce different classification results. Mitigated by shared test images validated across platforms.

## Consequences

- The CDS service includes a `preprocessing.py` module implementing all pipeline stages.
- Quality check results are included in the API response: `{"quality": {"blur_score": 450.2, "exposure": "normal", "resolution": "adequate"}}`.
- Rejected images return HTTP 422 with specific quality feedback (e.g., `{"detail": "Image too blurry (score: 45.3, threshold: 100.0). Please recapture with steady hold."}`).
- The Android app implements the same preprocessing pipeline in Kotlin (using Android Bitmap operations and TFLite's `ImageProcessor`).
- Quality thresholds are configurable via environment variables (`BLUR_THRESHOLD`, `MIN_RESOLUTION`).
- Exposure warnings are logged but do not block classification — they appear as advisories in the UI.

## References

- Related PRD: docs/experiments/18-PRD-ISICArchive-PMS-Integration.md (Section 9, image quality risk)
- Related Requirements: SYS-REQ-0012, SUB-PR-0013
- Related ADRs: ADR-0008 (CDS Microservice), ADR-0009 (AI Inference Runtime), ADR-0012 (Android On-Device Inference)
