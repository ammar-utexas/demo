# Domain: Release Management

Versioning strategy, deployment pipelines, compatibility tracking, and feature flag lifecycle across all platforms.

## Architecture & Strategy

| Document | Summary |
|----------|---------|
| [ADR-0006: Release Management Strategy](../architecture/0006-release-management-strategy.md) | Independent semantic versioning per repo, subsystem version tracking, four-environment pipeline |

## Processes & Configuration

| Document | Summary |
|----------|---------|
| [Release Process](../config/release-process.md) | Step-by-step workflow: feature dev, RC creation, QA/staging gates, production deploy, rollback, hotfix |
| [Feature Flags](../config/feature-flags.md) | 12 flags tied to requirement IDs, naming convention, lifecycle stages, per-environment state |
| [Environments](../config/environments.md) | Four deployment environments (Dev, QA, Staging, Production) plus Jetson edge |

## Tracking & Compatibility

| Document | Summary |
|----------|---------|
| [Subsystem Versions](../specs/subsystem-versions.md) | Per-subsystem version tracking with platform progress tables and version history |
| [Release Compatibility Matrix](../specs/release-compatibility-matrix.md) | Tested version combinations across repos for production certification |
