# Subsystem Version Tracking

**Related ADR:** [ADR-0006: Release Management Strategy](../architecture/0006-release-management-strategy.md)

---

## Versioning Rules

- Format: `SUB-XX-vMAJOR.MINOR`
- **MINOR** increments when a requirement is implemented and passes all verification tests
- **MAJOR** increments at significant milestones (e.g., all core requirements for a subsystem are complete)
- Version updates are recorded here when the requirement's status changes from "Not Started" or "Placeholder" to "Verified"

## Current Subsystem Versions

| Subsystem | Current Version | Requirements Complete | Requirements Total | Last Updated |
|---|---|---|---|---|
| Patient Records (SUB-PR) | SUB-PR-v0.6 | 6 | 11 | 2026-02-16 |
| Clinical Workflow (SUB-CW) | SUB-CW-v0.0 | 0 | 8 | 2026-02-16 |
| Medication Management (SUB-MM) | SUB-MM-v0.0 | 0 | 9 | 2026-02-16 |
| Reporting & Analytics (SUB-RA) | SUB-RA-v0.0 | 0 | 7 | 2026-02-16 |

**Note:** SUB-PR has 6 of 11 requirements implemented/verified (001-patient-crud feature). SUB-CW, SUB-MM, and SUB-RA remain at v0.0 with scaffold-only implementations.

## Version History

### SUB-PR (Patient Records)

| Version | Date | Requirements Completed | Notes |
|---|---|---|---|
| SUB-PR-v0.0 | 2026-02-15 | — | Initial scaffold; CRUD stubs, encryption service, audit middleware in place |
| — | 2026-02-16 | — | Added vision endpoints (SUB-PR-0009, 0010, 0011) with stubs; total reqs now 11 |
| SUB-PR-v0.6 | 2026-02-16 | SUB-PR-0001, 0002, 0003, 0004, 0005, 0006 | 001-patient-crud feature: full CRUD with 16 integration tests (0003), SSN encryption via Fernet (0004), email uniqueness (0006), JWT auth (0001), RBAC (0002), audit logging (0005). 157 tests pass on PostgreSQL. |

### SUB-CW (Clinical Workflow)

| Version | Date | Requirements Completed | Notes |
|---|---|---|---|
| SUB-CW-v0.0 | 2026-02-15 | — | Initial scaffold; encounter model, lifecycle stubs, status enum defined |

### SUB-MM (Medication Management)

| Version | Date | Requirements Completed | Notes |
|---|---|---|---|
| SUB-MM-v0.0 | 2026-02-15 | — | Initial scaffold; medication model, interaction checker stub, prescription stubs |

### SUB-RA (Reporting & Analytics)

| Version | Date | Requirements Completed | Notes |
|---|---|---|---|
| SUB-RA-v0.0 | 2026-02-15 | — | Initial scaffold; report endpoints with stub data |
