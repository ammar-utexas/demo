# Subsystem Requirements: Clinical Workflow (SUB-CW)

**Document ID:** PMS-SUB-CW-001
**Version:** 1.3
**Date:** 2026-02-17
**Parent:** [System Requirements](SYS-REQ.md)

---

## Scope

The Clinical Workflow subsystem manages encounter scheduling, status tracking, clinical notes, and care coordination. It is the primary workspace for physicians and nurses.

## Requirements

| Req ID | Parent | Description | Verification | Status |
|---|---|---|---|---|
| SUB-CW-0001 | SYS-REQ-0001 | Require authenticated session for all encounter operations | Test | Placeholder |
| SUB-CW-0002 | SYS-REQ-0005 | Enforce RBAC: physician/nurse can create/update; all roles can read | Test | Placeholder |
| SUB-CW-0003 | — | Support encounter lifecycle per the explicit state machine defined in SUB-CW-0007. Exception: emergency encounters (type = emergency) skip "scheduled" and are created directly in "in_progress" status (DC-CW-02). | Test | Placeholder |
| SUB-CW-0004 | SYS-REQ-0003 | Log all encounter access and status changes to the audit trail | Test | Placeholder |
| SUB-CW-0005 | SYS-REQ-0006 | Trigger clinical alerts when encounter notes indicate critical conditions. Alerts must be evaluated before status transitions to "completed" are committed — if the encounter has pending unacknowledged critical alerts, block the transition until the clinician acknowledges or overrides (DC-CW-03). | Test | Not Started |
| SUB-CW-0006 | — | Support encounter types: office_visit, telehealth, emergency, follow_up | Test | Placeholder |
| SUB-CW-0007 | — | Validate encounter status transitions against the explicit state machine: `scheduled → in_progress`, `scheduled → cancelled`, `in_progress → completed`, `in_progress → cancelled`. No transitions from terminal states (completed, cancelled). Emergency encounters may transition `created → in_progress` (see SUB-CW-0003, DC-CW-01, DC-CW-02). | Test | Not Started |
| SUB-CW-0008 | — | Associate encounters with exactly one patient via patient_id foreign key | Test | Placeholder |

## Platform Decomposition

### Backend (BE) — 8 requirements

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-CW-0001-BE | SUB-CW-0001 | Enforce JWT auth on all encounter API endpoints | `middleware/auth.py` | TST-CW-0001-BE | Placeholder |
| SUB-CW-0002-BE | SUB-CW-0002 | Enforce RBAC on encounter API endpoints | `middleware/auth.py:require_role` | TST-CW-0002-BE | Placeholder |
| SUB-CW-0003-BE | SUB-CW-0003 | REST endpoints for encounter lifecycle. Must serialize concurrent status transitions using `SELECT ... FOR UPDATE` or optimistic locking (version column) to prevent duplicate transitions (RC-BE-02). | `routers/encounters.py`, `models/encounter.py` | TST-CW-0003-BE | Placeholder |
| SUB-CW-0004-BE | SUB-CW-0004 | Audit log all encounter access and status changes. Must follow the audit event catalog (action strings: CREATE, READ, UPDATE, DELETE; resource_type: encounter) matching the pattern established by patient audit logging (PC-BE-03). | `services/audit_service.py` | TST-CW-0004-BE | Placeholder |
| SUB-CW-0005-BE | SUB-CW-0005 | Trigger clinical alerts for critical encounter conditions | — | TST-CW-0005-BE | Not Started |
| SUB-CW-0006-BE | SUB-CW-0006 | Validate encounter types (office_visit, telehealth, emergency, follow_up) | `models/encounter.py` | TST-CW-0006-BE | Placeholder |
| SUB-CW-0007-BE | SUB-CW-0007 | Validate encounter status transitions against the explicit state machine (see SUB-CW-0007). Enforce via `SELECT ... FOR UPDATE` to serialize concurrent transitions (RC-BE-02). | — | TST-CW-0007-BE | Not Started |
| SUB-CW-0008-BE | SUB-CW-0008 | Enforce patient_id FK constraint on encounters | `models/encounter.py` (FK) | TST-CW-0008-BE | Placeholder |

### Web Frontend (WEB) — 3 requirements

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-CW-0001-WEB | SUB-CW-0001 | Auth guard for encounter pages | `lib/auth.ts` | TST-CW-0001-WEB | Scaffolded |
| SUB-CW-0003-WEB | SUB-CW-0003 | Encounter lifecycle UI (list, create, status updates) | `app/encounters/` | TST-CW-0003-WEB | Not Started |
| SUB-CW-0006-WEB | SUB-CW-0006 | Encounter type selection in forms | `app/encounters/page.tsx` | TST-CW-0006-WEB | Not Started |

### Android (AND) — 3 requirements

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-CW-0001-AND | SUB-CW-0001 | Auth interceptor for encounter API calls | `data/api/AuthInterceptor.kt` | TST-CW-0001-AND | Scaffolded |
| SUB-CW-0003-AND | SUB-CW-0003 | Encounter lifecycle screens with Compose UI. Must implement offline-sync conflict resolution: sync requests include `version`/`updated_at`, backend 409 conflicts are queued and presented in a resolution UI (RC-AND-02). | `ui/encounters/` | TST-CW-0003-AND | Not Started |
| SUB-CW-0006-AND | SUB-CW-0006 | Encounter type selection in Compose forms | `ui/encounters/EncountersScreen.kt` | TST-CW-0006-AND | Not Started |
