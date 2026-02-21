# ADR-0020: Feature Flag Strategy

**Date:** 2026-02-21
**Status:** Accepted
**Deciders:** Development Team

---

## Context

The Dermatology CDS module (SYS-REQ-0012) introduces multiple capabilities across three implementation phases: classification (Phase 1), similarity search + risk scoring (Phase 2), and edge deployment + model updates + longitudinal tracking (Phase 3). Each capability has dependencies on infrastructure (CDS service, pgvector, model weights) and must be independently enabled/disabled during phased rollout.

The existing PMS uses a feature flag registry (docs/config/feature-flags.md) established in ADR-0006 for release management. The dermatology module needs granular per-requirement flags that integrate with this existing system.

## Options Considered

1. **Granular per-requirement flags** — One feature flag per functional capability (classification, similarity, risk scoring, longitudinal tracking, Android on-device, reporting dashboard), integrating with the existing flag registry.
   - Pros: Fine-grained control, independent rollout per capability, integrates with existing system, supports A/B testing.
   - Cons: More flags to manage, potential for inconsistent states.

2. **Single module-level flag** — One flag (`DERM_CDS_ENABLED`) that enables or disables the entire dermatology module.
   - Pros: Simple, binary on/off.
   - Cons: All-or-nothing rollout, can't deploy classification without similarity search, can't test individual capabilities.

3. **Phase-based flags** — Three flags: `DERM_PHASE_1`, `DERM_PHASE_2`, `DERM_PHASE_3`, each enabling a bundle of capabilities.
   - Pros: Simpler than per-requirement, maps to implementation phases.
   - Cons: Phases bundle unrelated capabilities (e.g., Phase 2 includes both similarity search and Android on-device), no individual control.

4. **No flags (always-on)** — Deploy all capabilities as they are implemented, with no flag control.
   - Pros: No flag management overhead.
   - Cons: Cannot disable broken capabilities without code rollback, cannot do phased deployment to specific clinics.

## Decision

Use **granular per-requirement feature flags** for the Dermatology CDS module, with one flag per functional capability, integrating with the existing PMS feature flag registry.

## Rationale

1. **Independent rollout** — Classification can be enabled before similarity search is ready. Longitudinal tracking can be deployed to select clinics for feedback. Android on-device inference can be tested with a subset of devices.
2. **Infrastructure decoupling** — If pgvector isn't configured (e.g., development environment), similarity search flags are off but classification still works.
3. **Graceful degradation** — If the CDS service is down, the backend checks the classification flag and returns a clear "service unavailable" message rather than cryptic errors.
4. **Per-environment control** — Development enables all flags, QA enables selectively, staging mirrors production, production enables progressively.
5. **Existing pattern** — The PMS already has a feature flag registry (ADR-0006, docs/config/feature-flags.md) with naming conventions, lifecycle states, and per-environment configuration. The derm flags follow the same pattern.
6. **Dependency validation** — Flags express dependencies: enabling `DERM_SIMILARITY_SEARCH` requires `DERM_CLASSIFICATION` to also be enabled. The flag system validates these dependencies at startup.

## Flag Registry

| Flag Name | Depends On | Controls | Default |
|---|---|---|---|
| `DERM_CLASSIFICATION` | (none) | Lesion image upload and AI classification | `false` |
| `DERM_SIMILARITY_SEARCH` | `DERM_CLASSIFICATION` | Similar ISIC reference image gallery | `false` |
| `DERM_RISK_SCORING` | `DERM_CLASSIFICATION` | Risk level calculation and referral urgency | `false` |
| `DERM_LONGITUDINAL_TRACKING` | `DERM_CLASSIFICATION` | Lesion change detection and timeline | `false` |
| `DERM_ANDROID_ON_DEVICE` | (none) | TFLite on-device classification on Android | `false` |
| `DERM_REPORTING_DASHBOARD` | `DERM_CLASSIFICATION` | Dermatology analytics in /api/reports | `false` |

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| Single module flag | All-or-nothing, can't test or deploy capabilities independently |
| Phase-based flags | Bundles unrelated capabilities, can't control individual features |
| No flags | Cannot disable broken capabilities without rollback, no phased deployment |
| External flag service (LaunchDarkly) | Cloud dependency, overkill for on-premises deployment, additional cost |

## Trade-offs

- **Flag proliferation** — Six new flags adds management overhead. Mitigated by clear naming convention (`DERM_` prefix), dependency graph, and lifecycle documentation.
- **Inconsistent states** — Enabling `DERM_SIMILARITY_SEARCH` without `DERM_CLASSIFICATION` would be invalid. Mitigated by startup dependency validation that fails fast with a clear error message.
- **Testing matrix** — Each flag combination is a potential test configuration. Mitigated by defining supported combinations: all-off, classification-only, classification+risk, all-on.

## Consequences

- Six new entries in `docs/config/feature-flags.md` with `DERM_` prefix.
- Backend endpoints check flag state before processing: disabled flags return HTTP 404 (feature not available) rather than 503 (service error).
- Frontend components conditionally render dermatology UI elements based on flag state exposed via `/api/config/features`.
- Android app checks `DERM_ANDROID_ON_DEVICE` flag (synced from backend on app startup) before showing the dermoscopy camera option.
- Docker Compose health checks for the CDS service are independent of feature flags — the service always runs, but endpoints are gated.
- Flag state transitions are logged to the audit trail for compliance.
- The CDS service itself has no feature flags — it always serves all endpoints. Gating happens at the backend and frontend layers.

## References

- Related PRD: docs/experiments/18-PRD-ISICArchive-PMS-Integration.md (Implementation Phases)
- Related Requirements: SYS-REQ-0012, all SUB-PR-0013 through SUB-PR-0016, SUB-RA-0008
- Related ADRs: ADR-0006 (Release Management Strategy), ADR-0008 (CDS Microservice), ADR-0018 (Inter-Service Communication)
