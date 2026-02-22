# ADR-0013: AI Model Lifecycle Management

**Date:** 2026-02-21
**Status:** Accepted
**Deciders:** Development Team

---

## Context

The Dermatology CDS module (SYS-REQ-0012) relies on deep learning models that are updated annually as the ISIC Challenge produces improved classification architectures. Each model version produces different classification outputs, and clinical decisions (risk scores, referrals) made using one model version must be traceable back to the exact model that generated them for reproducibility and liability.

The system deploys models across three runtimes (ADR-0009): ONNX Runtime (server), TensorRT (Jetson), and TFLite (Android). Model updates must be coordinated across all platforms while maintaining backward compatibility with existing classification records.

## Options Considered

1. **Versioned model artifacts with provenance tracking** — Store model versions in a structured directory with metadata files, track which version produced each classification.
   - Pros: Full traceability, simple to implement, works with existing Docker volume infrastructure, supports rollback.
   - Cons: Manual version management, no built-in experiment tracking.

2. **MLflow Model Registry** — Use MLflow for model versioning, staging, and deployment.
   - Pros: Industry-standard experiment tracking, model staging (staging → production), REST API for model retrieval.
   - Cons: Additional infrastructure (MLflow server + database), overkill for our single-model use case, deployment complexity on Jetson.

3. **DVC (Data Version Control)** — Git-based model versioning with DVC.
   - Pros: Git-native workflow, S3/GCS backend support.
   - Cons: Requires external storage backend, adds complexity to CI pipeline, not designed for deployment.

4. **Docker image tagging** — Bundle model weights into the Docker image, version via image tags.
   - Pros: Immutable deployments, simple rollback (pull previous tag).
   - Cons: 2 GB+ image rebuilds for every model change, can't update model without redeploying the entire service code.

## Decision

Use **versioned model artifacts with provenance tracking** — a structured model directory with JSON manifest files, stored in Docker volumes, with every classification record referencing the exact model version that produced it.

## Rationale

1. **Traceability** — Every `lesion_classifications` row records `model_name` and `model_version`, enabling auditors and clinicians to trace any classification back to the exact model checkpoint. This is critical for medical device liability.
2. **Simplicity** — A JSON manifest file per model version (`model-manifest.json`) captures: model name, version, training dataset, export date, accuracy metrics, SHA-256 checksum. No external infrastructure required.
3. **Multi-format export** — The manifest tracks all three exported formats (ONNX, TensorRT, TFLite) for a single model version, ensuring consistency across platforms.
4. **Rollback capability** — Previous model versions are retained in the volume. Rollback is a manifest pointer change + service restart. No image rebuild needed.
5. **Volume-based storage** — Model weights live in Docker volumes (`derm-models`), separate from the service code image. Model updates don't require rebuilding the application container.
6. **Annual cadence** — With one model update per year (post-ISIC Challenge), a full MLflow registry is unjustified overhead.

## Model Manifest Format

```json
{
  "model_name": "efficientnet_b4_isic",
  "version": "2024-v1",
  "training_dataset": "ISIC 2024 Challenge (401,059 images)",
  "export_date": "2026-02-21",
  "source_framework": "PyTorch 2.5.1",
  "formats": {
    "onnx": {
      "path": "efficientnet_b4_isic_2024v1.onnx",
      "sha256": "abc123...",
      "input_shape": [1, 3, 380, 380],
      "output_classes": 9
    },
    "tensorrt": {
      "path": "efficientnet_b4_isic_2024v1.engine",
      "precision": "FP16",
      "target_device": "Jetson Thor"
    },
    "tflite": {
      "path": "mobilenetv3_isic_2024v1_int8.tflite",
      "quantization": "INT8",
      "input_shape": [1, 3, 224, 224]
    }
  },
  "accuracy": {
    "top1": 0.883,
    "top3": 0.962,
    "melanoma_sensitivity": 0.951
  },
  "previous_version": "2023-v1"
}
```

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| MLflow Model Registry | Additional infrastructure, overkill for single-model annual update cadence |
| DVC | External storage backend required, designed for experiment tracking not deployment |
| Docker image tagging | 2 GB rebuilds per model change, couples model updates with code deployments |
| No versioning | Unacceptable for medical device traceability — cannot audit which model made a classification |

## Trade-offs

- **Manual process** — Model updates are manual (download new weights, update manifest, restart service). Acceptable for annual cadence. If update frequency increases, automate with a CI pipeline.
- **No A/B testing** — The system runs one active model version at a time. Parallel model evaluation requires manual shadow deployment.
- **Storage growth** — Each model version retains previous versions (~500 MB per ONNX model). Mitigation: keep only 2 most recent versions, archive older versions to cold storage.

## Consequences

- The `derm-models` Docker volume contains a `model-manifest.json` and versioned model files.
- The CDS service loads the model specified in the manifest at startup and logs the version.
- Every row in `lesion_classifications` records `model_name` and `model_version`.
- Model update SOP: download new weights → update manifest → restart CDS container → verify with test classification.
- Android model updates are distributed via APK updates or a background model download service.
- The ISIC reference cache (ADR-0017) is coupled to model version — embeddings must be recomputed when the model changes.

## References

- Related PRD: docs/experiments/18-PRD-ISICArchive-PMS-Integration.md (Section 6.1, model provenance)
- Related Requirements: SYS-REQ-0012
- Related ADRs: ADR-0009 (AI Inference Runtime), ADR-0012 (Android On-Device Inference), ADR-0017 (ISIC Reference Cache)
