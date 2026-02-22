# ADR-0012: Android On-Device Inference

**Date:** 2026-02-21
**Status:** Accepted
**Deciders:** Development Team

---

## Context

The PMS Android app (ADR-0005) must support offline skin lesion triage for clinicians who may be away from the clinic network (e.g., home visits, rural clinics without reliable Wi-Fi). When the `pms-derm-cds` server is unreachable, the Android app should still provide a preliminary classification to guide whether a patient needs urgent referral.

SUB-PR-0013-AND requires camera capture for dermoscopic images with on-device TFLite classification using MobileNetV3 for offline skin lesion triage, with results synced to the backend when connectivity is available.

The Android app targets devices with 4-8 GB RAM, ARMv8 CPUs, and no dedicated ML accelerator. APK size must remain reasonable (<100 MB total).

## Options Considered

1. **TFLite with MobileNetV3** — TensorFlow Lite runtime with a quantized MobileNetV3 model (~15 MB).
   - Pros: Smallest model size, fastest inference on ARM, NNAPI delegate for hardware acceleration, battle-tested on Android, <3s inference on mid-range devices.
   - Cons: Lower accuracy than EfficientNet-B4 (top-1 ~78% vs ~88%), limited to 9-class classification (no embedding extraction for similarity search).

2. **ONNX Runtime Mobile** — ONNX Runtime for Android with EfficientNet-B4.
   - Pros: Same model format as server, higher accuracy, embedding extraction possible.
   - Cons: ~30 MB runtime + ~80 MB model = 110 MB added to APK, 6-8s inference on CPU, no NNAPI delegate.

3. **PyTorch Mobile / ExecuTorch** — PyTorch's mobile runtime.
   - Pros: Same training framework, active Meta development.
   - Cons: ExecuTorch is early-stage, PyTorch Mobile deprecated, limited Android optimization.

4. **MediaPipe** — Google's ML framework with pre-built image classification pipeline.
   - Pros: Easy integration, pre-built camera pipeline, GPU delegate.
   - Cons: Limited to MediaPipe-compatible model formats, no custom 9-class ISIC classifier support out of the box.

## Decision

Use **TensorFlow Lite with a quantized MobileNetV3** model for on-device inference on Android, providing offline skin lesion triage with sync-to-backend when connectivity returns.

## Rationale

1. **Model size** — INT8-quantized MobileNetV3 is ~15 MB, keeping the APK size impact minimal. EfficientNet-B4 via ONNX Runtime would add 110 MB.
2. **Inference speed** — MobileNetV3 on TFLite achieves <3s classification on mid-range Android devices, meeting the clinical workflow target. ONNX Runtime would be 6-8s.
3. **NNAPI delegation** — TFLite's NNAPI delegate transparently uses hardware accelerators (Qualcomm Hexagon DSP, Samsung NPU) when available, further reducing latency.
4. **Offline-first design** — The TFLite model runs entirely on-device with no network dependency. Classification results are stored in Room database and synced to the backend (`/api/lesions/upload`) when connectivity is restored.
5. **Triage, not diagnosis** — On-device inference is explicitly a triage tool (high/medium/low urgency), not a diagnostic tool. Lower accuracy is acceptable because the result is always re-classified by the server-side EfficientNet-B4 upon sync.
6. **Camera integration** — TFLite integrates with CameraX via the CameraSessionManager singleton (SUB-PR-0012) for consistent camera lifecycle management alongside wound assessment and patient ID verification.

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| ONNX Runtime Mobile | 110 MB size impact, 6-8s inference, no NNAPI delegate |
| PyTorch Mobile / ExecuTorch | Deprecated / early-stage, limited Android optimization |
| MediaPipe | No support for custom 9-class ISIC classifier |
| Server-only inference | No offline capability, fails requirement for disconnected workflows |

## Trade-offs

- **Accuracy gap** — MobileNetV3 achieves ~78% top-1 accuracy vs ~88% for server-side EfficientNet-B4. Mitigated by: on-device results are clearly labeled as "preliminary triage", and full classification runs on backend upon sync.
- **No similarity search offline** — Embedding extraction and pgvector search require the server. On-device mode only provides classification and risk level, not similar reference images.
- **Model update distribution** — TFLite model updates require an APK update or dynamic download. ADR-0013 covers the model update pipeline for Android.
- **Battery consumption** — ML inference is CPU/GPU intensive. A single classification uses ~2% battery on a typical device. Mitigated by running inference only on explicit user action (capture button), not continuously.

## Consequences

- The Android APK bundles `mobilenetv3_isic_int8.tflite` (~15 MB) in the `assets/models/` directory.
- `LesionClassifier.kt` wraps the TFLite interpreter with preprocessing (resize to 224x224, normalize) and postprocessing (softmax, risk scoring).
- Classification results are persisted to Room database with `synced = false` and uploaded to `/api/lesions/upload` when connectivity is detected.
- On-device results include a `source: "on_device"` field to distinguish from server classifications.
- The camera capture flow goes through `CameraSessionManager` (SUB-PR-0012) to avoid conflicts with wound assessment and patient ID verification.
- The risk scoring engine (ADR-0015) runs on-device with the same threshold configuration as the server.

## References

- Related PRD: docs/experiments/18-PRD-ISICArchive-PMS-Integration.md (Section 3.2, 6.3)
- Related Requirements: SYS-REQ-0012, SUB-PR-0013-AND, SUB-PR-0012
- Related ADRs: ADR-0005 (Android Tech Stack), ADR-0009 (AI Inference Runtime), ADR-0013 (AI Model Lifecycle), ADR-0015 (Risk Scoring Engine)
