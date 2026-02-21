# Platform Requirements: Medication Management — Backend (SUB-MM-BE)

**Parent:** [SUB-MM (Domain)](../domain/SUB-MM.md)
**Platform:** Backend (BE) — 9 requirements

---

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-MM-0001-BE | SUB-MM-0001 | Drug interaction check API endpoint (< 5 sec response). The interaction check must complete synchronously before the prescription is committed — implement as a pre-save hook: validate → check interactions → save (RC-BE-03). Must use `REPEATABLE READ` isolation for a consistent medication snapshot during concurrent changes (RC-BE-07). Use a dedicated connection pool or priority queue for medication-safety queries to avoid contention with CRUD load (PC-BE-05). | `services/interaction_checker.py` | TST-MM-0001-BE | Placeholder |
| SUB-MM-0002-BE | SUB-MM-0002 | Interaction severity classification logic | `services/interaction_checker.py` | TST-MM-0002-BE | Placeholder |
| SUB-MM-0003-BE | SUB-MM-0003 | Encrypt prescription PHI at rest using AES-256 | `services/encryption_service.py` | TST-MM-0003-BE | Placeholder |
| SUB-MM-0004-BE | SUB-MM-0004 | Audit log all prescription events. Must follow the audit event catalog (action strings: CREATE, READ, UPDATE, DELETE; resource_type: prescription) matching the pattern established by patient audit logging (PC-BE-03). | `services/audit_service.py` | TST-MM-0004-BE | Placeholder |
| SUB-MM-0005-BE | SUB-MM-0005 | FHIR R4 MedicationRequest/MedicationDispense endpoints | — | TST-MM-0005-BE | Not Started |
| SUB-MM-0006-BE | SUB-MM-0006 | Enforce JWT auth on all medication API endpoints | `middleware/auth.py` | TST-MM-0006-BE | Placeholder |
| SUB-MM-0007-BE | SUB-MM-0007 | Enforce RBAC on medication endpoints (physician prescribe, nurse view, pharmacist dispense) | `middleware/auth.py:require_role` | TST-MM-0007-BE | Placeholder |
| SUB-MM-0008-BE | SUB-MM-0008 | Prescription status lifecycle API (active → completed/cancelled). New prescriptions must not be committed until the interaction check (SUB-MM-0001-BE) completes. Contraindicated interactions reject the save; major/moderate interactions save with "pending_review" status requiring prescriber acknowledgment (RC-BE-03). | `models/medication.py` | TST-MM-0008-BE | Placeholder |
| SUB-MM-0009-BE | SUB-MM-0009 | Refill tracking and zero-refill prevention logic. Must use atomic update (`UPDATE ... SET refills_remaining = refills_remaining - 1 WHERE id = ? AND refills_remaining > 0`); check affected row count — if 0, the refill was already claimed. Do not use read-then-write in application code (RC-BE-08). | — | TST-MM-0009-BE | Not Started |
