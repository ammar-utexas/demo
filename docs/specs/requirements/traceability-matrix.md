# Requirements Traceability Matrix (RTM)

**Document ID:** PMS-RTM-001
**Version:** 1.1
**Date:** 2026-02-16
**Last Updated:** 2026-02-16

---

## Forward Traceability: System Requirements → Subsystem → Implementation → Tests

| System Req | Subsystem Reqs | Backend Module(s) | Test Case(s) | Verification Status |
|---|---|---|---|---|
| SYS-REQ-0001 (MFA) | SUB-PR-0001, SUB-CW-0001, SUB-MM-0006, SUB-RA-0004 | `middleware/auth.py`, `services/auth_service.py` | TST-PR-0001, TST-CW-0001, TST-MM-0006, TST-RA-0004, TST-AUTH-0001 | Partial (stub token only) |
| SYS-REQ-0002 (Encryption) | SUB-PR-0004, SUB-MM-0003 | `services/encryption_service.py` | TST-PR-0004, TST-MM-0003, TST-SYS-0002 | Placeholder |
| SYS-REQ-0003 (Audit) | SUB-PR-0005, SUB-CW-0004, SUB-MM-0004, SUB-RA-0003 | `services/audit_service.py`, `middleware/audit.py` | TST-PR-0005, TST-CW-0004, TST-MM-0004, TST-RA-0003, TST-SYS-0003 | Placeholder |
| SYS-REQ-0004 (FHIR) | SUB-MM-0005 | — | TST-MM-0005, TST-SYS-0004 | Not Started |
| SYS-REQ-0005 (RBAC) | SUB-PR-0002, SUB-CW-0002, SUB-MM-0007, SUB-RA-0005 | `middleware/auth.py:require_role` | TST-PR-0002, TST-CW-0002, TST-MM-0007, TST-RA-0005, TST-SYS-0005 | Placeholder |
| SYS-REQ-0006 (Alerts) | SUB-MM-0001, SUB-MM-0002, SUB-CW-0005 | `services/interaction_checker.py` | TST-MM-0001, TST-MM-0002, TST-CW-0005, TST-SYS-0006 | Partial (stub endpoint only) |
| SYS-REQ-0007 (Performance) | — | — | TST-SYS-0007 | Not Started |
| SYS-REQ-0008 (Web UI) | — | — | TST-SYS-0008 | Scaffolded |
| SYS-REQ-0009 (Android) | — | — | TST-SYS-0009 | Scaffolded |
| SYS-REQ-0010 (Docker) | — | `Dockerfile` (all repos) | TST-SYS-0010 | Scaffolded |

---

## Backward Traceability: Tests → Requirements

### Subsystem Tests (Unit / Integration)

| Test Case | Description | Repository | Test Function | Traces To | Last Result | Run ID |
|---|---|---|---|---|---|---|
| TST-AUTH-0001 | Login endpoint returns JWT access_token with bearer type | pms-backend | `test_login_returns_token` | SYS-REQ-0001 | PASS | RUN-2026-02-16-001 |
| TST-PR-0001 | Verify patient endpoints require auth token | pms-backend | — (not implemented) | SUB-PR-0001, SYS-REQ-0001 | — | — |
| TST-PR-0002 | Verify RBAC enforcement on patient endpoints | pms-backend | — (not implemented) | SUB-PR-0002, SYS-REQ-0005 | — | — |
| TST-PR-0003 | Patient list endpoint returns 200 with empty array (stub) | pms-backend | `test_list_patients_empty` | SUB-PR-0003 | PASS | RUN-2026-02-16-001 |
| TST-PR-0004 | SSN encryption at rest via encryption_service | pms-backend | — (not implemented) | SUB-PR-0004, SYS-REQ-0002 | — | — |
| TST-PR-0005 | Audit log entries created on patient access | pms-backend | — (not implemented) | SUB-PR-0005, SYS-REQ-0003 | — | — |
| TST-PR-0006 | Patient email uniqueness validation | pms-backend | — (not implemented) | SUB-PR-0006 | — | — |
| TST-PR-0007 | Patient search by last name, DOB, or ID | pms-backend | — (not implemented) | SUB-PR-0007 | — | — |
| TST-PR-0008 | Paginated patient list results | pms-backend | — (not implemented) | SUB-PR-0008 | — | — |
| TST-PR-0009 | Wound assessment endpoint returns valid response | pms-backend | — (not implemented) | SUB-PR-0009 | — | — |
| TST-PR-0010 | Patient ID verification endpoint returns match result | pms-backend | — (not implemented) | SUB-PR-0010 | — | — |
| TST-PR-0011 | Document OCR endpoint returns extracted text and fields | pms-backend | — (not implemented) | SUB-PR-0011 | — | — |
| TST-CW-0001 | Verify encounter endpoints require auth token | pms-backend | — (not implemented) | SUB-CW-0001, SYS-REQ-0001 | — | — |
| TST-CW-0002 | Verify RBAC enforcement on encounter endpoints | pms-backend | — (not implemented) | SUB-CW-0002, SYS-REQ-0005 | — | — |
| TST-CW-0003 | Encounter list endpoint returns 200 with empty array (stub) | pms-backend | `test_list_encounters_empty` | SUB-CW-0003 | PASS | RUN-2026-02-16-001 |
| TST-CW-0004 | Audit log entries created on encounter access | pms-backend | — (not implemented) | SUB-CW-0004, SYS-REQ-0003 | — | — |
| TST-CW-0005 | Clinical alerts triggered on critical encounter notes | pms-backend | — (not implemented) | SUB-CW-0005, SYS-REQ-0006 | — | — |
| TST-CW-0006 | Encounter types validated (office_visit, telehealth, emergency, follow_up) | pms-backend | — (not implemented) | SUB-CW-0006 | — | — |
| TST-CW-0007 | Encounter status transition validation | pms-backend | — (not implemented) | SUB-CW-0007 | — | — |
| TST-CW-0008 | Encounter associated with patient via FK | pms-backend | — (not implemented) | SUB-CW-0008 | — | — |
| TST-MM-0001 | Interaction check endpoint returns 200 with empty array for unknown patient | pms-backend | `test_check_interactions_empty` | SUB-MM-0001, SYS-REQ-0006 | PASS | RUN-2026-02-16-001 |
| TST-MM-0002 | Interaction severity classification (contraindicated, major, moderate, minor) | pms-backend | — (not implemented) | SUB-MM-0002, SYS-REQ-0006 | — | — |
| TST-MM-0003 | Prescription data PHI encryption | pms-backend | — (not implemented) | SUB-MM-0003, SYS-REQ-0002 | — | — |
| TST-MM-0004 | Prescription event audit logging | pms-backend | — (not implemented) | SUB-MM-0004, SYS-REQ-0003 | — | — |
| TST-MM-0005 | FHIR R4 MedicationRequest support | pms-backend | — (not implemented) | SUB-MM-0005, SYS-REQ-0004 | — | — |
| TST-MM-0006 | Medication endpoints require auth token | pms-backend | — (not implemented) | SUB-MM-0006, SYS-REQ-0001 | — | — |
| TST-MM-0007 | RBAC enforcement on medication endpoints | pms-backend | — (not implemented) | SUB-MM-0007, SYS-REQ-0005 | — | — |
| TST-MM-0008 | Medication list endpoint returns 200 with empty array (stub) | pms-backend | `test_list_medications_empty` | SUB-MM-0008 | PASS | RUN-2026-02-16-001 |
| TST-MM-0009 | Refill tracking prevents zero-refill fills | pms-backend | — (not implemented) | SUB-MM-0009 | — | — |
| TST-RA-0001 | Patient volume report endpoint | pms-backend | — (not implemented) | SUB-RA-0001 | — | — |
| TST-RA-0002 | Encounter summary report endpoint | pms-backend | — (not implemented) | SUB-RA-0002 | — | — |
| TST-RA-0003 | Audit log query interface | pms-backend | — (not implemented) | SUB-RA-0003, SYS-REQ-0003 | — | — |
| TST-RA-0004 | Report endpoints require auth | pms-backend | — (not implemented) | SUB-RA-0004, SYS-REQ-0001 | — | — |
| TST-RA-0005 | RBAC enforcement on report endpoints | pms-backend | — (not implemented) | SUB-RA-0005, SYS-REQ-0005 | — | — |
| TST-RA-0006 | Medication usage report endpoint | pms-backend | — (not implemented) | SUB-RA-0006 | — | — |
| TST-RA-0007 | Report CSV export | pms-backend | — (not implemented) | SUB-RA-0007 | — | — |
| TST-FE-0001 | Auth utilities: isAuthenticated, parseToken | pms-frontend | — | SYS-REQ-0001 | PASS | RUN-2026-02-15-002 |
| TST-FE-0002 | Utility functions: cn, formatDate | pms-frontend | — | — (infrastructure) | PASS | RUN-2026-02-15-002 |
| TST-FE-0003 | InteractionWarning type matches schema | pms-frontend | — | SUB-MM-0002 | PASS | RUN-2026-02-15-002 |
| TST-AND-0001 | PatientEntity roundtrip mapping | pms-android | — | SUB-PR-0003 | — | — |
| TST-AND-0002 | Model serialization (TokenRequest, InteractionWarning) | pms-android | — | SYS-REQ-0001, SUB-MM-0002 | — | — |

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

---

## Test Run Log

| Run ID | Date | Repository | Commit SHA | Tests Run | Passed | Failed | Skipped |
|---|---|---|---|---|---|---|---|
| RUN-2026-02-15-001 | 2026-02-15 | pms-backend | `c17c71b` | 5 | 5 | 0 | 0 |
| RUN-2026-02-15-002 | 2026-02-15 | pms-frontend | `d666016` | 9 | 9 | 0 | 0 |
| RUN-2026-02-16-001 | 2026-02-16 | pms-backend | `17ed00b` | 5 | 5 | 0 | 0 |

---

## Coverage Summary

| Subsystem | Total Reqs | With Tests | Passing | Failing | No Tests | Coverage |
|---|---|---|---|---|---|---|
| Patient Records (PR) | 11 | 1 | 1 | 0 | 10 | 9.1% |
| Clinical Workflow (CW) | 8 | 1 | 1 | 0 | 7 | 12.5% |
| Medication Mgmt (MM) | 9 | 2 | 2 | 0 | 7 | 22.2% |
| Reporting (RA) | 7 | 0 | 0 | 0 | 7 | 0.0% |
| System (SYS) | 10 | 1 | 1 | 0 | 9 | 10.0% |
| **TOTAL** | **45** | **5** | **5** | **0** | **40** | **11.1%** |

> **Note on v1.1 corrections:** The v1.0 matrix (2026-02-15) overstated coverage. TST-MM-0002 was incorrectly marked as PASS — no test for severity classification exists. TST-PR-0003, TST-CW-0003, and TST-MM-0001 test descriptions have been corrected to reflect that they only verify stub endpoint responses (200 + empty array), not full CRUD or interaction logic. The "Test Function" column was added to link each test case to its actual pytest function.

> **Gap Analysis:** 40 requirements lack test coverage. Priority:
> 1. **Auth/RBAC tests** — SUB-*-0001 and SUB-*-0002 (affects 4 subsystems)
> 2. **CRUD integration tests** — SUB-PR-0003 full CRUD, SUB-CW-0003 lifecycle, SUB-MM-0008 prescriptions
> 3. **Encryption/Audit tests** — SUB-PR-0004, SUB-PR-0005, SUB-MM-0003, SUB-MM-0004
> 4. **Reporting tests** — SUB-RA-0001 through SUB-RA-0007 (0% coverage)

---

## How to Update This Matrix

1. After implementing a requirement, add the source module to the "Implementation Mapping" section of the subsystem requirements doc.
2. After writing a test, add the test case row to the "Backward Traceability" section above. Include the `Test Function` name.
3. After each test run, add a row to the "Test Run Log" and update "Last Result" and "Run ID" columns.
4. Re-generate the "Coverage Summary" by counting requirements with/without passing tests.
5. Commit all changes: `git add docs/specs/ && git commit -m "evidence: update RTM" && git push`.
