# System-Level Requirements (SYS-REQ)

**Document ID:** PMS-SYS-REQ-001
**Version:** 1.4
**Date:** 2026-02-17
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

---

## Requirement Details

### SYS-REQ-0001: Multi-Factor Authentication

**Rationale:** HIPAA Security Rule §164.312(d) requires person or entity authentication.

**Acceptance Criteria:**
1. Users must provide username + password + TOTP code to access the system.
2. Failed MFA attempts must be logged (SYS-REQ-0003).
3. Session tokens expire after the configured timeout (default: 30 minutes).

**Current Implementation:** JWT bearer authentication enforced on all patient endpoints via `require_role` → `require_auth` dependency chain. TOTP (MFA) not yet implemented — current login issues JWT from username + password only.

**Decomposes To:** SUB-PR-0001 (→ BE, WEB, AND), SUB-CW-0001 (→ BE, WEB, AND), SUB-MM-0006 (→ BE, WEB, AND), SUB-RA-0004 (→ BE, WEB, AND)

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

**Decomposes To:** SUB-PR-0005 (→ BE), SUB-CW-0004 (→ BE), SUB-MM-0004 (→ BE), SUB-RA-0003 (→ BE, WEB, AND)

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

**Decomposes To:** SUB-PR-0002 (→ BE), SUB-CW-0002 (→ BE), SUB-MM-0007 (→ BE), SUB-RA-0005 (→ BE)

---

### SYS-REQ-0006: Real-Time Clinical Alerts

**Rationale:** Patient safety requires immediate notification of critical conditions.

**Acceptance Criteria:**
1. Drug interaction alerts generated within 5 seconds of prescription entry.
2. Alert severity classified as: contraindicated, major, moderate, minor.
3. Prescriber can override with documented clinical justification.

**Decomposes To:** SUB-MM-0001 (→ BE, WEB, AND), SUB-MM-0002 (→ BE), SUB-CW-0005 (→ BE)
