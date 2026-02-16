# Subsystem Requirements: Reporting & Analytics (SUB-RA)

**Document ID:** PMS-SUB-RA-001
**Version:** 1.1
**Date:** 2026-02-16
**Parent:** [System Requirements](SYS-REQ.md)

---

## Scope

The Reporting & Analytics subsystem provides dashboards, compliance reports, and audit log queries for administrators and compliance officers. It operates in read-only mode against the data created by other subsystems.

## Requirements

| Req ID | Parent | Description | Verification | Status |
|---|---|---|---|---|
| SUB-RA-0001 | — | Provide a patient volume report showing registration and visit trends over configurable date ranges | Test | Placeholder |
| SUB-RA-0002 | — | Provide an encounter summary report with breakdowns by type, status, and completion rate | Test | Placeholder |
| SUB-RA-0003 | SYS-REQ-0003 | Provide an audit log query interface with filters for user, action, resource, and date range | Test | Not Started |
| SUB-RA-0004 | SYS-REQ-0001 | Require authenticated session for all report access | Test | Placeholder |
| SUB-RA-0005 | SYS-REQ-0005 | Enforce RBAC: only administrator and billing roles can access reports | Test | Placeholder |
| SUB-RA-0006 | — | Provide a medication usage report showing most prescribed medications and interaction alert frequency | Test | Placeholder |
| SUB-RA-0007 | — | Support export of reports to CSV format | Test | Not Started |

## Implementation Mapping

| Req ID | Backend Module | Frontend Component | Android Screen | Test Case(s) |
|---|---|---|---|---|
| SUB-RA-0001 | `routers/reports.py` | `app/reports/page.tsx` | `ui/reports/ReportsScreen.kt` | TST-RA-0001 |
| SUB-RA-0002 | `routers/reports.py` | `app/reports/page.tsx` | `ui/reports/ReportsScreen.kt` | TST-RA-0002 |
| SUB-RA-0003 | — | — | — | TST-RA-0003 |
| SUB-RA-0004 | `middleware/auth.py` | `lib/auth.ts` | `data/api/AuthInterceptor.kt` | TST-RA-0004 |
| SUB-RA-0005 | `middleware/auth.py:require_role` | — | — | TST-RA-0005 |
| SUB-RA-0006 | `routers/reports.py` | `app/reports/page.tsx` | `ui/reports/ReportsScreen.kt` | TST-RA-0006 |
| SUB-RA-0007 | — | — | — | TST-RA-0007 |
