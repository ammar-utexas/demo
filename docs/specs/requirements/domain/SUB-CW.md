# Subsystem Requirements: Clinical Workflow (SUB-CW)

**Document ID:** PMS-SUB-CW-001
**Version:** 1.3
**Date:** 2026-02-17
**Parent:** [System Requirements](../SYS-REQ.md)

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

| Platform | File | Req Count |
|----------|------|-----------|
| Backend (BE) | [SUB-BE](../platform/SUB-BE.md#clinical-workflow-sub-cw) | 8 |
| Web Frontend (WEB) | [SUB-WEB](../platform/SUB-WEB.md#clinical-workflow-sub-cw) | 3 |
| Android (AND) | [SUB-AND](../platform/SUB-AND.md#clinical-workflow-sub-cw) | 3 |
