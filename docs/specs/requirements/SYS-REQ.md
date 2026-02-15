# System-Level Requirements (SYS-REQ)

**Document ID:** PMS-SYS-REQ-001
**Version:** 1.0
**Date:** 2026-02-15
**Parent:** [System Specification](../system-spec.md)

---

## Requirements

| Req ID | Description | Priority | Verification | Status |
|---|---|---|---|---|
| SYS-REQ-0001 | Authenticate all users via MFA before granting access to patient data | Critical | Test / Demo | Placeholder |
| SYS-REQ-0002 | Encrypt all patient data at rest using AES-256 and in transit using TLS 1.3 | Critical | Inspection / Test | Placeholder |
| SYS-REQ-0003 | Maintain a complete audit trail of all data access and modifications with user ID, timestamp, action, and resource | Critical | Test | Placeholder |
| SYS-REQ-0004 | Support HL7 FHIR R4 for patient data exchange with external EHR systems | High | Test / Demo | Not Started |
| SYS-REQ-0005 | Enforce role-based access control with minimum four roles: physician, nurse, administrator, billing | Critical | Test | Placeholder |
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

**Decomposes To:** SUB-PR-0001, SUB-CW-0001, SUB-MM-0006, SUB-RA-0004

---

### SYS-REQ-0002: Data Encryption

**Rationale:** HIPAA Security Rule §164.312(a)(2)(iv) requires encryption of ePHI.

**Acceptance Criteria:**
1. All PHI fields (SSN, medical records) encrypted at rest using AES-256.
2. All API traffic uses TLS 1.3.
3. Encryption keys managed separately from application code.

**Decomposes To:** SUB-PR-0004, SUB-MM-0003

---

### SYS-REQ-0003: Audit Trail

**Rationale:** HIPAA Security Rule §164.312(b) requires audit controls.

**Acceptance Criteria:**
1. Every data access (read/write/delete) creates an audit log entry.
2. Audit entries include: user_id, action, resource_type, resource_id, timestamp, IP address.
3. Audit logs are immutable (append-only) and retained for 6+ years.

**Decomposes To:** SUB-PR-0005, SUB-CW-0004, SUB-MM-0004, SUB-RA-0003

---

### SYS-REQ-0005: Role-Based Access Control

**Rationale:** HIPAA Security Rule §164.312(a)(1) requires access controls.

**Acceptance Criteria:**
1. Four roles defined: physician, nurse, administrator, billing.
2. Each API endpoint enforces role requirements.
3. Role assignments modifiable only by administrators.
4. Unauthorized access attempts logged and rejected with 403.

**Decomposes To:** SUB-PR-0002, SUB-CW-0002, SUB-MM-0007, SUB-RA-0005

---

### SYS-REQ-0006: Real-Time Clinical Alerts

**Rationale:** Patient safety requires immediate notification of critical conditions.

**Acceptance Criteria:**
1. Drug interaction alerts generated within 5 seconds of prescription entry.
2. Alert severity classified as: contraindicated, major, moderate, minor.
3. Prescriber can override with documented clinical justification.

**Decomposes To:** SUB-MM-0001, SUB-MM-0002, SUB-CW-0005
