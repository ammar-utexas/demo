# Platform: Jetson/Edge

**Tech Stack:** NVIDIA Jetson Thor, JetPack 7.x, TensorRT, Docker, Wi-Fi 7, on-device AI inference

## Architecture

| Document | Summary |
|----------|---------|
| [ADR-0007: Jetson Edge Deployment](../architecture/0007-jetson-thor-edge-deployment.md) | Full PMS stack on Jetson Thor with TensorRT-optimized models, local Wi-Fi 7 |

## AI Inference

| Document | Summary |
|----------|---------|
| [Vision Capabilities](../features/vision-capabilities.md) | MONAI (wound), ArcFace (patient ID), PaddleOCR (documents) — TensorRT-optimized |
| [SUB-AI](../specs/requirements/platform/SUB-AI.md) | All AI infrastructure platform requirements across 2 domains (6 reqs) |

## Deployment & Configuration

| Document | Summary |
|----------|---------|
| [Jetson Deployment Guide](../config/jetson-deployment.md) | JetPack 7.x flashing, docker-compose deployment, Wi-Fi 7 config, GPU resource allocation |
| [Environments](../config/environments.md) | Jetson Thor edge environment definition and policies |
