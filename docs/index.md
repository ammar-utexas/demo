# Project Knowledge Base

This directory is the single source of truth for all project context, decisions, and implementation details.

## Architecture Decisions

- [ADR-0001: Use Repository-Based Knowledge Management](architecture/0001-repo-based-knowledge-management.md)
- [ADR-0002: Multi-Repository Structure with Shared Docs Submodule](architecture/0002-multi-repo-structure.md)
- [ADR-0003: Backend Tech Stack — FastAPI with Async SQLAlchemy](architecture/0003-backend-tech-stack.md)
- [ADR-0004: Frontend Tech Stack — Next.js with Tailwind CSS](architecture/0004-frontend-tech-stack.md)
- [ADR-0005: Android Tech Stack — Kotlin with Jetpack Compose](architecture/0005-android-tech-stack.md)

## Features

- [Initial Project Scaffolds](features/initial-project-scaffolds.md) — Backend, frontend, and Android app scaffolding

## Bug Fixes

<!-- Add links to bug analyses as they are resolved -->
_No bug fixes documented yet._

## API Contracts

- [Backend API Endpoints](api/backend-endpoints.md) — Full REST API reference for pms-backend

## Configuration & Dependencies

- [Project Setup Guide](config/project-setup.md) — How to clone, install, and run all three projects
- [Dependencies Overview](config/dependencies.md) — All libraries and why they were chosen

## Specifications & Requirements

- [System Specification](specs/system-spec.md) — System-level scope, context, and subsystem decomposition
- [System Requirements (SYS-REQ)](specs/requirements/SYS-REQ.md) — 10 system-level requirements
- [Patient Records (SUB-PR)](specs/requirements/SUB-PR.md) — 8 subsystem requirements
- [Clinical Workflow (SUB-CW)](specs/requirements/SUB-CW.md) — 8 subsystem requirements
- [Medication Management (SUB-MM)](specs/requirements/SUB-MM.md) — 9 subsystem requirements
- [Reporting & Analytics (SUB-RA)](specs/requirements/SUB-RA.md) — 7 subsystem requirements
- [Traceability Matrix (RTM)](specs/requirements/traceability-matrix.md) — Forward & backward traceability, test run log, coverage summary
- [Testing Strategy](specs/testing-strategy.md) — Test levels, naming conventions, run record format
