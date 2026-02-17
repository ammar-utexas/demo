# Subsystem Requirements: Patient Records (SUB-PR)

**Document ID:** PMS-SUB-PR-001
**Version:** 1.4
**Date:** 2026-02-17
**Parent:** [System Requirements](SYS-REQ.md)

---

## Scope

The Patient Records subsystem manages patient demographics, contact information, encrypted PHI, and consent records. It is the foundational data layer for all other subsystems.

## Requirements

| Req ID | Parent | Description | Verification | Status |
|---|---|---|---|---|
| SUB-PR-0001 | SYS-REQ-0001 | Require authenticated session for all patient data access | Test | Partial |
| SUB-PR-0002 | SYS-REQ-0005 | Enforce RBAC: admin/physician/nurse read & create; admin/physician update; admin deactivate | Test | Partial |
| SUB-PR-0003 | — | Support CRUD operations for patient demographics (name, DOB, gender, contact). List endpoint behavior is interim — superseded by SUB-PR-0008 pagination when implemented. Deactivation must be blocked if the patient has active encounters (see RC-BE-06). | Test | Partial |
| SUB-PR-0004 | SYS-REQ-0002 | Encrypt SSN and other PHI fields at rest using AES-256-GCM via encryption_service. Current implementation uses Fernet (AES-128-CBC); migration to AES-256-GCM required before production (see DC-PR-01, PC-BE-01). | Test / Inspection | Verified (dev) |
| SUB-PR-0005 | SYS-REQ-0003 | Log all patient record access and modifications to the audit trail | Test | Implemented |
| SUB-PR-0006 | — | Validate patient email uniqueness across the system. The database unique constraint is the authoritative enforcement; the service layer must handle IntegrityError and return HTTP 409 on concurrent violations (see DC-PR-04, RC-BE-05). | Test | Verified |
| SUB-PR-0007 | — | Support patient search by last name, date of birth, or ID | Test | Not Started |
| SUB-PR-0008 | — | Return paginated results for patient list queries (default: 20 per page) | Test | Not Started |
| SUB-PR-0009 | — | Capture and assess wound/condition photos with AI severity classification | Test | Not Started |
| SUB-PR-0010 | — | Verify patient identity via photo comparison against stored embedding | Test | Not Started |
| SUB-PR-0011 | — | Extract patient data from scanned documents via OCR | Test | Not Started |
| SUB-PR-0012 | — | Serialize AI inference requests per device with configurable timeout. Priority order: patient ID verification (SUB-PR-0010) > wound assessment (SUB-PR-0009) > document OCR (SUB-PR-0011). On Android, camera access must be serialized via a CameraSessionManager singleton (see DC-PR-03, PC-AND-01, RC-AND-01). | Test | Not Started |

> **Status rollup rule (v1.4):** Domain status reflects strict rollup from platform requirements — a domain requirement is "Verified" only when ALL of its platform requirements are verified. SUB-PR-0001 downgraded from Implemented → Partial (WEB/AND scaffolded only). SUB-PR-0002 downgraded from Implemented → Partial (BE implemented, explicit verification tests deferred). SUB-PR-0003 downgraded from Verified → Partial (WEB/AND not started). SUB-PR-0004 changed from Verified → Verified (dev) pending AES-256-GCM migration (DC-PR-01). SUB-PR-0006 remains Verified (BE-only). SUB-PR-0005 remains Implemented (BE-only). SUB-PR-0012 added for AI inference queuing (DC-PR-03).

## Platform Decomposition

### Backend (BE) — 11 requirements

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-PR-0001-BE | SUB-PR-0001 | Enforce JWT auth on all patient API endpoints | `middleware/auth.py`, `routers/patients.py` | TST-PR-0001-BE | Implemented |
| SUB-PR-0002-BE | SUB-PR-0002 | Enforce role-based access control on patient API endpoints | `middleware/auth.py:require_role`, `routers/patients.py` | TST-PR-0002-BE | Implemented |
| SUB-PR-0003-BE | SUB-PR-0003 | REST CRUD endpoints for patient demographics. Must implement optimistic locking via a `version` column — updates include version in request body, return 409 on mismatch (RC-BE-01). Deactivation must return 409 if patient has non-terminal encounters (RC-BE-06). | `routers/patients.py`, `services/patient_service.py`, `models/patient.py` | TST-PR-0003-BE | Verified |
| SUB-PR-0004-BE | SUB-PR-0004 | Encrypt SSN and PHI fields at rest. Current: Fernet (AES-128-CBC). Target: AES-256-GCM with versioned-envelope approach — new writes use AES-256-GCM, reads detect format and decrypt accordingly. Backfill existing Fernet data via one-time migration (DC-PR-01, PC-BE-01). | `services/encryption_service.py`, `services/patient_service.py` | TST-PR-0004-BE | Verified (dev) |
| SUB-PR-0005-BE | SUB-PR-0005 | Audit log all patient record access and modifications | `services/audit_service.py`, `routers/patients.py` | TST-PR-0005-BE | Implemented |
| SUB-PR-0006-BE | SUB-PR-0006 | Enforce unique email constraint in patient model. The DB unique constraint is authoritative; the service layer must catch IntegrityError and return 409 (RC-BE-05). | `models/patient.py` (unique constraint) | TST-PR-0006-BE | Verified |
| SUB-PR-0007-BE | SUB-PR-0007 | Patient search API endpoint (last name, DOB, ID) | — | TST-PR-0007-BE | Not Started |
| SUB-PR-0008-BE | SUB-PR-0008 | Paginated patient list API endpoint | — | TST-PR-0008-BE | Not Started |
| SUB-PR-0009-BE | SUB-PR-0009 | Wound assessment API endpoint with AI severity classification | `routers/vision.py`, `services/vision_service.py` | TST-PR-0009-BE | Not Started |
| SUB-PR-0010-BE | SUB-PR-0010 | Patient ID verification API endpoint | `routers/vision.py`, `services/vision_service.py` | TST-PR-0010-BE | Not Started |
| SUB-PR-0011-BE | SUB-PR-0011 | Document OCR API endpoint | `routers/vision.py`, `services/vision_service.py` | TST-PR-0011-BE | Not Started |

### Web Frontend (WEB) — 4 requirements

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-PR-0001-WEB | SUB-PR-0001 | Auth guard and token management for patient pages. Guard must be parameterized (`requireRole(['admin', 'physician'])`) — role lists are subsystem-specific (PC-WEB-01). Must implement token refresh lock: a single Promise serializes concurrent refresh attempts to prevent thundering herd (RC-WEB-01). | `lib/auth.ts` | TST-PR-0001-WEB | Scaffolded |
| SUB-PR-0003-WEB | SUB-PR-0003 | Patient CRUD forms and list views. Edit form must include patient `version` in hidden state; on 409 response (optimistic lock conflict), display conflict resolution dialog prompting user to reload (RC-WEB-02). | `app/patients/` | TST-PR-0003-WEB | Not Started |
| SUB-PR-0007-WEB | SUB-PR-0007 | Patient search UI with filters | — | TST-PR-0007-WEB | Not Started |
| SUB-PR-0008-WEB | SUB-PR-0008 | Paginated patient list with navigation controls | — | TST-PR-0008-WEB | Not Started |

### Android (AND) — 7 requirements

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-PR-0001-AND | SUB-PR-0001 | Auth interceptor for patient API calls. Must implement token refresh synchronization via Kotlin `Mutex` — first caller refreshes, subsequent callers wait and reuse the new token (PC-AND-02). | `data/api/AuthInterceptor.kt` | TST-PR-0001-AND | Scaffolded |
| SUB-PR-0003-AND | SUB-PR-0003 | Patient CRUD screens with Compose UI. Must implement offline-sync conflict resolution: sync requests include `version`/`updated_at`, backend 409 conflicts are queued and presented in a resolution UI showing local vs server versions (RC-AND-02). | `ui/patients/` | TST-PR-0003-AND | Not Started |
| SUB-PR-0007-AND | SUB-PR-0007 | Patient search screen with filters | — | TST-PR-0007-AND | Not Started |
| SUB-PR-0008-AND | SUB-PR-0008 | Paginated patient list with lazy loading | — | TST-PR-0008-AND | Not Started |
| SUB-PR-0009-AND | SUB-PR-0009 | Camera capture for wound assessment with on-device inference. Camera access must go through CameraSessionManager singleton (SUB-PR-0012, PC-AND-01, RC-AND-01). | — | TST-PR-0009-AND | Not Started |
| SUB-PR-0010-AND | SUB-PR-0010 | Camera capture for patient ID verification. Camera access must go through CameraSessionManager singleton (SUB-PR-0012, PC-AND-01, RC-AND-01). | — | TST-PR-0010-AND | Not Started |
| SUB-PR-0011-AND | SUB-PR-0011 | Document scanner for OCR capture. Camera access must go through CameraSessionManager singleton (SUB-PR-0012, PC-AND-01, RC-AND-01). | — | TST-PR-0011-AND | Not Started |

### AI Infrastructure (AI) — 3 requirements

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-PR-0009-AI | SUB-PR-0009 | Wound severity classification model (edge deployment) | — | TST-PR-0009-AI | Not Started |
| SUB-PR-0010-AI | SUB-PR-0010 | Face/ID verification embedding model (edge deployment) | — | TST-PR-0010-AI | Not Started |
| SUB-PR-0011-AI | SUB-PR-0011 | Document OCR model (edge deployment) | — | TST-PR-0011-AI | Not Started |
