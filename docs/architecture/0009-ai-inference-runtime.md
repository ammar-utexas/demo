# ADR-0009: AI Inference Runtime Selection

**Date:** 2026-02-21
**Status:** Accepted
**Deciders:** Development Team

---

## Context

The Dermatology CDS module (SYS-REQ-0012) must run deep learning inference for skin lesion classification across three deployment targets with vastly different hardware capabilities:

1. **Server/Docker** — The `pms-derm-cds` container on x86_64 Linux with optional NVIDIA GPU.
2. **Jetson Thor edge device** — ARM64 with integrated Blackwell GPU (ADR-0007).
3. **Android mobile** — ARM64 CPU with limited memory and no GPU access for ML.

Each target has different hardware constraints, model format requirements, and latency expectations. The primary model is EfficientNet-B4 (21M parameters, 380x380 input) for server/edge, and MobileNetV3 (~5M parameters, 224x224 input) for mobile.

## Options Considered

1. **ONNX Runtime (server) + TensorRT (Jetson) + TFLite (Android)** — Platform-optimized runtimes for each target.
   - Pros: Best performance per platform, mature ecosystem, all support the same source model (PyTorch → export to each format).
   - Cons: Three export pipelines to maintain, runtime-specific quirks.

2. **PyTorch everywhere** — Use PyTorch for server/Jetson, PyTorch Mobile for Android.
   - Pros: Single framework, consistent behavior.
   - Cons: PyTorch Mobile is deprecated in favor of ExecuTorch, no TensorRT integration on Jetson, Android APK size ~100 MB.

3. **TensorFlow everywhere** — TF Serving for server, TF-TRT for Jetson, TFLite for Android.
   - Pros: Single ecosystem with cross-platform export.
   - Cons: Model is trained in PyTorch (ISIC Challenge standard), TF conversion adds a lossy step, TF Serving is heavier than ONNX Runtime.

4. **ONNX Runtime everywhere** — ONNX Runtime for server, ONNX Runtime Mobile for Android, ONNX Runtime with TensorRT EP for Jetson.
   - Pros: Single runtime, single model format.
   - Cons: ONNX Runtime Mobile produces larger APKs (~30 MB) than TFLite (~15 MB), TensorRT EP doesn't match native TensorRT performance on Jetson.

## Decision

Use **ONNX Runtime** for server deployment, **TensorRT** for Jetson Thor edge, and **TensorFlow Lite** for Android on-device inference, with a single PyTorch source model exported to each format.

## Rationale

1. **ONNX Runtime for server** — Supports both CPU and CUDA execution providers, enabling GPU-accelerated inference where available with automatic CPU fallback. ONNX is the export format of choice for ISIC Challenge models (PyTorch → ONNX is a single `torch.onnx.export` call).
2. **TensorRT for Jetson** — Native NVIDIA runtime with FP16/INT8 quantization yields <200ms inference on Jetson Thor's Blackwell GPU, meeting the clinical latency target. TensorRT engines are compiled on-device for maximum optimization.
3. **TFLite for Android** — TFLite quantized models are ~15 MB (vs ~30 MB for ONNX Runtime Mobile), critical for APK size constraints. TFLite delegate for Android NNAPI enables hardware acceleration on supported devices. The MobileNetV3 architecture is specifically designed for TFLite efficiency.
4. **Single source model** — All three formats are exported from the same PyTorch checkpoint, ensuring classification consistency across platforms. Export pipeline: `PyTorch → ONNX → (TensorRT | TFLite via tf2onnx inverse or direct PyTorch → TFLite)`.
5. **Ecosystem maturity** — Each runtime is the market leader for its platform. ONNX Runtime has 13K+ GitHub stars, TensorRT is the standard for NVIDIA edge, TFLite powers billions of on-device inferences.

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| PyTorch everywhere | PyTorch Mobile deprecated, no TensorRT on Jetson, 100 MB APK size |
| TensorFlow everywhere | ISIC models are PyTorch-native, TF conversion adds lossy step |
| ONNX Runtime everywhere | ONNX Runtime Mobile produces larger APKs, TensorRT EP doesn't match native TensorRT |
| ExecuTorch for Android | Too new (2024), limited model support, not production-hardened |

## Trade-offs

- **Three export pipelines** — Maintaining ONNX, TensorRT, and TFLite exports adds CI complexity. Mitigated by model lifecycle management (ADR-0013) that automates export on model version change.
- **Numerical precision differences** — TensorRT FP16 and TFLite INT8 quantization may produce slightly different probabilities than ONNX FP32. Acceptable: differences are <1% and clinical thresholds (ADR-0015) absorb this variance.
- **Android offline inference** — TFLite model (MobileNetV3) has lower accuracy than server model (EfficientNet-B4). This is by design: on-device inference is for triage, not final diagnosis.

## Consequences

- The `pms-derm-cds` Docker service includes `onnxruntime` with CUDA execution provider.
- Jetson deployment converts ONNX models to TensorRT engines at deployment time via `trtexec`.
- Android app bundles a ~15 MB TFLite model in the APK assets directory.
- Model export scripts in the CI pipeline produce all three formats from a single PyTorch checkpoint.
- Classification results include `model_name` and `model_version` fields to track which runtime produced each result (ADR-0013).

## References

- Related PRD: docs/experiments/18-PRD-ISICArchive-PMS-Integration.md
- Related Requirements: SYS-REQ-0012, SUB-PR-0013, SUB-PR-0013-AI, SUB-PR-0013-AND
- Related ADRs: ADR-0007 (Jetson Edge Deployment), ADR-0008 (CDS Microservice Architecture), ADR-0012 (Android On-Device Inference), ADR-0013 (AI Model Lifecycle)
