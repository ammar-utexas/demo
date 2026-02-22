# Subsystem Requirements: Reporting & Analytics (SUB-RA)

**Document ID:** PMS-SUB-RA-001
**Version:** 1.5
**Date:** 2026-02-21
**Parent:** [System Requirements](../SYS-REQ.md)

---

## Scope

The Reporting & Analytics subsystem provides dashboards, compliance reports, and audit log queries for administrators and compliance officers. It operates in read-only mode against the data created by other subsystems.

SUB-RA-0008 adds **dermatology classification analytics** — aggregating lesion classification volumes, risk score distributions, referral urgency trends, and model confidence metrics from the Dermatology CDS service (SYS-REQ-0012). Architecture defined via ADR-0008 (CDS microservice) and ADR-0020 (feature flags).

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
| SUB-RA-0008 | SYS-REQ-0012 | Provide a dermatology classification analytics report showing lesion classification volumes, risk score distributions, referral urgency trends, and model confidence metrics over configurable date ranges | Test | Not Started |

## Platform Decomposition

| Platform | File | Req Count |
|----------|------|-----------|
| Backend (BE) | [SUB-BE](../platform/SUB-BE.md#reporting--analytics-sub-ra) | 8 |
| Web Frontend (WEB) | [SUB-WEB](../platform/SUB-WEB.md#reporting--analytics-sub-ra) | 6 |
| Android (AND) | [SUB-AND](../platform/SUB-AND.md#reporting--analytics-sub-ra) | 5 |
