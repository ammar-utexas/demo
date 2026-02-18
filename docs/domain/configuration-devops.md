# Domain: Configuration & DevOps

Dependencies, environment setup, CI/CD pipelines, deployment configuration, and infrastructure tooling.

## Project Setup

| Document | Summary |
|----------|---------|
| [Project Setup](../config/project-setup.md) | Quick-start guide: cloning repos, installing deps, running servers, executing tests |
| [Dependencies](../config/dependencies.md) | All libraries and versions for Backend (Python), Frontend (Node.js), Android (Kotlin/Gradle) |
| [Environments](../config/environments.md) | Four deployment environments plus Jetson edge with URLs, triggers, data policies |

## Architecture

| Document | Summary |
|----------|---------|
| [ADR-0001: Repo-Based Knowledge Management](../architecture/0001-repo-based-knowledge-management.md) | Markdown in repo as single source of truth |
| [ADR-0002: Multi-Repo Structure](../architecture/0002-multi-repo-structure.md) | Separate repos with shared docs submodule |
| [ADR-0006: Release Management](../architecture/0006-release-management-strategy.md) | CI/CD pipeline strategy and deployment gates |

## Security & Quality

| Document | Summary |
|----------|---------|
| [Security Scanning](../config/security-scanning.md) | SonarCloud, CodeRabbit, Snyk configuration and Docker CI workflows |
| [Feature Flags](../config/feature-flags.md) | Flag implementation in Python/TypeScript/Kotlin with per-environment state |

## Edge Deployment

| Document | Summary |
|----------|---------|
| [ADR-0007: Jetson Edge Deployment](../architecture/0007-jetson-thor-edge-deployment.md) | Full PMS stack on NVIDIA Jetson Thor |
| [Jetson Deployment Guide](../config/jetson-deployment.md) | JetPack 7.x flashing, docker-compose deployment, Wi-Fi 7, GPU allocation |

## Release Process

| Document | Summary |
|----------|---------|
| [Release Process](../config/release-process.md) | End-to-end release workflow with rollback and hotfix procedures |
| [Release Compatibility Matrix](../specs/release-compatibility-matrix.md) | Tested version combinations for production certification |

## Tool Evaluations

| Document | Summary |
|----------|---------|
| [Tambo Setup Guide](../experiments/00-Tambo-PMS-Developer-Setup-Guide.md) | NestJS + PostgreSQL Docker self-hosting for Tambo |
| [Storybook Getting Started](../experiments/01-Storybook-Getting-Started.md) | Storybook 8 installation in Next.js 15 project |
| [OpenClaw Setup Guide](../experiments/05-OpenClaw-PMS-Developer-Setup-Guide.md) | Docker-based agent deployment with sandboxed execution |
