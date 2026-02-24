# Specification Analysis Report: SUB-AU-BE (Authentication & User Management)

**Feature**: 002-authentication | **Date**: 2026-02-24
**Artifacts analyzed**: spec.md, plan.md, tasks.md, data-model.md, research.md, contracts/auth-api.yaml, constitution.md, traceability-matrix.md

---

## Findings

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| C1 | Constitution | CRITICAL | tasks.md Phase 2 (T003) vs Phase 3 (T008) | **Test-First violation**: T003 implements `validate_password()` in Phase 2 (Foundational) but its tests (T008) are in Phase 3 (US1). Constitution Principle I: "Tests MUST be written before implementation code." | Move T008 before T003 or restructure: create T003a (test) + T003b (impl) within Phase 2 |
| C2 | Constitution | CRITICAL | tasks.md Phase 2 (T004) vs Phase 5 (T019) | **Test-First violation**: T004 creates `email_service.py` in Phase 2 but its tests (T019) are in Phase 5 (US3). Implementation precedes tests by 15+ tasks. | Move T019 before T004 or restructure: create T004a (test) + T004b (impl) within Phase 2 |
| C3 | Coverage | CRITICAL | traceability-matrix.md | **Traceability matrix missing all SUB-AU entries**: Forward traceability for SYS-REQ-0001/0005 does not reference any SUB-AU-* requirements. Backward traceability has zero TST-AU-* test case IDs. 14 platform requirements are untraceable. | Add SUB-AU section to Platform Traceability Summary. Add TST-AU-0001-BE through TST-AU-0014-BE entries to Backward Traceability. |
| H1 | Coverage | HIGH | tasks.md (all phases) | **No lint check task**: Constitution Quality Gates require "Zero ruff violations" via `ruff check src/ tests/`. No task in tasks.md runs the linter. | Add a lint task to Phase 7 (Polish): `ruff check src/ tests/` and fix violations |
| H2 | Inconsistency | HIGH | spec.md:237-238 vs contracts/auth-api.yaml:178,199 | **Endpoint path mismatch**: spec.md uses `/auth/password/reset-request` and `/auth/password/reset`; contract uses `/auth/password-reset` and `/auth/password-reset/confirm`. Existing code follows the contract paths. | Update spec.md Section 6.1 to match contract/implementation paths |
| H3 | Inconsistency | HIGH | spec.md:208 vs data-model.md:83 | **Nullability conflict**: spec.md defines `provider_email` as `NOT NULL`; data-model.md defines it as `Nullable`. These are contradictory constraints on the same column. | Align to data-model.md (`Nullable`) since OAuth providers may not always return email. Update spec.md. |
| H4 | Coverage | HIGH | tasks.md Phase 2 (T007) | **Missing test update for rbac.py change**: T007 replaces stale role names (physician, nurse, pharmacist, billing) with (clinician, sales, lab-staff) in `middleware/rbac.py`, but no task updates `tests/test_auth_middleware.py`. Test `test_require_auth_normalizes_legacy_role` and role-specific tests may break. | Add a task after T007: update test_auth_middleware.py to use new role names |
| M1 | Inconsistency | MEDIUM | spec.md:169 vs data-model.md:15-16 | **Spec drift (name field)**: spec.md defines single `name VARCHAR(255)` column; data-model.md and implementation use `first_name`/`last_name`. Resolved in research.md TD-1 but spec.md never updated. | Update spec.md Section 5.1 users table to show first_name/last_name |
| M2 | Inconsistency | MEDIUM | spec.md:171 vs data-model.md:30-33 | **Spec drift (status field)**: spec.md defines `status ENUM(invited, active, inactive)`; data-model.md and implementation use `is_active`/`is_verified` booleans with status mapping. Resolved in research.md TD-2 but spec.md never updated. | Update spec.md Section 5.1 users table to show boolean flags with status mapping |
| M3 | Inconsistency | MEDIUM | spec.md:170 vs data-model.md:17 | **Terminology drift**: spec.md uses `password_hash`; data-model.md and implementation use `hashed_password` for the same column. | Standardize to `hashed_password` (matches implementation). Update spec.md. |
| M4 | Ambiguity | MEDIUM | tasks.md Phase 6 (T023, T024) | **Vague verification tasks**: T023 ("Verify and standardize all 12 audit action strings") and T024 ("Verify require_role coverage") lack specific pass/fail criteria. What constitutes "verified"? No test assertions specified. | Add measurable criteria: T023 should produce a checklist of all 12 actions found in code; T024 should list each endpoint with its `require_role` decorator and expected roles |
| M5 | Coverage | MEDIUM | tasks.md Phase 2 (T005, T006, T007) | **Foundational code changes without dedicated tests**: T005 (schema change), T006 (default role fix), T007 (rbac cleanup) modify production code but rely on existing tests catching regressions. No explicit task to verify existing tests still pass after these changes. | Add a checkpoint task after Phase 2: run `pytest` to verify no regressions |
| L1 | Ambiguity | LOW | spec.md:340-344 | **Stale open questions**: spec.md Section 11 lists 4 open questions as unresolved (TOTP, session concurrency, password rotation, OAuth configurability). All 4 were resolved in research.md. | Update spec.md Section 11 to mark questions as resolved with links to research.md decisions |
| L2 | Coverage | LOW | tasks.md Phase 2 | **Over-conservative blocking**: Phase 2 declares "CRITICAL: No user story work can begin until this phase is complete" but T004 (email service) only blocks US3, not US1/US2/US4. T003 only blocks US1. This prevents available parallelism. | Refine Phase 2 blocking: only T001+T002 are universal blockers; other foundational tasks can be co-scheduled with non-dependent stories |

---

## Coverage Summary: Acceptance Criteria → Tasks

| AC | Description | Has Task? | Task IDs | Notes |
|----|-------------|-----------|----------|-------|
| AC 1 | OAuth login returns JWT | Yes | T012-T018 | US2: OAuth code exchange |
| AC 2 | Email/password login returns JWT | Existing | — | SUB-AU-0002-BE: Done. Tested by `test_login_success` |
| AC 3 | OAuth 403 for unregistered email | Yes | T017, T018 | US2: callback rejects unknown emails |
| AC 4 | OAuth 403 for inactive user | Yes | T017, T018 | US2: callback checks active status |
| AC 5 | Account lockout after 5 failures (30 min) | Yes | T002 | Config change 15 → 30 min. Tested by `test_login_locked_account` |
| AC 6 | Locked account cannot auth | Existing | — | Already works. Tested by `test_login_locked_account` |
| AC 7 | Seeded admin can log in | Existing | — | SUB-AU-0005-BE: Done. Migration 003 seeds admin |
| AC 8 | Admin creates user with email/name/roles | Existing | — | SUB-AU-0006-BE: Done. Tested by `test_create_user_with_invite` |
| AC 9 | New user receives invite email | Yes | T019-T022 | US3: email service integration |
| AC 10 | Invite expiry 72h + resend | Yes | T020-T022 | US3: resend-invite sends email |
| AC 11 | Admin deactivates user | Existing | — | Done. Tested by `test_activate_deactivate_user` |
| AC 12 | Admin reactivates user | Existing | — | Done. Tested by `test_activate_deactivate_user` |
| AC 13 | Non-admin 403 on user management | Existing | — | Done. Tested by `test_list_users_non_admin_forbidden` + 4 more |
| AC 14 | Multi-role assignment | Existing | — | Done. Tested by `test_assign_roles` |
| AC 15 | JWT roles claim contains all role codes | Existing | — | Done. JWT creation includes roles array |
| AC 16 | Union-based permission (any role grants) | Existing | — | Done. Tested by `test_require_role_with_multiple_roles` |
| AC 17 | Last-admin protection | Existing | — | Done. Tested by `test_last_admin_protection_*` (2 tests) |
| AC 18 | Role changes on next token issuance | Existing | — | Done. Stateless JWT with roles |

**Acceptance Criteria Coverage**: 18/18 (100%) — 6 have new tasks, 12 covered by existing implementation + tests

---

## Coverage Summary: SUB-AU-BE Requirements → Tasks

| Requirement | Has Task? | Task IDs | Test Task? | Notes |
|-------------|-----------|----------|------------|-------|
| SUB-AU-0001-BE (OAuth code exchange) | Yes | T012-T018 | T012, T018 | US2: largest work item |
| SUB-AU-0002-BE (Email/password login) | Done | — | Existing | 7 existing tests in test_auth.py |
| SUB-AU-0003-BE (JWT tokens) | Done | — | Existing | 4 existing token tests |
| SUB-AU-0004-BE (Account lockout) | Yes | T002 | Existing | Config change only; `test_login_locked_account` covers |
| SUB-AU-0005-BE (Admin seed) | Done | — | Existing | Migration 003 |
| SUB-AU-0006-BE (User CRUD) | Done | — | Existing | 20+ tests in test_users.py |
| SUB-AU-0007-BE (Invite flow) | Done | — | Existing | 3 invite tests in test_auth.py |
| SUB-AU-0008-BE (Role names) | Yes | T006, T007 | **None** | Schema fix + rbac cleanup. No test update task (H4) |
| SUB-AU-0009-BE (RBAC enforcement) | Yes | T024 | Existing | Verification only; 4 existing RBAC tests |
| SUB-AU-0010-BE (Last-admin) | Done | — | Existing | 2 existing protection tests |
| SUB-AU-0011-BE (Audit trail) | Yes | T023 | **None** | Verification task; no test assertions (M4) |
| SUB-AU-0012-BE (OAuth accounts) | Yes | T013 | T012 | Verify model + test via OAuth tests |
| SUB-AU-0013-BE (Password complexity) | Yes | T003, T005, T008-T011 | T008, T011 | Full Red-Green-Refactor (if reordered) |
| SUB-AU-0014-BE (Email service) | Yes | T004, T019-T022 | T019, T022 | Full Red-Green-Refactor (if reordered) |

**Platform Requirement Coverage**: 14/14 (100%) — all have tasks or are already Done

---

## Constitution Alignment

| Principle | Status | Finding IDs | Notes |
|-----------|--------|-------------|-------|
| I. Test-First (NON-NEGOTIABLE) | **VIOLATED** | C1, C2 | Implementation tasks precede test tasks in 2 cases |
| II. Layered Architecture | PASS | — | All new code follows routers → services → models |
| III. HIPAA Compliance | PASS | — | Auth feature has no PHI; audit (T023) and RBAC (T024) verified |
| IV. Code Coverage | PASS | — | T025 runs `pytest --cov=pms` with threshold targets |
| V. Async-First | PASS | — | All handlers async, UUID PKs, Alembic migrations |
| VI. Simplicity & YAGNI | PASS | — | Single new dependency (authlib) justified in research.md TD-5 |

| Quality Gate | Status | Finding IDs | Notes |
|-------------|--------|-------------|-------|
| Lint (ruff) | **NO TASK** | H1 | No task runs `ruff check src/ tests/` |
| Type Safety | PASS | — | Pydantic schemas enforce at boundaries (T005 adds new schema) |
| Tests | PASS | — | T025 runs full test suite |
| Coverage | PASS | — | T025 checks coverage thresholds |
| No PHI Leaks | N/A | — | Auth feature does not handle PHI |
| Migrations | PASS | — | T013 checks/creates Alembic migration if needed |

---

## Traceability Matrix Gap Analysis

The current traceability matrix (`docs/docs/testing/traceability-matrix.md` v1.5) has **zero SUB-AU entries**:

- **Forward Traceability**: SYS-REQ-0001 and SYS-REQ-0005 reference SUB-PR, SUB-CW, SUB-MM, SUB-RA, SUB-PM subsystems but do NOT reference SUB-AU-*
- **Backward Traceability**: No TST-AU-* test case IDs exist. Only `TST-AUTH-0001` (login JWT) exists but uses non-standard naming
- **Platform Traceability Summary**: No SUB-AU section exists (PR, CW, MM, RA, PM are present)

**Required additions** (post-implementation):

| Test Case ID | Description | Traces To | Planned Task |
|-------------|-------------|-----------|--------------|
| TST-AU-0001-BE | OAuth code exchange returns JWT for registered user | SUB-AU-0001-BE, SYS-REQ-0001 | T012, T018 |
| TST-AU-0002-BE | Email/password login returns JWT | SUB-AU-0002-BE, SYS-REQ-0001 | Existing |
| TST-AU-0003-BE | JWT access + refresh token issuance and refresh | SUB-AU-0003-BE | Existing |
| TST-AU-0004-BE | Account lockout after 5 failures, 30-minute duration | SUB-AU-0004-BE, SYS-REQ-0001 | T002 |
| TST-AU-0005-BE | Admin seeded on migration with correct role | SUB-AU-0005-BE | Existing |
| TST-AU-0006-BE | User CRUD operations (create, read, update, list) | SUB-AU-0006-BE | Existing |
| TST-AU-0007-BE | Invite token generation, acceptance, and expiry | SUB-AU-0007-BE | Existing |
| TST-AU-0008-BE | Four-role model seeded correctly (admin, clinician, sales, lab-staff) | SUB-AU-0008-BE, SYS-REQ-0005 | T006, T007 |
| TST-AU-0009-BE | require_role middleware enforces per-endpoint access | SUB-AU-0009-BE, SYS-REQ-0005 | T024 |
| TST-AU-0010-BE | Last-admin protection prevents admin lockout | SUB-AU-0010-BE | Existing |
| TST-AU-0011-BE | All 12 audit action strings logged correctly | SUB-AU-0011-BE, SYS-REQ-0003 | T023 |
| TST-AU-0012-BE | OAuth account linking on first provider login | SUB-AU-0012-BE | T013, T018 |
| TST-AU-0013-BE | Password complexity validation (5 rules, 422 on failure) | SUB-AU-0013-BE | T008, T011 |
| TST-AU-0014-BE | Email service sends invite and password reset emails | SUB-AU-0014-BE | T019, T022 |

---

## Unmapped Tasks

All 27 tasks map to at least one SUB-AU-BE requirement or to cross-cutting infrastructure. No orphan tasks.

---

## Metrics

| Metric | Value |
|--------|-------|
| Acceptance Criteria (spec.md) | 18 |
| Platform Requirements (SUB-AU-*-BE) | 14 |
| Total Tasks (tasks.md) | 27 |
| AC Coverage (AC with >= 1 task or existing impl) | 18/18 (100%) |
| Requirement Coverage (SUB-AU-BE with >= 1 task or Done) | 14/14 (100%) |
| Constitution Principles Checked | 6 |
| Constitution Violations | 1 (Principle I — 2 instances) |
| Quality Gate Gaps | 1 (lint task missing) |
| Traceability Matrix Test Case IDs for SUB-AU | 0/14 (gap) |
| Ambiguity Count | 2 (M4, L1) |
| Duplication Count | 0 |
| Inconsistency Count | 5 (H2, H3, M1, M2, M3) |
| **Critical Issues** | **3** |
| **High Issues** | **4** |
| **Medium Issues** | **5** |
| **Low Issues** | **2** |
| **Total Findings** | **14** |

---

## Next Actions

### Before `/speckit.implement` (CRITICAL issues must be resolved):

1. **Fix Test-First ordering (C1, C2)**: Restructure tasks.md so that test tasks precede their implementation counterparts. Recommended approach: within Phase 2, pair each implementation task with its test (e.g., T003a: write test, T003b: implement). This satisfies Constitution Principle I without changing the phase structure.

2. **Add lint task (H1)**: Add a task to Phase 7: `Run ruff check src/ tests/ and fix violations`. This satisfies the Quality Gate.

3. **Add test update task for rbac.py (H4)**: Add a task after T007: `Update tests/test_auth_middleware.py to use new role names (clinician, sales, lab-staff)`.

### After implementation (before PR merge):

4. **Update traceability matrix (C3)**: Add SUB-AU section to traceability-matrix.md with all 14 TST-AU-*-BE entries and forward traceability updates for SYS-REQ-0001 and SYS-REQ-0005.

5. **Update spec.md (H2, H3, M1, M2, M3)**: Align spec.md Sections 5.1 and 6.1 with data-model.md and contracts. Fix endpoint paths, column names, and nullability.

### Optional improvements (LOW priority):

6. **Resolve stale open questions (L1)**: Mark spec.md Section 11 questions as resolved.
7. **Refine Phase 2 blocking (L2)**: Allow US2/US4 to start before email service (T004) completes.

### Suggested commands:

- Resolve C1+C2+H1+H4: manually edit `tasks.md` to reorder tests and add missing tasks
- Resolve H2+H3+M1-M3: run `/speckit.clarify` to update spec.md
- Resolve C3: after implementation, update traceability-matrix.md per template in this report
- Proceed to implementation: `/speckit.implement`
