# Platform Requirements: Reporting & Analytics — Backend (SUB-RA-BE)

**Parent:** [SUB-RA (Domain)](../domain/SUB-RA.md)
**Platform:** Backend (BE) — 8 requirements

---

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-RA-0001-BE | SUB-RA-0001 | Patient volume report API endpoint | `routers/reports.py` | TST-RA-0001-BE | Placeholder |
| SUB-RA-0002-BE | SUB-RA-0002 | Encounter summary report API endpoint | `routers/reports.py` | TST-RA-0002-BE | Placeholder |
| SUB-RA-0003-BE | SUB-RA-0003 | Audit log query API with filters (user, action, resource, date) | — | TST-RA-0003-BE | Not Started |
| SUB-RA-0004-BE | SUB-RA-0004 | Enforce JWT auth on all report API endpoints | `middleware/auth.py` | TST-RA-0004-BE | Placeholder |
| SUB-RA-0005-BE | SUB-RA-0005 | Enforce RBAC on report endpoints (administrator/billing only) | `middleware/auth.py:require_role` | TST-RA-0005-BE | Placeholder |
| SUB-RA-0006-BE | SUB-RA-0006 | Medication usage report API endpoint | `routers/reports.py` | TST-RA-0006-BE | Placeholder |
| SUB-RA-0007-BE | SUB-RA-0007 | CSV export API for all report types | — | TST-RA-0007-BE | Not Started |
| SUB-RA-0008-BE | SUB-RA-0008 | Dermatology analytics report API endpoint aggregating lesion classification counts, risk distributions, referral trends, and model confidence from the CDS service | `routers/reports.py`, `services/lesion_service.py` | TST-RA-0008-BE | Not Started |
