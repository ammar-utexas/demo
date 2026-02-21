# Platform Requirements: Backend (SUB-BE)

**Version:** 1.0
**Date:** 2026-02-21
**Platform:** Backend (BE) — 47 requirements across 5 domains
**Repository:** pms-backend
**Technology:** FastAPI, Python 3.12, async SQLAlchemy, asyncpg, Pydantic v2, JWT auth, AES-256 encryption

---

## Summary

| Domain | Req Count | Status Breakdown |
|--------|-----------|-----------------|
| Patient Records (PR) | 15 | 3 Implemented, 2 Verified, 1 Verified (dev), 9 Not Started |
| Clinical Workflow (CW) | 8 | 6 Placeholder, 2 Not Started |
| Medication Management (MM) | 9 | 7 Placeholder, 2 Not Started |
| Reporting & Analytics (RA) | 8 | 5 Placeholder, 3 Not Started |
| Prompt Management (PM) | 7 | 7 Not Started |
| **Total** | **47** | |

---

## Patient Records (SUB-PR)

**Parent:** [SUB-PR (Domain)](../domain/SUB-PR.md)

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-PR-0001-BE | SUB-PR-0001 | Enforce JWT auth on all patient API endpoints | `middleware/auth.py`, `routers/patients.py` | TST-PR-0001-BE | Implemented |
| SUB-PR-0002-BE | SUB-PR-0002 | Enforce role-based access control on patient API endpoints | `middleware/auth.py:require_role`, `routers/patients.py` | TST-PR-0002-BE | Implemented |
| SUB-PR-0003-BE | SUB-PR-0003 | REST CRUD endpoints for patient demographics. Must implement optimistic locking via a `version` column — updates include version in request body, return 409 on mismatch (RC-BE-01). Deactivation must return 409 if patient has non-terminal encounters (RC-BE-06). | `routers/patients.py`, `services/patient_service.py`, `models/patient.py` | TST-PR-0003-BE | Verified |
| SUB-PR-0004-BE | SUB-PR-0004 | Encrypt SSN and PHI fields at rest. Current: Fernet (AES-128-CBC). Target: AES-256-GCM with versioned-envelope approach — new writes use AES-256-GCM, reads detect format and decrypt accordingly. Backfill existing Fernet data via one-time migration (DC-PR-01, PC-BE-01). | `services/encryption_service.py`, `services/patient_service.py` | TST-PR-0004-BE | Verified (dev) |
| SUB-PR-0005-BE | SUB-PR-0005 | Audit log all patient record access and modifications, including lesion operations. `routers/lesions.py` must call `audit_service.log_action` for every endpoint. Audit event catalog extended with derm-specific actions: LESION_UPLOAD, LESION_CLASSIFY, LESION_VIEW, SIMILARITY_SEARCH, TIMELINE_VIEW (resource_type: `lesion_image`) (DC-PR-06). | `services/audit_service.py`, `routers/patients.py`, `routers/lesions.py` | TST-PR-0005-BE | Implemented |
| SUB-PR-0006-BE | SUB-PR-0006 | Enforce unique email constraint in patient model. The DB unique constraint is authoritative; the service layer must catch IntegrityError and return 409 (RC-BE-05). | `models/patient.py` (unique constraint) | TST-PR-0006-BE | Verified |
| SUB-PR-0007-BE | SUB-PR-0007 | Patient search API endpoint (last name, DOB, ID) | — | TST-PR-0007-BE | Not Started |
| SUB-PR-0008-BE | SUB-PR-0008 | Paginated patient list API endpoint | — | TST-PR-0008-BE | Not Started |
| SUB-PR-0009-BE | SUB-PR-0009 | Wound assessment API endpoint with AI severity classification | `routers/vision.py`, `services/vision_service.py` | TST-PR-0009-BE | Not Started |
| SUB-PR-0010-BE | SUB-PR-0010 | Patient ID verification API endpoint | `routers/vision.py`, `services/vision_service.py` | TST-PR-0010-BE | Not Started |
| SUB-PR-0011-BE | SUB-PR-0011 | Document OCR API endpoint | `routers/vision.py`, `services/vision_service.py` | TST-PR-0011-BE | Not Started |
| SUB-PR-0013-BE | SUB-PR-0013 | Lesion image upload API endpoint (`/api/lesions/upload`) that accepts multipart image, encrypts with AES-256-GCM, stores in PostgreSQL, forwards to Dermatology CDS service for classification, and returns structured results with risk assessment. Must validate encounter-patient consistency: when `encounter_id` is provided, verify its `patient_id` matches the upload's `patient_id`, return 422 on mismatch (DC-PR-07). Must call `audit_service.log_action` with action `LESION_UPLOAD` and resource_type `lesion_image` (DC-PR-06). Must serialize uploads per (patient_id, anatomical_site) using `SELECT ... FOR UPDATE` with configurable minimum interval (default 24h), return 409 if violated unless clinician overrides (RC-BE-11). Entire pipeline (validate → encrypt → store → CDS call → store results) must be wrapped in a single DB transaction with rollback on CDS failure. Must support `X-Idempotency-Key` header for retry deduplication (RC-BE-12). | `routers/lesions.py`, `services/lesion_service.py`, `services/encryption_service.py` | TST-PR-0013-BE | Not Started |
| SUB-PR-0014-BE | SUB-PR-0014 | Similarity search API endpoint that accepts a lesion image, extracts embedding via CDS service, and queries pgvector for top-K similar ISIC reference images with diagnosis and similarity score. Must call `audit_service.log_action` with action `SIMILARITY_SEARCH` and resource_type `lesion_image` (DC-PR-06). | `routers/lesions.py`, `services/lesion_service.py` | TST-PR-0014-BE | Not Started |
| SUB-PR-0015-BE | SUB-PR-0015 | Risk score calculation service with configurable clinical thresholds for malignant class probability, patient age, and anatomical site. Returns risk level and referral urgency. Must call `audit_service.log_action` with action `LESION_CLASSIFY` and resource_type `lesion_image` when risk score is computed (DC-PR-06). | `services/risk_scorer.py` (in CDS service) | TST-PR-0015-BE | Not Started |
| SUB-PR-0016-BE | SUB-PR-0016 | Lesion history API endpoint (`/api/lesions/history/{patient_id}`) returning chronological classification results with change detection scores computed via embedding cosine distance. Must call `audit_service.log_action` with action `TIMELINE_VIEW` and resource_type `lesion_image` (DC-PR-06). Change_score computation must use `SELECT ... FOR UPDATE` on the lesion identity row to serialize against concurrent uploads (RC-BE-11). | `routers/lesions.py`, `services/lesion_service.py` | TST-PR-0016-BE | Not Started |

---

## Clinical Workflow (SUB-CW)

**Parent:** [SUB-CW (Domain)](../domain/SUB-CW.md)

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

---

## Medication Management (SUB-MM)

**Parent:** [SUB-MM (Domain)](../domain/SUB-MM.md)

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

---

## Reporting & Analytics (SUB-RA)

**Parent:** [SUB-RA (Domain)](../domain/SUB-RA.md)

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-RA-0001-BE | SUB-RA-0001 | Patient volume report API endpoint | `routers/reports.py` | TST-RA-0001-BE | Placeholder |
| SUB-RA-0002-BE | SUB-RA-0002 | Encounter summary report API endpoint | `routers/reports.py` | TST-RA-0002-BE | Placeholder |
| SUB-RA-0003-BE | SUB-RA-0003 | Audit log query API with filters (user, action, resource, date) | — | TST-RA-0003-BE | Not Started |
| SUB-RA-0004-BE | SUB-RA-0004 | Enforce JWT auth on all report API endpoints | `middleware/auth.py` | TST-RA-0004-BE | Placeholder |
| SUB-RA-0005-BE | SUB-RA-0005 | Enforce RBAC on report endpoints (administrator/billing only) | `middleware/auth.py:require_role` | TST-RA-0005-BE | Placeholder |
| SUB-RA-0006-BE | SUB-RA-0006 | Medication usage report API endpoint | `routers/reports.py` | TST-RA-0006-BE | Placeholder |
| SUB-RA-0007-BE | SUB-RA-0007 | CSV export API for all report types | — | TST-RA-0007-BE | Not Started |
| SUB-RA-0008-BE | SUB-RA-0008 | Dermatology analytics report API endpoint aggregating lesion classification counts, risk distributions, referral trends, and model confidence from the CDS service | `routers/reports.py`, `services/lesion_service.py` | TST-RA-0008-BE | Not Started |

---

## Prompt Management (SUB-PM)

**Parent:** [SUB-PM (Domain)](../domain/SUB-PM.md)

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-PM-0001-BE | SUB-PM-0001 | Enforce JWT auth on all prompt API endpoints via shared `require_auth` middleware (follows PC-BE-02 / PC-BE-06 precedent) | `middleware/auth.py`, `routers/prompts.py` | TST-PM-0001-BE | Not Started |
| SUB-PM-0002-BE | SUB-PM-0002 | Enforce role-based access control on prompt API endpoints: admin for create/update/delete, admin+physician for read | `middleware/auth.py:require_role`, `routers/prompts.py` | TST-PM-0002-BE | Not Started |
| SUB-PM-0003-BE | SUB-PM-0003 | REST CRUD endpoints for prompts (`POST /prompts/`, `GET /prompts/`, `GET /prompts/{id}`, `PUT /prompts/{id}`, `DELETE /prompts/{id}`). Prompt name uniqueness enforced via DB unique constraint; service catches IntegrityError and returns 409. | `routers/prompts.py`, `services/prompt_service.py`, `models/prompt.py` | TST-PM-0003-BE | Not Started |
| SUB-PM-0004-BE | SUB-PM-0004 | Auto-versioning: on every prompt text save, insert a new row into `prompt_versions` with an auto-incremented version number. Use `SELECT MAX(version) FROM prompt_versions WHERE prompt_id = ? FOR UPDATE` to serialize concurrent version creation (DC-PM-02, RC-BE-09). Versions are immutable once created. | `services/prompt_service.py`, `models/prompt_version.py` | TST-PM-0004-BE | Not Started |
| SUB-PM-0005-BE | SUB-PM-0005 | Audit log all prompt operations using standardized action strings: PROMPT_CREATE, PROMPT_READ, PROMPT_UPDATE, PROMPT_DELETE, VERSION_CREATE, VERSION_COMPARE. Resource type: `prompt`. Follows audit event catalog pattern (PC-BE-03 / PC-BE-07). | `services/audit_service.py`, `routers/prompts.py` | TST-PM-0005-BE | Not Started |
| SUB-PM-0006-BE | SUB-PM-0006 | Paginated version history API endpoint (`GET /prompts/{id}/versions?page=1&size=20`). Returns versions ordered by version number descending with total count. | `routers/prompts.py`, `services/prompt_service.py` | TST-PM-0006-BE | Not Started |
| SUB-PM-0007-BE | SUB-PM-0007 | Version comparison API endpoint (`POST /prompts/{id}/versions/compare`). Accepts two version numbers, retrieves both version texts, calls Anthropic Claude API (`claude-sonnet-4-20250514`) with the managed comparison prompt, and returns the natural-language diff summary. 30-second timeout on LLM call; rate-limited to prevent abuse (RC-BE-10). Endpoint validates that both versions belong to the same prompt (DC-PM-03). | `routers/prompts.py`, `services/prompt_service.py`, `services/llm_service.py` | TST-PM-0007-BE | Not Started |
