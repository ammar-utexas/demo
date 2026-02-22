# Platform: Backend/Server

**Tech Stack:** FastAPI, Python 3.12, async SQLAlchemy, asyncpg, Pydantic v2, JWT auth, AES-256 encryption

## Architecture

| Document | Summary |
|----------|---------|
| [ADR-0003: Backend Tech Stack](../architecture/0003-backend-tech-stack.md) | Tech stack selection: FastAPI, async SQLAlchemy, Pydantic v2, JWT, AES encryption |
| [ADR-0002: Multi-Repo Structure](../architecture/0002-multi-repo-structure.md) | Backend as independent repo with own release cycle |

## API & Endpoints

| Document | Summary |
|----------|---------|
| [Backend Endpoints](../api/backend-endpoints.md) | Full REST API reference: auth, patients, encounters, meds, prescriptions, reports, vision |

## Requirements (Backend Platform Reqs)

| Document | BE Reqs | Summary |
|----------|---------|---------|
| [SUB-BE](../specs/requirements/platform/SUB-BE.md) | 47 | All backend platform requirements across 5 domains |

## Features & Implementation

| Document | Summary |
|----------|---------|
| [Initial Project Scaffolds](../features/initial-project-scaffolds.md) | 42-file backend scaffold with stub implementations and passing tests |
| [Vision Capabilities](../features/vision-capabilities.md) | Three AI vision endpoints: MONAI, ArcFace, PaddleOCR |

## Configuration

| Document | Summary |
|----------|---------|
| [Dependencies](../config/dependencies.md) | Python library versions and rationale |
| [Project Setup](../config/project-setup.md) | Backend clone, install, run, and test commands |
| [Feature Flags](../config/feature-flags.md) | Python implementation examples for feature flags |
| [Environments](../config/environments.md) | Backend deployment URLs and environment-specific config |

## Experiments

| Document | Summary |
|----------|---------|
| [OpenClaw Developer Tutorial](../experiments/05-OpenClaw-Developer-Tutorial.md) | Building server-side PMS skills for the OpenClaw agent |
| [OpenClaw Setup Guide](../experiments/05-OpenClaw-PMS-Developer-Setup-Guide.md) | Docker-based agent deployment with backend API integration |
| [OpenClaw PMS Integration PRD](../experiments/05-PRD-OpenClaw-PMS-Integration.md) | Agent skills interacting with backend APIs |
