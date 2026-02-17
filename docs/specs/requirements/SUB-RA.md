# Subsystem Requirements: Reporting & Analytics (SUB-RA)

**Document ID:** PMS-SUB-RA-001
**Version:** 1.3
**Date:** 2026-02-17
**Parent:** [System Requirements](SYS-REQ.md)

---

## Scope

The Reporting & Analytics subsystem provides dashboards, compliance reports, and audit log queries for administrators and compliance officers. It operates in read-only mode against the data created by other subsystems.

## Requirements

| Req ID | Parent | Description | Verification | Status |
|---|---|---|---|---|
| SUB-RA-0001 | — | Provide a patient volume report showing registration and visit trends over configurable date ranges | Test | Placeholder |
| SUB-RA-0002 | — | Provide an encounter summary report with breakdowns by type, status, and completion rate | Test | Placeholder |
| SUB-RA-0003 | SYS-REQ-0003 | Provide an audit log query interface with filters for user, action, resource, and date range. For v1.0, audit log access is granted to the administrator role (compliance duties assigned to administrators). A dedicated compliance role with audit-read-only access is deferred to a future RBAC enhancement (DC-RA-01). | Test | Not Started |
| SUB-RA-0004 | SYS-REQ-0001 | Require authenticated session for all report access | Test | Placeholder |
| SUB-RA-0005 | SYS-REQ-0005 | Enforce RBAC: only administrator and billing roles can access reports. Administrator role additionally has audit log query access for compliance duties (DC-RA-01). | Test | Placeholder |
| SUB-RA-0006 | — | Provide a medication usage report showing most prescribed medications and interaction alert frequency | Test | Placeholder |
| SUB-RA-0007 | — | Support export of reports to CSV format | Test | Not Started |

## Platform Decomposition

### Backend (BE) — 7 requirements

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-RA-0001-BE | SUB-RA-0001 | Patient volume report API endpoint | `routers/reports.py` | TST-RA-0001-BE | Placeholder |
| SUB-RA-0002-BE | SUB-RA-0002 | Encounter summary report API endpoint | `routers/reports.py` | TST-RA-0002-BE | Placeholder |
| SUB-RA-0003-BE | SUB-RA-0003 | Audit log query API with filters (user, action, resource, date) | — | TST-RA-0003-BE | Not Started |
| SUB-RA-0004-BE | SUB-RA-0004 | Enforce JWT auth on all report API endpoints | `middleware/auth.py` | TST-RA-0004-BE | Placeholder |
| SUB-RA-0005-BE | SUB-RA-0005 | Enforce RBAC on report endpoints (administrator/billing only) | `middleware/auth.py:require_role` | TST-RA-0005-BE | Placeholder |
| SUB-RA-0006-BE | SUB-RA-0006 | Medication usage report API endpoint | `routers/reports.py` | TST-RA-0006-BE | Placeholder |
| SUB-RA-0007-BE | SUB-RA-0007 | CSV export API for all report types | — | TST-RA-0007-BE | Not Started |

### Web Frontend (WEB) — 5 requirements

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-RA-0001-WEB | SUB-RA-0001 | Patient volume dashboard with date range controls. Must display a "last refreshed" timestamp and use a cache TTL. Dashboard data may lag real-time patient list data by up to the cache TTL (eventual consistency accepted) (PC-WEB-02). | `app/reports/page.tsx` | TST-RA-0001-WEB | Not Started |
| SUB-RA-0002-WEB | SUB-RA-0002 | Encounter summary dashboard with charts | `app/reports/page.tsx` | TST-RA-0002-WEB | Not Started |
| SUB-RA-0003-WEB | SUB-RA-0003 | Audit log query interface with filter controls | — | TST-RA-0003-WEB | Not Started |
| SUB-RA-0004-WEB | SUB-RA-0004 | Auth guard for report pages | `lib/auth.ts` | TST-RA-0004-WEB | Scaffolded |
| SUB-RA-0006-WEB | SUB-RA-0006 | Medication usage dashboard with charts | `app/reports/page.tsx` | TST-RA-0006-WEB | Not Started |

### Android (AND) — 5 requirements

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-RA-0001-AND | SUB-RA-0001 | Patient volume report screen | `ui/reports/ReportsScreen.kt` | TST-RA-0001-AND | Not Started |
| SUB-RA-0002-AND | SUB-RA-0002 | Encounter summary report screen | `ui/reports/ReportsScreen.kt` | TST-RA-0002-AND | Not Started |
| SUB-RA-0003-AND | SUB-RA-0003 | Audit log query screen with filters | — | TST-RA-0003-AND | Not Started |
| SUB-RA-0004-AND | SUB-RA-0004 | Auth interceptor for report API calls | `data/api/AuthInterceptor.kt` | TST-RA-0004-AND | Scaffolded |
| SUB-RA-0006-AND | SUB-RA-0006 | Medication usage report screen | `ui/reports/ReportsScreen.kt` | TST-RA-0006-AND | Not Started |
