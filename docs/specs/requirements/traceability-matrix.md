# Requirements Traceability Matrix (RTM)

**Document ID:** PMS-RTM-001
**Version:** 1.0
**Date:** 2026-02-15
**Last Updated:** 2026-02-15

---

## Forward Traceability: System Requirements → Subsystem → Implementation → Tests

| System Req | Subsystem Reqs | Backend Module(s) | Test Case(s) | Verification Status |
|---|---|---|---|---|
| SYS-REQ-0001 (MFA) | SUB-PR-0001, SUB-CW-0001, SUB-MM-0006, SUB-RA-0004 | `middleware/auth.py`, `services/auth_service.py` | TST-PR-0001, TST-CW-0001, TST-MM-0006, TST-RA-0004, TST-SYS-0001 | Placeholder |
| SYS-REQ-0002 (Encryption) | SUB-PR-0004, SUB-MM-0003 | `services/encryption_service.py` | TST-PR-0004, TST-MM-0003, TST-SYS-0002 | Placeholder |
| SYS-REQ-0003 (Audit) | SUB-PR-0005, SUB-CW-0004, SUB-MM-0004, SUB-RA-0003 | `services/audit_service.py`, `middleware/audit.py` | TST-PR-0005, TST-CW-0004, TST-MM-0004, TST-RA-0003, TST-SYS-0003 | Placeholder |
| SYS-REQ-0004 (FHIR) | SUB-MM-0005 | — | TST-MM-0005, TST-SYS-0004 | Not Started |
| SYS-REQ-0005 (RBAC) | SUB-PR-0002, SUB-CW-0002, SUB-MM-0007, SUB-RA-0005 | `middleware/auth.py:require_role` | TST-PR-0002, TST-CW-0002, TST-MM-0007, TST-RA-0005, TST-SYS-0005 | Placeholder |
| SYS-REQ-0006 (Alerts) | SUB-MM-0001, SUB-MM-0002, SUB-CW-0005 | `services/interaction_checker.py` | TST-MM-0001, TST-MM-0002, TST-CW-0005, TST-SYS-0006 | Placeholder |
| SYS-REQ-0007 (Performance) | — | — | TST-SYS-0007 | Not Started |
| SYS-REQ-0008 (Web UI) | — | — | TST-SYS-0008 | Scaffolded |
| SYS-REQ-0009 (Android) | — | — | TST-SYS-0009 | Scaffolded |
| SYS-REQ-0010 (Docker) | — | `Dockerfile` (all repos) | TST-SYS-0010 | Scaffolded |

---

## Backward Traceability: Tests → Requirements

### Subsystem Tests (Unit / Integration)

| Test Case | Description | Repository | Traces To | Last Result | Run ID |
|---|---|---|---|---|---|
| TST-PR-0001 | Verify patient endpoints require auth token | pms-backend | SUB-PR-0001, SYS-REQ-0001 | — | — |
| TST-PR-0002 | Verify RBAC enforcement on patient endpoints | pms-backend | SUB-PR-0002, SYS-REQ-0005 | — | — |
| TST-PR-0003 | CRUD operations for patient records | pms-backend | SUB-PR-0003 | PASS | RUN-2026-02-15-001 |
| TST-PR-0004 | SSN encryption at rest via encryption_service | pms-backend | SUB-PR-0004, SYS-REQ-0002 | — | — |
| TST-PR-0005 | Audit log entries created on patient access | pms-backend | SUB-PR-0005, SYS-REQ-0003 | — | — |
| TST-PR-0006 | Patient email uniqueness validation | pms-backend | SUB-PR-0006 | — | — |
| TST-CW-0001 | Verify encounter endpoints require auth token | pms-backend | SUB-CW-0001, SYS-REQ-0001 | — | — |
| TST-CW-0003 | Encounter CRUD and status lifecycle | pms-backend | SUB-CW-0003 | PASS | RUN-2026-02-15-001 |
| TST-MM-0001 | Drug interaction check within 5 seconds | pms-backend | SUB-MM-0001, SYS-REQ-0006 | PASS | RUN-2026-02-15-001 |
| TST-MM-0002 | Interaction severity classification | pms-backend | SUB-MM-0002, SYS-REQ-0006 | PASS | RUN-2026-02-15-001 |
| TST-AUTH-0001 | Login endpoint returns valid JWT token | pms-backend | SYS-REQ-0001 | PASS | RUN-2026-02-15-001 |
| TST-FE-0001 | Auth utilities: isAuthenticated, parseToken | pms-frontend | SYS-REQ-0001 | PASS | RUN-2026-02-15-002 |
| TST-FE-0002 | Utility functions: cn, formatDate | pms-frontend | — (infrastructure) | PASS | RUN-2026-02-15-002 |
| TST-FE-0003 | InteractionWarning type matches schema | pms-frontend | SUB-MM-0002 | PASS | RUN-2026-02-15-002 |
| TST-AND-0001 | PatientEntity roundtrip mapping | pms-android | SUB-PR-0003 | — | — |
| TST-AND-0002 | Model serialization (TokenRequest, InteractionWarning) | pms-android | SYS-REQ-0001, SUB-MM-0002 | — | — |

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

---

## Coverage Summary

| Subsystem | Total Reqs | With Tests | Passing | Failing | No Tests | Coverage |
|---|---|---|---|---|---|---|
| Patient Records (PR) | 8 | 3 | 1 | 0 | 5 | 37.5% |
| Clinical Workflow (CW) | 8 | 2 | 1 | 0 | 6 | 25.0% |
| Medication Mgmt (MM) | 9 | 3 | 2 | 0 | 6 | 33.3% |
| Reporting (RA) | 7 | 0 | 0 | 0 | 7 | 0.0% |
| System (SYS) | 10 | 2 | 2 | 0 | 8 | 20.0% |
| **TOTAL** | **42** | **10** | **6** | **0** | **32** | **23.8%** |

> **Gap Analysis:** 32 requirements lack test coverage. Priority for next sprint: implement CRUD tests (SUB-PR-0003 through 0008), then RBAC tests (SUB-*-0002), then audit trail tests (SUB-*-0004/0005).

---

## How to Update This Matrix

1. After implementing a requirement, add the source module to the "Implementation Mapping" section of the subsystem requirements doc.
2. After writing a test, add the test case row to the "Backward Traceability" section above.
3. After each test run, add a row to the "Test Run Log" and update "Last Result" and "Run ID" columns.
4. Re-generate the "Coverage Summary" by counting requirements with/without passing tests.
5. Commit all changes: `git add docs/specs/ && git commit -m "evidence: update RTM" && git push`.
