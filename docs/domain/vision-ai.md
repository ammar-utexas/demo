# Domain: Vision & AI

Computer vision capabilities including wound assessment, patient identification, and document OCR — deployed on edge hardware with TensorRT optimization.

## Requirements

| Document | Summary |
|----------|---------|
| [SUB-PR](../specs/requirements/SUB-PR.md) | 3 AI platform requirements for vision endpoints (wound assessment, patient ID, document OCR) |
| [SYS-REQ](../specs/requirements/SYS-REQ.md) | System-level requirements governing AI inference performance |

## Implementation

| Document | Summary |
|----------|---------|
| [Vision Capabilities](../features/vision-capabilities.md) | Three AI vision endpoints: MONAI (wound), ArcFace (patient ID), PaddleOCR (documents) with feature flags |
| [Backend Endpoints](../api/backend-endpoints.md) | Vision API endpoint specifications and request/response schemas |

## Edge Deployment

| Document | Summary |
|----------|---------|
| [ADR-0007: Jetson Edge Deployment](../architecture/0007-jetson-thor-edge-deployment.md) | TensorRT-optimized vision models on NVIDIA Jetson Thor |
| [Jetson Deployment Guide](../config/jetson-deployment.md) | GPU resource allocation for AI inference workloads |
