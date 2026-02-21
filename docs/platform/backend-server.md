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
| [SUB-PR-BE](../specs/requirements/platform/SUB-PR-BE.md) | 15 | Patient CRUD, encryption, audit, search, pagination, lesion endpoints |
| [SUB-CW-BE](../specs/requirements/platform/SUB-CW-BE.md) | 8 | Encounter lifecycle, auth, RBAC, alerts, audit |
| [SUB-MM-BE](../specs/requirements/platform/SUB-MM-BE.md) | 9 | Drug interactions, encryption, FHIR, RBAC, refill tracking |
| [SUB-RA-BE](../specs/requirements/platform/SUB-RA-BE.md) | 8 | Dashboard data, audit log queries, CSV export, derm analytics |

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
