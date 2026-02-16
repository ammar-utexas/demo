# Subsystem Requirements: Clinical Workflow (SUB-CW)

**Document ID:** PMS-SUB-CW-001
**Version:** 1.1
**Date:** 2026-02-16
**Parent:** [System Requirements](SYS-REQ.md)

---

## Scope

The Clinical Workflow subsystem manages encounter scheduling, status tracking, clinical notes, and care coordination. It is the primary workspace for physicians and nurses.

## Requirements

| Req ID | Parent | Description | Verification | Status |
|---|---|---|---|---|
| SUB-CW-0001 | SYS-REQ-0001 | Require authenticated session for all encounter operations | Test | Placeholder |
| SUB-CW-0002 | SYS-REQ-0005 | Enforce RBAC: physician/nurse can create/update; all roles can read | Test | Placeholder |
| SUB-CW-0003 | — | Support encounter lifecycle: scheduled → in_progress → completed/cancelled | Test | Placeholder |
| SUB-CW-0004 | SYS-REQ-0003 | Log all encounter access and status changes to the audit trail | Test | Placeholder |
| SUB-CW-0005 | SYS-REQ-0006 | Trigger clinical alerts when encounter notes indicate critical conditions | Test | Not Started |
| SUB-CW-0006 | — | Support encounter types: office_visit, telehealth, emergency, follow_up | Test | Placeholder |
| SUB-CW-0007 | — | Validate encounter status transitions (e.g., cannot go from completed to scheduled) | Test | Not Started |
| SUB-CW-0008 | — | Associate encounters with exactly one patient via patient_id foreign key | Test | Placeholder |

## Implementation Mapping

| Req ID | Backend Module | Frontend Component | Android Screen | Test Case(s) |
|---|---|---|---|---|
| SUB-CW-0001 | `middleware/auth.py` | `lib/auth.ts` | `data/api/AuthInterceptor.kt` | TST-CW-0001 |
| SUB-CW-0002 | `middleware/auth.py:require_role` | — | — | TST-CW-0002 |
| SUB-CW-0003 | `routers/encounters.py`, `models/encounter.py` | `app/encounters/` | `ui/encounters/` | TST-CW-0003 |
| SUB-CW-0004 | `services/audit_service.py` | — | — | TST-CW-0004 |
| SUB-CW-0005 | — | — | — | TST-CW-0005 |
| SUB-CW-0006 | `models/encounter.py` | `app/encounters/page.tsx` | `ui/encounters/EncountersScreen.kt` | TST-CW-0006 |
| SUB-CW-0007 | — | — | — | TST-CW-0007 |
| SUB-CW-0008 | `models/encounter.py` (FK) | — | — | TST-CW-0008 |
