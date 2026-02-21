# Platform Requirements: Patient Records — Backend (SUB-PR-BE)

**Parent:** [SUB-PR (Domain)](../domain/SUB-PR.md)
**Platform:** Backend (BE) — 15 requirements

---

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
| SUB-PR-0013-BE | SUB-PR-0013 | Lesion image upload API endpoint (`/api/lesions/upload`) that accepts multipart image, encrypts with AES-256-GCM, stores in PostgreSQL, forwards to Dermatology CDS service for classification, and returns structured results with risk assessment | `routers/lesions.py`, `services/lesion_service.py`, `core/encryption.py` | TST-PR-0013-BE | Not Started |
| SUB-PR-0014-BE | SUB-PR-0014 | Similarity search API endpoint that accepts a lesion image, extracts embedding via CDS service, and queries pgvector for top-K similar ISIC reference images with diagnosis and similarity score | `routers/lesions.py`, `services/lesion_service.py` | TST-PR-0014-BE | Not Started |
| SUB-PR-0015-BE | SUB-PR-0015 | Risk score calculation service with configurable clinical thresholds for malignant class probability, patient age, and anatomical site. Returns risk level and referral urgency. | `services/risk_scorer.py` (in CDS service) | TST-PR-0015-BE | Not Started |
| SUB-PR-0016-BE | SUB-PR-0016 | Lesion history API endpoint (`/api/lesions/history/{patient_id}`) returning chronological classification results with change detection scores computed via embedding cosine distance | `routers/lesions.py`, `services/lesion_service.py` | TST-PR-0016-BE | Not Started |
