# Subsystem Requirements: Patient Records (SUB-PR)

**Document ID:** PMS-SUB-PR-001
**Version:** 1.0
**Date:** 2026-02-15
**Parent:** [System Requirements](SYS-REQ.md)

---

## Scope

The Patient Records subsystem manages patient demographics, contact information, encrypted PHI, and consent records. It is the foundational data layer for all other subsystems.

## Requirements

| Req ID | Parent | Description | Verification | Status |
|---|---|---|---|---|
| SUB-PR-0001 | SYS-REQ-0001 | Require authenticated session for all patient data access | Test | Placeholder |
| SUB-PR-0002 | SYS-REQ-0005 | Enforce RBAC: all roles can read; only physician/nurse/admin can write | Test | Placeholder |
| SUB-PR-0003 | — | Support CRUD operations for patient demographics (name, DOB, gender, contact) | Test | Placeholder |
| SUB-PR-0004 | SYS-REQ-0002 | Encrypt SSN and other PHI fields at rest using AES-256 via encryption_service | Test / Inspection | Placeholder |
| SUB-PR-0005 | SYS-REQ-0003 | Log all patient record access and modifications to the audit trail | Test | Placeholder |
| SUB-PR-0006 | — | Validate patient email uniqueness across the system | Test | Placeholder |
| SUB-PR-0007 | — | Support patient search by last name, date of birth, or ID | Test | Not Started |
| SUB-PR-0008 | — | Return paginated results for patient list queries (default: 20 per page) | Test | Not Started |

## Implementation Mapping

| Req ID | Backend Module | Frontend Component | Android Screen | Test Case(s) |
|---|---|---|---|---|
| SUB-PR-0001 | `middleware/auth.py` | `lib/auth.ts` | `data/api/AuthInterceptor.kt` | TST-PR-0001 |
| SUB-PR-0002 | `middleware/auth.py:require_role` | — | — | TST-PR-0002 |
| SUB-PR-0003 | `routers/patients.py`, `models/patient.py` | `app/patients/` | `ui/patients/` | TST-PR-0003 |
| SUB-PR-0004 | `services/encryption_service.py` | — | — | TST-PR-0004 |
| SUB-PR-0005 | `services/audit_service.py`, `middleware/audit.py` | — | — | TST-PR-0005 |
| SUB-PR-0006 | `models/patient.py` (unique constraint) | — | — | TST-PR-0006 |
| SUB-PR-0007 | — | — | — | TST-PR-0007 |
| SUB-PR-0008 | — | — | — | TST-PR-0008 |
