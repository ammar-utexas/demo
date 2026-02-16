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
| Patient Records (SUB-PR) | SUB-PR-v0.0 | 0 | 11 | 2026-02-16 |
| Clinical Workflow (SUB-CW) | SUB-CW-v0.0 | 0 | 8 | 2026-02-16 |
| Medication Management (SUB-MM) | SUB-MM-v0.0 | 0 | 9 | 2026-02-16 |
| Reporting & Analytics (SUB-RA) | SUB-RA-v0.0 | 0 | 7 | 2026-02-16 |

**Note:** All requirements are currently in "Placeholder" or "Not Started" status. SUB-PR was updated from 8 to 11 requirements after adding vision capabilities (SUB-PR-0009 through SUB-PR-0011). Subsystem versions will begin incrementing as requirements are implemented and verified through the testing strategy defined in [Testing Strategy](testing-strategy.md).

## Version History

### SUB-PR (Patient Records)

| Version | Date | Requirements Completed | Notes |
|---|---|---|---|
| SUB-PR-v0.0 | 2026-02-15 | — | Initial scaffold; CRUD stubs, encryption service, audit middleware in place |
| — | 2026-02-16 | — | Added vision endpoints (SUB-PR-0009, 0010, 0011) with stubs; total reqs now 11 |

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
