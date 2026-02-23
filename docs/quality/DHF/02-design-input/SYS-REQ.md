# System-Level Requirements (SYS-REQ)

**Document ID:** PMS-SYS-REQ-001
**Version:** 1.7
**Date:** 2026-02-21
**Parent:** [System Specification](../system-spec.md)

---

## Requirements

| Req ID | Description | Priority | Verification | Status |
|---|---|---|---|---|
| SYS-REQ-0001 | Authenticate all users via MFA before granting access to patient data | Critical | Test / Demo | Partial |
| SYS-REQ-0002 | Encrypt all patient data at rest using AES-256 and in transit using TLS 1.3 | Critical | Inspection / Test | Partial |
| SYS-REQ-0003 | Maintain a complete audit trail of all data access and modifications with user ID, timestamp, action, and resource | Critical | Test | Partial |
| SYS-REQ-0004 | Support HL7 FHIR R4 for patient data exchange with external EHR systems | High | Test / Demo | Not Started |
| SYS-REQ-0005 | Enforce role-based access control with minimum five roles: physician, nurse, administrator, billing, pharmacist | Critical | Test | Partial |
| SYS-REQ-0006 | Generate real-time clinical alerts for critical lab values and drug interactions within 30 seconds | High | Test | Placeholder |
| SYS-REQ-0007 | Support 500+ concurrent users with API response times under 2 seconds | High | Load Test | Not Started |
| SYS-REQ-0008 | Provide a web-based interface accessible from modern browsers (Chrome, Firefox, Safari, Edge) | High | Demo | Scaffolded |
| SYS-REQ-0009 | Provide a native Android application for mobile clinical workflows | High | Demo | Scaffolded |
| SYS-REQ-0010 | All system components must be deployable via Docker containers | Medium | Inspection | Scaffolded |
| SYS-REQ-0011 | Provide centralized prompt management with versioning, CRUD operations, and LLM-powered comparison for all AI prompts used across the system | High | Test / Demo | Not Started |
| SYS-REQ-0012 | Provide AI-assisted skin lesion classification and dermatology clinical decision support using ISIC Archive-trained models with on-premises inference, similarity search, and structured risk scoring | High | Test / Demo | Architecture Defined |

---

## Requirement Details

### SYS-REQ-0001: Multi-Factor Authentication

**Rationale:** HIPAA Security Rule §164.312(d) requires person or entity authentication.

**Acceptance Criteria:**
1. Users must provide username + password + TOTP code to access the system.
2. Failed MFA attempts must be logged (SYS-REQ-0003).
3. Session tokens expire after the configured timeout (default: 30 minutes).

**Current Implementation:** JWT bearer authentication enforced on all patient endpoints via `require_role` → `require_auth` dependency chain. TOTP (MFA) not yet implemented — current login issues JWT from username + password only.

**Decomposes To:** SUB-PR-0001 (→ BE, WEB, AND), SUB-CW-0001 (→ BE, WEB, AND), SUB-MM-0006 (→ BE, WEB, AND), SUB-RA-0004 (→ BE, WEB, AND), SUB-PM-0001 (→ BE, WEB)

---

### SYS-REQ-0002: Data Encryption

**Rationale:** HIPAA Security Rule §164.312(a)(2)(iv) requires encryption of ePHI.

**Acceptance Criteria:**
1. All PHI fields (SSN, medical records) encrypted at rest using AES-256.
2. All API traffic uses TLS 1.3.
3. Encryption keys managed separately from application code.

**Current Implementation:** Patient SSN is encrypted at rest via Fernet (AES-128-CBC) using `cryptography.fernet`. Production migration to AES-256-GCM (via `cryptography.hazmat.primitives.ciphers.aead.AESGCM` with a 32-byte KMS-derived key) is required before deployment to satisfy the AES-256 criterion above.

**Decomposes To:** SUB-PR-0004 (→ BE), SUB-MM-0003 (→ BE)

---

### SYS-REQ-0003: Audit Trail

**Rationale:** HIPAA Security Rule §164.312(b) requires audit controls.

**Acceptance Criteria:**
1. Every data access (read/write/delete) creates an audit log entry.
2. Audit entries include: user_id, action, resource_type, resource_id, timestamp, IP address.
3. Audit logs are immutable (append-only) and retained for 6+ years.

**Current Implementation:** All 5 patient router methods call `audit_service.log_action` with user_id, action, resource_type, resource_id, and IP address. Encounter, medication, and report endpoint audit logging not yet implemented.

**Decomposes To:** SUB-PR-0005 (→ BE), SUB-CW-0004 (→ BE), SUB-MM-0004 (→ BE), SUB-RA-0003 (→ BE, WEB, AND), SUB-PM-0005 (→ BE)

---

### SYS-REQ-0005: Role-Based Access Control

**Rationale:** HIPAA Security Rule §164.312(a)(1) requires access controls.

**Acceptance Criteria:**
1. Five roles defined: physician, nurse, administrator, billing, pharmacist.
2. Each API endpoint enforces role requirements.
3. Role assignments modifiable only by administrators.
4. Unauthorized access attempts logged and rejected with 403.
5. A consolidated RBAC matrix maps every endpoint to its allowed roles across all subsystems.

**Current Implementation:** `require_role` dependency enforced on all 5 patient endpoints with per-endpoint role lists (admin/physician/nurse for read & create, admin/physician for update, admin only for deactivate). Encounter, medication, and report endpoint RBAC not yet implemented.

> **Governance note (PC-BE-04):** The pharmacist role is required by SUB-MM-0007 (medication dispensing). The original 4-role model has been expanded to 5 roles to eliminate the cross-subsystem role inconsistency.

**Decomposes To:** SUB-PR-0002 (→ BE), SUB-CW-0002 (→ BE), SUB-MM-0007 (→ BE), SUB-RA-0005 (→ BE), SUB-PM-0002 (→ BE)

---

### SYS-REQ-0006: Real-Time Clinical Alerts

**Rationale:** Patient safety requires immediate notification of critical conditions.

**Acceptance Criteria:**
1. Drug interaction alerts generated within 5 seconds of prescription entry.
2. Alert severity classified as: contraindicated, major, moderate, minor.
3. Prescriber can override with documented clinical justification.

**Decomposes To:** SUB-MM-0001 (→ BE, WEB, AND), SUB-MM-0002 (→ BE), SUB-CW-0005 (→ BE)

---

### SYS-REQ-0011: Centralized Prompt Management

**Rationale:** The PMS uses AI prompts in multiple contexts (OpenClaw skills, MiniMax M2.5 agents, clinical document drafting). Prompts are currently scattered across code and configuration with no centralized management, versioning, or change tracking. A centralized subsystem enables consistent governance, audit trailing, and LLM-powered comparison of prompt versions.

**Acceptance Criteria:**
1. Administrators can create, read, update, and delete AI prompts via the web interface.
2. Every prompt text modification creates a new immutable version with an auto-incremented version number.
3. All prompt operations are recorded in the system audit trail.
4. Users can view paginated version history for any prompt.
5. Users can compare any two versions of a prompt via LLM-generated natural-language diff summary.

**Current Implementation:** Not started.

**Decomposes To:** SUB-PM-0003 (→ BE, WEB), SUB-PM-0004 (→ BE, WEB), SUB-PM-0006 (→ BE, WEB), SUB-PM-0007 (→ BE, WEB, AI)

---

### SYS-REQ-0012: Dermatology Clinical Decision Support

**Rationale:** Primary care clinicians encounter suspicious skin lesions daily but lack dermoscopy expertise. Visual inspection alone achieves ~60% accuracy for skin lesion classification. The ISIC Archive (International Skin Imaging Collaboration) provides 400,000+ expert-annotated dermoscopic images that have been used to train AI models achieving 85-95% classification accuracy — matching or exceeding general dermatologists. On-premises inference ensures patient images never leave the network, satisfying HIPAA requirements.

**Acceptance Criteria:**
1. Clinicians can upload a dermoscopic image and receive AI classification across 9 ISIC diagnostic categories within 5 seconds.
2. Classification results include a structured risk score (low/medium/high) with referral urgency (routine/expedited/urgent).
3. The system displays visually similar ISIC reference images for clinical comparison (top-10 by cosine similarity).
4. Patient dermoscopic images are encrypted at rest using AES-256-GCM and never transmitted to external services.
5. All image uploads, classifications, and result views are recorded in the audit trail.
6. Lesion assessments are linked to patient records and encounters for longitudinal tracking.
7. The Android app supports on-device inference via TFLite for offline skin lesion triage.

**Current Implementation:** Architecture fully defined via 14 ADRs (ADR-0008 through ADR-0021). No code implementation started. PRD, developer setup guide, and developer tutorial completed (experiment 18).

**Architecture Decisions:**
- [ADR-0008](../../architecture/0008-derm-cds-microservice-architecture.md): Separate Docker service (`pms-derm-cds` :8090)
- [ADR-0009](../../architecture/0009-ai-inference-runtime.md): ONNX Runtime (server) + TensorRT (Jetson) + TFLite (Android)
- [ADR-0010](../../architecture/0010-dermoscopic-image-storage.md): AES-256-GCM encrypted BYTEA in PostgreSQL
- [ADR-0011](../../architecture/0011-vector-database-pgvector.md): pgvector extension for similarity search
- [ADR-0012](../../architecture/0012-android-on-device-inference.md): TFLite with MobileNetV3 for offline triage
- [ADR-0013](../../architecture/0013-ai-model-lifecycle.md): Versioned model artifacts with provenance tracking
- [ADR-0014](../../architecture/0014-image-preprocessing-pipeline.md): Resize/normalize pipeline with quality gates
- [ADR-0015](../../architecture/0015-risk-scoring-engine.md): Configurable threshold-based risk scoring
- [ADR-0016](../../architecture/0016-image-encryption-key-management.md): Unified versioned-envelope key management
- [ADR-0017](../../architecture/0017-isic-reference-cache.md): S3 bulk population with model-version coupling
- [ADR-0018](../../architecture/0018-inter-service-communication.md): HTTP client pooling with circuit breaking
- [ADR-0019](../../architecture/0019-lesion-longitudinal-tracking.md): Persistent lesion identity with embedding cosine distance
- [ADR-0020](../../architecture/0020-derm-cds-feature-flags.md): Granular per-requirement feature flags
- [ADR-0021](../../architecture/0021-derm-database-migration.md): Alembic-managed migrations for pgvector tables

**Decomposes To:** SUB-PR-0013 (→ BE, WEB, AND, AI), SUB-PR-0014 (→ BE, WEB, AI), SUB-PR-0015 (→ BE, WEB), SUB-PR-0016 (→ BE, WEB), SUB-RA-0008 (→ BE, WEB)
