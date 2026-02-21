# Platform Requirements: Clinical Workflow — Backend (SUB-CW-BE)

**Parent:** [SUB-CW (Domain)](../domain/SUB-CW.md)
**Platform:** Backend (BE) — 8 requirements

---

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-CW-0001-BE | SUB-CW-0001 | Enforce JWT auth on all encounter API endpoints | `middleware/auth.py` | TST-CW-0001-BE | Placeholder |
| SUB-CW-0002-BE | SUB-CW-0002 | Enforce RBAC on encounter API endpoints | `middleware/auth.py:require_role` | TST-CW-0002-BE | Placeholder |
| SUB-CW-0003-BE | SUB-CW-0003 | REST endpoints for encounter lifecycle. Must serialize concurrent status transitions using `SELECT ... FOR UPDATE` or optimistic locking (version column) to prevent duplicate transitions (RC-BE-02). | `routers/encounters.py`, `models/encounter.py` | TST-CW-0003-BE | Placeholder |
| SUB-CW-0004-BE | SUB-CW-0004 | Audit log all encounter access and status changes. Must follow the audit event catalog (action strings: CREATE, READ, UPDATE, DELETE; resource_type: encounter) matching the pattern established by patient audit logging (PC-BE-03). | `services/audit_service.py` | TST-CW-0004-BE | Placeholder |
| SUB-CW-0005-BE | SUB-CW-0005 | Trigger clinical alerts for critical encounter conditions | — | TST-CW-0005-BE | Not Started |
| SUB-CW-0006-BE | SUB-CW-0006 | Validate encounter types (office_visit, telehealth, emergency, follow_up) | `models/encounter.py` | TST-CW-0006-BE | Placeholder |
| SUB-CW-0007-BE | SUB-CW-0007 | Validate encounter status transitions against the explicit state machine (see SUB-CW-0007). Enforce via `SELECT ... FOR UPDATE` to serialize concurrent transitions (RC-BE-02). | — | TST-CW-0007-BE | Not Started |
| SUB-CW-0008-BE | SUB-CW-0008 | Enforce patient_id FK constraint on encounters | `models/encounter.py` (FK) | TST-CW-0008-BE | Placeholder |
