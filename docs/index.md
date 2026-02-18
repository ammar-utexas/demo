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
- [Security Scanning](config/security-scanning.md) — SonarCloud, CodeRabbit, and Snyk configuration across all repos

## Release Management

- [ADR-0006: Release Management Strategy](architecture/0006-release-management-strategy.md) — Independent versioning, feature flags, 4-environment pipeline
- [Release Process](config/release-process.md) — Step-by-step release workflow, approval gates, rollback strategy
- [Feature Flag Registry](config/feature-flags.md) — Flag naming, lifecycle, per-environment state
- [Environment Configuration](config/environments.md) — Dev, QA, Staging, Production environment setup
- [Subsystem Versions](specs/subsystem-versions.md) — Per-subsystem version tracking tied to requirement completion
- [Release Compatibility Matrix](specs/release-compatibility-matrix.md) — Tested version combinations across repos

## Edge Deployment

- [ADR-0007: Jetson Thor Edge Deployment](architecture/0007-jetson-thor-edge-deployment.md) — Edge-only deployment on NVIDIA Jetson Thor with on-device vision inference
- [Vision Capabilities](features/vision-capabilities.md) — Wound assessment, patient ID verification, and document OCR
- [Jetson Deployment Guide](config/jetson-deployment.md) — Setup, docker-compose, Wi-Fi 7 network config

## Experiments & Tool Evaluations

### Tambo AI (Conversational Analytics)
- [PRD: Tambo PMS Integration](Experiments/00-PRD-Tambo-PMS-Integration.md) — Conversational analytics sidebar with generative UI components
- [Tambo Setup Guide](Experiments/00-Tambo-PMS-Developer-Setup-Guide.md) — Self-hosted backend, component registration, tool definitions
- [Tambo Developer Tutorial](Experiments/00-Tambo-Developer-Onboarding-Tutorial.md) — Hands-on onboarding: build your first component and tool

### Storybook (Component Documentation)
- [Storybook Getting Started](Experiments/01-Storybook-Getting-Started.md) — Installation and basic setup
- [Storybook Developer Tutorial](Experiments/01-Storybook-Developer-Tutorial.md) — Writing stories, addons, and CI integration

### v0 (AI Code Generation)
- [v0 Getting Started](Experiments/02-v0-Getting-Started.md) — Setup and basic usage
- [v0 Developer Tutorial](Experiments/02-v0-Developer-Tutorial.md) — Prompt engineering for component generation

### Banani (AI Design-to-Code)
- [Banani Getting Started](Experiments/03-Banani-Getting-Started.md) — Setup and basic usage
- [Banani Developer Tutorial](Experiments/03-Banani-Developer-Tutorial.md) — Design-to-code workflow with Figma integration

### POC Analysis
- [POC Gap Analysis](Experiments/04-POC-Gap-Analysis.md) — Gap analysis of kind-clinical-data POC against system requirements

### OpenClaw (Agentic AI Workflow Automation)
- [PRD: OpenClaw PMS Integration](Experiments/05-PRD-OpenClaw-PMS-Integration.md) — Autonomous workflow automation: prior auth, care coordination, clinical documentation
- [OpenClaw Setup Guide](Experiments/05-OpenClaw-PMS-Developer-Setup-Guide.md) — HIPAA-hardened Docker deployment, custom PMS skills, frontend integration
- [OpenClaw Developer Tutorial](Experiments/05-OpenClaw-Developer-Tutorial.md) — Hands-on onboarding: build your first skill with approval tiers

---

## Documentation Views

### By Domain
Browse documentation organized by business/functional domain — [full index](domain/index.md)

- [Property Management](domain/property-management.md) — Clinical workflows, patient records, medications, reporting
- [Security & Compliance](domain/security-compliance.md) — HIPAA, encryption, auth, audit, scanning
- [Vision & AI](domain/vision-ai.md) — Computer vision, AI inference, edge models
- [Agentic AI](domain/agentic-ai.md) — OpenClaw autonomous workflow automation
- [Frontend UI/UX](domain/frontend-ui.md) — UI design tools, component libraries, design systems
- [Release Management](domain/release-management.md) — Versioning, deployment, compatibility, feature flags
- [Testing & QA](domain/testing-qa.md) — Test strategy, traceability, coverage
- [Configuration & DevOps](domain/configuration-devops.md) — Dependencies, environments, setup, CI/CD
- [Project Management](domain/project-management.md) — Repository structure, knowledge management

### By Platform
Browse documentation organized by deployment platform — [full index](platform/index.md)

- [Backend/Server](platform/backend-server.md) — FastAPI, Python, SQLAlchemy, PostgreSQL
- [Web Frontend](platform/web-frontend.md) — Next.js 15, React 19, TypeScript, Tailwind CSS
- [Android](platform/android.md) — Kotlin, Jetpack Compose, Hilt, Retrofit, Room
- [Jetson/Edge](platform/jetson-edge.md) — NVIDIA Jetson Thor, TensorRT, JetPack 7.x
- [Infrastructure/CI-CD](platform/infrastructure-cicd.md) — Docker, GitHub Actions, SonarCloud, Snyk
- [Cross-Platform](platform/cross-platform.md) — Docs spanning all platforms

---

## Specifications & Requirements

The PMS uses a **three-tier requirements decomposition**: System (SYS-REQ) → Domain (SUB-*) → Platform (SUB-*-BE/WEB/AND/AI). There are 10 system requirements, 36 domain requirements, and 69 platform requirements across 4 platforms.

- [System Specification](specs/system-spec.md) — System-level scope, context, subsystem decomposition, and platform codes
- [System Requirements (SYS-REQ)](specs/requirements/SYS-REQ.md) — 10 system-level requirements with platform annotations
- [Patient Records (SUB-PR)](specs/requirements/SUB-PR.md) — 12 domain requirements, 25 platform requirements (BE=11, WEB=4, AND=7, AI=3)
- [Clinical Workflow (SUB-CW)](specs/requirements/SUB-CW.md) — 8 domain requirements, 14 platform requirements (BE=8, WEB=3, AND=3)
- [Medication Management (SUB-MM)](specs/requirements/SUB-MM.md) — 9 domain requirements, 13 platform requirements (BE=9, WEB=2, AND=2)
- [Reporting & Analytics (SUB-RA)](specs/requirements/SUB-RA.md) — 7 domain requirements, 17 platform requirements (BE=7, WEB=5, AND=5)
- [Traceability Matrix (RTM)](specs/requirements/traceability-matrix.md) — Forward & backward traceability, platform traceability summary, test run log, coverage summary
- [Testing Strategy](specs/testing-strategy.md) — Test levels, platform-scoped naming conventions, run record format
- [Requirements Governance & Conflict Analysis](specs/requirements-governance.md) — Governance procedures, 11 domain conflicts, 9 platform conflicts, 12 race conditions
