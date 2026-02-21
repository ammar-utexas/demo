# Project Knowledge Base

This directory is the single source of truth for all project context, decisions, and implementation details.

- [Documentation Workflow](documentation-workflow.md) — How features flow through requirements, testing, and release across all docs
- [PMS Project Overview](PMS_Project_Overview.md) — Bird's eye view of all repositories, requirements, and coverage

## Architecture Decisions

- [ADR-0001: Use Repository-Based Knowledge Management](architecture/0001-repo-based-knowledge-management.md)
- [ADR-0002: Multi-Repository Structure with Shared Docs Submodule](architecture/0002-multi-repo-structure.md)
- [ADR-0003: Backend Tech Stack — FastAPI with Async SQLAlchemy](architecture/0003-backend-tech-stack.md)
- [ADR-0004: Frontend Tech Stack — Next.js with Tailwind CSS](architecture/0004-frontend-tech-stack.md)
- [ADR-0005: Android Tech Stack — Kotlin with Jetpack Compose](architecture/0005-android-tech-stack.md)

### ISIC Dermatology CDS (SYS-REQ-0012)

- [ADR-0008: CDS Microservice Architecture](architecture/0008-derm-cds-microservice-architecture.md) — Separate Docker service (`pms-derm-cds` :8090) for AI inference
- [ADR-0009: AI Inference Runtime Selection](architecture/0009-ai-inference-runtime.md) — ONNX Runtime (server) + TensorRT (Jetson) + TFLite (Android)
- [ADR-0010: Patient Image Storage Strategy](architecture/0010-dermoscopic-image-storage.md) — AES-256-GCM encrypted BYTEA in PostgreSQL
- [ADR-0011: Vector Database Strategy](architecture/0011-vector-database-pgvector.md) — pgvector extension for similarity search
- [ADR-0012: Android On-Device Inference](architecture/0012-android-on-device-inference.md) — TFLite with MobileNetV3 for offline skin lesion triage
- [ADR-0013: AI Model Lifecycle Management](architecture/0013-ai-model-lifecycle.md) — Versioned model artifacts with provenance tracking
- [ADR-0014: Image Preprocessing & Quality Validation](architecture/0014-image-preprocessing-pipeline.md) — Resize/normalize pipeline with blur/exposure quality gates
- [ADR-0015: Risk Scoring Engine Design](architecture/0015-risk-scoring-engine.md) — Configurable threshold-based rules for clinical risk assessment
- [ADR-0016: Encryption Key Management](architecture/0016-image-encryption-key-management.md) — Unified versioned-envelope key management
- [ADR-0017: ISIC Reference Cache Management](architecture/0017-isic-reference-cache.md) — S3 bulk population, model-version coupling, incremental updates
- [ADR-0018: Backend-to-CDS Communication](architecture/0018-inter-service-communication.md) — HTTP client pooling, circuit breaking, timeout configuration
- [ADR-0019: Lesion Longitudinal Tracking](architecture/0019-lesion-longitudinal-tracking.md) — Persistent lesion identity with embedding cosine distance change detection
- [ADR-0020: Feature Flag Strategy](architecture/0020-derm-cds-feature-flags.md) — Granular per-requirement flags for phased rollout
- [ADR-0021: Database Migration Strategy](architecture/0021-derm-database-migration.md) — Alembic-managed migrations for pgvector tables

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
- [PRD: Tambo PMS Integration](experiments/00-PRD-Tambo-PMS-Integration.md) — Conversational analytics sidebar with generative UI components
- [Tambo Setup Guide](experiments/00-Tambo-PMS-Developer-Setup-Guide.md) — Self-hosted backend, component registration, tool definitions
- [Tambo Developer Tutorial](experiments/00-Tambo-Developer-Onboarding-Tutorial.md) — Hands-on onboarding: build your first component and tool

### Storybook (Component Documentation)
- [Storybook Getting Started](experiments/01-Storybook-Getting-Started.md) — Installation and basic setup
- [Storybook Developer Tutorial](experiments/01-Storybook-Developer-Tutorial.md) — Writing stories, addons, and CI integration

### v0 (AI Code Generation)
- [v0 Getting Started](experiments/02-v0-Getting-Started.md) — Setup and basic usage
- [v0 Developer Tutorial](experiments/02-v0-Developer-Tutorial.md) — Prompt engineering for component generation

### Banani (AI Design-to-Code)
- [Banani Getting Started](experiments/03-Banani-Getting-Started.md) — Setup and basic usage
- [Banani Developer Tutorial](experiments/03-Banani-Developer-Tutorial.md) — Design-to-code workflow with Figma integration

### POC Analysis
- [POC Gap Analysis](experiments/04-POC-Gap-Analysis.md) — Gap analysis of kind-clinical-data POC against system requirements

### OpenClaw (Agentic AI Workflow Automation)
- [PRD: OpenClaw PMS Integration](experiments/05-PRD-OpenClaw-PMS-Integration.md) — Autonomous workflow automation: prior auth, care coordination, clinical documentation
- [OpenClaw Setup Guide](experiments/05-OpenClaw-PMS-Developer-Setup-Guide.md) — HIPAA-hardened Docker deployment, custom PMS skills, frontend integration
- [OpenClaw Developer Tutorial](experiments/05-OpenClaw-Developer-Tutorial.md) — Hands-on onboarding: build your first skill with approval tiers

### MedASR (Medical Speech Recognition)
- [PRD: MedASR PMS Integration](experiments/07-PRD-MedASR-PMS-Integration.md) — On-premise medical speech-to-text for clinical dictation, encounter documentation, and structured note extraction
- [MedASR Setup Guide](experiments/07-MedASR-PMS-Developer-Setup-Guide.md) — Self-hosted GPU Docker deployment, FastAPI inference service, PMS backend and frontend integration
- [MedASR Developer Tutorial](experiments/07-MedASR-Developer-Tutorial.md) — Hands-on onboarding: build your first clinical dictation integration end-to-end

### Adaptive Thinking (AI Reasoning Optimization)
- [PRD: Adaptive Thinking PMS Integration](experiments/08-PRD-AdaptiveThinking-PMS-Integration.md) — Effort-routed AI reasoning for clinical decision support, cost optimization, and interleaved agentic workflows
- [Adaptive Thinking Setup Guide](experiments/08-AdaptiveThinking-PMS-Developer-Setup-Guide.md) — SDK migration from deprecated extended thinking, effort routing, telemetry, and streaming integration
- [Adaptive Thinking Developer Tutorial](experiments/08-AdaptiveThinking-Developer-Tutorial.md) — Hands-on onboarding: build effort-routed clinical AI features end-to-end

### MCP (Universal AI Integration Protocol)
- [PRD: MCP PMS Integration](experiments/09-PRD-MCP-PMS-Integration.md) — Standardized Model Context Protocol server exposing PMS APIs as discoverable tools, resources, and prompts for all AI clients
- [MCP Setup Guide](experiments/09-MCP-PMS-Developer-Setup-Guide.md) — FastMCP server deployment, OAuth 2.1 auth, audit logging, Claude Desktop and Next.js client integration
- [MCP Developer Tutorial](experiments/09-MCP-Developer-Tutorial.md) — Hands-on onboarding: build custom MCP tools, resources, and prompts for PMS clinical workflows

### Speechmatics Medical (Real-Time Clinical Speech-to-Text)
- [PRD: Speechmatics Medical PMS Integration](experiments/10-PRD-SpeechmaticsMedical-PMS-Integration.md) — Real-time medical transcription with speaker diarization, 93% clinical accuracy, and HIPAA-compliant cloud/on-prem deployment
- [Speechmatics Medical Setup Guide](experiments/10-SpeechmaticsMedical-PMS-Developer-Setup-Guide.md) — WebSocket proxy, Speechmatics API configuration, Next.js transcription UI, audit logging
- [Speechmatics Medical Developer Tutorial](experiments/10-SpeechmaticsMedical-Developer-Tutorial.md) — Hands-on onboarding: build real-time clinical dictation with speaker labels end-to-end

### Sanford Guide (Antimicrobial Clinical Decision Support)

- [PRD: Sanford Guide PMS Integration](experiments/11-PRD-SanfordGuide-PMS-Integration.md) — Real-time antimicrobial treatment recommendations, dose adjustments, drug interactions, and stewardship support embedded in prescribing workflows
- [Sanford Guide Setup Guide](experiments/11-SanfordGuide-PMS-Developer-Setup-Guide.md) — API client configuration, Redis caching, CDS sidebar panel, audit logging, and HIPAA-compliant data sanitization
- [Sanford Guide Developer Tutorial](experiments/11-SanfordGuide-Developer-Tutorial.md) — Hands-on onboarding: build a syndrome-to-prescription CDS pipeline with interaction checking end-to-end

### AI Zero-Day Vulnerability Scan (AI-Powered Security)
- [PRD: AI Zero-Day Scan PMS Integration](experiments/12-PRD-AIZeroDayScan-PMS-Integration.md) — AI-powered zero-day vulnerability scanning using Claude Opus 4.6 for continuous security assurance of PMS codebase and dependencies
- [AI Zero-Day Scan Setup Guide](experiments/12-AIZeroDayScan-PMS-Developer-Setup-Guide.md) — CI/CD security gate, deep dependency auditor service, security dashboard integration
- [AI Zero-Day Scan Developer Tutorial](experiments/12-AIZeroDayScan-Developer-Tutorial.md) — Hands-on onboarding: scan vulnerable code, triage findings, build custom healthcare security prompts

### Gemma 3 (On-Premise Open-Weight Clinical AI)
- [PRD: Gemma 3 PMS Integration](experiments/13-PRD-Gemma3-PMS-Integration.md) — Self-hosted multimodal AI backbone using Google's Gemma 3 and MedGemma for HIPAA-compliant clinical summarization, structured extraction, and medication intelligence with zero PHI egress
- [Gemma 3 Setup Guide](experiments/13-Gemma3-PMS-Developer-Setup-Guide.md) — Ollama deployment, AI Gateway service, OpenAI-compatible API, PMS backend and frontend integration
- [Gemma 3 Developer Tutorial](experiments/13-Gemma3-Developer-Tutorial.md) — Hands-on onboarding: build a medication reconciliation pipeline with drug interaction checking end-to-end

### Claude Code Multi-Agent Modes (AI-Assisted Development Workflows)
- [Agent Teams Reference](experiments/14-agent-teams-claude-whitepaper.md) — Official Claude Code agent teams documentation: architecture, shared task lists, mailbox messaging, display modes
- [Multi-Agent Modes Developer Tutorial](experiments/14-AgentTeams-Developer-Tutorial.md) — Hands-on comparison of single session, subagents, agent teams, and git worktrees with PMS-specific exercises and decision framework

### Claude Model Selection (AI Model Routing & Cost Optimization)
- [PRD: Claude Model Selection PMS Integration](experiments/15-PRD-ClaudeModelSelection-PMS-Integration.md) — Intelligent model routing between Claude Opus 4.6, Sonnet 4.6, and Haiku 4.5 based on task complexity, latency, and cost for 60-70% cost reduction
- [Claude Model Selection Setup Guide](experiments/15-ClaudeModelSelection-PMS-Developer-Setup-Guide.md) — Model Router service deployment, Anthropic SDK configuration, PHI sanitization, Redis caching, and PMS integration
- [Claude Model Selection Developer Tutorial](experiments/15-ClaudeModelSelection-Developer-Tutorial.md) — Hands-on onboarding: build a multi-tier clinical encounter pipeline with Haiku extraction, Sonnet summarization, and Opus escalation

### FHIR (Healthcare Data Interoperability Standard)
- [PRD: FHIR PMS Integration](experiments/16-PRD-FHIR-PMS-Integration.md) — FHIR R4 Facade for bidirectional clinical data exchange with external EHRs, HIEs, pharmacies, and labs via standards-compliant REST API with SMART on FHIR authorization
- [FHIR Setup Guide](experiments/16-FHIR-PMS-Developer-Setup-Guide.md) — FHIR Facade FastAPI deployment, resource mappers, CapabilityStatement, SMART OAuth 2.0, AuditEvent logging, and Next.js FHIR dashboard
- [FHIR Developer Tutorial](experiments/16-FHIR-Developer-Tutorial.md) — Hands-on onboarding: build FHIR resource mappers, Encounter endpoints, and external data import end-to-end

### HL7 v2 LIS Messaging (Legacy Lab System Integration)
- [PRD: HL7v2LIS PMS Integration](experiments/17-PRD-HL7v2LIS-PMS-Integration.md) — Bidirectional HL7 v2 messaging with laboratory information systems via MLLP for electronic lab ordering (ORM) and result reception (ORU) with TLS encryption and HIPAA audit logging
- [HL7v2LIS Setup Guide](experiments/17-HL7v2LIS-PMS-Developer-Setup-Guide.md) — MLLP listener/sender deployment, hl7apy parser/builder, stunnel TLS, lab order/result API endpoints, and Next.js lab dashboard
- [HL7v2LIS Developer Tutorial](experiments/17-HL7v2LIS-Developer-Tutorial.md) — Hands-on onboarding: parse ORU lab results, build ORM orders, detect critical values, and test with synthetic HL7 messages end-to-end

### ISIC Archive (AI-Powered Dermatology Clinical Decision Support)
- [PRD: ISICArchive PMS Integration](experiments/18-PRD-ISICArchive-PMS-Integration.md) — AI skin lesion classification using ISIC Archive's 400K+ dermoscopic images with EfficientNet-B4, pgvector similarity search, and structured risk scoring for dermatology triage
- [ISICArchive Setup Guide](experiments/18-ISICArchive-PMS-Developer-Setup-Guide.md) — Dermatology CDS Docker service deployment, ONNX Runtime classification, pgvector reference cache, lesion API endpoints, and Next.js classification UI
- [ISICArchive Developer Tutorial](experiments/18-ISICArchive-Developer-Tutorial.md) — Hands-on onboarding: classify a skin lesion, build similarity search, implement risk scoring, and track lesion changes over time end-to-end

### Superpowers (AI Development Workflow Enforcement)
- [PRD: Superpowers PMS Integration](experiments/19-PRD-Superpowers-PMS-Integration.md) — Agentic skills framework enforcing TDD, Socratic brainstorming, subagent-driven development, and two-stage code review for healthcare-grade AI-assisted development with PMS-specific HIPAA and architecture custom skills
- [Superpowers Setup Guide](experiments/19-Superpowers-PMS-Developer-Setup-Guide.md) — Claude Code plugin installation, PMS custom skills creation (HIPAA patterns, testing requirements, architecture conventions), and TDD workflow configuration
- [Superpowers Developer Tutorial](experiments/19-Superpowers-Developer-Tutorial.md) — Hands-on onboarding: build a PMS feature using the full Superpowers workflow (brainstorm, plan, TDD execute, review) with custom healthcare skills end-to-end

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

The PMS uses a **three-tier requirements decomposition**: System (SYS-REQ) → Domain (SUB-*) → Platform (SUB-*-BE/WEB/AND/AI). There are 12 system requirements, 48 domain requirements, and 95 platform requirements across 4 platforms. Domain requirements live in `specs/requirements/domain/` and platform requirements in `specs/requirements/platform/`.

- [System Specification](specs/system-spec.md) — System-level scope, context, subsystem decomposition, and platform codes
- [System Requirements (SYS-REQ)](specs/requirements/SYS-REQ.md) — 12 system-level requirements with platform annotations

### Domain Requirements

- [Patient Records (SUB-PR)](specs/requirements/domain/SUB-PR.md) — 16 domain requirements
- [Clinical Workflow (SUB-CW)](specs/requirements/domain/SUB-CW.md) — 8 domain requirements
- [Medication Management (SUB-MM)](specs/requirements/domain/SUB-MM.md) — 9 domain requirements
- [Reporting & Analytics (SUB-RA)](specs/requirements/domain/SUB-RA.md) — 8 domain requirements
- [Prompt Management (SUB-PM)](specs/requirements/domain/SUB-PM.md) — 7 domain requirements

### Platform Requirements

- [Backend (SUB-BE)](specs/requirements/platform/SUB-BE.md) — 47 requirements across 5 domains
- [Web Frontend (SUB-WEB)](specs/requirements/platform/SUB-WEB.md) — 24 requirements across 5 domains
- [Android (SUB-AND)](specs/requirements/platform/SUB-AND.md) — 18 requirements across 4 domains
- [AI Infrastructure (SUB-AI)](specs/requirements/platform/SUB-AI.md) — 6 requirements across 2 domains

## Testing & Traceability

- [Testing Strategy](testing/testing-strategy.md) — Test levels, platform-scoped naming conventions, run record format
- [Traceability Matrix (RTM)](testing/traceability-matrix.md) — Forward & backward traceability, platform traceability summary, test run log, coverage summary

## Quality Management

- [Requirements Governance & Conflict Analysis](quality/processes/requirements-governance.md) — Governance procedures, feature branching & release strategy, 14 domain conflicts, 12 platform conflicts, 14 race conditions
- [PMS Developer Working Instructions](quality/processes/PMS_Developer_Working_Instructions.md) — Development process guide
- [Development Pipeline Tutorial](quality/processes/Development_Pipeline_Tutorial.md) — CI/CD pipeline tutorial
- [Repository Setup Guide](quality/processes/repository-setup-guide.md) — Step-by-step guide to bootstrap a new repository with this documentation process
- [ISO 13485:2016 Standard](quality/standards/iso-13485-2016.pdf) — Medical device QMS standard

### Design History File (DHF)

- [DHF Master Index](quality/DHF/DHF-index.md) — ISO 13485:2016 Clause 7.3 traceability matrix mapping all deliverables
- [Release Evidence: v0.2.0-arch](quality/DHF/10-release-evidence/DHF-release-2026-02-21-v0.2.0-arch.md) — Documentation & Architecture release conformity record

### Risk Management

- Risk assessment files are created per feature using Step 5b of the [Documentation Workflow](documentation-workflow.md)
- Location: `quality/risk-management/RA-{CODE}-{FEATURE}.md`
