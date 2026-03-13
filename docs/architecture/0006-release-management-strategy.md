# ADR-0006: Release Management Strategy

**Status:** Accepted
**Date:** 2026-02-15
**Deciders:** Development Team

---

## Context

The PMS spans four implementation repositories (pms-backend, pms-frontend, pms-android, pms-ai) plus a shared documentation submodule (demo). The system must comply with HIPAA regulations, requiring auditable, controlled releases. All repos are currently at v0.1.0 with no CI/CD, no changelogs, no git tags, and no formal release process.

We need a release strategy that:
- Allows each repo to evolve at its own pace
- Provides tight control over what features ship and when
- Supports a multi-environment deployment pipeline
- Enables safe rollback without downtime
- Tracks which combinations of repo versions have been tested together

## Decision

### 1. Independent Semantic Versioning per Repository

Each repository follows [Semantic Versioning 2.0.0](https://semver.org/) independently:
- **MAJOR** — Breaking API/schema changes or backwards-incompatible behavioral changes
- **MINOR** — New features, new endpoints, new screens (backwards-compatible)
- **PATCH** — Bug fixes, security patches, documentation corrections

Versions are defined in each repo's native package manifest:
- `pms-backend`: `pyproject.toml` → `version = "X.Y.Z"`
- `pms-frontend`: `package.json` → `"version": "X.Y.Z"`
- `pms-android`: `app/build.gradle.kts` → `versionName = "X.Y.Z"`
- `pms-ai`: `pyproject.toml` → `version = "X.Y.Z"`

### 2. Subsystem-Level Version Tracking

Each subsystem (SUB-PR, SUB-CW, SUB-MM, SUB-RA, SUB-PM) has its own version tracked in `docs/specs/subsystem-versions.md`:
- Format: `SUB-XX-vMAJOR.MINOR`
- MINOR increments when a requirement is implemented and tested
- MAJOR increments at significant milestones (e.g., all core requirements complete)

### 3. Feature Flags for Release Control

Feature flags decouple deployment from release:
- Flags are named after requirement IDs (e.g., `FEATURE_SUB_PR_0007_PATIENT_SEARCH`)
- Flags are environment variables loaded at startup, defaulting to `false`
- Each environment (Dev/QA/Staging/Prod) can independently toggle flags
- Lifecycle: Create → Develop → Test-Dev → Test-QA → Test-Staging → Enable-Prod → Monitor → Remove

### 4. Four-Environment Pipeline

| Environment | Deploy Trigger | Data | Approval Gate |
|---|---|---|---|
| Dev | Auto on merge to `main` | Synthetic | None (CI must pass) |
| QA | Manual trigger | Synthetic | CI pass |
| Staging | RC tag deploy | Sanitized prod copy | QA team sign-off |
| Production | Manual promotion | Real PHI | Change control board |

### 5. Keep a Changelog

Each repo maintains a `CHANGELOG.md` following [Keep a Changelog 1.1.0](https://keepachangelog.com/) format, with requirement IDs referenced in each entry.

## Options Considered

### Option A: Monorepo with Single Version
- **Pros:** Simpler versioning, atomic cross-component changes
- **Cons:** Forces lockstep releases, large CI builds, three different tech stacks in one repo
- **Rejected:** Conflicting toolchains and forced coupling outweigh simplicity

### Option B: Independent Repos with Coordinated Releases
- **Pros:** Independent cadence, smaller CI, team autonomy
- **Cons:** Must track cross-repo compatibility separately
- **Selected:** Compatibility matrix document addresses the coordination concern

### Option C: Release Trains (Fixed Schedule, Ship What's Ready)
- **Pros:** Predictable schedule
- **Cons:** Features may slip or ship half-ready
- **Rejected:** Feature flags give better control than time-based cutoffs

## Consequences

### Positive
- Each team can release independently without blocking others
- Feature flags allow deploying code to production without exposing incomplete features
- Rollback is fast: toggle flag off (zero downtime) or redeploy previous tag
- Full audit trail of what was deployed, when, and what was enabled
- Subsystem versions give fine-grained progress visibility

### Negative
- Must maintain a compatibility matrix mapping tested version combinations
- Feature flag cleanup is a recurring chore (flags must be removed after stabilization)
- Developers must remember to guard new code behind flags

### Risks
- Flag proliferation if cleanup is neglected — mitigated by flag lifecycle policy
- Version drift between repos — mitigated by system-level integration tests (TST-SYS-*)
