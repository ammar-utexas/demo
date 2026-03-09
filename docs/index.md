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
- [ADR-0022: DermaCheck Core Workflow Orchestration](architecture/0022-dermacheck-workflow-orchestration.md) — Parallel fan-out pipeline for Journey 1 capture-classify-review flow

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

- **[Experiment Interconnection Roadmap](experiments/00-Experiment-Interconnection-Roadmap.md)** — Master navigation guide: dependency graph, execution tiers, parallel tracks, critical path analysis, and quick-start recommendations for all 41 experiments

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
- [AI Zero-Day Scan Implementation Plan](experiments/12-AIZeroDayScan-Implementation-Plan.md) — Phased rollout steps to incorporate Claude Code Security into PMS screening

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

### Qwen 3.5 (On-Premise MoE Reasoning & Code Generation AI)
- [PRD: Qwen 3.5 PMS Integration](experiments/20-PRD-Qwen35-PMS-Integration.md) — 397B MoE model (17B active) for complex clinical reasoning, differential diagnosis, drug interaction analysis, and clinical rule code generation, complementing Gemma 3 in a dual-model on-premise strategy
- [Qwen 3.5 Setup Guide](experiments/20-Qwen35-PMS-Developer-Setup-Guide.md) — vLLM deployment with Qwen3-32B, AI Gateway dual-model routing (Qwen + Gemma), reasoning endpoints, and medication interaction analysis pipeline
- [Qwen 3.5 Developer Tutorial](experiments/20-Qwen35-Developer-Tutorial.md) — Hands-on onboarding: build a medication interaction analyzer with thinking mode reasoning chains, compare Qwen vs Gemma output quality, and implement task-based model routing end-to-end

### Voxtral Transcribe 2 (Open-Weight Real-Time Clinical Speech-to-Text)
- [PRD: Voxtral Transcribe 2 PMS Integration](experiments/21-PRD-VoxtralTranscribe2-PMS-Integration.md) — Dual-mode open-weight ASR using Mistral's Voxtral Realtime (4B, self-hosted streaming) and Voxtral Mini Transcribe V2 (batch API with diarization) for HIPAA-compliant clinical dictation with context biasing
- [Voxtral Transcribe 2 Setup Guide](experiments/21-VoxtralTranscribe2-PMS-Developer-Setup-Guide.md) — Docker GPU/Metal/CPU deployment, FastAPI WebSocket inference server, context biasing, PMS backend proxy, and Next.js dictation UI
- [Voxtral Transcribe 2 Developer Tutorial](experiments/21-VoxtralTranscribe2-Developer-Tutorial.md) — Hands-on onboarding: build clinical dictation with medical context biasing, SOAP note extraction via Gemma 3/Qwen 3.5, and compare Voxtral vs MedASR vs Speechmatics end-to-end

### Patient Safety AI Reference (AI Extension Ideas)
- [PMS AI Extension Ideas](experiments/22-PMS_AI_Extension_Ideas.md) — AI feature ideas mapped from IHI Patient Safety report to PMS subsystems

### Atlas — Agentic AI in Healthcare (50 Use Cases Synergy Analysis)
- [Atlas Agentic AI Healthcare Synergies](experiments/23-Atlas-Agentic-AI-Healthcare-Synergies.md) — Mapping of 50 agentic AI healthcare use cases from the Atlas publication against PMS subsystems and experiments, with priority synergy matrix and new agentic ideas

### Knowledge Work Plugins (Claude Code Plugin Framework for Healthcare Development)
- [PRD: Knowledge Work Plugins PMS Integration](experiments/24-PRD-KnowledgeWorkPlugins-PMS-Integration.md) — Custom Claude Code healthcare plugin bundling PMS-specific skills, HIPAA compliance enforcement, clinical workflow commands, and MCP connections into an installable developer experience package
- [Knowledge Work Plugins Setup Guide](experiments/24-KnowledgeWorkPlugins-PMS-Developer-Setup-Guide.md) — Plugin directory creation, skill authoring, command building, MCP configuration, hook setup, and local testing with `--plugin-dir`
- [Knowledge Work Plugins Developer Tutorial](experiments/24-KnowledgeWorkPlugins-Developer-Tutorial.md) — Hands-on onboarding: build a medication reconciliation command, FHIR interop skill, evaluate plugin strengths/weaknesses, and distribute via marketplace

### Edge Vision Stream (AR Glasses / Phone Camera Streaming to Jetson Thor)
- [PRD: Edge Vision Stream PMS Integration](experiments/25-PRD-EdgeVisionStream-PMS-Integration.md) — Real-time camera streaming from AR glasses or Android phones to Jetson Thor for QR/barcode scanning, background context analysis, patient/medication verification, and hands-free clinical workflow
- [Edge Vision Stream Setup Guide](experiments/25-EdgeVisionStream-PMS-Developer-Setup-Guide.md) — GStreamer RTSP ingestion, NVDEC hardware decode, ZBar QR detection, YOLOv8 background analysis, Android RTSP server, and PMS backend integration
- [Edge Vision Stream Developer Tutorial](experiments/25-EdgeVisionStream-Developer-Tutorial.md) — Hands-on onboarding: stream video from phone to Jetson, detect patient wristband QR codes, analyze clinical background context, and verify against PMS data end-to-end

### LangGraph 1.0 GA (Stateful Agent Orchestration for Clinical Workflows)
- [PRD: LangGraph PMS Integration](experiments/26-PRD-LangGraph-PMS-Integration.md) — Durable, stateful agent orchestration using LangGraph 1.0 GA with PostgreSQL checkpointing, human-in-the-loop approval gates, SSE streaming, and `langchain.agents` middleware for multi-step clinical workflows (prior auth, med reconciliation, care coordination)
- [LangGraph Setup Guide](experiments/26-LangGraph-PMS-Developer-Setup-Guide.md) — LangGraph 1.0 installation, `langgraph.prebuilt` deprecation notes, PostgreSQL checkpointer setup, FastAPI agent endpoints, HITL manager, and Next.js progress component integration
- [LangGraph Developer Tutorial](experiments/26-LangGraph-Developer-Tutorial.md) — Hands-on onboarding: build a medication reconciliation agent with stateful checkpointing, clinician HITL review, conditional routing, and fault-tolerant execution end-to-end (updated for LangGraph 1.0 GA)

### Claude Code (AI-Native Development Environment)
- [Claude Code Developer Tutorial](experiments/27-ClaudeCode-Developer-Tutorial.md) — Comprehensive Claude Code mastery guide: foundations (tools, context window, permissions), personalization (CLAUDE.md, memory, models), power features (sub-agents, MCP, hooks, skills), and autonomous usage (headless mode, worktrees, git integration)

### AI Coding Tools Landscape (Strategic Assessment)
- [AI Coding Tools Landscape 2026](experiments/28-AI-Coding-Tools-Landscape-2026.md) — Comprehensive comparison of 12+ AI coding tools (Claude Code, Codex, Qwen 3.5, Copilot, Cursor, Windsurf, Gemini, Amazon Q, Aider, Cline, Roo Code, Devin), healthcare compliance matrix, vendor lock-in risk analysis, and emergency transition playbook

### MCP Docker (Containerized MCP Server Infrastructure)
- [PRD: MCP Docker PMS Integration](experiments/29-PRD-MCPDocker-PMS-Integration.md) — Docker MCP Gateway, Catalog, and Toolkit for containerized MCP server deployment with supply-chain verification, secret management, and security interceptors
- [MCP Docker Setup Guide](experiments/29-MCPDocker-PMS-Developer-Setup-Guide.md) — Docker MCP CLI installation, PMS MCP Server containerization, catalog server enablement, Gateway configuration, and AI client connection
- [MCP Docker Developer Tutorial](experiments/29-MCPDocker-Developer-Tutorial.md) — Hands-on onboarding: containerize a custom MCP server, deploy through the Gateway, configure security interceptors, and build a developer dashboard integration end-to-end

### Gemini Interactions API (Cloud-Hosted Agentic Research & Extraction)
- [PRD: Gemini Interactions API PMS Integration](experiments/29-PRD-GeminiInteractions-PMS-Integration.md) — Managed cloud agentic layer using Google's Interactions API for stateful multi-turn conversations, Deep Research Agent for clinical evidence synthesis, and structured extraction with JSON Schema enforcement
- [Gemini Interactions API Setup Guide](experiments/29-GeminiInteractions-PMS-Developer-Setup-Guide.md) — SDK installation, PHI de-identification gateway, FastAPI router, Next.js research and chat components, and Vertex AI BAA configuration
- [Gemini Interactions API Developer Tutorial](experiments/29-GeminiInteractions-Developer-Tutorial.md) — Hands-on onboarding: build a drug interaction research pipeline with Deep Research Agent, streaming events, structured extraction, and PHI-safe clinical workflows end-to-end

### ElevenLabs (Cloud Voice AI — TTS, STT, Conversational Agents)
- [PRD: ElevenLabs PMS Integration](experiments/30-PRD-ElevenLabs-PMS-Integration.md) — Unified voice AI layer with Flash v2.5 TTS for clinical readback, Scribe v2 STT as cloud ASR fallback, and Conversational AI 2.0 agents for patient-facing phone interactions
- [ElevenLabs Setup Guide](experiments/30-ElevenLabs-PMS-Developer-Setup-Guide.md) — Python SDK installation, TTS and Scribe client configuration, PHI de-identification, FastAPI router, and React audio player components
- [ElevenLabs Developer Tutorial](experiments/30-ElevenLabs-Developer-Tutorial.md) — Hands-on onboarding: build a clinical readback pipeline with PHI-safe TTS, Scribe transcription, and streaming audio delivery end-to-end

### VS Code 1.109 Multi-Agent (AI-Powered Multi-Agent Development Platform)
- [PRD: VS Code Multi-Agent PMS Integration](experiments/31-PRD-VSCodeMultiAgent-PMS-Integration.md) — Standardized multi-agent IDE with Claude, Copilot, and Codex agents, PMS Agent Skills for HIPAA compliance, terminal sandboxing, and workspace priming for healthcare development
- [VS Code Multi-Agent Setup Guide](experiments/31-VSCodeMultiAgent-PMS-Developer-Setup-Guide.md) — VS Code 1.109 configuration, Agent Skills creation, MCP server setup, terminal sandbox rules, and auto-approval configuration
- [VS Code Multi-Agent Developer Tutorial](experiments/31-VSCodeMultiAgent-Developer-Tutorial.md) — Hands-on onboarding: orchestrate Claude, Copilot, and Codex agents to build a lab results endpoint with parallel test generation and HIPAA-compliant code end-to-end

### GitHub Agent HQ (Platform-Level Multi-Agent Governance & Orchestration)
- [PRD: GitHub Agent HQ PMS Integration](experiments/32-PRD-GitHubAgentHQ-PMS-Integration.md) — Organization-level agent governance with AGENTS.md, cloud agent sessions, Mission Control dashboard, branch protection, audit trails, and GitHub Actions integration for healthcare-compliant AI-assisted development
- [GitHub Agent HQ Setup Guide](experiments/32-GitHubAgentHQ-PMS-Developer-Setup-Guide.md) — Organization governance policies, AGENTS.md creation, branch protection rules, cloud agent task templates, and Mission Control configuration
- [GitHub Agent HQ Developer Tutorial](experiments/32-GitHubAgentHQ-Developer-Tutorial.md) — Hands-on onboarding: run an agent-powered security audit, monitor via Mission Control, and practice the three-layer agent stack (Agent HQ, VS Code, Claude Code CLI) end-to-end

### Speechmatics Flow API (Conversational Voice Agents for Clinical Workflows)
- [PRD: Speechmatics Flow API PMS Integration](experiments/33-PRD-SpeechmaticsFlow-PMS-Integration.md) — Unified voice agent platform combining ASR, LLM, and TTS for interactive clinical conversations with 4.0% medical KWER, Nordic language models, and custom LLM routing
- [Speechmatics Flow API Setup Guide](experiments/33-SpeechmaticsFlow-PMS-Developer-Setup-Guide.md) — Flow API WebSocket proxy, medical language models, Voice Agent Manager, Redis session caching, and React voice agent components
- [Speechmatics Flow API Developer Tutorial](experiments/33-SpeechmaticsFlow-Developer-Tutorial.md) — Hands-on onboarding: build a medication reconciliation voice agent with real-time structured extraction, multilingual medical models, and HIPAA-compliant audit logging end-to-end

### n8n 2.0+ (Visual Clinical Workflow Automation with AI Agents & HITL)
- [PRD: n8n 2.0+ PMS Integration](experiments/34-PRD-n8nUpdates-PMS-Integration.md) — Self-hosted visual workflow automation with task runners, HITL approval gates for AI agent actions, bidirectional MCP integration, enterprise security (RBAC, audit, encrypted credentials), and clinical workflow templates
- [n8n 2.0+ Setup Guide](experiments/34-n8nUpdates-PMS-Developer-Setup-Guide.md) — Docker Compose self-hosted deployment, AI Agent node with Claude, HITL Chat node, MCP Server and Client workflows, and PostgreSQL Memory configuration
- [n8n 2.0+ Developer Tutorial](experiments/34-n8nUpdates-Developer-Tutorial.md) — Hands-on onboarding: build a prior authorization workflow with AI analysis, clinician HITL review, MCP tool exposure, and enterprise audit logging end-to-end

### Kintsugi Voice Biomarker (Privacy-Preserving Mental Health Screening)
- [PRD: Kintsugi Voice Biomarker PMS Integration](experiments/35-PRD-KintsugiOpenSource-PMS-Integration.md) — Three integration paths: self-hosted DAM model from Hugging Face (fine-tuned Whisper-Small EN, Apache 2.0), `kintsugi-python` PyPI SDK (cloud API fallback), and direct REST API; depression/anxiety severity mapped to PHQ-9 and GAD-7 clinical scales with 71.3% sensitivity
- [Kintsugi Setup Guide](experiments/35-KintsugiOpenSource-PMS-Developer-Setup-Guide.md) — DAM model deployment from Hugging Face, `kintsugi-python` PyPI SDK configuration, dual-path screening engine (local + cloud fallback), API endpoints, and React voice biomarker recording component
- [Kintsugi Developer Tutorial](experiments/35-KintsugiOpenSource-Developer-Tutorial.md) — Hands-on onboarding: build a longitudinal mood tracking pipeline with DAM model inference, severity-based trend analysis, threshold tuning with dam-dataset, and HIPAA-compliant screening audit logging

### Claude Context Mode (AI Session Context Optimization)
- [PRD: Claude Context Mode PMS Integration](experiments/36-PRD-ClaudeContextMode-PMS-Integration.md) — MCP server plugin reducing Claude Code context window consumption by up to 98% via sandbox execution, SQLite FTS5 knowledge indexing, batch processing, and automatic subagent routing for extended AI-assisted development sessions
- [Claude Context Mode Setup Guide](experiments/36-ClaudeContextMode-PMS-Developer-Setup-Guide.md) — Plugin installation, PreToolUse hook configuration, PMS documentation indexing, PHI-safe sandbox conventions, and session stats monitoring
- [Claude Context Mode Developer Tutorial](experiments/36-ClaudeContextMode-Developer-Tutorial.md) — Hands-on onboarding: build a PMS development session optimizer with documentation indexing, PHI-safe patient data analysis, full-stack batch health checks, and medication reconciliation debugging end-to-end

### WebSocket (Real-Time Bidirectional Clinical Data Synchronization)
- [PRD: WebSocket PMS Integration](experiments/37-PRD-WebSocket-PMS-Integration.md) — Full-duplex real-time communication layer using FastAPI/Starlette WebSocket, PostgreSQL LISTEN/NOTIFY, and Redis pub/sub for instant patient record synchronization, clinical alerts, encounter collaboration with presence indicators, and conflict detection across all connected clients
- [WebSocket Setup Guide](experiments/37-WebSocket-PMS-Developer-Setup-Guide.md) — WebSocket endpoint implementation, PostgreSQL NOTIFY triggers, Redis pub/sub cross-instance broadcasting, Nginx WSS proxy configuration, React useWebSocket hook, and connection manager setup
- [WebSocket Developer Tutorial](experiments/37-WebSocket-Developer-Tutorial.md) — Hands-on onboarding: build a real-time encounter collaboration panel with presence indicators, section focus tracking, edit conflict warnings, and clinical alert notifications end-to-end

### Apache Kafka (Durable Event Streaming Backbone for Clinical Data Pipelines)
- [PRD: Kafka PMS Integration](experiments/38-PRD-Kafka-PMS-Integration.md) — Distributed event streaming platform with KRaft consensus, Debezium PostgreSQL CDC, Schema Registry with Avro, exactly-once delivery, and 7-year HIPAA-compliant retention for decoupled clinical event pipelines across all PMS services
- [Kafka Setup Guide](experiments/38-Kafka-PMS-Developer-Setup-Guide.md) — KRaft Docker Compose deployment, Debezium CDC connector, Schema Registry configuration, aiokafka async producer, consumer framework, WebSocket bridge consumer, and HIPAA audit consumer setup
- [Kafka Developer Tutorial](experiments/38-Kafka-Developer-Tutorial.md) — Hands-on onboarding: build a prescription drug interaction detection pipeline with Kafka event production, Avro serialization, CDC replay, consumer lag monitoring, and WebSocket alert delivery end-to-end

### Docker (Container Platform for Unified Service Deployment)
- [PRD: Docker PMS Integration](experiments/39-PRD-Docker-PMS-Integration.md) — Docker containerization and Docker Compose orchestration for all PMS services with multi-stage builds, custom bridge network isolation, Docker secrets for HIPAA-compliant credential management, health check dependency ordering, and Compose profiles for core, Kafka, AI, and monitoring service groups
- [Docker Setup Guide](experiments/39-Docker-PMS-Developer-Setup-Guide.md) — Dockerfiles for FastAPI backend and Next.js frontend, PostgreSQL and Redis containers, Docker Compose with profiles, secrets management, development hot-reload overrides, and production hardening configuration
- [Docker Developer Tutorial](experiments/39-Docker-Developer-Tutorial.md) — Hands-on onboarding: build a containerized patient encounter audit logger with PostgreSQL durable storage, Redis caching, network isolation, and Docker secrets for PHI protection end-to-end

### ExcalidrawSkill (AI-Generated Visual Diagram Tool for Claude Code)
- [PRD: ExcalidrawSkill PMS Integration](experiments/40-PRD-ExcalidrawSkill-PMS-Integration.md) — Claude Code skill for generating semantically structured, evidence-rich Excalidraw diagrams of clinical workflows, system architecture, and HIPAA data boundaries with a built-in Playwright render-and-validate loop
- [ExcalidrawSkill Setup Guide](experiments/40-ExcalidrawSkill-PMS-Developer-Setup-Guide.md) — Plugin installation, Playwright renderer setup, MPS brand color configuration, `/api/diagrams` FastAPI endpoint, and `DiagramViewer` Next.js component integration
- [ExcalidrawSkill Developer Tutorial](experiments/40-ExcalidrawSkill-Developer-Tutorial.md) — Hands-on onboarding: build a complete prescription approval workflow diagram with fan-out evidence artifacts, section-by-section generation, and validated PNG output end-to-end

### GPT-5.4 Clinical Benchmark (Cross-Vendor AI Model Cost-Benefit Analysis)
- [PRD: GPT-5.4 Clinical Benchmark PMS Integration](experiments/42-PRD-GPT54ClinicalBenchmark-PMS-Integration.md) — Head-to-head evaluation framework benchmarking GPT-5.4 ($2.50/$15 per MTok) against Claude Opus 4.6 ($5/$25 per MTok) on encounter summarization, medication interaction analysis, and prior authorization decision support with LLM-as-Judge quality scoring and cost projections
- [GPT-5.4 Clinical Benchmark Setup Guide](experiments/42-GPT54ClinicalBenchmark-PMS-Developer-Setup-Guide.md) — Dual-provider SDK configuration, Benchmark Runner service, Quality Evaluator, Cost Analysis Engine, and Next.js comparison dashboard
- [GPT-5.4 Clinical Benchmark Developer Tutorial](experiments/42-GPT54ClinicalBenchmark-Developer-Tutorial.md) — Hands-on onboarding: run a 15-task clinical benchmark suite, evaluate quality with LLM-as-Judge, generate cost-benefit reports, and produce Model Router routing recommendations end-to-end

### CMS Prior Authorization ML Dataset (MarginLogic PA Outcome Intelligence)
- [PRD: CMS Prior Auth Dataset PMS Integration](experiments/43-PRD-CMSPriorAuthDataset-PMS-Integration.md) — ML training dataset for PA prediction built from CMS DE-SynPUF synthetic Medicare claims (3.16M claims) joined with 115 PA-required HCPCS codes across DMEPOS, Hospital OPD, and RSNAT programs; XGBoost GPU training pipeline with SHAP interpretability
- [CMS Prior Auth Dataset Setup Guide](experiments/43-CMSPriorAuthDataset-PMS-Developer-Setup-Guide.md) — HIPAA hardening the Jetson Thor (LUKS encryption, UFW firewall, auditd logging, SSH hardening), ML stack installation with GPU-accelerated XGBoost, PostgreSQL feature store, MLflow experiment tracking, and CMS data download/build pipeline
- [CMS Prior Auth Dataset Developer Tutorial](experiments/43-CMSPriorAuthDataset-Developer-Tutorial.md) — End-to-end PA prediction pipeline on Jetson Thor: data exploration, XGBoost baseline training (GPU vs CPU benchmark), Optuna hyperparameter tuning, SHAP explanations, FastAPI risk scoring API, Streamlit dashboard, and transition guide from CMS synthetic data to real TRA clinical data

### Payer Policy Download (Anti-VEGF PA Rule Library)
- [PRD: Payer Policy Download PMS Integration](experiments/44-PRD-PayerPolicyDownload-PMS-Integration.md) — Automated download pipeline for anti-VEGF prior authorization policy documents from 6 major payers (CMS Medicare, UHC, Aetna, BCBSTX, Humana, Cigna) with structured rule extraction, SHA-256 integrity verification, and manifest tracking

### UHC API Marketplace (Real-Time UHC Eligibility, PA, and Claims)
- [PRD: UHC API Marketplace PMS Integration](experiments/46-PRD-UHCAPIMarketplace-PMS-Integration.md) — Real-time eligibility verification, benefit checks, prior authorization submission, and claim pre-validation via UHC's Optum Real APIs with OAuth 2.0, X12-to-JSON mapping, and Gold Card integration
- [UHC API Marketplace Setup Guide](experiments/46-UHCAPIMarketplace-PMS-Developer-Setup-Guide.md) — OneHealthcare ID registration, sandbox credentials, OAuth client, FastAPI endpoints, PostgreSQL audit tables, and eligibility panel component
- [UHC API Marketplace Developer Tutorial](experiments/46-UHCAPIMarketplace-Developer-Tutorial.md) — Hands-on onboarding: build a pre-visit workflow (eligibility → benefits → PA submission → claim pre-check) against UHC sandbox with HIPAA audit logging end-to-end

### CMS Coverage API (Real-Time Medicare Coverage Determination)
- [PRD: CMS Coverage API PMS Integration](experiments/45-PRD-CMSCoverageAPI-PMS-Integration.md) — Real-time LCD/NCD lookup via CMS Coverage API v1.5 for automated Medicare coverage determination, replacing web scraping with structured JSON responses, PostgreSQL caching, and daily change detection
- [CMS Coverage API Setup Guide](experiments/45-CMSCoverageAPI-PMS-Developer-Setup-Guide.md) — API client with automatic license token management, FastAPI endpoints, PostgreSQL cache schema, and Next.js coverage lookup component
- [CMS Coverage API Developer Tutorial](experiments/45-CMSCoverageAPI-Developer-Tutorial.md) — Hands-on onboarding: build a coverage check for intravitreal injections, query LCD ICD-10 codes, detect policy changes, and integrate with encounter workflows end-to-end

### Availity API (Multi-Payer Clearinghouse — Eligibility, PA, Claims)
- [PRD: Availity API PMS Integration](experiments/47-PRD-AvailityAPI-PMS-Integration.md) — Multi-payer clearinghouse integration via Availity REST API for unified eligibility (270/271), prior authorization (278), claim status (276/277), and care cost estimation across all 6 TRA-contracted payers through one set of credentials
- [Availity API Setup Guide](experiments/47-AvailityAPI-PMS-Developer-Setup-Guide.md) — Developer portal registration, Demo plan subscription, OAuth 2.0 client with 5-minute token refresh, FastAPI endpoints, PostgreSQL audit schema, and multi-payer eligibility panel
- [Availity API Developer Tutorial](experiments/47-AvailityAPI-Developer-Tutorial.md) — Hands-on onboarding: build a multi-payer batch eligibility checker, submit a PA to any connected payer, query claim status, and integrate with the PA Decision Engine end-to-end

### FHIR Prior Authorization APIs (Da Vinci CRD/DTR/PAS — CMS-0057-F Compliance)
- [PRD: FHIR Prior Auth PMS Integration](experiments/48-PRD-FHIRPriorAuth-PMS-Integration.md) — Direct payer-to-provider FHIR PA workflow using Da Vinci PAS (Claim/$submit), CRD (coverage requirements discovery), and DTR (auto-documentation) replacing X12 278 transactions, with dual-path routing (FHIR primary, Availity X12 fallback) for CMS-0057-F compliance by January 2027
- [FHIR Prior Auth Setup Guide](experiments/48-FHIRPriorAuth-PMS-Developer-Setup-Guide.md) — HAPI FHIR test server deployment, fhir.resources Pydantic models, PAS Bundle Builder, SMART on FHIR auth, PA Router (FHIR vs X12), and FastAPI endpoints
- [FHIR Prior Auth Developer Tutorial](experiments/48-FHIRPriorAuth-Developer-Tutorial.md) — Hands-on onboarding: build an Eylea intravitreal injection PA submission with FHIR Claim, Coverage, and Condition resources, submit via Claim/$submit, process ClaimResponse, and understand the CRD → DTR → PAS workflow end-to-end

### NextGen FHIR API (Referring Provider EHR Data Import — 50%+ Ophthalmology Market Share)
- [PRD: NextGen FHIR API PMS Integration](experiments/49-PRD-NextGenFHIRAPI-PMS-Integration.md) — Inbound clinical data import from referring ophthalmology practices via NextGen's FHIR R4 Patient Access API (Patient, Condition, MedicationRequest, AllergyIntolerance, Encounter, Observation) with SMART on FHIR auth, clinical reconciliation engine, C-CDA parsing, and Mirth Connect bridge for HL7v2 practices
- [NextGen FHIR API Setup Guide](experiments/49-NextGenFHIRAPI-PMS-Developer-Setup-Guide.md) — NextGen Developer Program registration, SMART on FHIR authentication, NextGen FHIR Client, Referral Import Service, PostgreSQL schema for external records, and FastAPI endpoints
- [NextGen FHIR API Developer Tutorial](experiments/49-NextGenFHIRAPI-Developer-Tutorial.md) — Hands-on onboarding: import a complete referral patient record (conditions, medications, allergies, visual acuity) from a simulated NextGen ophthalmology practice, display clinical summary, and understand reconciliation workflow end-to-end

### OWASP LLM Top 10 (AI Security Assessment & Red Teaming)
- [PRD: OWASP LLM Top 10 PMS Security Assessment](experiments/50-PRD-OWASPLLMTop10-PMS-Integration.md) — Comprehensive security assessment framework mapping all 10 OWASP LLM vulnerabilities to PMS AI components with 48 test cases and DeepTeam red teaming integration
- [OWASP LLM Top 10 Setup Guide](experiments/50-OWASPLLMTop10-PMS-Developer-Setup-Guide.md) — DeepTeam installation, PMS test harness configuration, automated vulnerability scanning, and security assessment dashboard
- [OWASP LLM Top 10 Developer Tutorial](experiments/50-OWASPLLMTop10-Developer-Tutorial.md) — Hands-on red teaming: build a healthcare prompt injection scanner, run DeepTeam adversarial tests, and verify security controls for clinical AI endpoints

### Amazon Connect Health (Cloud Contact Center + Agentic Clinical AI)
- [PRD: Amazon Connect Health PMS Integration](experiments/51-PRD-AmazonConnectHealth-PMS-Integration.md) — AWS-managed healthcare contact center with five agentic AI capabilities: patient verification, appointment scheduling, pre-visit insights, ambient clinical documentation (22+ specialties), and automated ICD-10/CPT medical coding at $99/user/month
- [Amazon Connect Health Setup Guide](experiments/51-AmazonConnectHealth-PMS-Developer-Setup-Guide.md) — Amazon Connect instance provisioning, KMS encryption, Patient Verification and Ambient Documentation agent configuration, Lambda contact flow integration, and FastAPI/Next.js endpoints
- [Amazon Connect Health Developer Tutorial](experiments/51-AmazonConnectHealth-Developer-Tutorial.md) — Hands-on onboarding: simulate patient call verification, capture ambient ophthalmology encounter documentation, review auto-generated SOAP notes with ICD-10/CPT codes, and monitor call center metrics end-to-end

### vLLM (Self-Hosted LLM Inference Engine)
- [PRD: vLLM PMS Integration](experiments/52-PRD-vLLM-PMS-Integration.md) — Self-hosted, HIPAA-compliant LLM inference with PagedAttention for clinical note summarization, ICD-10/CPT code suggestion, patient communication drafting, and medication interaction analysis
- [vLLM Setup Guide](experiments/52-vLLM-PMS-Developer-Setup-Guide.md) — Docker deployment with GPU passthrough, OpenAI-compatible API configuration, FastAPI LLMService integration, and Prometheus metrics collection
- [vLLM Developer Tutorial](experiments/52-vLLM-Developer-Tutorial.md) — Hands-on onboarding: generate SOAP notes from encounter transcripts, suggest medical codes with confidence scores, draft patient communications, and check medication interactions — all on local GPU

### Llama 4 Scout/Maverick (Self-Hosted Open-Weight Multimodal LLM)
- [PRD: Llama 4 PMS Integration](experiments/53-PRD-Llama4-PMS-Integration.md) — Self-hosted Llama 4 Scout (17B active/109B MoE, 10M context) and Maverick (17B active/400B MoE, 1M context) for HIPAA-compliant clinical AI: SOAP notes, ICD-10 coding, medication interaction checks, and multimodal image+text analysis on vLLM
- [Llama 4 Setup Guide](experiments/53-Llama4-PMS-Developer-Setup-Guide.md) — HuggingFace model download, vLLM INT4 deployment on H100, clinical prompt templates, LLM Service routing, FastAPI AI endpoints, and Next.js Clinical AI Assistant panel
- [Llama 4 Developer Tutorial](experiments/53-Llama4-Developer-Tutorial.md) — Hands-on onboarding: build an encounter summarizer with SOAP note generation, ICD-10 code suggestion with validation, medication interaction checking, and model routing between local Llama 4 and cloud Claude API

### InfraNodus (Text Network Analysis & Clinical Knowledge Graphs)
- [PRD: InfraNodus PMS Integration](experiments/41-PRD-InfraNodus-PMS-Integration.md) — Text network analysis transforming clinical encounter notes into interactive knowledge graphs via InfraNodus Cloud API (RapidAPI) with `doNotSave=true` PHI protection, PHI De-ID Gateway, topical cluster detection, structural gap identification, and MCP Server for developer workflows
- [InfraNodus Setup Guide](experiments/41-InfraNodus-PMS-Developer-Setup-Guide.md) — Cloud API configuration via RapidAPI, MCP Server setup for Claude Code, PHI De-ID Gateway, Knowledge Graph Service, D3.js graph visualization, and gap analysis panel integration
- [InfraNodus Developer Tutorial](experiments/41-InfraNodus-Developer-Tutorial.md) — Hands-on onboarding: build a clinical encounter knowledge graph analyzer with Cloud API integration, longitudinal patient documentation analysis, structural gap detection, and interactive graph visualization end-to-end

### Mistral 3 Family (Open-Weight Tiered Clinical AI — Edge to Server)
- [PRD: Mistral 3 PMS Integration](experiments/54-PRD-Mistral3-PMS-Integration.md) — Apache 2.0 open-weight model family (Ministral 3B/8B/14B dense + Mistral Large 3 675B MoE) for tiered self-hosted clinical AI spanning edge devices to GPU servers, with multimodal vision, 256K context, and reasoning variants for HIPAA-compliant encounter summarization, medication analysis, and document extraction
- [Mistral 3 Setup Guide](experiments/54-Mistral3-PMS-Developer-Setup-Guide.md) — vLLM Docker deployment for Ministral 14B and Mistral Large 3, FastAPI MistralService integration, OpenAI-compatible API configuration, Next.js AI panel, and Prometheus metrics
- [Mistral 3 Developer Tutorial](experiments/54-Mistral3-Developer-Tutorial.md) — Hands-on onboarding: build an ophthalmology encounter summarizer with structured SOAP note generation, ICD-10/CPT code suggestions, physician approval workflow, and model tier routing end-to-end

### CrewAI (Multi-Agent Clinical Workflow Orchestration)
- [PRD: CrewAI PMS Integration](experiments/55-PRD-CrewAI-PMS-Integration.md) — Multi-agent orchestration framework (44.6K stars, MIT license) coordinating Scribe, Coding, Compliance, and Communication agents into clinical documentation pipelines with shared memory, structured Pydantic outputs, and event-driven Flows — compared to LangGraph, AutoGen, and OpenAI Agents SDK
- [CrewAI Setup Guide](experiments/55-CrewAI-PMS-Developer-Setup-Guide.md) — Python library installation in existing FastAPI backend, vLLM + Claude LLM provider configuration, custom PMS API tools, CrewService orchestration, and crew pipeline endpoints
- [CrewAI Developer Tutorial](experiments/55-CrewAI-Developer-Tutorial.md) — Hands-on onboarding: build a four-agent Encounter Documentation Crew that generates SOAP notes, suggests ICD-10/CPT codes, validates compliance, and drafts patient letters — all coordinated automatically from a single trigger

### PA Competitive Landscape & MarginLogic Positioning
- [PA Competitive Landscape](experiments/56-PA-Competitive-Landscape.md) — Maps Abridge ($5.3B ambient→PA), Amazon Connect Health ($99/mo platform), Dragon Copilot (partner marketplace), and Epic AI Charting (62.6% ambient adoption) against MarginLogic's defensible wedge: specialty-specific, explainable PA prediction with payer-pattern learning

### notebooklm-py (Programmatic Clinical Content Generation)
- [PRD: notebooklm-py PMS Integration](experiments/57-PRD-NotebookLM-Py-PMS-Integration.md) — Unofficial Python SDK (MIT, v0.3.2) for Google NotebookLM enabling automated generation of audio podcasts, quizzes, flashcards, study guides, and slide decks from clinical protocols and guidelines — with PHI de-identification gateway and HIPAA audit logging
- [notebooklm-py Setup Guide](experiments/57-NotebookLM-Py-PMS-Developer-Setup-Guide.md) — Cookie-based Google authentication via Playwright, NotebookLMService async wrapper for FastAPI, REST API endpoints, Next.js Content Library page, and end-to-end verification
- [notebooklm-py Developer Tutorial](experiments/57-NotebookLM-Py-Developer-Tutorial.md) — Hands-on onboarding: build a Clinical Protocol Podcast Generator that creates notebooks, ingests guidelines, generates audio briefings and comprehension quizzes, and queries sources via grounded Q&A

### Supabase + Claude Code (AI-Assisted Backend-as-a-Service)
- [PRD: Supabase + Claude Code PMS Integration](experiments/58-PRD-SupabaseClaudeCode-PMS-Integration.md) — HIPAA-compliant BaaS platform (PostgreSQL, Auth, Realtime, Edge Functions) with Claude Code MCP for AI-driven schema design, migration generation, RLS policy auditing, and type generation — replacing manual database workflows with conversational AI
- [Supabase + Claude Code Setup Guide](experiments/58-SupabaseClaudeCode-PMS-Developer-Setup-Guide.md) — Supabase Cloud project creation with HIPAA add-on, MCP server and Claude Code Templates installation, FastAPI/Next.js/Android client integration, and RLS-protected schema setup
- [Supabase + Claude Code Developer Tutorial](experiments/58-SupabaseClaudeCode-Developer-Tutorial.md) — Hands-on onboarding: build a real-time vitals monitor with RLS-protected tables, PostgREST auto-API, WebSocket subscriptions, and Claude Code security auditing

### Obsidian + Claude Code (AI-Powered Clinical Knowledge Management)
- [PRD: Obsidian + Claude Code PMS Integration](experiments/59-PRD-ObsidianClaudeCode-PMS-Integration.md) — Local-first, AI-queryable clinical knowledge vault using Obsidian's markdown-based bidirectional linking with Claude Code MCP integration for protocol search, drug interaction lookup, and developer knowledge graph — with HIPAA-compliant PHI isolation and Git version control
- [Obsidian + Claude Code Setup Guide](experiments/59-ObsidianClaudeCode-PMS-Developer-Setup-Guide.md) — Vault structure creation, Filesystem MCP and obsidian-claude-code-mcp plugin configuration, Knowledge Vault Service (FastAPI), Knowledge Search Panel (Next.js), and Obsidian CLI v1.12+ setup
- [Obsidian + Claude Code Developer Tutorial](experiments/59-ObsidianClaudeCode-Developer-Tutorial.md) — Hands-on onboarding: build a drug interaction knowledge workflow with structured notes, wikilinks, vault search API, interaction lookup endpoint, and Claude Code automated vault curation end-to-end

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

The PMS uses a **three-tier requirements decomposition**: System (SYS-REQ) → Domain (SUB-*) → Platform (SUB-*-BE/WEB/AND/AI). There are 13 system requirements, 50 domain requirements, and 100 platform requirements across 4 platforms. Domain requirements live in `specs/requirements/domain/` and platform requirements in `specs/requirements/platform/`.

- [System Specification](specs/system-spec.md) — System-level scope, context, subsystem decomposition, and platform codes
- [System Requirements (SYS-REQ)](specs/requirements/SYS-REQ.md) — 13 system-level requirements with platform annotations

### Domain Requirements

- [Patient Records (SUB-PR)](specs/requirements/domain/SUB-PR.md) — 17 domain requirements
- [Clinical Workflow (SUB-CW)](specs/requirements/domain/SUB-CW.md) — 9 domain requirements
- [Medication Management (SUB-MM)](specs/requirements/domain/SUB-MM.md) — 9 domain requirements
- [Reporting & Analytics (SUB-RA)](specs/requirements/domain/SUB-RA.md) — 8 domain requirements
- [Prompt Management (SUB-PM)](specs/requirements/domain/SUB-PM.md) — 7 domain requirements

### Platform Requirements

- [Backend (SUB-BE)](specs/requirements/platform/SUB-BE.md) — 49 requirements across 5 domains
- [Web Frontend (SUB-WEB)](specs/requirements/platform/SUB-WEB.md) — 25 requirements across 5 domains
- [Android (SUB-AND)](specs/requirements/platform/SUB-AND.md) — 19 requirements across 4 domains
- [AI Infrastructure (SUB-AI)](specs/requirements/platform/SUB-AI.md) — 7 requirements across 2 domains

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
- [RA-DERM-DermaCheckOrchestration](quality/risk-management/RA-DERM-DermaCheckOrchestration.md) — DermaCheck Workflow Orchestration (SYS-REQ-0013): 20 risks across Clinical Safety, Data Integrity, Availability, and Concurrency categories; 0 residual unacceptable
