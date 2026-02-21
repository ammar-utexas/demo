# Subsystem Requirements: Medication Management (SUB-MM)

**Document ID:** PMS-SUB-MM-001
**Version:** 1.3
**Date:** 2026-02-17
**Parent:** [System Requirements](../SYS-REQ.md)

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

| Platform | File | Req Count |
|----------|------|-----------|
| Backend (BE) | [SUB-MM-BE](../platform/SUB-MM-BE.md) | 9 |
| Web Frontend (WEB) | [SUB-MM-WEB](../platform/SUB-MM-WEB.md) | 2 |
| Android (AND) | [SUB-MM-AND](../platform/SUB-MM-AND.md) | 2 |
