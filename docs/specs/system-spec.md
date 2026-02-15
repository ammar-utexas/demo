# System Specification: Patient Management System (PMS)

**Document ID:** PMS-SYS-SPEC-001
**Version:** 1.0
**Date:** 2026-02-15
**Status:** Approved

---

## 1. Purpose

This document defines the system-level specification for the Patient Management System (PMS), a HIPAA-compliant software suite for managing patient records, clinical workflows, medications, and reporting across a multi-facility healthcare organization.

## 2. Scope

The PMS consists of three deployable components sharing a common backend API:

| Component | Repository | Technology |
|---|---|---|
| Backend API | `ammar-utexas/pms-backend` | Python, FastAPI, PostgreSQL |
| Web Frontend | `ammar-utexas/pms-frontend` | Next.js, React, TypeScript |
| Android App | `ammar-utexas/pms-android` | Kotlin, Jetpack Compose |

All components share a documentation submodule (`ammar-utexas/demo`) containing specifications, requirements, and traceability evidence.

## 3. System Context

```
┌─────────────────────────────────────────────────┐
│                  PMS System                     │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │  Web UI  │  │ Android  │  │  Backend API │  │
│  │ (Next.js)│  │ (Kotlin) │  │  (FastAPI)   │  │
│  └────┬─────┘  └────┬─────┘  └──────┬───────┘  │
│       │              │               │          │
│       └──────────────┴───────────────┘          │
│                      │                          │
│              ┌───────┴────────┐                 │
│              │  PostgreSQL DB │                 │
│              └────────────────┘                 │
└─────────────────────────────────────────────────┘
         │                    │
    ┌────┴────┐         ┌────┴────┐
    │ External│         │  Audit  │
    │  EHR    │         │  Log    │
    │ (FHIR)  │         │ Archive │
    └─────────┘         └─────────┘
```

## 4. Subsystem Decomposition

| Code | Subsystem | Scope | Primary Actor |
|---|---|---|---|
| SUB-PR | Patient Records | Demographics, medical history, documents, consent, encrypted PHI | All roles |
| SUB-CW | Clinical Workflow | Scheduling, encounters, status tracking, clinical notes, referrals | Physicians, Nurses |
| SUB-MM | Medication Management | Prescriptions, drug interactions, formulary, dispensing | Physicians, Pharmacists |
| SUB-RA | Reporting & Analytics | Clinical dashboards, compliance reports, audit log queries | Administrators, Compliance |

## 5. User Roles

| Role | Access Level | Description |
|---|---|---|
| Physician | Full clinical | All patient data, prescribe medications, clinical notes |
| Nurse | Clinical read/write | Patient vitals, encounter notes, medication administration |
| Administrator | System management | User management, configuration, compliance reports |
| Billing | Financial only | Insurance, billing codes, financial reports |

## 6. Regulatory Constraints

- **HIPAA Privacy Rule**: All PHI must be access-controlled with minimum necessary standard.
- **HIPAA Security Rule**: Encryption at rest (AES-256) and in transit (TLS 1.3), audit trails, access controls.
- **HIPAA Breach Notification**: System must support incident detection and reporting.
- **21 CFR Part 11**: Electronic signatures and audit trails for clinical records.

## 7. Quality Attributes

| Attribute | Target | Verification Method |
|---|---|---|
| Availability | 99.9% uptime | System test (monitoring) |
| Response Time | < 2 seconds for all API calls | Performance test |
| Concurrent Users | 500+ simultaneous | Load test |
| Data Integrity | Zero data loss | Integration test |
| Security | Zero critical vulnerabilities | Snyk + SonarQube scans |
| Auditability | 100% data access logged | Audit log inspection |

## 8. Requirement ID Convention

All requirements follow IEEE 830 / DOD-STD-498 conventions:

| Level | Format | Example |
|---|---|---|
| System | `SYS-REQ-XXXX` | SYS-REQ-0001 |
| Subsystem | `SUB-{code}-XXXX` | SUB-PR-0001 |
| Test Case | `TST-{code}-XXXX` | TST-PR-0001 |
| Test Run | `RUN-{YYYY-MM-DD}-{NNN}` | RUN-2026-02-15-001 |

## 9. Traceability Policy

Every requirement must trace forward to:
1. **Design** — Architecture decision or technical plan
2. **Implementation** — Source module(s) in the corresponding repository
3. **Test Case** — One or more test cases verifying the requirement
4. **Test Result** — Recorded pass/fail for every test run

Every test run must produce a **run record** linking to:
- Test case IDs executed
- Pass/fail status per case
- Timestamp and environment
- Commit SHA of the code under test

See [Traceability Matrix](requirements/traceability-matrix.md) for the live mapping.
