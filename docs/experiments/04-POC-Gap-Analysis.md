# POC Gap Analysis: kind-clinical-data vs PMS System Requirements

**Document ID:** PMS-EXP-GAP-001
**Version:** 1.0
**Date:** 2026-02-16
**POC URL:** https://kind-clinical-data.lovable.app
**POC Source:** https://github.com/utexas-demo/kind-clinical-data
**Built With:** Lovable (React 18 / TypeScript / shadcn-ui / Tailwind CSS / Vite)

---

## Executive Summary

The POC is a **client-side only prototype** demonstrating a clinical data management UI with CRUD operations across patients, encounters, and medications. It includes drug interaction detection, an analytics dashboard, and audit logging — but **lacks all backend infrastructure, authentication, encryption, and persistent storage**.

### Coverage at a Glance

| Category | POC Status |
|---|---|
| UI/UX | Strong — polished, responsive, comprehensive forms |
| Data Models | Strong — well-typed, matches PMS domain |
| CRUD Operations | Implemented for patients, partial for encounters/medications |
| Authentication | **Not implemented** |
| Authorization/RBAC | **Not implemented** |
| Encryption | **Not implemented** |
| Audit Logging | UI only — no backend persistence |
| Backend API | **Not implemented** (client-side state only) |
| Database | **Not implemented** (in-memory, data lost on refresh) |
| Drug Interactions | Basic detection with severity levels |
| Reports | Basic charts with mock data |
| Android App | **Not applicable** (web only) |
| Docker Deployment | **Not implemented** |

---

## System Requirements Gap Analysis

### SYS-REQ-0001: Multi-Factor Authentication (Critical) — NOT MET

| Aspect | Required | POC Status | Gap |
|---|---|---|---|
| Username/password login | Required | Not implemented | No login page or auth flow |
| TOTP/MFA | Required | Not implemented | No MFA support |
| Session tokens | 30-min timeout | Not implemented | No session management |
| Failed attempt logging | Required | Not implemented | No attempt tracking |
| JWT bearer auth | Required on all endpoints | Not implemented | No backend, no tokens |

**Gap Severity: CRITICAL** — No authentication of any kind. All data is accessible without login.

---

### SYS-REQ-0002: Data Encryption (Critical) — NOT MET

| Aspect | Required | POC Status | Gap |
|---|---|---|---|
| PHI encryption at rest (AES-256) | Required | Not implemented | No encryption service |
| SSN field encryption | Required | No SSN field exists | SSN not in data model |
| TLS 1.3 in transit | Required | N/A (no backend) | No API traffic to encrypt |
| Key management | Separate from app code | Not implemented | No key management |

**Gap Severity: CRITICAL** — No encryption. No PHI fields (SSN) in the data model.

---

### SYS-REQ-0003: Audit Trail (Critical) — PARTIALLY MET

| Aspect | Required | POC Status | Gap |
|---|---|---|---|
| Audit log for all data access | Required | UI implemented | Seed data only, not generated from actual actions |
| Fields: user_id, action, resource, timestamp, IP | Required | user_id, action, resource, timestamp present | Missing IP address |
| Immutable (append-only) | Required | Not implemented | In-memory array, deletable |
| 6+ year retention | Required | Not implemented | Data lost on page refresh |
| Covers all subsystems | Required | Shows patient, encounter, medication, report | Seed data only — not triggered by real operations |

**Gap Severity: HIGH** — Audit log UI exists but is cosmetic. Entries are seed data, not generated from actual CRUD operations. No persistence, no immutability, no IP tracking.

---

### SYS-REQ-0004: FHIR R4 Interoperability (High) — NOT MET

| Aspect | Required | POC Status | Gap |
|---|---|---|---|
| HL7 FHIR R4 data exchange | Required | Not implemented | No FHIR resources or endpoints |
| MedicationRequest resource | Required | Not implemented | No FHIR schema mapping |
| MedicationDispense resource | Required | Not implemented | No FHIR schema mapping |

**Gap Severity: HIGH** — No FHIR support. Not unexpected for a UI POC.

---

### SYS-REQ-0005: Role-Based Access Control (Critical) — NOT MET

| Aspect | Required | POC Status | Gap |
|---|---|---|---|
| 4 roles: physician, nurse, admin, billing | Required | Not implemented | No role model |
| Per-endpoint role enforcement | Required | Not implemented | No permission checks |
| Role assignment by admins only | Required | Not implemented | No user management |
| 403 on unauthorized access | Required | Not implemented | All operations allowed for all users |

**Gap Severity: CRITICAL** — No RBAC. Static provider IDs exist (`dr-001`, `dr-002`, `admin-001`) but no role-based permissions.

---

### SYS-REQ-0006: Real-Time Clinical Alerts (High) — PARTIALLY MET

| Aspect | Required | POC Status | Gap |
|---|---|---|---|
| Drug interaction alerts < 5 sec | Required | Implemented (client-side) | Static interaction database, no real-time check |
| Severity classification (4 levels) | Required | All 4 levels implemented | Correct: contraindicated, major, moderate, minor |
| Override with clinical justification | Required | Not implemented | No override workflow |

**Gap Severity: MEDIUM** — Drug interaction detection exists with correct severity levels and color coding. Missing: real-time checking against a drug database, prescriber override workflow.

---

### SYS-REQ-0007: 500+ Concurrent Users (High) — NOT MET

| Aspect | Required | POC Status | Gap |
|---|---|---|---|
| 500+ concurrent users | Required | Not applicable | Client-side only, no backend |
| API response < 2 seconds | Required | Not applicable | No API |
| Load testing | Required | Not implemented | No performance infrastructure |

**Gap Severity: HIGH** — N/A for a client-side POC. Requires backend infrastructure.

---

### SYS-REQ-0008: Web-Based Interface (High) — SUBSTANTIALLY MET

| Aspect | Required | POC Status | Gap |
|---|---|---|---|
| Modern browser support | Required | Implemented (React SPA) | Builds with Vite, uses modern APIs |
| Responsive design | Required | Implemented | Mobile hamburger menu, responsive tables |
| Dashboard | Required | Implemented | Stats, charts, tabs |
| Patient management | Required | Implemented | Full CRUD with forms |
| Encounter management | Required | Implemented | Create, view, status transitions |
| Medication management | Required | Partial | View/filter only, no create/edit |
| Reports | Required | Implemented | 3 chart tabs with Recharts |

**Gap Severity: LOW** — This is the POC's strongest area. Comprehensive web UI with responsive design.

---

### SYS-REQ-0009: Native Android Application (High) — NOT MET

| Aspect | Required | POC Status | Gap |
|---|---|---|---|
| Native Android app | Required | Not implemented | Web-only POC |
| Kotlin/Jetpack Compose | Required | Not applicable | No Android code |
| Offline support | Required | Not implemented | No local storage |

**Gap Severity: HIGH** — POC is web-only. The PMS Android app (`pms-android`) is a separate effort.

---

### SYS-REQ-0010: Docker Deployment (Medium) — NOT MET

| Aspect | Required | POC Status | Gap |
|---|---|---|---|
| Docker containers | Required | Not implemented | No Dockerfile |
| docker-compose | Required | Not implemented | No orchestration |
| All components containerized | Required | Not implemented | Deployed via Lovable hosting |

**Gap Severity: MEDIUM** — No Docker setup. POC is deployed on Lovable's hosting platform.

---

## Subsystem Gap Analysis

### SUB-PR — Patient Records

| Req ID | Description | POC Status | Gap |
|---|---|---|---|
| SUB-PR-0001 | Auth for patient data access | Not implemented | No auth |
| SUB-PR-0002 | RBAC on patient operations | Not implemented | No roles |
| SUB-PR-0003 | CRUD for patient demographics | **Implemented** | Full CRUD with validation |
| SUB-PR-0004 | Encrypt SSN/PHI at rest | Not implemented | No SSN field, no encryption |
| SUB-PR-0005 | Audit log patient access | Cosmetic only | Seed data, not real logging |
| SUB-PR-0006 | Email uniqueness | Not implemented | No uniqueness validation |
| SUB-PR-0007 | Patient search | **Implemented** | Search by name and phone |
| SUB-PR-0008 | Paginated results | **Implemented** | 10 per page with prev/next |
| SUB-PR-0009 | Wound assessment (AI vision) | Not implemented | No camera/AI features |
| SUB-PR-0010 | Patient ID verification (AI) | Not implemented | No camera/AI features |
| SUB-PR-0011 | Document OCR | Not implemented | No OCR features |

**POC Coverage: 3/11 requirements implemented (27%)**

---

### SUB-CW — Clinical Workflow

| Req ID | Description | POC Status | Gap |
|---|---|---|---|
| SUB-CW-0001 | Auth for encounter access | Not implemented | No auth |
| SUB-CW-0002 | RBAC on encounters | Not implemented | No roles |
| SUB-CW-0003 | Encounter lifecycle | **Implemented** | Valid state transitions enforced |
| SUB-CW-0004 | Audit encounter access | Cosmetic only | Seed data, not real logging |
| SUB-CW-0005 | Clinical alerts from encounters | Not implemented | No alert triggers |
| SUB-CW-0006 | Encounter types (4 types) | **Implemented** | office_visit, telehealth, emergency, follow_up |
| SUB-CW-0007 | Status transition validation | **Implemented** | VALID_STATUS_TRANSITIONS enforced |
| SUB-CW-0008 | Patient FK on encounters | **Implemented** | patientId required on creation |

**POC Coverage: 4/8 requirements implemented (50%)**

---

### SUB-MM — Medication Management

| Req ID | Description | POC Status | Gap |
|---|---|---|---|
| SUB-MM-0001 | Drug interaction check < 5 sec | **Partially implemented** | Client-side check against static data |
| SUB-MM-0002 | Interaction severity (4 levels) | **Implemented** | contraindicated, major, moderate, minor |
| SUB-MM-0003 | Encrypt prescription PHI | Not implemented | No encryption |
| SUB-MM-0004 | Audit prescription events | Cosmetic only | Seed data |
| SUB-MM-0005 | FHIR R4 MedicationRequest | Not implemented | No FHIR |
| SUB-MM-0006 | Auth for medication access | Not implemented | No auth |
| SUB-MM-0007 | RBAC on medications | Not implemented | No roles |
| SUB-MM-0008 | Prescription lifecycle | **Partially implemented** | Status displayed but no transitions |
| SUB-MM-0009 | Refill tracking | **Implemented** | refillsRemaining with zero-refill highlight |

**POC Coverage: 3.5/9 requirements implemented (39%)**

---

### SUB-RA — Reporting & Analytics

| Req ID | Description | POC Status | Gap |
|---|---|---|---|
| SUB-RA-0001 | Patient volume report | **Implemented** | Bar chart of registrations by month |
| SUB-RA-0002 | Encounter summary report | **Implemented** | Pie charts by type and status |
| SUB-RA-0003 | Audit log query interface | **Implemented** | Filterable/searchable audit table |
| SUB-RA-0004 | Auth for report access | Not implemented | No auth |
| SUB-RA-0005 | RBAC on reports | Not implemented | No roles |
| SUB-RA-0006 | Medication usage report | **Implemented** | Bar chart of top medications |
| SUB-RA-0007 | CSV export | Not implemented | No export functionality |

**POC Coverage: 4/7 requirements implemented (57%)**

---

## Feature Comparison: POC vs PMS Backend

| Feature | POC (kind-clinical-data) | PMS Backend (pms-backend) |
|---|---|---|
| **Tech Stack** | React SPA (client-only) | FastAPI + PostgreSQL + SQLAlchemy |
| **Data Persistence** | In-memory (lost on refresh) | PostgreSQL database |
| **Authentication** | None | JWT bearer tokens |
| **RBAC** | None | Per-endpoint role enforcement |
| **Encryption** | None | Fernet (AES-128-CBC) for SSN |
| **Audit Logging** | UI cosmetic | audit_service with real logging |
| **Patient CRUD** | Full UI with validation | Full API with tests (157 passing) |
| **Encounter CRUD** | Create + status transitions | Stub endpoints |
| **Medication CRUD** | View/filter only | Stub endpoints |
| **Drug Interactions** | Static client-side check | Stub interaction checker |
| **Reports** | Charts with Recharts | Stub report endpoints |
| **Search** | Client-side filtering | Not implemented |
| **Pagination** | Client-side (10/page) | Not implemented |
| **Tests** | Vitest configured (no tests written) | 157 tests passing |
| **CI/CD** | None | CI + SonarCloud + Snyk |

---

## Strengths of the POC

1. **UI Quality** — Polished, responsive design with shadcn-ui components
2. **Data Models** — Well-typed TypeScript interfaces that align with PMS domain models
3. **Encounter Workflow** — Status transition validation correctly implemented
4. **Drug Interactions** — Severity classification with 4 levels and color coding
5. **Reports Dashboard** — Three-tab analytics with interactive charts
6. **Audit Log UI** — Filterable, searchable audit trail interface
7. **Form Validation** — Comprehensive Zod validation on patient forms
8. **Patient Search** — Multi-field search with sorting and pagination
9. **Responsive Design** — Mobile-friendly with hamburger sidebar

---

## Critical Gaps Summary

### Must-Have Before Production (HIPAA Blockers)

| # | Gap | SYS-REQ | Severity |
|---|---|---|---|
| 1 | **No authentication** — anyone can access all data | SYS-REQ-0001 | CRITICAL |
| 2 | **No RBAC** — no role-based access control | SYS-REQ-0005 | CRITICAL |
| 3 | **No encryption** — PHI fields not encrypted, SSN not in model | SYS-REQ-0002 | CRITICAL |
| 4 | **No backend** — all data is client-side, lost on refresh | All | CRITICAL |
| 5 | **No real audit trail** — seed data only, not triggered by actions | SYS-REQ-0003 | CRITICAL |

### High Priority Gaps

| # | Gap | SYS-REQ | Severity |
|---|---|---|---|
| 6 | No persistent database (PostgreSQL) | All | HIGH |
| 7 | No Android app | SYS-REQ-0009 | HIGH |
| 8 | No FHIR R4 interoperability | SYS-REQ-0004 | HIGH |
| 9 | No Docker deployment | SYS-REQ-0010 | HIGH |
| 10 | No CI/CD pipeline | — | HIGH |

### Medium Priority Gaps

| # | Gap | SYS-REQ | Severity |
|---|---|---|---|
| 11 | Medication CRUD incomplete (view only, no create/edit) | SUB-MM-0008 | MEDIUM |
| 12 | No prescriber override for drug interactions | SYS-REQ-0006 | MEDIUM |
| 13 | No CSV export for reports | SUB-RA-0007 | MEDIUM |
| 14 | No email uniqueness validation | SUB-PR-0006 | MEDIUM |
| 15 | No real drug interaction database | SUB-MM-0001 | MEDIUM |

### Low Priority / Future Gaps

| # | Gap | SYS-REQ | Severity |
|---|---|---|---|
| 16 | No AI vision features (wound assessment, patient ID, OCR) | SUB-PR-0009/10/11 | LOW (future) |
| 17 | No performance/load testing | SYS-REQ-0007 | LOW (future) |
| 18 | No patient search by DOB or ID | SUB-PR-0007 | LOW |

---

## Recommendations

### 1. Adopt POC UI Patterns into pms-frontend

The POC demonstrates excellent UI patterns that should be adopted:
- **Patient form** with Zod validation → port to `pms-frontend`
- **Encounter status transitions** → port the `VALID_STATUS_TRANSITIONS` logic
- **Drug interaction severity badges** → adopt color coding scheme
- **Reports dashboard** with Recharts → port chart implementations
- **Audit log viewer** with filters → port to reports page
- **Responsive sidebar** → evaluate against current `pms-frontend` sidebar

### 2. Use POC Data Models as Reference

The POC's TypeScript interfaces closely match the PMS domain models. Validate alignment:
- `Patient` type → compare with `src/types/patient.ts` in `pms-frontend`
- `Encounter` type → compare with `src/types/encounter.ts`
- `Medication` type → compare with `src/types/medication.ts`

### 3. Bridge POC UI to PMS Backend

Connect POC-quality UI to the existing `pms-backend` FastAPI server:
- Replace React Context state with API calls to FastAPI endpoints
- Replace seed data with real database queries
- Add JWT auth token management
- Add RBAC-aware UI (hide/disable features based on user role)

### 4. Address HIPAA Gaps Before Any Production Use

The 5 critical gaps (auth, RBAC, encryption, backend, audit) must be resolved through the existing `pms-backend` infrastructure — not by adding them to the client-side POC.

---

## Overall Assessment

| Metric | Score |
|---|---|
| **System Requirements Met** | 1.5 / 10 (15%) |
| **Subsystem Requirements Met** | 14.5 / 35 (41%) — but only UI layer |
| **UI/UX Quality** | Excellent |
| **Production Readiness** | Not production-ready (HIPAA blockers) |
| **Value as Reference** | High — excellent UI patterns for adoption |

The POC is a **strong UI demonstration** that validates the PMS user experience design. Its value is as a **reference implementation for the frontend layer**, not as a production system. All HIPAA-critical requirements (auth, RBAC, encryption, audit, persistence) must come from the `pms-backend` infrastructure.
