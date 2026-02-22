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
| Prompt Management (SUB-PM) | SUB-PM-v0.0 | 0 | 7 | 2026-02-22 |

**Note:** SUB-PR has 6 of 11 domain requirements with BE platform work (001-patient-crud feature), but strict rollup reduces domain-level "Verified" count since WEB/AND platform reqs are not started. SUB-CW, SUB-MM, SUB-RA, and SUB-PM remain at v0.0 with scaffold-only implementations.

## Platform Progress

### SUB-PR — Patient Records (38 platform reqs)

| Platform | Total Reqs | Verified | Implemented | Scaffolded | Not Started | Completion |
|---|---|---|---|---|---|---|
| BE | 11 | 3 | 2 | 0 | 6 | 45.5% |
| WEB | 4 | 0 | 0 | 1 | 3 | 0.0% |
| AND | 7 | 0 | 0 | 1 | 6 | 0.0% |
| AI | 3 | 0 | 0 | 0 | 3 | 0.0% |

### SUB-CW — Clinical Workflow (17 platform reqs)

| Platform | Total Reqs | Verified | Implemented | Scaffolded | Not Started | Completion |
|---|---|---|---|---|---|---|
| BE | 8 | 0 | 0 | 0 | 8 | 0.0% |
| WEB | 3 | 0 | 0 | 1 | 2 | 0.0% |
| AND | 3 | 0 | 0 | 1 | 2 | 0.0% |

### SUB-MM — Medication Management (13 platform reqs)

| Platform | Total Reqs | Verified | Implemented | Scaffolded | Not Started | Completion |
|---|---|---|---|---|---|---|
| BE | 9 | 0 | 0 | 0 | 9 | 0.0% |
| WEB | 2 | 0 | 0 | 1 | 1 | 0.0% |
| AND | 2 | 0 | 0 | 1 | 1 | 0.0% |

### SUB-RA — Reporting & Analytics (19 platform reqs)

| Platform | Total Reqs | Verified | Implemented | Scaffolded | Not Started | Completion |
|---|---|---|---|---|---|---|
| BE | 7 | 0 | 0 | 0 | 7 | 0.0% |
| WEB | 5 | 0 | 0 | 1 | 4 | 0.0% |
| AND | 5 | 0 | 0 | 1 | 4 | 0.0% |

### AI Infrastructure (SUB-*-AI)

| Subsystem | AI Reqs | Verified | Not Started | Repository | Completion |
|---|---|---|---|---|---|
| Patient Records (PR) | 6 | 0 | 6 | pms-ai | 0.0% |
| Prompt Management (PM) | 1 | 0 | 1 | pms-ai | 0.0% |
| **Total** | **7** | **0** | **7** | | **0.0%** |

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
