# Subsystem Requirements: Medication Management (SUB-MM)

**Document ID:** PMS-SUB-MM-001
**Version:** 1.1
**Date:** 2026-02-16
**Parent:** [System Requirements](SYS-REQ.md)

---

## Scope

The Medication Management subsystem handles the medication catalog, prescriptions, drug interaction checking, and formulary management. It is the critical safety layer for prescription workflows.

## Requirements

| Req ID | Parent | Description | Verification | Status |
|---|---|---|---|---|
| SUB-MM-0001 | SYS-REQ-0006 | Check new prescriptions against patient's active medications for interactions within 5 seconds | Test | Placeholder |
| SUB-MM-0002 | SYS-REQ-0006 | Classify drug interactions by severity: contraindicated, major, moderate, minor | Test | Placeholder |
| SUB-MM-0003 | SYS-REQ-0002 | Encrypt all prescription data containing PHI using AES-256 | Test / Inspection | Placeholder |
| SUB-MM-0004 | SYS-REQ-0003 | Log all prescription events (create, modify, dispense) with prescriber ID and timestamp | Test | Placeholder |
| SUB-MM-0005 | SYS-REQ-0004 | Support FHIR R4 MedicationRequest and MedicationDispense resources | Test / Demo | Not Started |
| SUB-MM-0006 | SYS-REQ-0001 | Require authenticated session for all medication operations | Test | Placeholder |
| SUB-MM-0007 | SYS-REQ-0005 | Enforce RBAC: only physicians can prescribe; nurses can view; pharmacists can dispense | Test | Placeholder |
| SUB-MM-0008 | — | Support prescription status lifecycle: active → completed/cancelled | Test | Placeholder |
| SUB-MM-0009 | — | Track remaining refills and prevent prescriptions with zero refills from being filled | Test | Not Started |

## Implementation Mapping

| Req ID | Backend Module | Frontend Component | Android Screen | Test Case(s) |
|---|---|---|---|---|
| SUB-MM-0001 | `services/interaction_checker.py` | `app/medications/page.tsx` | `ui/medications/MedicationsScreen.kt` | TST-MM-0001 |
| SUB-MM-0002 | `services/interaction_checker.py` | — | — | TST-MM-0002 |
| SUB-MM-0003 | `services/encryption_service.py` | — | — | TST-MM-0003 |
| SUB-MM-0004 | `services/audit_service.py` | — | — | TST-MM-0004 |
| SUB-MM-0005 | — | — | — | TST-MM-0005 |
| SUB-MM-0006 | `middleware/auth.py` | `lib/auth.ts` | `data/api/AuthInterceptor.kt` | TST-MM-0006 |
| SUB-MM-0007 | `middleware/auth.py:require_role` | — | — | TST-MM-0007 |
| SUB-MM-0008 | `models/medication.py` | — | — | TST-MM-0008 |
| SUB-MM-0009 | — | — | — | TST-MM-0009 |
