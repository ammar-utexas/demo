# ADR-0007: Jetson Thor Edge Deployment

**Date:** 2026-02-15
**Status:** Accepted
**Deciders:** Development Team

---

## Context

The Patient Management System requires on-premises deployment for clinical environments where cloud connectivity is unreliable or restricted by HIPAA data-locality policies. Three AI-powered vision capabilities — wound/condition assessment, patient identity verification, and document OCR — must run on-device with sub-second inference latency. All Protected Health Information (PHI) must remain on the local network.

## Decision

Deploy the complete PMS stack (backend, frontend, PostgreSQL) on an **NVIDIA Jetson Thor T5000** development kit connected to a local **Wi-Fi 7** network. Vision inference runs on the Jetson's integrated Blackwell GPU using TensorRT-optimized models.

## Hardware

| Spec | Value |
|---|---|
| SoC | NVIDIA Thor (T5000) |
| CPU | 14-core ARM Neoverse-V3AE |
| GPU | 2560-core Blackwell, FP4/FP8/INT8 |
| Memory | 128 GB LPDDR5X (unified CPU+GPU) |
| Storage | NVMe SSD (user-supplied) |
| Connectivity | Wi-Fi 7 (802.11be), 10GbE, USB-C |

## Software Stack

| Component | Version |
|---|---|
| JetPack | 7.x |
| Ubuntu | 24.04 LTS (ARM64) |
| CUDA | 13.x |
| TensorRT | 10.13 |
| cuDNN | 9.x |
| Container Runtime | NVIDIA Container Toolkit + Docker |

Jetson Thor is SBSA-compliant (Server Base System Architecture), so standard ARM64 NGC containers run without Jetson-specific patches.

## Vision Stack

| Capability | Model / Library | Optimization |
|---|---|---|
| Wound assessment | MONAI (segmentation + classification) | TensorRT FP16/INT8 |
| Patient ID verification | ArcFace (face embedding comparison) | TensorRT FP16 |
| Document OCR | PaddleOCR (detection + recognition) | TensorRT FP16 |

All models are converted to TensorRT engines at deployment time for maximum GPU utilization.

## Network Architecture

```
┌──────────────────────────────────────────────────┐
│                  Jetson Thor                       │
│  ┌─────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │ FastAPI  │  │ Next.js  │  │   PostgreSQL     │ │
│  │ :8000   │←→│ :3000    │  │   :5432          │ │
│  │ + Vision │  └──────────┘  └──────────────────┘ │
│  └─────────┘                                      │
│       ↕ GPU (TensorRT)                            │
└──────────────────────────────────────────────────┘
         ↕ Wi-Fi 7 (802.11be)
┌──────────────────────┐
│   Android App        │
│   (PMS Client)       │
└──────────────────────┘
```

- All traffic stays on the local Wi-Fi 7 network
- No internet dependency for normal operations
- Android app connects to `http://<jetson-ip>:3000` (frontend) and `:8000` (API)

## Rationale

1. **HIPAA PHI containment** — All patient data, images, and inference results stay on the local device. No cloud egress eliminates an entire category of compliance risk.
2. **Sub-second inference** — Blackwell GPU with TensorRT provides <200ms inference for all three vision tasks, well within clinical workflow tolerance.
3. **Unified memory** — 128GB shared between CPU and GPU eliminates PCIe transfer bottlenecks for large medical images.
4. **Standard containers** — SBSA compliance means we use the same ARM64 NGC containers as data center GPUs, simplifying CI/CD.
5. **Wi-Fi 7** — Multi-link operation and 320MHz channels provide reliable, low-latency connectivity for multiple concurrent Android clients.

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| Cloud GPU inference (AWS/GCP) | PHI egress compliance burden, internet dependency, variable latency |
| Jetson Orin (previous gen) | Less GPU compute, non-SBSA (requires Jetson-specific containers) |
| x86 server + discrete GPU | Higher power draw, larger form factor, more complex deployment |
| CPU-only inference | Too slow for real-time clinical workflow (>5s per image) |

## Trade-offs

- **Single point of failure** — One Jetson per clinic site. Mitigation: local PostgreSQL backups, quick replacement SOP.
- **Model updates require on-site deployment** — TensorRT engines are device-specific. Mitigation: automated OTA model update pipeline (future work).
- **Cost** — Jetson Thor dev kit is more expensive than consumer hardware. Justified by GPU capability and NVIDIA enterprise support.

## Consequences

- Backend Docker image must build for ARM64 with CUDA/TensorRT base image
- Vision endpoints are feature-flagged and return stubs until models are deployed
- docker-compose.yml manages the full stack on-device
- Android app must be configurable to point to local Jetson IP
