# System-Level Requirements (SYS-REQ)

**Document ID:** PMS-SYS-REQ-001
**Version:** 1.9
**Date:** 2026-02-23
**Parent:** [System Specification](../system-spec.md)

---

## Requirements

| Req ID | Description | Priority | Verification | Status |
| --- | --- | --- | --- | --- |
| SYS-REQ-0001 | Authenticate all users via multi-factor authentication before granting access to patient data; OAuth users satisfy MFA via provider-enforced policies, email/password users via TOTP (deferred to follow-up) | Critical | Test / Demo | Partial |
| SYS-REQ-0002 | Encrypt all patient data at rest using AES-256 and in transit using TLS 1.3 | Critical | Inspection / Test | Partial |
| SYS-REQ-0003 | Maintain a complete audit trail of all data access and modifications with user ID, timestamp, action, and resource | Critical | Test | Partial |
| SYS-REQ-0004 | Support HL7 FHIR R4 for patient data exchange with external EHR systems | High | Test / Demo | Not Started |
| SYS-REQ-0005 | Enforce role-based access control with four roles: admin, clinician, sales, lab-staff; permissions evaluated as the union of all assigned roles | Critical | Test | Partial |
| SYS-REQ-0006 | Generate real-time clinical alerts for critical lab values and drug interactions within 30 seconds | High | Test | Placeholder |
| SYS-REQ-0007 | Support 500+ concurrent users with API response times under 2 seconds | High | Load Test | Not Started |
| SYS-REQ-0008 | Provide a web-based interface accessible from modern browsers (Chrome, Firefox, Safari, Edge) | High | Demo | Scaffolded |
| SYS-REQ-0009 | Provide a native Android application for mobile clinical workflows | High | Demo | Scaffolded |
| SYS-REQ-0010 | All system components must be deployable via Docker containers | Medium | Inspection | Scaffolded |
| SYS-REQ-0011 | Provide centralized prompt management with versioning, CRUD operations, and LLM-powered comparison for all AI prompts used across the system | High | Test / Demo | Not Started |
| SYS-REQ-0012 | Provide AI-assisted skin lesion classification and dermatology clinical decision support using ISIC Archive-trained models with on-premises inference, similarity search, and structured risk scoring | High | Test / Demo | Architecture Defined |
| SYS-REQ-0013 | Orchestrate the DermaCheck capture-classify-review pipeline as a single-request parallel fan-out with graceful degradation, completing all AI stages within 5 seconds | High | Test / Demo | Architecture Defined |
| SYS-REQ-0014 | Support closed-registration authentication via OAuth 2.0 (Google, Microsoft, GitHub) and email/password with JWT-based session management | Critical | Test / Demo | Not Started |
| SYS-REQ-0015 | Provide admin-controlled user management with invite-based onboarding, account lifecycle (invited/active/inactive), and role assignment | Critical | Test / Demo | Not Started |

---

## Requirement Details

### SYS-REQ-0001: Multi-Factor Authentication

**Rationale:** HIPAA Security Rule §164.312(d) requires person or entity authentication.

**Acceptance Criteria:**

1. OAuth users (Google, Microsoft, GitHub) satisfy MFA via provider-enforced authentication policies (providers support and enforce their own MFA).
2. Email/password users authenticate via credentials with TOTP as a second factor (TOTP deferred to follow-up release).
3. Failed authentication attempts must be logged (SYS-REQ-0003).
4. Session tokens (JWT) expire after the configured timeout (default: 30 minutes, configurable via `JWT_EXPIRY_MINUTES`).
5. Refresh tokens (opaque, server-side) enable silent session renewal with a 7-day lifetime.
6. Account locks after 5 consecutive failed email/password attempts (30-minute lockout).

**Current Implementation:** JWT bearer authentication enforced on all patient endpoints via `require_role` → `require_auth` dependency chain. TOTP (MFA) not yet implemented — current login issues JWT from username + password only. OAuth providers and refresh tokens not yet implemented.

**Related Feature:** [Authentication & User Management](../../features/authentication.md)

**Decomposes To:** SUB-AU-0003 (→ BE, WEB, AND), SUB-AU-0004 (→ BE, WEB, AND), SUB-PR-0001 (→ BE, WEB, AND), SUB-CW-0001 (→ BE, WEB, AND), SUB-MM-0006 (→ BE, WEB, AND), SUB-RA-0004 (→ BE, WEB, AND), SUB-PM-0001 (→ BE, WEB)

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

1. Four roles defined: `admin`, `clinician`, `sales`, `lab-staff`.
2. A user can hold one or more roles simultaneously; permissions are the **union** of all assigned roles.
3. Each API endpoint enforces role requirements; access granted if any of the user's roles is in the endpoint's allowed list.
4. Role assignments modifiable only by administrators.
5. An admin cannot remove the `admin` role from the last remaining admin user (lockout prevention).
6. Unauthorized access attempts logged and rejected with 403.
7. A consolidated role-permission matrix maps every feature area to its allowed roles (see [Authentication feature §4.3](../../features/authentication.md)).
8. Role changes take effect on the next token issuance; existing tokens retain previous roles until expiry.

**Role Mapping (from previous model):**

| Previous Role | New Role | Rationale |
| --- | --- | --- |
| physician | clinician | `clinician` covers physicians, nurses, and pharmacists |
| nurse | clinician | Consolidated under `clinician` |
| administrator | admin | Renamed for consistency |
| billing | sales | `sales` covers billing and patient intake |
| pharmacist | clinician | Consolidated under `clinician` |

**Current Implementation:** `require_role` dependency enforced on all 5 patient endpoints with per-endpoint role lists. Role model migration from 5 roles to 4 roles not yet implemented. Encounter, medication, and report endpoint RBAC not yet implemented.

> **Governance note:** The previous 5-role model (physician, nurse, administrator, billing, pharmacist — see PC-BE-04) has been superseded by the 4-role model defined in the [Authentication & User Management](../../features/authentication.md) feature. The `clinician` role now covers physicians, nurses, and pharmacists. The `sales` role covers billing and patient intake.

**Related Feature:** [Authentication & User Management](../../features/authentication.md)

**Decomposes To:** SUB-AU-0008 (→ BE, WEB), SUB-AU-0009 (→ BE, WEB, AND), SUB-AU-0010 (→ BE), SUB-PR-0002 (→ BE), SUB-CW-0002 (→ BE), SUB-MM-0007 (→ BE), SUB-RA-0005 (→ BE), SUB-PM-0002 (→ BE)

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

---

### SYS-REQ-0013: DermaCheck Workflow Orchestration

**Rationale:** The DermaCheck workflow (Journey 1) chains four AI processing stages — EfficientNet-B4 classification, Gemma 3 clinical narrative, pgvector similarity search, and risk scoring — into a single clinical interaction. Without explicit orchestration requirements, stages may execute sequentially (exceeding latency targets), fail silently (returning incomplete results without indication), or create ambiguous ownership between the Backend and CDS services. HIPAA Security Rule §164.312(b) requires audit controls over each processing stage, and §164.306(a) requires contingency planning for component failures. A defined orchestration pattern ensures predictable latency, transparent degradation, and auditable processing for every lesion assessment.

**Acceptance Criteria:**
1. The DermaCheck pipeline completes classification, clinical narrative, similarity search, and risk scoring within a single HTTP request/response cycle — no client-side polling, streaming, or multi-request assembly required.
2. EfficientNet-B4 classification executes first; Gemma 3 narrative generation, pgvector similarity search, and risk scoring execute in parallel after classification completes (fan-out pattern).
3. Total end-to-end latency from image upload to full results response is under 5 seconds for a single image on server-side inference.
4. If a non-critical parallel stage (Gemma 3 narrative, similarity search, or risk scoring) fails or times out, the system returns partial results with a `degraded` indicator — classification is the only hard-fail stage.
5. The DermCDS Service (:8090) owns all AI orchestration logic; the PMS Backend (:8000) acts as a thin proxy that validates input, forwards to CDS, persists results, and returns the response.
6. The response payload (`DermaCheckResult`) includes classification, narrative, risk score, similar images, embedding ID, model version, and degradation status as a single atomic structure.
7. Every pipeline execution is recorded in the audit trail with: model version, per-stage latency, degradation status, and the physician who initiated the assessment.

**Current Implementation:** Architecture defined in ADR-0022 (DermaCheck Core Workflow Orchestration). No code implementation started.

**Architecture Decisions:**
- [ADR-0022](../../architecture/0022-dermacheck-workflow-orchestration.md): Parallel fan-out pipeline with graceful degradation
- [ADR-0008](../../architecture/0008-derm-cds-microservice-architecture.md): CDS as separate Docker service (pipeline host)
- [ADR-0018](../../architecture/0018-inter-service-communication.md): Backend-to-CDS HTTP communication with circuit breaking

**Decomposes To:** SUB-PR-0017 (→ BE, AI), SUB-CW-0009 (→ BE, WEB, AND)

---

### SYS-REQ-0014: Authentication Methods

**Rationale:** The PMS operates under a closed-registration model where only administrator-created accounts can access the system. Supporting multiple authentication methods (OAuth 2.0 and email/password) accommodates diverse organizational identity providers while maintaining strict access control. HIPAA Security Rule §164.312(d) requires person or entity authentication.

**Acceptance Criteria:**

1. The system supports three OAuth 2.0 providers: Google, Microsoft, and GitHub, using the Authorization Code flow with PKCE.
2. OAuth login succeeds only if the user's email already exists in the system (no self-registration).
3. OAuth login for an inactive user returns 403 ("Account disabled").
4. OAuth login for an unregistered email returns 403 ("Account not registered").
5. On first OAuth login for a provider, the system creates a `user_oauth_accounts` record linking the provider identity to the user.
6. Email/password login validates credentials and issues a JWT session token.
7. Passwords must meet minimum complexity requirements: 12+ characters, mixed case, digit, and special character.
8. Passwords are stored as bcrypt hashes with cost factor 12.
9. JWT tokens include `sub` (user UUID), `email`, `name`, `roles`, `iat`, and `exp` claims.
10. All authentication endpoints are accessible without prior authentication (public endpoints).

**Current Implementation:** Not started.

**Related Feature:** [Authentication & User Management](../../features/authentication.md)

**Decomposes To:** SUB-AU-0001 (→ BE, WEB, AND), SUB-AU-0002 (→ BE, WEB, AND), SUB-AU-0012 (→ BE), SUB-AU-0013 (→ BE), SUB-AU-0014 (→ BE)

---

### SYS-REQ-0015: Admin-Controlled User Management

**Rationale:** Under the closed-registration model, an administrator must control all user provisioning to satisfy HIPAA's minimum necessary access principle. Users cannot self-register. A seeded admin account bootstraps the system on first deployment.

**Acceptance Criteria:**

1. On first deployment, the system seeds a default admin account from environment variables (`ADMIN_SEED_EMAIL`, `ADMIN_SEED_NAME`, `ADMIN_SEED_PASSWORD`); the seed operation is idempotent.
2. Only users with the `admin` role can create, update, deactivate, or reactivate user accounts.
3. User creation requires email, full name, and at least one role; the system validates email uniqueness and role existence.
4. Newly created users receive status `invited` and a one-time invite token (72-hour expiry) sent via email.
5. Users activate their account by accepting the invite and setting a password; status transitions to `active`.
6. Admins can deactivate a user (status → `inactive`), immediately revoking all active sessions.
7. Admins can reactivate a previously deactivated user (status → `active`).
8. Admins can update a user's roles at any time; every user must retain at least one role.
9. Admins can resend an expired invite, generating a new token.
10. A non-admin user receives 403 for any user management operation.

**Current Implementation:** Not started.

**Related Feature:** [Authentication & User Management](../../features/authentication.md)

**Decomposes To:** SUB-AU-0005 (→ BE), SUB-AU-0006 (→ BE, WEB), SUB-AU-0007 (→ BE, WEB, AND), SUB-AU-0011 (→ BE), SUB-AU-0014 (→ BE), SUB-AU-0015 (→ WEB, AND)
