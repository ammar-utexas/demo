# Subsystem Requirements: Patient Records (SUB-PR)

**Document ID:** PMS-SUB-PR-001
**Version:** 1.2
**Date:** 2026-02-16
**Parent:** [System Requirements](SYS-REQ.md)

---

## Scope

The Patient Records subsystem manages patient demographics, contact information, encrypted PHI, and consent records. It is the foundational data layer for all other subsystems.

## Requirements

| Req ID | Parent | Description | Verification | Status |
|---|---|---|---|---|
| SUB-PR-0001 | SYS-REQ-0001 | Require authenticated session for all patient data access | Test | Implemented |
| SUB-PR-0002 | SYS-REQ-0005 | Enforce RBAC: admin/physician/nurse read & create; admin/physician update; admin deactivate | Test | Implemented |
| SUB-PR-0003 | — | Support CRUD operations for patient demographics (name, DOB, gender, contact) | Test | Verified |
| SUB-PR-0004 | SYS-REQ-0002 | Encrypt SSN and other PHI fields at rest using Fernet (AES-128-CBC) via encryption_service; production migration to AES-256-GCM planned | Test / Inspection | Verified |
| SUB-PR-0005 | SYS-REQ-0003 | Log all patient record access and modifications to the audit trail | Test | Implemented |
| SUB-PR-0006 | — | Validate patient email uniqueness across the system | Test | Verified |
| SUB-PR-0007 | — | Support patient search by last name, date of birth, or ID | Test | Not Started |
| SUB-PR-0008 | — | Return paginated results for patient list queries (default: 20 per page) | Test | Not Started |
| SUB-PR-0009 | — | Capture and assess wound/condition photos with AI severity classification | Test | Not Started |
| SUB-PR-0010 | — | Verify patient identity via photo comparison against stored embedding | Test | Not Started |
| SUB-PR-0011 | — | Extract patient data from scanned documents via OCR | Test | Not Started |

## Implementation Mapping

| Req ID | Backend Module | Frontend Component | Android Screen | Test Case(s) |
|---|---|---|---|---|
| SUB-PR-0001 | `middleware/auth.py`, `routers/patients.py` | `lib/auth.ts` | `data/api/AuthInterceptor.kt` | TST-PR-0001 |
| SUB-PR-0002 | `middleware/auth.py:require_role`, `routers/patients.py` | — | — | TST-PR-0002 |
| SUB-PR-0003 | `routers/patients.py`, `services/patient_service.py`, `models/patient.py` | `app/patients/` | `ui/patients/` | TST-PR-0003 |
| SUB-PR-0004 | `services/encryption_service.py`, `services/patient_service.py` | — | — | TST-PR-0004 |
| SUB-PR-0005 | `services/audit_service.py`, `routers/patients.py` | — | — | TST-PR-0005 |
| SUB-PR-0006 | `models/patient.py` (unique constraint) | — | — | TST-PR-0006 |
| SUB-PR-0007 | — | — | — | TST-PR-0007 |
| SUB-PR-0008 | — | — | — | TST-PR-0008 |
| SUB-PR-0009 | `routers/vision.py`, `services/vision_service.py` | — | — | TST-PR-0009 |
| SUB-PR-0010 | `routers/vision.py`, `services/vision_service.py` | — | — | TST-PR-0010 |
| SUB-PR-0011 | `routers/vision.py`, `services/vision_service.py` | — | — | TST-PR-0011 |
