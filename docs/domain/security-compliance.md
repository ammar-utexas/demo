# Domain: Security & Compliance

HIPAA compliance, encryption, authentication, authorization, audit trails, and security scanning across all platforms.

## Requirements & Specifications

| Document | Summary |
|----------|---------|
| [System Spec](../specs/system-spec.md) | HIPAA regulatory constraints, quality attributes |
| [SYS-REQ](../specs/requirements/SYS-REQ.md) | MFA (SYS-01), AES-256 encryption (SYS-02), audit trails (SYS-03), RBAC (SYS-05) |
| [Requirements Governance](../specs/requirements-governance.md) | 2 critical race conditions identified in security-related workflows |

## Architecture & Implementation

| Document | Summary |
|----------|---------|
| [ADR-0003: Backend Tech Stack](../architecture/0003-backend-tech-stack.md) | JWT auth, AES encryption, HIPAA-compliant backend design |
| [ADR-0007: Jetson Edge Deployment](../architecture/0007-jetson-thor-edge-deployment.md) | Air-gapped edge security, local-only data processing |
| [Backend Endpoints](../api/backend-endpoints.md) | Auth endpoints, token management, role-based access |

## Configuration & Scanning

| Document | Summary |
|----------|---------|
| [Security Scanning](../config/security-scanning.md) | SonarCloud, CodeRabbit (HIPAA-aware), Snyk (dependency/SAST/container) |
| [Environments](../config/environments.md) | Per-environment security policies and data handling |
| [Feature Flags](../config/feature-flags.md) | Security-related feature flags and rollout controls |

## Experiments

| Document | Summary |
|----------|---------|
| [POC Gap Analysis](../Experiments/04-POC-Gap-Analysis.md) | 5 critical HIPAA gaps identified in POC evaluation |
| [OpenClaw Setup Guide](../Experiments/05-OpenClaw-PMS-Developer-Setup-Guide.md) | HIPAA-hardened sandboxed agent deployment |
| [OpenClaw Developer Tutorial](../Experiments/05-OpenClaw-Developer-Tutorial.md) | Security reminders and approval tiers for autonomous agents |
