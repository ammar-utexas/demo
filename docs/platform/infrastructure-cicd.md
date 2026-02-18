# Platform: Infrastructure/CI-CD

**Tech Stack:** Docker, GitHub Actions, SonarCloud, CodeRabbit, Snyk, semantic versioning

## Architecture & Strategy

| Document | Summary |
|----------|---------|
| [ADR-0002: Multi-Repo Structure](../architecture/0002-multi-repo-structure.md) | Independent repos with focused CI pipelines |
| [ADR-0006: Release Management Strategy](../architecture/0006-release-management-strategy.md) | Semantic versioning, four-environment deployment pipeline |

## CI/CD & Quality

| Document | Summary |
|----------|---------|
| [Security Scanning](../config/security-scanning.md) | SonarCloud quality gates, CodeRabbit AI review, Snyk dependency/SAST/container scanning, Docker CI workflows |
| [Release Process](../config/release-process.md) | Feature dev, RC creation, QA/staging gates, production deploy, rollback, hotfix |
| [Release Compatibility Matrix](../specs/release-compatibility-matrix.md) | Tested version combinations for production certification |

## Environments & Deployment

| Document | Summary |
|----------|---------|
| [Environments](../config/environments.md) | Dev, QA, Staging, Production environments with triggers and data policies |
| [Jetson Deployment Guide](../config/jetson-deployment.md) | Docker-based edge deployment with docker-compose |
| [Feature Flags](../config/feature-flags.md) | Per-environment feature flag state management |

## Tool Deployments

| Document | Summary |
|----------|---------|
| [Tambo Setup Guide](../Experiments/00-Tambo-PMS-Developer-Setup-Guide.md) | NestJS + PostgreSQL Docker self-hosting |
| [OpenClaw Setup Guide](../Experiments/05-OpenClaw-PMS-Developer-Setup-Guide.md) | HIPAA-hardened Docker deployment with sandboxed execution |
| [OpenClaw PMS Integration PRD](../Experiments/05-PRD-OpenClaw-PMS-Integration.md) | Scheduled background workflow infrastructure |
