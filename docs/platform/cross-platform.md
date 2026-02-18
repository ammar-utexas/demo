# Platform: Cross-Platform

Documentation that spans all platforms or applies system-wide.

## System Specifications

| Document | Summary |
|----------|---------|
| [System Spec](../specs/system-spec.md) | System scope, 3 deployable components, 4 subsystems, user roles, HIPAA constraints |
| [SYS-REQ](../specs/requirements/SYS-REQ.md) | 10 system-level requirements with acceptance criteria |
| [Requirements Governance](../quality/processes/requirements-governance.md) | Governance procedures, conflict analysis across platforms |

## Traceability & Testing

| Document | Summary |
|----------|---------|
| [Traceability Matrix](../testing/traceability-matrix.md) | 69 platform reqs across 4 platforms, 157 passing tests, 22.2% coverage |
| [Testing Strategy](../testing/testing-strategy.md) | Platform-scoped test naming, testing pyramid, per-repo commands |
| [Subsystem Versions](../specs/subsystem-versions.md) | Per-subsystem version tracking across all platforms |

## Architecture & Structure

| Document | Summary |
|----------|---------|
| [ADR-0001: Repo-Based Knowledge Management](../architecture/0001-repo-based-knowledge-management.md) | Markdown in repo as single source of truth |
| [ADR-0002: Multi-Repo Structure](../architecture/0002-multi-repo-structure.md) | Separate repos with shared docs submodule |
| [ADR-0006: Release Management Strategy](../architecture/0006-release-management-strategy.md) | Independent versioning, deployment pipeline |

## Configuration

| Document | Summary |
|----------|---------|
| [Dependencies](../config/dependencies.md) | Libraries and versions for all three platforms |
| [Project Setup](../config/project-setup.md) | Quick-start guide for all repos |
| [Environments](../config/environments.md) | Four environments plus Jetson edge |
| [Feature Flags](../config/feature-flags.md) | 12 flags with Python/TypeScript/Kotlin implementation examples |
| [Release Process](../config/release-process.md) | Release workflow applicable to all repos |
| [Release Compatibility Matrix](../specs/release-compatibility-matrix.md) | Cross-repo version compatibility |
