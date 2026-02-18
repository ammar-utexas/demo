# Domain: Property Management

Core clinical and patient management functionality — the primary business domain of the PMS system. Covers patient records, clinical workflows, medication management, and reporting/analytics.

## System-Level

| Document | Summary |
|----------|---------|
| [System Spec](../specs/system-spec.md) | System scope, subsystem decomposition, user roles, regulatory constraints |
| [System Requirements (SYS-REQ)](../specs/requirements/SYS-REQ.md) | 10 system-level requirements with acceptance criteria and status |
| [Requirements Governance](../specs/requirements-governance.md) | Governance procedures, conflict analysis (11 intra-domain, 9 cross-platform) |
| [Subsystem Versions](../specs/subsystem-versions.md) | Per-subsystem version tracking and platform progress |

## Subsystem Requirements

| Document | Subsystem | Domain Reqs | Platform Reqs |
|----------|-----------|-------------|---------------|
| [SUB-PR](../specs/requirements/SUB-PR.md) | Patient Records | 11 | 25 (BE=11, WEB=4, AND=7, AI=3) |
| [SUB-CW](../specs/requirements/SUB-CW.md) | Clinical Workflow | 8 | 14 (BE=8, WEB=3, AND=3) |
| [SUB-MM](../specs/requirements/SUB-MM.md) | Medication Management | 9 | 13 (BE=9, WEB=2, AND=2) |
| [SUB-RA](../specs/requirements/SUB-RA.md) | Reporting & Analytics | 7 | 17 (BE=7, WEB=5, AND=5) |

## API & Implementation

| Document | Summary |
|----------|---------|
| [Backend Endpoints](../api/backend-endpoints.md) | Full REST API reference (auth, patients, encounters, meds, prescriptions, reports, vision) |
| [Initial Project Scaffolds](../features/initial-project-scaffolds.md) | Scaffolding of all three repos with stub implementations |
| [Traceability Matrix](../specs/requirements/traceability-matrix.md) | RTM with forward/backward traceability and 157 passing tests |

## Architecture Decisions

| Document | Summary |
|----------|---------|
| [ADR-0003: Backend Tech Stack](../architecture/0003-backend-tech-stack.md) | FastAPI, async SQLAlchemy, Pydantic v2, JWT auth |
| [ADR-0004: Frontend Tech Stack](../architecture/0004-frontend-tech-stack.md) | Next.js 15, React 19, TypeScript, Tailwind CSS |
| [ADR-0005: Android Tech Stack](../architecture/0005-android-tech-stack.md) | Kotlin, Jetpack Compose, Hilt, Retrofit, Room |

## Experiments & Tool Evaluations

| Document | Summary |
|----------|---------|
| [Tambo PMS Integration PRD](../Experiments/00-PRD-Tambo-PMS-Integration.md) | Conversational analytics sidebar with generative UI |
| [Tambo Developer Tutorial](../Experiments/00-Tambo-Developer-Onboarding-Tutorial.md) | Building Tambo components and tools |
| [OpenClaw PMS Integration PRD](../Experiments/05-PRD-OpenClaw-PMS-Integration.md) | Autonomous workflow automation agent with 8 PMS skills |
| [POC Gap Analysis](../Experiments/04-POC-Gap-Analysis.md) | kind-clinical-data POC vs. system requirements (15% coverage) |
| [v0 Developer Tutorial](../Experiments/02-v0-Developer-Tutorial.md) | v0 prompts for generating PMS UI pages |
