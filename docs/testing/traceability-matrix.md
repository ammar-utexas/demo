# Requirements Traceability Matrix (RTM)

**Document ID:** PMS-RTM-001
**Version:** 1.8
**Date:** 2026-02-23
**Last Updated:** 2026-02-23

---

## Forward Traceability: System Requirements → Subsystem → Implementation → Tests

| System Req | Subsystem Reqs | Backend Module(s) | Test Case(s) | Verification Status |
|---|---|---|---|---|
| SYS-REQ-0001 (MFA) | SUB-PR-0001, SUB-CW-0001, SUB-MM-0006, SUB-RA-0004, SUB-PM-0001, SUB-AU-0003, SUB-AU-0004 | `middleware/auth.py`, `services/auth_service.py`, `services/token_service.py` | TST-PR-0001, TST-CW-0001, TST-MM-0006, TST-RA-0004, TST-PM-0001, TST-AUTH-0001, TST-AU-0003, TST-AU-0004 | Partial (JWT auth enforced on patient endpoints; MFA not yet implemented) |
| SYS-REQ-0002 (Encryption) | SUB-PR-0004, SUB-MM-0003 | `services/encryption_service.py`, `services/patient_service.py` | TST-PR-0004, TST-MM-0003, TST-SYS-0002 | Partial (patient SSN encryption implemented) |
| SYS-REQ-0003 (Audit) | SUB-PR-0005, SUB-CW-0004, SUB-MM-0004, SUB-RA-0003, SUB-PM-0005, SUB-AU-0011 | `services/audit_service.py`, `middleware/audit.py`, `routers/patients.py`, `routers/auth.py`, `routers/users.py` | TST-PR-0005, TST-CW-0004, TST-MM-0004, TST-RA-0003, TST-PM-0005, TST-AU-0011, TST-SYS-0003 | Partial (patient endpoint audit logging implemented) |
| SYS-REQ-0004 (FHIR) | SUB-MM-0005 | — | TST-MM-0005, TST-SYS-0004 | Not Started |
| SYS-REQ-0005 (RBAC) | SUB-PR-0002, SUB-CW-0002, SUB-MM-0007, SUB-RA-0005, SUB-PM-0002, SUB-AU-0008, SUB-AU-0009, SUB-AU-0010 | `middleware/auth.py:require_role`, `routers/patients.py`, `routers/users.py`, `models/role.py`, `models/user_role.py` | TST-PR-0002, TST-CW-0002, TST-MM-0007, TST-RA-0005, TST-PM-0002, TST-AU-0008, TST-AU-0009, TST-AU-0010, TST-SYS-0005 | Partial (patient endpoints enforce role-based access) |
| SYS-REQ-0006 (Alerts) | SUB-MM-0001, SUB-MM-0002, SUB-CW-0005 | `services/interaction_checker.py` | TST-MM-0001, TST-MM-0002, TST-CW-0005, TST-SYS-0006 | Partial (stub endpoint only) |
| SYS-REQ-0007 (Performance) | — | — | TST-SYS-0007 | Not Started |
| SYS-REQ-0008 (Web UI) | — | — | TST-SYS-0008 | Scaffolded |
| SYS-REQ-0009 (Android) | — | — | TST-SYS-0009 | Scaffolded |
| SYS-REQ-0010 (Docker) | — | `Dockerfile` (all repos) | TST-SYS-0010 | Scaffolded |
| SYS-REQ-0011 (Prompts) | SUB-PM-0003, SUB-PM-0004, SUB-PM-0006, SUB-PM-0007 | — | TST-PM-0003, TST-PM-0004, TST-PM-0006, TST-PM-0007, TST-SYS-0011 | Not Started |
| SYS-REQ-0012 (Derm CDS) | SUB-PR-0013, SUB-PR-0014, SUB-PR-0015, SUB-PR-0016, SUB-RA-0008 | `routers/lesions.py`, `services/lesion_service.py`, `services/risk_scorer.py` (CDS) | TST-PR-0013, TST-PR-0014, TST-PR-0015, TST-PR-0016, TST-RA-0008, TST-SYS-0012 | Not Started |
| SYS-REQ-0013 (DermaCheck Orchestration) | SUB-PR-0017, SUB-CW-0009 | `routers/lesions.py`, `services/derm-cds/orchestrator.py`, `services/derm-cds/classifier.py`, `services/derm-cds/similarity.py`, `services/derm-cds/risk_scorer.py` | TST-PR-0017, TST-CW-0009, TST-SYS-0013 | Not Started |
| SYS-REQ-0014 (Authentication) | SUB-AU-0001, SUB-AU-0002, SUB-AU-0012, SUB-AU-0013, SUB-AU-0014 | `routers/auth.py`, `services/auth_service.py`, `services/oauth_service.py`, `models/user_oauth_account.py` | TST-AU-0001, TST-AU-0002, TST-AU-0012, TST-AU-0013, TST-AU-0014, TST-SYS-0014 | Not Started |
| SYS-REQ-0015 (User Management) | SUB-AU-0005, SUB-AU-0006, SUB-AU-0007, SUB-AU-0011, SUB-AU-0014, SUB-AU-0015 | `routers/users.py`, `services/user_service.py`, `services/email_service.py`, `models/user.py` | TST-AU-0005, TST-AU-0006, TST-AU-0007, TST-AU-0011, TST-AU-0014, TST-AU-0015, TST-SYS-0015 | Not Started |
| SYS-REQ-0016 (Auth Bypass) | SUB-AU-0016 | `middleware/auth.py`, `core/config.py` | TST-AU-0016, TST-SYS-0016 | Not Started |

---

## Backward Traceability: Tests → Requirements

### Subsystem Tests (Unit / Integration)

| Test Case | Description | Repository | Test Function | Traces To | Last Result | Run ID |
|---|---|---|---|---|---|---|
| TST-AUTH-0001 | Login endpoint returns JWT access_token with bearer type | pms-backend | `test_login_returns_token` | SYS-REQ-0001 | PASS | RUN-2026-02-16-003 |
| TST-PR-0001 | Verify patient endpoints require auth token | pms-backend | Implemented via `require_role` → `require_auth` dependency; explicit rejection test deferred | SUB-PR-0001, SYS-REQ-0001 | IMPL | RUN-2026-02-16-003 |
| TST-PR-0002 | Verify RBAC enforcement on patient endpoints | pms-backend | Implemented via `require_role` with per-endpoint role lists; explicit role-rejection test deferred | SUB-PR-0002, SYS-REQ-0005 | IMPL | RUN-2026-02-16-003 |
| TST-PR-0003a | Create patient with demographics returns 201 with UUID and timestamps | pms-backend | `test_create_patient_success` | SUB-PR-0003 | PASS | RUN-2026-02-16-003 |
| TST-PR-0003b | Create patient with missing required fields returns 422 | pms-backend | `test_create_patient_missing_required_fields_returns_422` | SUB-PR-0003 | PASS | RUN-2026-02-16-003 |
| TST-PR-0003c | Get patient by ID returns 200 with matching demographics | pms-backend | `test_get_patient_success` | SUB-PR-0003 | PASS | RUN-2026-02-16-003 |
| TST-PR-0003d | Get non-existent patient returns 404 | pms-backend | `test_get_patient_not_found_returns_404` | SUB-PR-0003 | PASS | RUN-2026-02-16-003 |
| TST-PR-0003e | List patients returns all active patients | pms-backend | `test_list_patients_returns_created_patients` | SUB-PR-0003 | PASS | RUN-2026-02-16-003 |
| TST-PR-0003f | List patients on empty DB returns empty array | pms-backend | `test_list_patients_empty_returns_empty_list` | SUB-PR-0003 | PASS | RUN-2026-02-16-003 |
| TST-PR-0003g | Partial update changes only specified fields, refreshes updated_at | pms-backend | `test_update_patient_partial` | SUB-PR-0003 | PASS | RUN-2026-02-16-003 |
| TST-PR-0003h | Update non-existent patient returns 404 | pms-backend | `test_update_patient_not_found_returns_404` | SUB-PR-0003 | PASS | RUN-2026-02-16-003 |
| TST-PR-0003i | Deactivate patient returns 204, sets is_active=false | pms-backend | `test_deactivate_patient_success` | SUB-PR-0003 | PASS | RUN-2026-02-16-003 |
| TST-PR-0003j | Deactivated patient excluded from list endpoint | pms-backend | `test_deactivated_patient_excluded_from_list` | SUB-PR-0003 | PASS | RUN-2026-02-16-003 |
| TST-PR-0003k | Deactivate non-existent patient returns 404 | pms-backend | `test_deactivate_patient_not_found_returns_404` | SUB-PR-0003 | PASS | RUN-2026-02-16-003 |
| TST-PR-0003l | POST /patients/ completes in under 2 seconds | pms-backend | `test_response_time_under_2_seconds` | SUB-PR-0003 | PASS | RUN-2026-02-16-003 |
| TST-PR-0004a | SSN not present in create response body | pms-backend | `test_create_patient_with_ssn_not_in_response` | SUB-PR-0004, SYS-REQ-0002 | PASS | RUN-2026-02-16-003 |
| TST-PR-0004b | SSN not present in get-by-ID response body | pms-backend | `test_get_patient_ssn_not_in_response` | SUB-PR-0004, SYS-REQ-0002 | PASS | RUN-2026-02-16-003 |
| TST-PR-0005 | Audit log entries created on patient access | pms-backend | Implemented via `audit_service.log_action` in all 5 router methods; explicit audit assertion test deferred | SUB-PR-0005, SYS-REQ-0003 | IMPL | RUN-2026-02-16-003 |
| TST-PR-0006a | Duplicate email on create returns 409 | pms-backend | `test_create_patient_duplicate_email_returns_409` | SUB-PR-0006 | PASS | RUN-2026-02-16-003 |
| TST-PR-0006b | Duplicate email on update returns 409 | pms-backend | `test_update_patient_duplicate_email_returns_409` | SUB-PR-0006 | PASS | RUN-2026-02-16-003 |
| TST-PR-0007 | Patient search by last name, DOB, or ID | pms-backend | — (not implemented) | SUB-PR-0007 | — | — |
| TST-PR-0008 | Paginated patient list results | pms-backend | — (not implemented) | SUB-PR-0008 | — | — |
| TST-PR-0009 | Wound assessment endpoint returns valid response | pms-backend | — (not implemented) | SUB-PR-0009 | — | — |
| TST-PR-0010 | Patient ID verification endpoint returns match result | pms-backend | — (not implemented) | SUB-PR-0010 | — | — |
| TST-PR-0011 | Document OCR endpoint returns extracted text and fields | pms-backend | — (not implemented) | SUB-PR-0011 | — | — |
| TST-PR-0013-BE | Lesion upload endpoint accepts image, encrypts, classifies, returns results with risk | pms-backend | — (not implemented) | SUB-PR-0013, SYS-REQ-0012 | — | — |
| TST-PR-0013-WEB | Lesion upload component with drag-and-drop and anatomical site selector | pms-frontend | — (not implemented) | SUB-PR-0013, SYS-REQ-0012 | — | — |
| TST-PR-0013-AND | Camera capture for dermoscopic images with on-device TFLite classification | pms-android | — (not implemented) | SUB-PR-0013, SYS-REQ-0012 | — | — |
| TST-PR-0013-AI | EfficientNet-B4 ONNX classification across 9 ISIC categories | pms-backend (CDS) | — (not implemented) | SUB-PR-0013, SYS-REQ-0012 | — | — |
| TST-PR-0014-BE | Similarity search endpoint returns top-K ISIC reference images | pms-backend | — (not implemented) | SUB-PR-0014, SYS-REQ-0012 | — | — |
| TST-PR-0014-WEB | Similar lesions gallery displays reference images with scores | pms-frontend | — (not implemented) | SUB-PR-0014, SYS-REQ-0012 | — | — |
| TST-PR-0014-AI | Image embedding generation and pgvector cosine similarity search | pms-backend (CDS) | — (not implemented) | SUB-PR-0014, SYS-REQ-0012 | — | — |
| TST-PR-0015-BE | Risk score calculation with configurable clinical thresholds | pms-backend | — (not implemented) | SUB-PR-0015, SYS-REQ-0012 | — | — |
| TST-PR-0015-WEB | Risk assessment banner with severity color coding and disclaimer | pms-frontend | — (not implemented) | SUB-PR-0015, SYS-REQ-0012 | — | — |
| TST-PR-0016-BE | Lesion history endpoint returns chronological results with change detection | pms-backend | — (not implemented) | SUB-PR-0016, SYS-REQ-0012 | — | — |
| TST-PR-0016-WEB | Lesion change timeline with assessment history and change indicators | pms-frontend | — (not implemented) | SUB-PR-0016, SYS-REQ-0012 | — | — |
| TST-PR-0017-BE | Backend thin proxy for DermaCheck pipeline: validate input, forward to CDS, persist DermaCheckResult, return response | pms-backend | — (not implemented) | SUB-PR-0017, SYS-REQ-0013 | — | — |
| TST-PR-0017-AI | CDS parallel fan-out orchestration: classify then gather(narrative, similarity, risk) with per-stage timeouts and graceful degradation | pms-backend (CDS) | — (not implemented) | SUB-PR-0017, SYS-REQ-0013 | — | — |
| TST-CW-0001 | Verify encounter endpoints require auth token | pms-backend | — (not implemented) | SUB-CW-0001, SYS-REQ-0001 | — | — |
| TST-CW-0002 | Verify RBAC enforcement on encounter endpoints | pms-backend | — (not implemented) | SUB-CW-0002, SYS-REQ-0005 | — | — |
| TST-CW-0003 | Encounter list endpoint returns 200 with empty array (stub) | pms-backend | `test_list_encounters_empty` | SUB-CW-0003 | PASS | RUN-2026-02-16-003 |
| TST-CW-0004 | Audit log entries created on encounter access | pms-backend | — (not implemented) | SUB-CW-0004, SYS-REQ-0003 | — | — |
| TST-CW-0005 | Clinical alerts triggered on critical encounter notes | pms-backend | — (not implemented) | SUB-CW-0005, SYS-REQ-0006 | — | — |
| TST-CW-0006 | Encounter types validated (office_visit, telehealth, emergency, follow_up) | pms-backend | — (not implemented) | SUB-CW-0006 | — | — |
| TST-CW-0007 | Encounter status transition validation | pms-backend | — (not implemented) | SUB-CW-0007 | — | — |
| TST-CW-0008 | Encounter associated with patient via FK | pms-backend | — (not implemented) | SUB-CW-0008 | — | — |
| TST-CW-0009-BE | Encounter-lesion linkage: GET /api/encounters/{id}/lesions with encounter-patient validation | pms-backend | — (not implemented) | SUB-CW-0009, SYS-REQ-0013 | — | — |
| TST-CW-0009-WEB | DermaCheck workflow at /encounters/[id]/dermatology with capture widget, results panel, and degradation banners | pms-frontend | — (not implemented) | SUB-CW-0009, SYS-REQ-0013 | — | — |
| TST-CW-0009-AND | Android DermaCheck encounter workflow: camera capture, upload, results review, save/discard, degradation handling | pms-android | — (not implemented) | SUB-CW-0009, SYS-REQ-0013 | — | — |
| TST-MM-0001 | Interaction check endpoint returns 200 with empty array for unknown patient | pms-backend | `test_check_interactions_empty` | SUB-MM-0001, SYS-REQ-0006 | PASS | RUN-2026-02-16-003 |
| TST-MM-0002 | Interaction severity classification (contraindicated, major, moderate, minor) | pms-backend | — (not implemented) | SUB-MM-0002, SYS-REQ-0006 | — | — |
| TST-MM-0003 | Prescription data PHI encryption | pms-backend | — (not implemented) | SUB-MM-0003, SYS-REQ-0002 | — | — |
| TST-MM-0004 | Prescription event audit logging | pms-backend | — (not implemented) | SUB-MM-0004, SYS-REQ-0003 | — | — |
| TST-MM-0005 | FHIR R4 MedicationRequest support | pms-backend | — (not implemented) | SUB-MM-0005, SYS-REQ-0004 | — | — |
| TST-MM-0006 | Medication endpoints require auth token | pms-backend | — (not implemented) | SUB-MM-0006, SYS-REQ-0001 | — | — |
| TST-MM-0007 | RBAC enforcement on medication endpoints | pms-backend | — (not implemented) | SUB-MM-0007, SYS-REQ-0005 | — | — |
| TST-MM-0008 | Medication list endpoint returns 200 with empty array (stub) | pms-backend | `test_list_medications_empty` | SUB-MM-0008 | PASS | RUN-2026-02-16-003 |
| TST-MM-0009 | Refill tracking prevents zero-refill fills | pms-backend | — (not implemented) | SUB-MM-0009 | — | — |
| TST-RA-0001 | Patient volume report endpoint | pms-backend | — (not implemented) | SUB-RA-0001 | — | — |
| TST-RA-0002 | Encounter summary report endpoint | pms-backend | — (not implemented) | SUB-RA-0002 | — | — |
| TST-RA-0003 | Audit log query interface | pms-backend | — (not implemented) | SUB-RA-0003, SYS-REQ-0003 | — | — |
| TST-RA-0004 | Report endpoints require auth | pms-backend | — (not implemented) | SUB-RA-0004, SYS-REQ-0001 | — | — |
| TST-RA-0005 | RBAC enforcement on report endpoints | pms-backend | — (not implemented) | SUB-RA-0005, SYS-REQ-0005 | — | — |
| TST-RA-0006 | Medication usage report endpoint | pms-backend | — (not implemented) | SUB-RA-0006 | — | — |
| TST-RA-0007 | Report CSV export | pms-backend | — (not implemented) | SUB-RA-0007 | — | — |
| TST-RA-0008-BE | Dermatology analytics report API with classification volumes and risk distributions | pms-backend | — (not implemented) | SUB-RA-0008, SYS-REQ-0012 | — | — |
| TST-RA-0008-WEB | Dermatology analytics dashboard with charts for classifications and referrals | pms-frontend | — (not implemented) | SUB-RA-0008, SYS-REQ-0012 | — | — |
| TST-FE-0001 | Auth utilities: isAuthenticated, parseToken | pms-frontend | — | SYS-REQ-0001 | PASS | RUN-2026-02-15-002 |
| TST-FE-0002 | Utility functions: cn, formatDate | pms-frontend | — | — (infrastructure) | PASS | RUN-2026-02-15-002 |
| TST-FE-0003 | InteractionWarning type matches schema | pms-frontend | — | SUB-MM-0002 | PASS | RUN-2026-02-15-002 |
| TST-AND-0001 | PatientEntity roundtrip mapping | pms-android | — | SUB-PR-0003 | — | — |
| TST-AND-0002 | Model serialization (TokenRequest, InteractionWarning) | pms-android | — | SYS-REQ-0001, SUB-MM-0002 | — | — |
| TST-PM-0001-BE | Verify prompt endpoints require auth token | pms-backend | — (not implemented) | SUB-PM-0001, SYS-REQ-0001 | — | — |
| TST-PM-0001-WEB | Verify prompt pages enforce auth guard | pms-frontend | — (not implemented) | SUB-PM-0001, SYS-REQ-0001 | — | — |
| TST-PM-0002-BE | Verify RBAC enforcement on prompt endpoints (admin CRUD, admin+physician read) | pms-backend | — (not implemented) | SUB-PM-0002, SYS-REQ-0005 | — | — |
| TST-PM-0003-BE | Prompt CRUD operations and name uniqueness (409 on duplicate) | pms-backend | — (not implemented) | SUB-PM-0003, SYS-REQ-0011 | — | — |
| TST-PM-0003-WEB | Prompt CRUD forms render and submit correctly | pms-frontend | — (not implemented) | SUB-PM-0003, SYS-REQ-0011 | — | — |
| TST-PM-0004-BE | Auto-versioning creates immutable version on text save | pms-backend | — (not implemented) | SUB-PM-0004, SYS-REQ-0011 | — | — |
| TST-PM-0004-WEB | Version indicator displays current version in prompt editor | pms-frontend | — (not implemented) | SUB-PM-0004, SYS-REQ-0011 | — | — |
| TST-PM-0005-BE | Audit log entries created on all prompt operations | pms-backend | — (not implemented) | SUB-PM-0005, SYS-REQ-0003 | — | — |
| TST-PM-0006-BE | Paginated version history returns correct page with total count | pms-backend | — (not implemented) | SUB-PM-0006, SYS-REQ-0011 | — | — |
| TST-PM-0006-WEB | Version history list displays with pagination controls | pms-frontend | — (not implemented) | SUB-PM-0006, SYS-REQ-0011 | — | — |
| TST-PM-0007-BE | Version comparison endpoint returns LLM-generated diff summary | pms-backend | — (not implemented) | SUB-PM-0007, SYS-REQ-0011 | — | — |
| TST-PM-0007-WEB | Comparison UI renders version selector and diff display | pms-frontend | — (not implemented) | SUB-PM-0007, SYS-REQ-0011 | — | — |
| TST-PM-0007-AI | Anthropic Claude API integration returns valid comparison | pms-backend | — (not implemented) | SUB-PM-0007, SYS-REQ-0011 | — | — |
| TST-AU-0001-BE | OAuth endpoints: authorize redirect and callback token exchange | pms-backend | — (not implemented) | SUB-AU-0001, SYS-REQ-0014 | — | — |
| TST-AU-0002-BE | Email/password login and password reset endpoints | pms-backend | — (not implemented) | SUB-AU-0002, SYS-REQ-0014 | — | — |
| TST-AU-0003-BE | JWT issuance with claims, refresh token storage, logout revocation | pms-backend | — (not implemented) | SUB-AU-0003, SYS-REQ-0001 | — | — |
| TST-AU-0004-BE | Account lockout after 5 failed attempts with 30-min auto-unlock | pms-backend | — (not implemented) | SUB-AU-0004, SYS-REQ-0001 | — | — |
| TST-AU-0005-BE | Admin seed migration from environment variables (idempotent) | pms-backend | — (not implemented) | SUB-AU-0005, SYS-REQ-0015 | — | — |
| TST-AU-0006-BE | User management CRUD endpoints (admin-only, deactivation revokes sessions) | pms-backend | — (not implemented) | SUB-AU-0006, SYS-REQ-0015 | — | — |
| TST-AU-0007-BE | Invite token generation, acceptance with password set, and expiry rejection | pms-backend | — (not implemented) | SUB-AU-0007, SYS-REQ-0015 | — | — |
| TST-AU-0008-BE | Role seeding and multi-role user_roles join table management | pms-backend | — (not implemented) | SUB-AU-0008, SYS-REQ-0005 | — | — |
| TST-AU-0009-BE | require_role middleware enforcement per endpoint with 403 on unauthorized | pms-backend | — (not implemented) | SUB-AU-0009, SYS-REQ-0005 | — | — |
| TST-AU-0010-BE | Last-admin lockout prevention (409 when sole admin role removal attempted) | pms-backend | — (not implemented) | SUB-AU-0010, SYS-REQ-0005 | — | — |
| TST-AU-0011-BE | Audit logging of auth events (login, logout, lockout, OAuth link) and user management operations | pms-backend | — (not implemented) | SUB-AU-0011, SYS-REQ-0003 | — | — |
| TST-AU-0012-BE | OAuth accounts table with unique constraint on (provider, provider_user_id) | pms-backend | — (not implemented) | SUB-AU-0012, SYS-REQ-0014 | — | — |
| TST-AU-0013-BE | Password complexity validation (12+ chars, mixed case, digit, special) | pms-backend | — (not implemented) | SUB-AU-0013, SYS-REQ-0014 | — | — |
| TST-AU-0014-BE | Email service integration for invite and password reset emails | pms-backend | — (not implemented) | SUB-AU-0014, SYS-REQ-0014, SYS-REQ-0015 | — | — |
| TST-AU-0016-BE | Auth bypass middleware with environment guard (500 on prod/staging/qa) | pms-backend | — (not implemented) | SUB-AU-0016, SYS-REQ-0016 | — | — |
| TST-AU-0001-WEB | Login page with OAuth provider buttons and callback redirect handling | pms-frontend | — (not implemented) | SUB-AU-0001, SYS-REQ-0014 | — | — |
| TST-AU-0002-WEB | Email/password login form and password reset request/reset pages | pms-frontend | — (not implemented) | SUB-AU-0002, SYS-REQ-0014 | — | — |
| TST-AU-0003-WEB | JWT storage (httpOnly cookie), auth guard with requireRole, token refresh lock | pms-frontend | — (not implemented) | SUB-AU-0003, SYS-REQ-0001 | — | — |
| TST-AU-0004-WEB | Account lockout message display with remaining duration on login form | pms-frontend | — (not implemented) | SUB-AU-0004, SYS-REQ-0001 | — | — |
| TST-AU-0006-WEB | User management admin pages (list, create, edit, deactivate/reactivate, resend invite) | pms-frontend | — (not implemented) | SUB-AU-0006, SYS-REQ-0015 | — | — |
| TST-AU-0007-WEB | Invite acceptance page with set-password form and token validation | pms-frontend | — (not implemented) | SUB-AU-0007, SYS-REQ-0015 | — | — |
| TST-AU-0008-WEB | Multi-role checkbox selection in user create/edit forms with at-least-one validation | pms-frontend | — (not implemented) | SUB-AU-0008, SYS-REQ-0005 | — | — |
| TST-AU-0009-WEB | Navigation visibility and route protection based on JWT role claims | pms-frontend | — (not implemented) | SUB-AU-0009, SYS-REQ-0005 | — | — |
| TST-AU-0015-WEB | Current user profile page displaying name, email, and roles from GET /users/me | pms-frontend | — (not implemented) | SUB-AU-0015, SYS-REQ-0015 | — | — |
| TST-AU-0016-WEB | Frontend auth bypass with mock user injection and non-dismissible warning banner | pms-frontend | — (not implemented) | SUB-AU-0016, SYS-REQ-0016 | — | — |
| TST-AU-0001-AND | Login screen with OAuth via Chrome Custom Tabs and redirect callback | pms-android | — (not implemented) | SUB-AU-0001, SYS-REQ-0014 | — | — |
| TST-AU-0002-AND | Email/password login form and password reset request screen | pms-android | — (not implemented) | SUB-AU-0002, SYS-REQ-0014 | — | — |
| TST-AU-0003-AND | JWT encrypted DataStore storage and Kotlin Mutex token refresh synchronization | pms-android | — (not implemented) | SUB-AU-0003, SYS-REQ-0001 | — | — |
| TST-AU-0004-AND | Account lockout message display with remaining duration on login screen | pms-android | — (not implemented) | SUB-AU-0004, SYS-REQ-0001 | — | — |
| TST-AU-0007-AND | Invite deep link (pms://invite/accept) with set-password screen and token validation | pms-android | — (not implemented) | SUB-AU-0007, SYS-REQ-0015 | — | — |
| TST-AU-0015-AND | Current user profile screen displaying name, email, and roles | pms-android | — (not implemented) | SUB-AU-0015, SYS-REQ-0015 | — | — |

### System Tests (End-to-End)

| Test Case | Description | Traces To | Last Result | Run ID |
|---|---|---|---|---|
| TST-SYS-0001 | End-to-end login flow across all clients | SYS-REQ-0001 | — | — |
| TST-SYS-0002 | Verify PHI encryption at database level | SYS-REQ-0002 | — | — |
| TST-SYS-0003 | Verify audit trail completeness across CRUD operations | SYS-REQ-0003 | — | — |
| TST-SYS-0005 | Verify role-based access denied/allowed across endpoints | SYS-REQ-0005 | — | — |
| TST-SYS-0006 | End-to-end drug interaction alert flow | SYS-REQ-0006 | — | — |
| TST-SYS-0007 | Load test: 500 concurrent users, <2s response | SYS-REQ-0007 | — | — |
| TST-SYS-0008 | Web frontend renders all pages without errors | SYS-REQ-0008 | — | — |
| TST-SYS-0009 | Android app renders all screens without crashes | SYS-REQ-0009 | — | — |
| TST-SYS-0010 | All Dockerfiles build and containers start | SYS-REQ-0010 | — | — |
| TST-SYS-0011 | End-to-end prompt management: create, version, compare | SYS-REQ-0011 | — | — |
| TST-SYS-0012 | End-to-end dermatology CDS: upload lesion, classify, similarity search, risk score | SYS-REQ-0012 | — | — |
| TST-SYS-0013 | End-to-end DermaCheck pipeline orchestration: upload image, verify parallel fan-out (classify → narrative + similarity + risk), verify degraded response handling, verify atomic DermaCheckResult | SYS-REQ-0013 | — | — |
| TST-SYS-0014 | End-to-end authentication: OAuth login flow (authorize → callback → JWT), email/password login, token refresh, logout, failed login lockout | SYS-REQ-0014 | — | — |
| TST-SYS-0015 | End-to-end user management: admin creates user, invite email sent, user accepts invite and sets password, admin assigns roles, admin deactivates user (sessions revoked) | SYS-REQ-0015 | — | — |
| TST-SYS-0016 | Auth bypass flag: verify bypass active injects mock user, verify HTTP 500 on production/staging/qa environment, verify disabled by default with zero code-path changes | SYS-REQ-0016 | — | — |

---

## Test Run Log

| Run ID | Date | Repository | Commit SHA | Tests Run | Passed | Failed | Skipped |
|---|---|---|---|---|---|---|---|
| RUN-2026-02-15-001 | 2026-02-15 | pms-backend | `c17c71b` | 5 | 5 | 0 | 0 |
| RUN-2026-02-15-002 | 2026-02-15 | pms-frontend | `d666016` | 9 | 9 | 0 | 0 |
| RUN-2026-02-16-001 | 2026-02-16 | pms-backend | `17ed00b` | 5 | 5 | 0 | 0 |
| RUN-2026-02-16-002 | 2026-02-16 | pms-backend | `f2cfaf8` | 157 | 157 | 0 | 0 |
| RUN-2026-02-16-003 | 2026-02-16 | pms-backend | `77fd003` | 157 | 157 | 0 | 0 |

---

## Platform Traceability Summary

Compact view of platform requirement status per domain requirement. Domain status uses **strict rollup**: a domain req is "Verified" only when all platform reqs are verified.

### SUB-PR — Patient Records (38 platform reqs)

| Domain Req | Domain Status | BE | WEB | AND | AI |
|---|---|---|---|---|---|
| SUB-PR-0001 | Partial | Implemented | Scaffolded | Scaffolded | — |
| SUB-PR-0002 | Partial | Implemented | — | — | — |
| SUB-PR-0003 | Partial | Verified | Not Started | Not Started | — |
| SUB-PR-0004 | Verified | Verified | — | — | — |
| SUB-PR-0005 | Implemented | Implemented | — | — | — |
| SUB-PR-0006 | Verified | Verified | — | — | — |
| SUB-PR-0007 | Not Started | Not Started | Not Started | Not Started | — |
| SUB-PR-0008 | Not Started | Not Started | Not Started | Not Started | — |
| SUB-PR-0009 | Not Started | Not Started | — | Not Started | Not Started |
| SUB-PR-0010 | Not Started | Not Started | — | Not Started | Not Started |
| SUB-PR-0011 | Not Started | Not Started | — | Not Started | Not Started |
| SUB-PR-0013 | Not Started | Not Started | Not Started | Not Started | Not Started |
| SUB-PR-0014 | Not Started | Not Started | Not Started | — | Not Started |
| SUB-PR-0015 | Not Started | Not Started | Not Started | — | — |
| SUB-PR-0016 | Not Started | Not Started | Not Started | — | — |
| SUB-PR-0017 | Not Started | Not Started | — | — | Not Started |

### SUB-CW — Clinical Workflow (17 platform reqs)

| Domain Req | Domain Status | BE | WEB | AND | AI |
|---|---|---|---|---|---|
| SUB-CW-0001 | Placeholder | Placeholder | Scaffolded | Scaffolded | — |
| SUB-CW-0002 | Placeholder | Placeholder | — | — | — |
| SUB-CW-0003 | Placeholder | Placeholder | Not Started | Not Started | — |
| SUB-CW-0004 | Placeholder | Placeholder | — | — | — |
| SUB-CW-0005 | Not Started | Not Started | — | — | — |
| SUB-CW-0006 | Placeholder | Placeholder | Not Started | Not Started | — |
| SUB-CW-0007 | Not Started | Not Started | — | — | — |
| SUB-CW-0008 | Placeholder | Placeholder | — | — | — |
| SUB-CW-0009 | Not Started | Not Started | Not Started | Not Started | — |

### SUB-MM — Medication Management (13 platform reqs)

| Domain Req | Domain Status | BE | WEB | AND | AI |
|---|---|---|---|---|---|
| SUB-MM-0001 | Placeholder | Placeholder | Not Started | Not Started | — |
| SUB-MM-0002 | Placeholder | Placeholder | — | — | — |
| SUB-MM-0003 | Placeholder | Placeholder | — | — | — |
| SUB-MM-0004 | Placeholder | Placeholder | — | — | — |
| SUB-MM-0005 | Not Started | Not Started | — | — | — |
| SUB-MM-0006 | Placeholder | Placeholder | Scaffolded | Scaffolded | — |
| SUB-MM-0007 | Placeholder | Placeholder | — | — | — |
| SUB-MM-0008 | Placeholder | Placeholder | — | — | — |
| SUB-MM-0009 | Not Started | Not Started | — | — | — |

### SUB-RA — Reporting & Analytics (19 platform reqs)

| Domain Req | Domain Status | BE | WEB | AND | AI |
|---|---|---|---|---|---|
| SUB-RA-0001 | Placeholder | Placeholder | Not Started | Not Started | — |
| SUB-RA-0002 | Placeholder | Placeholder | Not Started | Not Started | — |
| SUB-RA-0003 | Not Started | Not Started | Not Started | Not Started | — |
| SUB-RA-0004 | Placeholder | Placeholder | Scaffolded | Scaffolded | — |
| SUB-RA-0005 | Placeholder | Placeholder | — | — | — |
| SUB-RA-0006 | Placeholder | Placeholder | Not Started | Not Started | — |
| SUB-RA-0007 | Not Started | Not Started | — | — | — |
| SUB-RA-0008 | Not Started | Not Started | Not Started | — | — |

### SUB-PM — Prompt Management (13 platform reqs)

| Domain Req | Domain Status | BE | WEB | AND | AI |
|---|---|---|---|---|---|
| SUB-PM-0001 | Not Started | Not Started | Not Started | — | — |
| SUB-PM-0002 | Not Started | Not Started | — | — | — |
| SUB-PM-0003 | Not Started | Not Started | Not Started | — | — |
| SUB-PM-0004 | Not Started | Not Started | Not Started | — | — |
| SUB-PM-0005 | Not Started | Not Started | — | — | — |
| SUB-PM-0006 | Not Started | Not Started | Not Started | — | — |
| SUB-PM-0007 | Not Started | Not Started | Not Started | — | Not Started |

### SUB-AU — Authentication & User Management (31 platform reqs)

| Domain Req | Domain Status | BE | WEB | AND | AI |
|---|---|---|---|---|---|
| SUB-AU-0001 | Not Started | Not Started | Not Started | Not Started | — |
| SUB-AU-0002 | Not Started | Not Started | Not Started | Not Started | — |
| SUB-AU-0003 | Not Started | Not Started | Not Started | Not Started | — |
| SUB-AU-0004 | Not Started | Not Started | Not Started | Not Started | — |
| SUB-AU-0005 | Not Started | Not Started | — | — | — |
| SUB-AU-0006 | Not Started | Not Started | Not Started | Not Started | — |
| SUB-AU-0007 | Not Started | Not Started | Not Started | Not Started | — |
| SUB-AU-0008 | Not Started | Not Started | Not Started | — | — |
| SUB-AU-0009 | Not Started | Not Started | Not Started | — | — |
| SUB-AU-0010 | Not Started | Not Started | — | — | — |
| SUB-AU-0011 | Not Started | Not Started | — | — | — |
| SUB-AU-0016 | Not Started | Not Started | Not Started | — | — |

### Coverage Summary by Platform

| Platform | Total Reqs | Verified | Implemented | Partial | Scaffolded | Placeholder | Not Started |
|---|---|---|---|---|---|---|---|
| BE | 64 | 3 | 2 | 0 | 0 | 16 | 43 |
| WEB | 35 | 0 | 0 | 0 | 5 | 0 | 30 |
| AND | 25 | 0 | 0 | 0 | 4 | 0 | 21 |
| AI | 7 | 0 | 0 | 0 | 0 | 0 | 7 |
| **Total** | **131** | **3** | **2** | **0** | **9** | **16** | **101** |

### Test ID Migration Note

Existing test IDs are preserved as-is in the backward traceability section. The following aliases map legacy IDs to the new platform-scoped convention:

| Legacy ID | New Convention Alias | Notes |
|---|---|---|
| TST-PR-0003a … TST-PR-0003l | TST-PR-0003-BE-a … TST-PR-0003-BE-l | Backend CRUD tests |
| TST-PR-0004a, TST-PR-0004b | TST-PR-0004-BE-a, TST-PR-0004-BE-b | Backend encryption tests |
| TST-PR-0006a, TST-PR-0006b | TST-PR-0006-BE-a, TST-PR-0006-BE-b | Backend email uniqueness tests |
| TST-FE-0001 | TST-PR-0001-WEB | Frontend auth utilities |
| TST-FE-0002 | — (infrastructure, no req mapping) | Frontend utility functions |
| TST-FE-0003 | TST-MM-0002-WEB | Frontend interaction warning type |
| TST-AND-0001 | TST-PR-0003-AND | Android patient entity mapping |
| TST-AND-0002 | TST-MM-0001-AND | Android model serialization |

> **Note:** Legacy IDs are retained in existing backward traceability rows. New tests should use the platform-scoped `TST-{domain}-{NNNN}-{platform}` convention.

---

## Coverage Summary

| Subsystem | Domain Reqs | Platform Reqs | With Tests | Passing | Failing | No Tests | Domain Coverage |
|---|---|---|---|---|---|---|---|
| Patient Records (PR) | 17 | 38 | 6 | 6 | 0 | 11 | 35.3% |
| Clinical Workflow (CW) | 9 | 17 | 1 | 1 | 0 | 8 | 11.1% |
| Medication Mgmt (MM) | 9 | 13 | 2 | 2 | 0 | 7 | 22.2% |
| Reporting (RA) | 8 | 19 | 0 | 0 | 0 | 8 | 0.0% |
| Prompt Mgmt (PM) | 7 | 13 | 0 | 0 | 0 | 7 | 0.0% |
| Auth & User Mgmt (AU) | 12 | 31 | 0 | 0 | 0 | 12 | 0.0% |
| System (SYS) | 16 | — | 1 | 1 | 0 | 15 | 6.3% |
| **TOTAL** | **78** | **131** | **10** | **10** | **0** | **68** | **12.8%** |

> **Note on v1.8 updates (Authentication & User Management — SUB-AU):** Added SUB-AU (Authentication & User Management) subsystem with 12 domain requirements and 31 platform requirements (BE=15, WEB=10, AND=6). Three new system requirements added to forward traceability: SYS-REQ-0014 (Authentication), SYS-REQ-0015 (User Management), SYS-REQ-0016 (Auth Bypass). Existing forward traceability rows updated: SYS-REQ-0001 expanded with SUB-AU-0003/0004, SYS-REQ-0003 expanded with SUB-AU-0011, SYS-REQ-0005 expanded with SUB-AU-0008/0009/0010. Added 31 backward traceability test stubs (TST-AU-0001-BE through TST-AU-0016-BE, TST-AU-0001-WEB through TST-AU-0016-WEB, TST-AU-0001-AND through TST-AU-0015-AND) plus 3 system tests (TST-SYS-0014/0015/0016). Platform Traceability Summary: new SUB-AU section with 31 platform reqs across 12 domain reqs. Coverage Summary by Platform updated: BE 49→64, WEB 25→35, AND 19→25, AI 7 (unchanged), Total 100→131. Domain req totals: AU=12 added, SYS 13→16, overall 63→78. Overall domain coverage: 15.9%→12.8% (increased denominator from new requirements).

> **Note on v1.7 updates (DermaCheck Orchestration — SYS-REQ-0013):** Added SYS-REQ-0013 (DermaCheck Workflow Orchestration) to forward traceability with 2 subsystem requirements (SUB-PR-0017, SUB-CW-0009). Added 5 backward traceability test stubs: TST-PR-0017-BE/AI, TST-CW-0009-BE/WEB/AND, plus TST-SYS-0013 system test. Platform Traceability Summary updated: SUB-PR expanded from 36→38 platform reqs (BE=15→16, AI=5→6), SUB-CW expanded from 14→17 platform reqs (BE=8→9, WEB=3→4, AND=3→4). Coverage Summary by Platform updated: BE 47→49, WEB 24→25, AND 18→19, AI 6→7, Total 95→100. Domain req totals: PR 16→17, CW 8→9, SYS 12→13, overall 60→63. Overall domain coverage: 16.7%→15.9% (increased denominator from new requirements).

> **Note on v1.6 updates (ISIC Dermatology CDS — SYS-REQ-0012):** Added SYS-REQ-0012 (Dermatology Clinical Decision Support) to forward traceability with 5 subsystem requirements (SUB-PR-0013/0014/0015/0016, SUB-RA-0008). Added 14 backward traceability test stubs: TST-PR-0013-BE/WEB/AND/AI, TST-PR-0014-BE/WEB/AI, TST-PR-0015-BE/WEB, TST-PR-0016-BE/WEB, TST-RA-0008-BE/WEB, TST-SYS-0012. Platform Traceability Summary updated: SUB-PR expanded from 25→36 platform reqs (BE=11→15, WEB=4→8, AND=7→8, AI=3→5), SUB-RA expanded from 17→19 platform reqs (BE=7→8, WEB=5→6). Coverage Summary by Platform updated: BE 42→47, WEB 19→24, AND 17→18, AI 4→6, Total 82→95. Domain req totals: PR 12→16, RA 7→8, SYS 11→12, overall 54→60. Overall domain coverage: 18.5%→16.7% (increased denominator from new requirements).

> **Note on v1.5 updates (SUB-PM subsystem):** Added Prompt Management (SUB-PM) subsystem with 7 domain requirements and 13 platform requirements (BE=7, WEB=5, AI=1). SYS-REQ-0011 added for centralized prompt management. Forward traceability updated for SYS-REQ-0001, 0003, 0005, and 0011. 13 backward traceability test stubs added (TST-PM-*). Platform Traceability Summary includes SUB-PM section. Coverage Summary by Platform updated: BE 35→42, WEB 14→19, AI 3→4, Total 69→82. PR domain req count corrected from 11→12 (SUB-PR-0012 was added in v1.4 but count was not updated). Overall domain coverage: 22.2%→18.5%.

> **Note on v1.4 updates (three-tier decomposition):** Added Platform Traceability Summary section with 69 platform requirements across 4 platforms (BE=35, WEB=14, AND=17, AI=3). Coverage Summary by Platform added. Domain statuses updated with strict rollup — SUB-PR-0001 (Implemented → Partial), SUB-PR-0002 (Implemented → Partial), SUB-PR-0003 (Verified → Partial). Test ID migration note maps legacy TST-FE-* and TST-AND-* IDs to new platform-scoped convention. Existing backward traceability rows preserved without renaming.

> **Note on v1.3 updates (001-patient-crud — RBAC & audit):** All 5 patient endpoints now enforce authentication via `require_role` → `require_auth` dependency chain (SUB-PR-0001). Role-based access control applied per endpoint: admin/physician/nurse for read and create, admin/physician for update, admin only for deactivate (SUB-PR-0002). Audit logging via `audit_service.log_action` added to all 5 router methods — each operation logs user_id, action, resource_type, resource_id, and IP address (SUB-PR-0005). These 3 requirements are marked IMPL (implementation verified by code inspection; explicit assertion tests deferred). Forward traceability updated: SYS-REQ-0001, 0003, 0005 upgraded from "Placeholder" to "Partial". New test run RUN-2026-02-16-003 recorded against commit `77fd003`. PR coverage: 36.4% → 54.5%; overall: 17.8% → 22.2%.

> **Note on v1.2 updates (001-patient-crud):** Patient CRUD feature fully implemented and tested against PostgreSQL. TST-PR-0003 expanded from a single stub test into 12 sub-cases (a–l) covering all 5 CRUD operations with full integration tests. TST-PR-0004 expanded into 2 sub-cases verifying SSN is excluded from both create and get responses (encryption at rest via `encryption_service.encrypt()`). TST-PR-0006 expanded into 2 sub-cases covering email uniqueness on both create and update paths. SYS-REQ-0002 verification status upgraded from "Placeholder" to "Partial" — patient SSN encryption is implemented; prescription PHI encryption (SUB-MM-0003) remains pending.

> **Note on v1.1 corrections:** The v1.0 matrix (2026-02-15) overstated coverage. TST-MM-0002 was incorrectly marked as PASS — no test for severity classification exists. TST-PR-0003, TST-CW-0003, and TST-MM-0001 test descriptions have been corrected to reflect that they only verify stub endpoint responses (200 + empty array), not full CRUD or interaction logic. The "Test Function" column was added to link each test case to its actual pytest function.

> **Gap Analysis:** 35 requirements lack test coverage. Priority:
> 1. **Explicit auth/RBAC rejection tests** — TST-PR-0001, TST-PR-0002 have IMPL code but no dedicated test functions verifying 401/403 on patient endpoints
> 2. **Explicit audit assertion tests** — TST-PR-0005 has IMPL code but no test verifying audit log entries are created
> 3. **Auth/RBAC for other subsystems** — SUB-CW-0001/0002, SUB-MM-0006/0007, SUB-RA-0004/0005
> 4. **Remaining CRUD integration tests** — SUB-CW-0003 lifecycle, SUB-MM-0008 prescriptions
> 5. **Reporting tests** — SUB-RA-0001 through SUB-RA-0007 (0% coverage)

---

## How to Update This Matrix

1. After implementing a requirement, add the source module to the platform requirements file in `docs/specs/requirements/platform/SUB-*-{PLATFORM}.md`.
2. After writing a test, add the test case row to the "Backward Traceability" section above. Include the `Test Function` name.
3. After each test run, add a row to the "Test Run Log" and update "Last Result" and "Run ID" columns.
4. Re-generate the "Coverage Summary" by counting requirements with/without passing tests.
5. Commit all changes: `git add docs/specs/ docs/testing/ && git commit -m "evidence: update RTM" && git push`.
