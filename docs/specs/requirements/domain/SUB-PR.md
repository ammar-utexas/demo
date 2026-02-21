# Subsystem Requirements: Patient Records (SUB-PR)

**Document ID:** PMS-SUB-PR-001
**Version:** 1.6
**Date:** 2026-02-21
**Parent:** [System Requirements](../SYS-REQ.md)

---

## Scope

The Patient Records subsystem manages patient demographics, contact information, encrypted PHI, and consent records. It is the foundational data layer for all other subsystems.

Starting with SYS-REQ-0012, this subsystem also encompasses **dermatology clinical decision support**: skin lesion image capture, AI classification via the `pms-derm-cds` microservice (ADR-0008), pgvector similarity search (ADR-0011), threshold-based risk scoring (ADR-0015), and longitudinal lesion tracking (ADR-0019). Patient dermoscopic images are stored as AES-256-GCM encrypted BYTEA (ADR-0010) with versioned-envelope key management (ADR-0016). Architecture is fully defined via 14 ADRs (ADR-0008 through ADR-0021).

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
| SUB-PR-0013 | SYS-REQ-0012 | Capture and classify dermoscopic skin lesion images using ISIC-trained deep learning models (EfficientNet-B4 / MobileNetV3), returning probability distribution across 9 ISIC diagnostic categories with confidence scores | Test | Not Started |
| SUB-PR-0014 | SYS-REQ-0012 | Provide visually similar ISIC reference images for clinical comparison via pgvector cosine similarity search against a cached reference database of pre-computed 512-dimensional embeddings | Test | Not Started |
| SUB-PR-0015 | SYS-REQ-0012 | Calculate structured risk scores (low/medium/high) for classified skin lesions with referral urgency recommendations (routine/expedited/urgent) based on malignant class probabilities, patient age, and anatomical site | Test | Not Started |
| SUB-PR-0016 | SYS-REQ-0012 | Track skin lesion assessments over time with longitudinal change detection by comparing current and prior image embeddings at the same anatomical site | Test | Not Started |

> **Status rollup rule (v1.6):** Domain status reflects strict rollup from platform requirements — a domain requirement is "Verified" only when ALL of its platform requirements are verified. SUB-PR-0001 downgraded from Implemented → Partial (WEB/AND scaffolded only). SUB-PR-0002 downgraded from Implemented → Partial (BE implemented, explicit verification tests deferred). SUB-PR-0003 downgraded from Verified → Partial (WEB/AND not started). SUB-PR-0004 changed from Verified → Verified (dev) pending AES-256-GCM migration (DC-PR-01). SUB-PR-0006 remains Verified (BE-only). SUB-PR-0005 remains Implemented (BE-only). SUB-PR-0012 added for AI inference queuing (DC-PR-03). SUB-PR-0013 through SUB-PR-0016 added for ISIC Archive dermatology CDS (SYS-REQ-0012). Architecture for SUB-PR-0013–0016 fully defined via 14 ADRs (ADR-0008–0021); implementation not started.

## Platform Decomposition

| Platform | File | Req Count |
|----------|------|-----------|
| Backend (BE) | [SUB-PR-BE](../platform/SUB-PR-BE.md) | 15 |
| Web Frontend (WEB) | [SUB-PR-WEB](../platform/SUB-PR-WEB.md) | 8 |
| Android (AND) | [SUB-PR-AND](../platform/SUB-PR-AND.md) | 8 |
| AI Infrastructure (AI) | [SUB-PR-AI](../platform/SUB-PR-AI.md) | 5 |
