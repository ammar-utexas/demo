# Subsystem Requirements: Medication Management (SUB-MM)

**Document ID:** PMS-SUB-MM-001
**Version:** 1.3
**Date:** 2026-02-17
**Parent:** [System Requirements](SYS-REQ.md)

---

## Scope

The Medication Management subsystem handles the medication catalog, prescriptions, drug interaction checking, and formulary management. It is the critical safety layer for prescription workflows.

## Requirements

| Req ID | Parent | Description | Verification | Status |
|---|---|---|---|---|
| SUB-MM-0001 | SYS-REQ-0006 | Check new prescriptions against patient's active medications for interactions within 5 seconds. Interaction checks must operate on medication IDs (RxNorm codes), not on encrypted PHI, to avoid decryption latency (DC-MM-01). | Test | Placeholder |
| SUB-MM-0002 | SYS-REQ-0006 | Classify drug interactions by severity: contraindicated, major, moderate, minor | Test | Placeholder |
| SUB-MM-0003 | SYS-REQ-0002 | Encrypt prescription PHI (patient name, dosage instructions) at rest using AES-256. Drug interaction lookup keys (RxNorm codes) must be stored in plaintext to support the 5-second interaction check SLA (DC-MM-01). | Test / Inspection | Placeholder |
| SUB-MM-0004 | SYS-REQ-0003 | Log all prescription events (create, modify, dispense) with prescriber ID and timestamp | Test | Placeholder |
| SUB-MM-0005 | SYS-REQ-0004 | Support FHIR R4 MedicationRequest and MedicationDispense resources | Test / Demo | Not Started |
| SUB-MM-0006 | SYS-REQ-0001 | Require authenticated session for all medication operations | Test | Placeholder |
| SUB-MM-0007 | SYS-REQ-0005 | Enforce RBAC: only physicians can prescribe; nurses can view; pharmacists can dispense. Status transition-to-role mapping: physician can cancel (override), pharmacist can mark completed (upon final dispense), nurse cannot change status (DC-MM-03). | Test | Placeholder |
| SUB-MM-0008 | — | Support prescription status lifecycle: active → completed/cancelled. Cancellation is a terminal state — sets refills_remaining to 0 and is irreversible. Cancelled prescriptions cannot be reactivated; a new prescription must be created if the medication is needed again (DC-MM-02). | Test | Placeholder |
| SUB-MM-0009 | — | Track remaining refills and prevent prescriptions with zero refills from being filled. Refill decrement must be atomic (`UPDATE ... SET refills_remaining = refills_remaining - 1 WHERE refills_remaining > 0`); check affected row count to detect concurrent claims (RC-BE-08). | Test | Not Started |

## Platform Decomposition

### Backend (BE) — 9 requirements

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-MM-0001-BE | SUB-MM-0001 | Drug interaction check API endpoint (< 5 sec response). The interaction check must complete synchronously before the prescription is committed — implement as a pre-save hook: validate → check interactions → save (RC-BE-03). Must use `REPEATABLE READ` isolation for a consistent medication snapshot during concurrent changes (RC-BE-07). Use a dedicated connection pool or priority queue for medication-safety queries to avoid contention with CRUD load (PC-BE-05). | `services/interaction_checker.py` | TST-MM-0001-BE | Placeholder |
| SUB-MM-0002-BE | SUB-MM-0002 | Interaction severity classification logic | `services/interaction_checker.py` | TST-MM-0002-BE | Placeholder |
| SUB-MM-0003-BE | SUB-MM-0003 | Encrypt prescription PHI at rest using AES-256 | `services/encryption_service.py` | TST-MM-0003-BE | Placeholder |
| SUB-MM-0004-BE | SUB-MM-0004 | Audit log all prescription events. Must follow the audit event catalog (action strings: CREATE, READ, UPDATE, DELETE; resource_type: prescription) matching the pattern established by patient audit logging (PC-BE-03). | `services/audit_service.py` | TST-MM-0004-BE | Placeholder |
| SUB-MM-0005-BE | SUB-MM-0005 | FHIR R4 MedicationRequest/MedicationDispense endpoints | — | TST-MM-0005-BE | Not Started |
| SUB-MM-0006-BE | SUB-MM-0006 | Enforce JWT auth on all medication API endpoints | `middleware/auth.py` | TST-MM-0006-BE | Placeholder |
| SUB-MM-0007-BE | SUB-MM-0007 | Enforce RBAC on medication endpoints (physician prescribe, nurse view, pharmacist dispense) | `middleware/auth.py:require_role` | TST-MM-0007-BE | Placeholder |
| SUB-MM-0008-BE | SUB-MM-0008 | Prescription status lifecycle API (active → completed/cancelled). New prescriptions must not be committed until the interaction check (SUB-MM-0001-BE) completes. Contraindicated interactions reject the save; major/moderate interactions save with "pending_review" status requiring prescriber acknowledgment (RC-BE-03). | `models/medication.py` | TST-MM-0008-BE | Placeholder |
| SUB-MM-0009-BE | SUB-MM-0009 | Refill tracking and zero-refill prevention logic. Must use atomic update (`UPDATE ... SET refills_remaining = refills_remaining - 1 WHERE id = ? AND refills_remaining > 0`); check affected row count — if 0, the refill was already claimed. Do not use read-then-write in application code (RC-BE-08). | — | TST-MM-0009-BE | Not Started |

### Web Frontend (WEB) — 2 requirements

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-MM-0001-WEB | SUB-MM-0001 | Drug interaction warning display on medication page | `app/medications/page.tsx` | TST-MM-0001-WEB | Not Started |
| SUB-MM-0006-WEB | SUB-MM-0006 | Auth guard for medication pages | `lib/auth.ts` | TST-MM-0006-WEB | Scaffolded |

### Android (AND) — 2 requirements

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-MM-0001-AND | SUB-MM-0001 | Drug interaction warning display on medications screen | `ui/medications/MedicationsScreen.kt` | TST-MM-0001-AND | Not Started |
| SUB-MM-0006-AND | SUB-MM-0006 | Auth interceptor for medication API calls | `data/api/AuthInterceptor.kt` | TST-MM-0006-AND | Scaffolded |
