# Platform Requirements: Reporting & Analytics — Web Frontend (SUB-RA-WEB)

**Parent:** [SUB-RA (Domain)](../domain/SUB-RA.md)
**Platform:** Web Frontend (WEB) — 6 requirements

---

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-RA-0001-WEB | SUB-RA-0001 | Patient volume dashboard with date range controls. Must display a "last refreshed" timestamp and use a cache TTL. Dashboard data may lag real-time patient list data by up to the cache TTL (eventual consistency accepted) (PC-WEB-02). | `app/reports/page.tsx` | TST-RA-0001-WEB | Not Started |
| SUB-RA-0002-WEB | SUB-RA-0002 | Encounter summary dashboard with charts | `app/reports/page.tsx` | TST-RA-0002-WEB | Not Started |
| SUB-RA-0003-WEB | SUB-RA-0003 | Audit log query interface with filter controls | — | TST-RA-0003-WEB | Not Started |
| SUB-RA-0004-WEB | SUB-RA-0004 | Auth guard for report pages | `lib/auth.ts` | TST-RA-0004-WEB | Scaffolded |
| SUB-RA-0006-WEB | SUB-RA-0006 | Medication usage dashboard with charts | `app/reports/page.tsx` | TST-RA-0006-WEB | Not Started |
| SUB-RA-0008-WEB | SUB-RA-0008 | Dermatology analytics dashboard with classification volume charts, risk distribution pie chart, referral trend line chart, and model confidence histogram | `app/reports/dermatology/page.tsx` | TST-RA-0008-WEB | Not Started |
