# Requirements Governance & Conflict Analysis

**Document ID:** PMS-GOV-001
**Version:** 1.5
**Date:** 2026-02-21
**Parent:** [System Specification](../../specs/system-spec.md)

---

## 1. Purpose

This document defines the governance procedures for evolving the PMS three-tier requirements decomposition (System → Domain → Platform) and provides a systematic conflict and race condition analysis across all 48 domain requirements and 95 platform requirements.

---

## 2. Governance Procedures

### 2.1 Procedure: Adding a New Platform

Use this when a new deployable component is introduced (e.g., an iOS app or a desktop client).

| Step | Action | Artifacts Updated |
|---|---|---|
| 1 | **Assign platform code** — choose a unique 2–3 letter code (e.g., `IOS`). Verify it does not collide with existing codes (BE, WEB, AND, AI). | — |
| 2 | **Register in system-spec.md** — add a row to Section 8.1 (Platform Codes) with the code, platform name, repository, and technology. | `system-spec.md` |
| 3 | **Audit every domain requirement** — for each of the 35 domain requirements across SUB-PR, SUB-CW, SUB-MM, and SUB-RA, determine if the new platform requires a platform-specific requirement. Record the decision (yes/no) and rationale. | Governance log |
| 4 | **Create platform requirements** — for each "yes" decision, create a platform file `platform/SUB-{domain}-{PLATFORM}.md` (or add to an existing one). Use the format `SUB-{domain}-{NNNN}-{PLATFORM}`. Update the Platform Decomposition index table in the corresponding `domain/SUB-{domain}.md`. | `platform/SUB-*-{PLATFORM}.md`, `domain/SUB-*.md` |
| 5 | **Create test case stubs** — add `TST-{domain}-{NNNN}-{PLATFORM}` entries to the backward traceability section of `traceability-matrix.md`. | `traceability-matrix.md` |
| 6 | **Update platform traceability summary** — add a column for the new platform in the Platform Traceability Summary section and set initial statuses. | `traceability-matrix.md` |
| 7 | **Update coverage summary** — add a row for the new platform in the Coverage Summary by Platform table. | `traceability-matrix.md` |
| 8 | **Update testing strategy** — add the platform code to the Test Naming Convention section and add platform-specific test runner commands. | `testing-strategy.md` |
| 9 | **Update index.md** — update the platform requirement count in the Specifications & Requirements section. | `index.md` |
| 10 | **Run conflict analysis** — execute Sections 4 and 5 of this document for the new platform. Document any new conflicts. | This document |

**Approval gate:** Steps 1–3 require tech lead sign-off before proceeding to step 4.

### 2.2 Procedure: Adding a New Domain Subsystem

Use this when a new functional domain is introduced (e.g., SUB-BL for Billing or SUB-SC for Scheduling).

| Step | Action | Artifacts Updated |
|---|---|---|
| 1 | **Assign subsystem code** — choose a unique 2-letter code (e.g., `BL`). Verify it does not collide with existing codes (PR, CW, MM, RA). | — |
| 2 | **Register in system-spec.md** — add a row to Section 4 (Subsystem Decomposition) with the code, subsystem name, scope, and primary actor. | `system-spec.md` |
| 3 | **Create subsystem requirements documents** — create `docs/specs/requirements/domain/SUB-{CODE}.md` for domain requirements and `docs/specs/requirements/platform/SUB-{CODE}-{PLATFORM}.md` for each applicable platform, following the template structure of existing subsystem docs. | `domain/SUB-{CODE}.md` (new), `platform/SUB-{CODE}-*.md` (new) |
| 4 | **Define domain requirements** — enumerate all domain requirements with IDs `SUB-{CODE}-NNNN` in `domain/SUB-{CODE}.md`. Link each to a parent SYS-REQ where applicable. | `domain/SUB-{CODE}.md` |
| 5 | **Decompose into platform requirements** — for each domain requirement, create platform-specific requirements in `platform/SUB-{CODE}-{PLATFORM}.md` for each applicable platform (BE, WEB, AND, AI). Update the Platform Decomposition index table in `domain/SUB-{CODE}.md`. | `platform/SUB-{CODE}-*.md`, `domain/SUB-{CODE}.md` |
| 6 | **Update SYS-REQ.md** — for any system requirement that the new subsystem satisfies, add the new SUB-{CODE}-NNNN to the "Decomposes To" field. | `SYS-REQ.md` |
| 7 | **Update traceability matrix** — add forward traceability rows, backward traceability test stubs, and platform traceability summary for the new subsystem. | `traceability-matrix.md` |
| 8 | **Update index.md** — add the new subsystem to the Specifications & Requirements section and update counts. | `index.md` |
| 9 | **Run conflict analysis** — execute Sections 3, 4, and 5 of this document for the new subsystem. Document any new intra-domain, cross-domain, and platform conflicts. | This document |

**Approval gate:** Steps 1–4 require product owner sign-off before platform decomposition.

### 2.3 Procedure: Decomposing a System Requirement

Use this when a new SYS-REQ is added or an existing one needs re-decomposition.

| Step | Action | Artifacts Updated |
|---|---|---|
| 1 | **Define or update the system requirement** — add/modify the entry in `SYS-REQ.md` with ID, description, priority, rationale, and acceptance criteria. | `SYS-REQ.md` |
| 2 | **Identify affected subsystems** — determine which of the 4 subsystems (PR, CW, MM, RA) must implement aspects of this requirement. | Governance log |
| 3 | **Create domain requirements** — in each affected `domain/SUB-*.md`, add a domain requirement that traces to the system requirement via the Parent field. | `domain/SUB-PR.md`, `domain/SUB-CW.md`, `domain/SUB-MM.md`, `domain/SUB-RA.md` |
| 4 | **Decompose into platform requirements** — for each new domain requirement, determine which platforms (BE, WEB, AND, AI) require implementation and add platform requirements to the corresponding `platform/SUB-*-{PLATFORM}.md` file. Update the Platform Decomposition index table in the domain file. | `platform/SUB-*-{PLATFORM}.md`, `domain/SUB-*.md` |
| 5 | **Update "Decomposes To"** — in `SYS-REQ.md`, update the requirement's "Decomposes To" field listing all new SUB-*-NNNN IDs with their platform annotations. | `SYS-REQ.md` |
| 6 | **Update traceability matrix** — add forward and backward traceability entries. Create test case stubs for each new platform requirement. | `traceability-matrix.md` |
| 7 | **Verify strict rollup** — confirm that the system requirement's verification status correctly reflects the strict rollup rule: "Verified" only when ALL domain requirements are verified, each domain requirement verified only when ALL its platform requirements are verified. | `traceability-matrix.md` |
| 8 | **Run conflict analysis** — check Sections 3, 4, and 5 for new conflicts introduced by the decomposition. | This document |

**Approval gate:** Step 2 decisions (subsystem mapping) require architecture review.

### 2.4 Procedure: Feature Branching & Release Strategy

Use this when developing features concurrently, evaluating MVP variant implementations, or preparing a prioritized feature for release. This section connects to [ADR-0006: Release Management Strategy](../../architecture/0006-release-management-strategy.md) and the [Release Process](../../config/release-process.md).

#### 2.4.1 Branch Naming Convention

| Branch Type | Pattern | Example | Purpose |
|---|---|---|---|
| Feature | `feature/{name}` | `feature/offline-sync` | Standard feature development |
| MVP Variant | `feature/{name}-v{N}` | `feature/search-v1`, `feature/search-v2` | Competing implementations of the same feature |
| Release | `release/v{X.Y.Z}` | `release/v1.2.0` | Release candidate preparation |
| Hotfix | `hotfix/v{X.Y.Z}` | `hotfix/v1.2.1` | Production emergency fix |
| Docs | `docs/{topic}` | `docs/governance-update` | Documentation-only changes |

**Rules:**
1. Variant branches (`feature/{name}-v1`, `feature/{name}-v2`) must share the same base commit from `main`.
2. Branch names must be consistent across all repositories in the multi-repo structure (pms-backend, pms-frontend, pms-android, pms-docs).
3. Feature names use lowercase kebab-case (e.g., `offline-sync`, not `offlineSync` or `Offline_Sync`).

#### 2.4.2 Concurrent Development Model

When two or more features are developed in parallel on separate branches:

| Step | Action | Artifacts Updated |
|---|---|---|
| 1 | **Create feature branch from `main`** — each feature starts from the latest `main`. Record the base commit SHA in the feature's tracking issue. | — |
| 2 | **Rebase onto `main` every 2 days** — each feature branch must rebase onto the latest `main` at least once every 2 calendar days to minimize drift. | Feature branch |
| 3 | **CI must pass on every push** — no feature branch may have a failing CI pipeline for more than 24 hours. | CI pipeline |
| 4 | **Identify shared-code touchpoints** — before development begins, list files and modules modified by both features. Flag potential conflicts early. | Governance log |
| 5 | **First-ready-first-merged** — the first feature to complete review and CI is merged to `main`. No feature has inherent merge priority unless the release corridor (Section 2.4.4) has been entered. | `main` branch |
| 6 | **Second-to-merge must rebase** — after the first feature merges, the remaining feature must rebase onto the updated `main` and resolve any conflicts before its own merge. | Feature branch |
| 7 | **Conflict analysis before merge** — run the conflict analysis (Sections 3, 4, and 5 of this document) for any requirement touched by the feature. Document new conflicts using the existing ID schemes (DC-*, PC-*, RC-*). | This document |

**Conflict resolution rules for concurrent features:**

| Conflict Type | Resolution |
|---|---|
| Shared file, different functions | Rebase resolves automatically; verify CI passes |
| Shared file, same function | Second-to-merge must reconcile changes manually; require code review from both feature leads |
| Shared requirement (same SUB-* ID modified) | Escalate to architecture review before merging the second feature |
| Docs submodule (pms-docs) | Second-to-merge rebases the submodule pointer; verify all cross-references resolve |

**Approval gate:** Step 7 conflict analysis requires tech lead sign-off before the merge to `main`.

#### 2.4.3 MVP Variant Branching Pattern

Use this when a feature has two or more candidate implementations and the team has not yet decided which approach to pursue. This pattern supports structured evaluation without committing to either approach prematurely.

**Phase 1 — Variant Development**

| Step | Action | Artifacts Updated |
|---|---|---|
| 1 | **Create variant branches from the same commit** — both `feature/{name}-v1` and `feature/{name}-v2` branch from the identical `main` commit. Record the shared base SHA. | — |
| 2 | **Define evaluation criteria upfront** — before development begins, agree on the weighted scoring criteria (see Phase 2 scoring matrix). Document criteria in the feature's tracking issue. | Tracking issue |
| 3 | **Time-box to 1 sprint** — variant development must not exceed 1 sprint (2 weeks). If neither variant is ready by sprint end, the decision gate proceeds with whatever is available. | — |
| 4 | **Independent CI** — each variant branch runs its own CI pipeline independently. Both must pass before the decision gate. | CI pipeline |

**Phase 2 — Decision Gate**

A review meeting (60 minutes maximum) evaluates both variants using a weighted scoring matrix:

| Criterion | Weight | Description |
|---|---|---|
| Requirement coverage | 30% | How many of the feature's acceptance criteria does the variant satisfy? |
| Implementation complexity | 25% | Lines of code, number of new dependencies, cognitive complexity |
| Test coverage | 20% | Unit, integration, and system test coverage percentage |
| Performance | 15% | Benchmark results (latency, throughput, resource usage) |
| Maintainability | 10% | Code readability, documentation quality, alignment with existing patterns |

**Decision gate outputs:**
1. Completed scoring matrix with per-criterion scores (1–5) and weighted totals.
2. An architectural decision record (ADR) in `docs/architecture/` documenting: context, both variants evaluated, scoring results, and rationale for the selected variant.
3. If scores are within 10%, the tech lead casts the deciding vote and documents the tiebreaker rationale in the ADR.

**Phase 3 — Variant Retirement**

| Step | Action | Artifacts Updated |
|---|---|---|
| 1 | **Merge the selected variant** — merge the winning variant branch into `main` following the standard merge process (CI pass, code review, conflict analysis per Section 2.4.2 Step 7). | `main` branch |
| 2 | **Archive the rejected variant** — tag the rejected branch with `archive/{name}-v{N}` (e.g., `archive/search-v2`) and delete the branch. The tag preserves the commit history for future reference. | Git tags |
| 3 | **Salvage reusable components** — if the rejected variant contains reusable code (utilities, tests, documentation), cherry-pick those commits into `main` or a follow-up feature branch. Reference the archive tag in the cherry-pick commit message. | `main` or feature branch |

#### 2.4.4 One-Week Release Corridor

Once a feature is prioritized for release, it enters a **7-day release corridor** that maps to the 4-environment pipeline defined in [ADR-0006](../../architecture/0006-release-management-strategy.md) and the [Release Process](../../config/release-process.md).

| Day | Environment | Activities |
|---|---|---|
| Day 0 | — | **Priority declared.** Product owner confirms the feature is release-ready. Prerequisites: feature branch merged to `main`, all CI green, all requirement statuses in SUB-*.md updated. |
| Day 1 | Dev | **Dev smoke test.** Deploy `main` to the dev environment. Run TST-UNIT-* and TST-INT-* suites. Fix any regressions before proceeding. |
| Day 2–3 | QA | **QA validation.** Create a release candidate tag (`rc-v{X.Y.Z}`). Deploy to QA. Run full regression suite (TST-SYS-* and TST-E2E-*). QA team signs off or returns blockers. |
| Day 4–5 | Staging | **Staging validation.** Deploy the RC to staging. Run platform compatibility tests. Update the [Release Compatibility Matrix](../../specs/release-compatibility-matrix.md) with tested version combinations. Execute TST-SYS-* acceptance tests against staging data. |
| Day 6 | — | **CCB approval.** Change Control Board reviews: test results, compatibility matrix, updated requirement statuses, and ADRs. CCB approves or rejects. If approved, create the production tag (`v{X.Y.Z}`). |
| Day 7 | Production | **Production deploy.** Deploy the production tag. Monitor error rates, latency, and key metrics for 4 hours post-deploy. If anomalies exceed thresholds, execute the rollback procedure from the [Release Process](../../config/release-process.md). |

**Escalation rules:**

| Scenario | Escalation |
|---|---|
| QA blocker (Day 2–3) | Fix on `main`, re-tag RC, restart from Day 2. Adds 2 days to corridor. |
| Staging failure (Day 4–5) | If the failure is environment-specific, fix and re-deploy to staging (no day reset). If the failure is a code defect, fix on `main`, re-tag RC, restart from Day 2. |
| CCB not available on Day 6 | Corridor pauses. Resume when CCB convenes (maximum 2 business days delay). |
| Production deploy failure (Day 7) | Execute rollback immediately. Open a hotfix branch (`hotfix/v{X.Y.Z}`). Hotfix follows an accelerated 3-day corridor (Dev → QA → Production, skip staging). |

**Multi-repo coordination:**
- All repositories (pms-backend, pms-frontend, pms-android) entering the release corridor must use the same RC tag version.
- The pms-docs submodule pointer is updated as part of the RC tag.
- Production tags are created simultaneously across all repos after CCB approval.

#### 2.4.5 Branch Lifecycle Diagram

```
main ─────────────●────────────────────────●──────────────────────●─── ...
                  │                        │                      ↑
                  ├── feature/offline-sync ─┘ (merge)             │
                  │                                               │
                  ├── feature/search-v1 ──────── (selected) ──────┘ (merge)
                  │                                │
                  └── feature/search-v2 ──── (rejected)
                                                   │
                                             archive/search-v2 (tag)

Release Corridor (7 days):
  Day 0        Day 1     Day 2-3     Day 4-5    Day 6      Day 7
  Priority  →  Dev    →   QA      →  Staging →  CCB    →  Production
  declared     smoke      rc-tag     compat     approve    v{X.Y.Z}
               test       regress    matrix     prod tag   deploy
```

#### 2.4.6 Integration with Existing Governance

This section maps branching and release events to existing governance procedures:

| Event | Governance Procedure | Reference |
|---|---|---|
| New platform requirement identified during feature development | Procedure 2.1 — Adding a New Platform | Section 2.1 |
| New subsystem requirement identified during feature development | Procedure 2.2 — Adding a New Domain Subsystem | Section 2.2 |
| Existing requirement modified by a feature branch | Procedure 2.3 — Decomposing a System Requirement | Section 2.3 |
| Concurrent features modify the same subsystem | Section 2.4.2 — Concurrent Development Model | Section 2.4.2 |
| MVP variant selected after evaluation | Section 2.4.3 — MVP Variant Branching Pattern | Section 2.4.3 |
| Feature enters release corridor | Section 2.4.4 — One-Week Release Corridor | Section 2.4.4 |

**Artifact update requirements per feature merge:**

| Artifact | When to Update |
|---|---|
| `domain/SUB-*.md` and `platform/SUB-*-{PLATFORM}.md` (requirement docs) | When the feature adds, modifies, or resolves a domain or platform requirement |
| `SYS-REQ.md` | When the feature affects a system-level requirement or its decomposition |
| `traceability-matrix.md` | When new test cases are added or requirement statuses change |
| `testing-strategy.md` | When new test patterns or platform-specific test runners are introduced |
| `release-compatibility-matrix.md` | During the staging phase (Day 4–5) of the release corridor |
| `subsystem-versions.md` | When the feature increments a subsystem version |
| This document (PMS-GOV-001) | When the feature introduces new conflicts or race conditions (Sections 3, 4, 5) |
| `docs/architecture/NNNN-*.md` | When an architectural decision is made (especially during MVP variant selection) |

#### 2.4.7 Conflict Analysis Tie-In

Feature branching introduces the risk of conflicts that span branches and are invisible until merge time. The following rules integrate the branching strategy with the conflict analysis framework in Sections 3, 4, and 5.

| Rule | Description |
|---|---|
| **Pre-merge conflict scan** | Before merging any feature branch to `main`, run a diff of all requirement documents (SUB-*.md, SYS-REQ.md) against the current `main`. Identify any requirement IDs that were modified on both the feature branch and `main` since the branch point. |
| **Cross-branch requirement audit** | When two feature branches are in concurrent development (Section 2.4.2), compare their modified requirement IDs weekly. If both branches modify the same requirement, escalate to architecture review before either merges. |
| **New conflict documentation** | Any new conflict discovered during a feature merge must be documented in Sections 3, 4, or 5 of this document using the existing ID schemes (DC-{domain}-NN, PC-{platform}-NN, RC-{platform}-NN). Increment the "Total" counts in each section summary. |
| **Post-merge verification** | After merging a feature branch, re-run the full conflict analysis (Sections 3, 4, 5) for all requirements touched by the feature. Verify that no new unresolved conflicts exist before the feature enters the release corridor. |

**Approval gate:** The pre-merge conflict scan (Rule 1) requires tech lead sign-off. The scan results must be attached to the merge pull request.

---

## 3. Intra-Domain Conflict Analysis

Conflicts where two or more requirements within the same domain subsystem impose contradictory or ambiguous obligations.

### SUB-PR — Patient Records (7 conflicts)

| ID | Conflict | Requirements | Severity | Resolution | Status |
|---|---|---|---|---|---|
| DC-PR-01 | **Encryption standard mismatch** — SUB-PR-0004 specifies Fernet (AES-128-CBC) for SSN encryption, but its parent SYS-REQ-0002 mandates AES-256. The domain requirement is marked "Verified" while the system requirement is only "Partial." | SUB-PR-0004 vs SYS-REQ-0002 | High | Planned migration to AES-256-GCM before production. SUB-PR-0004 status should be annotated as "Verified (dev)" until migration completes. Re-verify after migration. | **Resolved** — SUB-PR-0004 updated to target AES-256-GCM, status changed to "Verified (dev)". SUB-PR-0004-BE updated with versioned-envelope migration plan. |
| DC-PR-02 | **Unbounded list vs pagination** — SUB-PR-0003 (CRUD) includes a list endpoint that returns all active patients. SUB-PR-0008 requires paginated results (default 20/page). If both are implemented independently, the list endpoint in SUB-PR-0003 contradicts the pagination constraint. | SUB-PR-0003 vs SUB-PR-0008 | Medium | SUB-PR-0008 supersedes the list behavior of SUB-PR-0003. When SUB-PR-0008 is implemented, the existing list endpoint must be refactored to default to paginated results. Add a note to SUB-PR-0003 that the list behavior is interim. | **Resolved** — SUB-PR-0003 annotated that list behavior is interim, superseded by SUB-PR-0008. |
| DC-PR-03 | **AI vision resource contention** — SUB-PR-0009 (wound assessment), SUB-PR-0010 (patient ID verification), and SUB-PR-0011 (document OCR) all require edge AI inference on the same Jetson Thor device. No requirement specifies priority, queuing, or resource sharing. | SUB-PR-0009, SUB-PR-0010, SUB-PR-0011 | Medium | Add a shared non-functional requirement for AI inference queuing: requests must be serialized per device with a configurable timeout. Define priority order: patient ID verification > wound assessment > document OCR. | **Resolved** — SUB-PR-0012 added with priority order and CameraSessionManager requirement. SUB-PR-0009/0010/0011-AND updated to reference CameraSessionManager. |
| DC-PR-04 | **Email uniqueness during concurrent creation** — SUB-PR-0006 (unique email) is enforced at the database constraint level, but SUB-PR-0003 (CRUD) does not specify behavior when the constraint is violated during concurrent operations. The service layer checks uniqueness before insert, creating a TOCTOU gap. | SUB-PR-0006 vs SUB-PR-0003 | Low | The database unique constraint catches concurrent violations. The service layer should handle `IntegrityError` from the DB and return 409, not rely solely on the pre-check. Current implementation already does this correctly. | **Resolved** — SUB-PR-0006 and SUB-PR-0006-BE updated to specify IntegrityError → 409 handling. |
| DC-PR-05 | **AI inference queuing scope expansion** — SUB-PR-0012 defines inference serialization with a priority order covering three vision features (SUB-PR-0009, 0010, 0011). SUB-PR-0013-AND introduces a fourth camera-based AI feature (dermoscopic image capture with on-device TFLite classification) that must also go through the CameraSessionManager singleton, but SUB-PR-0012 does not include it in its priority order. | SUB-PR-0012 vs SUB-PR-0013 | Medium | Update SUB-PR-0012 priority order to include dermoscopic capture as the fourth feature. Recommended priority: patient ID verification (SUB-PR-0010) > wound assessment (SUB-PR-0009) ≥ dermoscopic capture (SUB-PR-0013) > document OCR (SUB-PR-0011). Dermoscopic capture and wound assessment share equal clinical urgency; break ties by submission order (FIFO). | Open |
| DC-PR-06 | **Lesion audit trail traceability gap** — SYS-REQ-0012 acceptance criterion #5 requires "all image uploads, classifications, and result views are recorded in the audit trail." However, SUB-PR-0013 through SUB-PR-0016 reference only SYS-REQ-0012 as their parent — they do not trace to SYS-REQ-0003 (audit trail). The audit event catalog (PC-BE-03) lacks derm-specific action strings. The `routers/lesions.py` module is not listed in SUB-PR-0005's scope. Dermoscopic images are PHI requiring HIPAA-compliant audit logging. | SUB-PR-0013, SUB-PR-0014, SUB-PR-0015, SUB-PR-0016 vs SYS-REQ-0003 | High | Add explicit audit logging requirements to SUB-PR-0013-BE through SUB-PR-0016-BE: `routers/lesions.py` must call `audit_service.log_action` for every endpoint. Extend the audit event catalog with derm-specific action strings (LESION_UPLOAD, LESION_CLASSIFY, LESION_VIEW, SIMILARITY_SEARCH, TIMELINE_VIEW; resource_type: lesion_image). Update SUB-PR-0005 scope to include lesion operations. | Open |
| DC-PR-07 | **Encounter-patient cross-reference validation** — SUB-PR-0013 upload accepts `patient_id` (required) and `encounter_id` (optional). SUB-CW-0008 requires encounters be linked to exactly one patient via patient_id FK. If a caller provides an `encounter_id` belonging to Patient A but a `patient_id` for Patient B, the lesion image is linked to an encounter for the wrong patient — a PHI cross-contamination risk. No requirement specifies this cross-reference validation. | SUB-PR-0013 vs SUB-CW-0008 | High | SUB-PR-0013-BE must validate encounter-patient consistency: when `encounter_id` is provided, query the encounter and verify its `patient_id` matches the upload's `patient_id`. Return 422 Unprocessable Entity on mismatch with message "encounter does not belong to the specified patient." | Open |

### SUB-CW — Clinical Workflow (3 conflicts)

| ID | Conflict | Requirements | Severity | Resolution | Status |
|---|---|---|---|---|---|
| DC-CW-01 | **Lifecycle vs transition validation ambiguity** — SUB-CW-0003 defines the lifecycle states (scheduled → in_progress → completed/cancelled) and SUB-CW-0007 requires transition validation. Neither specifies the complete valid transition set. Can "cancelled" be reached from any state? Can "completed" only come from "in_progress"? | SUB-CW-0003 vs SUB-CW-0007 | High | Define the explicit state machine: `scheduled → in_progress`, `scheduled → cancelled`, `in_progress → completed`, `in_progress → cancelled`. No transitions from terminal states (completed, cancelled). Add this to SUB-CW-0007's acceptance criteria. | **Resolved** — SUB-CW-0007 updated with the full explicit state machine. SUB-CW-0003 now references SUB-CW-0007 for the state machine definition. |
| DC-CW-02 | **Emergency encounter lifecycle exception** — SUB-CW-0006 defines encounter type "emergency" but SUB-CW-0003's lifecycle starts at "scheduled." Emergency encounters may need to skip "scheduled" and begin directly in "in_progress." | SUB-CW-0006 vs SUB-CW-0003 | Medium | Allow the transition `created → in_progress` for emergency encounters (bypassing "scheduled"). Add a creation-time rule: if type = emergency, initial status = in_progress. Document this exception in SUB-CW-0003. | **Resolved** — SUB-CW-0003 documents the emergency exception. SUB-CW-0007 includes `created → in_progress` for emergencies. |
| DC-CW-03 | **Alert timing vs encounter finalization** — SUB-CW-0005 triggers clinical alerts based on encounter notes. If a note is added during the transition from in_progress → completed, the alert may fire after the encounter is finalized, leaving no opportunity for the clinician to act within the encounter context. | SUB-CW-0005 vs SUB-CW-0003 | Medium | Alerts must be evaluated before status transitions to "completed" are committed. Add a pre-transition hook: if the encounter has pending unacknowledged critical alerts, block the transition to "completed" until the clinician acknowledges or overrides. | **Resolved** — SUB-CW-0005 updated with pre-transition alert evaluation and blocking behavior. |

### SUB-MM — Medication Management (3 conflicts)

| ID | Conflict | Requirements | Severity | Resolution | Status |
|---|---|---|---|---|---|
| DC-MM-01 | **Interaction check latency vs encryption overhead** — SUB-MM-0001 requires drug interaction checks within 5 seconds. SUB-MM-0003 requires encryption of prescription PHI. Decrypting patient medication history to run interaction checks adds latency that may exceed the 5-second SLA under load. | SUB-MM-0001 vs SUB-MM-0003 | High | The interaction checker should operate on medication IDs (not PHI), avoiding the need to decrypt PHI during the check. Only the prescription record (patient name, dosage instructions) needs encryption; drug interaction lookup keys (RxNorm codes) should be stored in plaintext. | **Resolved** — SUB-MM-0001 specifies RxNorm code usage. SUB-MM-0003 clarifies PHI-only encryption scope with RxNorm codes in plaintext. |
| DC-MM-02 | **Prescription cancellation vs refill tracking** — SUB-MM-0008 allows prescription cancellation. SUB-MM-0009 tracks remaining refills. Neither specifies whether a cancelled prescription's remaining refills can be reinstated, or whether cancellation zeroes the refill count. | SUB-MM-0008 vs SUB-MM-0009 | Medium | Cancellation sets refills_remaining to 0 and is irreversible. A new prescription must be created if the medication is needed again. Add to SUB-MM-0008 acceptance criteria: "Cancellation is a terminal state; cancelled prescriptions cannot be reactivated." | **Resolved** — SUB-MM-0008 updated with terminal cancellation semantics and irreversibility. |
| DC-MM-03 | **RBAC role ambiguity for status transitions** — SUB-MM-0007 defines roles (physician prescribe, nurse view, pharmacist dispense) but SUB-MM-0008 defines status transitions (active → completed/cancelled). Which role(s) can cancel a prescription? Can a pharmacist complete a prescription upon final dispense? | SUB-MM-0007 vs SUB-MM-0008 | Medium | Define transition-to-role mapping: physician can cancel (override), pharmacist can mark completed (upon final dispense), nurse cannot change status. Add this mapping to SUB-MM-0007 acceptance criteria. | **Resolved** — SUB-MM-0007 updated with explicit transition-to-role mapping. |

### SUB-RA — Reporting & Analytics (1 conflict)

| ID | Conflict | Requirements | Severity | Resolution | Status |
|---|---|---|---|---|---|
| DC-RA-01 | **Audit log access role gap** — SUB-RA-0003 provides an audit log query interface (required by SYS-REQ-0003 for HIPAA compliance). SUB-RA-0005 restricts report access to administrator and billing roles. Compliance officers need audit log access but the system defines no compliance officer role (SYS-REQ-0005 specifies only 4 roles: physician, nurse, administrator, billing). | SUB-RA-0003 vs SUB-RA-0005 | High | Either (a) extend the role model to include a "compliance" role with audit-read-only access, which requires updating SYS-REQ-0005, or (b) grant administrators audit log access and designate compliance duties to the administrator role. Option (b) is recommended for v1.0 with option (a) deferred to a future RBAC enhancement. | **Resolved** — Option (b) adopted. SUB-RA-0003 and SUB-RA-0005 updated to grant administrator role audit log access. Compliance role deferred. |

### SUB-PM — Prompt Management (3 conflicts)

| ID | Conflict | Requirements | Severity | Resolution | Status |
|---|---|---|---|---|---|
| DC-PM-01 | **Prompt name uniqueness TOCTOU** — SUB-PM-0003 requires unique prompt names. The service layer may check uniqueness with a SELECT before INSERT. Between the check and the insert, another concurrent request may create a prompt with the same name. The pre-check passes for both, but the second insert violates the unique constraint. | SUB-PM-0003 | Low | The database unique constraint on `name` is the authoritative enforcement. The service-layer pre-check is a UX optimization (fast feedback), not a safety mechanism. The service must catch `IntegrityError` on insert and translate it to HTTP 409. This mirrors the SUB-PR-0006 / DC-PR-04 pattern. | **Resolved** — SUB-PM-0003 specifies IntegrityError → 409 as authoritative enforcement. |
| DC-PM-02 | **Concurrent version creation** — SUB-PM-0004 requires auto-incrementing version numbers for each prompt. Two concurrent save operations may both read `MAX(version) = N` and both attempt to create version `N+1`, causing a duplicate or overwrite. | SUB-PM-0004 | High | Use `SELECT MAX(version) FROM prompt_versions WHERE prompt_id = ? FOR UPDATE` to serialize concurrent version creation at the database row level. The `FOR UPDATE` lock ensures only one transaction reads and increments at a time. This mirrors the RC-BE-01 / RC-BE-02 pattern. | **Resolved** — SUB-PM-0004 and SUB-PM-0004-BE specify `FOR UPDATE` serialization. |
| DC-PM-03 | **Cross-prompt comparison** — SUB-PM-0007 provides LLM-powered version comparison. A malicious or buggy request could attempt to compare versions across different prompts by supplying version IDs from different prompt records, potentially leaking prompt content across authorization boundaries. | SUB-PM-0007 | Medium | The comparison endpoint must validate that both requested versions belong to the same prompt ID specified in the URL path. Reject with 400 Bad Request if either version does not belong to the path-scoped prompt. | **Resolved** — SUB-PM-0007-BE specifies path-scoped endpoint validation for both versions. |

**Total intra-domain conflicts: 17 (14 resolved, 3 open)**

---

## 4. Cross-Platform Conflict Analysis

Conflicts where platform-specific requirements across different subsystems or platforms impose contradictory obligations on a shared component, API, or resource.

### Backend (BE) — 8 conflicts

| ID | Conflict | Requirements | Severity | Resolution | Status |
|---|---|---|---|---|---|
| PC-BE-01 | **Inconsistent encryption implementations** — SUB-PR-0004-BE uses Fernet (AES-128-CBC) for patient SSN encryption. SUB-MM-0003-BE requires AES-256 for prescription PHI. Both will use the same `encryption_service.py`. A single module cannot simultaneously provide Fernet and AES-256-GCM without a migration strategy or dual-mode support. | SUB-PR-0004-BE vs SUB-MM-0003-BE | High | When SUB-MM-0003-BE is implemented, migrate `encryption_service.py` to AES-256-GCM for all PHI (resolving DC-PR-01 simultaneously). Implement a versioned-envelope approach: new writes use AES-256-GCM, reads detect format (Fernet vs GCM) and decrypt accordingly. Backfill existing Fernet data in a one-time migration. | **Resolved** — SUB-PR-0004-BE updated with versioned-envelope migration plan. Both subsystems now target AES-256-GCM. |
| PC-BE-02 | **Shared auth middleware coupling** — SUB-PR-0001-BE, SUB-CW-0001-BE, SUB-MM-0006-BE, and SUB-RA-0004-BE all enforce JWT auth through the same `middleware/auth.py`. A change to the auth middleware (e.g., adding MFA token validation for SYS-REQ-0001) affects all four subsystems simultaneously. There is no subsystem-scoped auth configuration. | SUB-PR-0001-BE, SUB-CW-0001-BE, SUB-MM-0006-BE, SUB-RA-0004-BE | Medium | This is acceptable for a monolithic backend. The auth middleware should remain shared (DRY principle). Mitigate regression risk by maintaining TST-AUTH-0001 as a cross-cutting system test. When MFA is added, all four subsystem auth requirements are satisfied simultaneously. | **Resolved** — Accepted as designed. No requirements change needed; shared middleware is intentional for monolith. |
| PC-BE-03 | **Inconsistent audit logging** — SUB-PR-0005-BE is implemented (all 5 router methods call `audit_service.log_action`). SUB-CW-0004-BE, SUB-MM-0004-BE are placeholders. When encounter and medication audit logging is implemented, the audit schema, field names, and action strings must match the pattern established by patient audit logging — but no formal audit event catalog exists. | SUB-PR-0005-BE vs SUB-CW-0004-BE vs SUB-MM-0004-BE | Medium | Create an audit event catalog defining: action strings (CREATE, READ, UPDATE, DELETE, DEACTIVATE), resource_type values (patient, encounter, prescription), and required fields. Existing patient audit calls already set the pattern; formalize it before implementing encounter/medication audit logging. | **Resolved** — SUB-CW-0004-BE and SUB-MM-0004-BE updated to reference the audit event catalog with standardized action strings and resource_type values. |
| PC-BE-04 | **Role matrix inconsistency across subsystems** — SUB-PR-0002-BE grants access to admin/physician/nurse (with admin/physician for updates). SUB-RA-0005-BE restricts to administrator/billing. SUB-MM-0007-BE introduces pharmacist (not in SYS-REQ-0005's role list). The system defines 4 roles but the subsystems collectively reference 5 (physician, nurse, administrator, billing, pharmacist). | SUB-PR-0002-BE vs SUB-MM-0007-BE vs SUB-RA-0005-BE | High | Update SYS-REQ-0005 to define 5 roles (add pharmacist), or clarify that pharmacist is a specialization of an existing role. Create a consolidated RBAC matrix document mapping every endpoint to allowed roles. | **Resolved** — SYS-REQ-0005 updated to define 5 roles (pharmacist added). Consolidated RBAC matrix added as acceptance criterion. |
| PC-BE-05 | **Interaction check SLA under CRUD load** — SUB-MM-0001-BE requires a 5-second response for interaction checks. During peak load, concurrent CRUD operations (SUB-PR-0003-BE, SUB-CW-0003-BE) compete for the same database connection pool. No priority mechanism exists for safety-critical queries. | SUB-MM-0001-BE vs SUB-PR-0003-BE, SUB-CW-0003-BE | Medium | Implement a dedicated connection pool (or priority queue) for medication-safety queries. Alternatively, set the database connection pool size large enough that CRUD load does not block interaction checks. Add SLA monitoring for the interaction check endpoint. | **Resolved** — SUB-MM-0001-BE updated to require dedicated connection pool or priority queue for medication-safety queries. |
| PC-BE-06 | **Shared auth middleware (prompt endpoints)** — SUB-PM-0001-BE enforces JWT auth through the same `middleware/auth.py` shared by SUB-PR-0001-BE, SUB-CW-0001-BE, SUB-MM-0006-BE, and SUB-RA-0004-BE. A change to the auth middleware affects all subsystems simultaneously. | SUB-PM-0001-BE vs SUB-PR-0001-BE, SUB-CW-0001-BE, SUB-MM-0006-BE, SUB-RA-0004-BE | Low | Follows PC-BE-02 precedent — shared auth middleware is acceptable for the monolithic backend (DRY principle). Mitigate regression risk by maintaining TST-AUTH-0001 as a cross-cutting system test. No requirements change needed. | **Resolved** — Accepted as designed, following PC-BE-02 precedent. |
| PC-BE-07 | **Audit catalog extension** — SUB-PM-0005-BE introduces new audit action strings (PROMPT_CREATE, PROMPT_READ, PROMPT_UPDATE, PROMPT_DELETE, VERSION_CREATE, VERSION_COMPARE) and resource type `prompt`. These must be added to the audit event catalog established by PC-BE-03 without conflicting with existing action strings. | SUB-PM-0005-BE vs SUB-PR-0005-BE, SUB-CW-0004-BE, SUB-MM-0004-BE | Medium | Add the new action strings and resource type to the audit event catalog. The PROMPT_* and VERSION_* prefixes are unique and do not collide with existing CREATE/READ/UPDATE/DELETE/DEACTIVATE action strings used by other subsystems. | **Resolved** — SUB-PM-0005-BE specifies the new action strings. Audit event catalog updated. |
| PC-BE-08 | **Encryption module path divergence** — SUB-PR-0013-BE lists `core/encryption.py` as its encryption module, while SUB-PR-0004-BE uses `services/encryption_service.py`. Both reside in pms-backend. ADR-0016 mandates a unified versioned-envelope key management approach, but if two separate modules implement encryption, the shared KEK/DEK hierarchy cannot be enforced consistently. Key rotation would need to update both modules independently. | SUB-PR-0013-BE vs SUB-PR-0004-BE | Medium | Designate `services/encryption_service.py` as the single authoritative encryption module for all PHI (consistent with existing implementation). When AES-256-GCM support is added (per DC-PR-01/PC-BE-01 migration), both SSN and image encryption use the same module and key hierarchy. Update SUB-PR-0013-BE module reference from `core/encryption.py` to `services/encryption_service.py`. | Open |

### Web Frontend (WEB) — 3 conflicts

| ID | Conflict | Requirements | Severity | Resolution | Status |
|---|---|---|---|---|---|
| PC-WEB-01 | **Shared auth guard module** — SUB-PR-0001-WEB, SUB-CW-0001-WEB, SUB-MM-0006-WEB, and SUB-RA-0004-WEB all reference `lib/auth.ts` for auth guards. Different subsystems may need different guard behaviors (e.g., reports require admin/billing role check in the guard, while patient pages allow nurse access). A single auth guard implementation risks either over-permitting or under-permitting. | SUB-PR-0001-WEB, SUB-CW-0001-WEB, SUB-MM-0006-WEB, SUB-RA-0004-WEB | Medium | `lib/auth.ts` should provide a parameterized guard (e.g., `requireRole(['admin', 'physician'])`) rather than a single hardcoded check. Each page passes its allowed roles. The guard is shared; the role lists are subsystem-specific. | **Resolved** — SUB-PR-0001-WEB updated to specify parameterized auth guard with subsystem-specific role lists. |
| PC-WEB-02 | **Inconsistent patient data between list and dashboard** — SUB-PR-0008-WEB shows paginated patient lists with current data. SUB-RA-0001-WEB shows patient volume dashboards with aggregated data. If the dashboard caches aggregated counts while the patient list shows real-time data, the numbers may disagree within the same user session. | SUB-PR-0008-WEB vs SUB-RA-0001-WEB | Low | Add a cache TTL and "last refreshed" timestamp to the dashboard. Accept eventual consistency (reporting data may lag real-time data by up to the cache TTL). Document this in SUB-RA-0001-WEB acceptance criteria. | **Resolved** — SUB-RA-0001-WEB updated with cache TTL and "last refreshed" timestamp requirement. |
| PC-WEB-03 | **Shared auth guard (prompt pages)** — SUB-PM-0001-WEB uses the parameterized `requireRole` guard from `lib/auth.ts` shared by SUB-PR-0001-WEB, SUB-CW-0001-WEB, SUB-MM-0006-WEB, and SUB-RA-0004-WEB. Different prompt pages may need role combinations (admin-only for mutation pages, admin+physician for read pages). | SUB-PM-0001-WEB vs SUB-PR-0001-WEB, SUB-CW-0001-WEB, SUB-MM-0006-WEB, SUB-RA-0004-WEB | Low | Follows PC-WEB-01 precedent — the parameterized guard supports subsystem-specific role lists. Prompt pages pass `['admin']` for mutation routes and `['admin', 'physician']` for read routes. No code change to the guard itself is needed. | **Resolved** — Accepted as designed, following PC-WEB-01 precedent. SUB-PM-0001-WEB specifies role lists per route. |

### Android (AND) — 3 conflicts

| ID | Conflict | Requirements | Severity | Resolution | Status |
|---|---|---|---|---|---|
| PC-AND-01 | **Camera resource contention** — SUB-PR-0009-AND (wound assessment), SUB-PR-0010-AND (patient ID verification), and SUB-PR-0011-AND (document OCR) all require camera access. Android's CameraX allows only one active camera session. Rapid switching between features without proper lifecycle management will cause `CameraAccessException` or ANR. | SUB-PR-0009-AND, SUB-PR-0010-AND, SUB-PR-0011-AND | High | Implement a `CameraSessionManager` singleton that serializes camera access. Each vision feature requests and releases the camera through this manager. Use Kotlin coroutines with a `Mutex` to prevent concurrent access. | **Resolved** — SUB-PR-0012 added for CameraSessionManager. SUB-PR-0009/0010/0011-AND all reference CameraSessionManager. |
| PC-AND-02 | **Shared auth interceptor coupling** — SUB-PR-0001-AND, SUB-CW-0001-AND, SUB-MM-0006-AND, and SUB-RA-0004-AND all share `AuthInterceptor.kt`. The interceptor handles token refresh, but if multiple concurrent API calls trigger refresh simultaneously, duplicate refresh requests are sent. | SUB-PR-0001-AND, SUB-CW-0001-AND, SUB-MM-0006-AND, SUB-RA-0004-AND | Medium | Implement token refresh synchronization in `AuthInterceptor.kt`: use a `Mutex` to serialize refresh attempts. The first caller performs the refresh; subsequent callers wait and reuse the new token. OkHttp's `Authenticator` interface supports this pattern natively. | **Resolved** — SUB-PR-0001-AND updated with Mutex-based token refresh synchronization requirement. |
| PC-AND-03 | **Camera contention expansion for dermoscopy** — PC-AND-01 was resolved for three camera-using features (wound, ID verification, OCR). SUB-PR-0013-AND adds a fourth feature (dermoscopic image capture) that also requires CameraSessionManager access. Additionally, dermoscopic imaging may require different camera configuration (macro mode, higher resolution, specific white balance) than the other vision features. The CameraSessionManager state machine does not specify feature-specific camera configuration profiles. | SUB-PR-0013-AND vs SUB-PR-0009-AND, SUB-PR-0010-AND, SUB-PR-0011-AND | Medium | Update CameraSessionManager to support feature-specific camera configuration profiles: each feature passes a `CameraProfile` (resolution, focus mode, white balance) when requesting camera access. The manager applies the profile during the BINDING phase. Update SUB-PR-0012 to reference four features (ties to DC-PR-05 priority order expansion). | Open |

### AI Infrastructure (AI) — 1 conflict

| ID | Conflict | Requirements | Severity | Resolution | Status |
|---|---|---|---|---|---|
| PC-AI-01 | **Model version parity between server and mobile** — SUB-PR-0013-AI deploys EfficientNet-B4 via ONNX Runtime on the server. SUB-PR-0013-AND deploys MobileNetV3 via TFLite on Android. These are architecturally different models that may produce divergent classifications for the same input image. ADR-0013 (model lifecycle) covers single-model versioning but does not specify cross-platform model version parity. A clinician receiving a "low risk" triage on-device that is later reclassified as "high risk" by the server undermines trust in the system. | SUB-PR-0013-AI vs SUB-PR-0013-AND | High | Define a model compatibility matrix in the model-manifest.json (ADR-0013): server and mobile models must be trained on the same ISIC dataset version and validated to produce concordant top-1 predictions on a reference test set (target: ≥90% agreement rate). The on-device result must be labeled "preliminary triage — pending server confirmation" and never presented as a final diagnosis. When the server classification becomes available, if it differs from the on-device result, surface a notification to the clinician. | Open |

**Total cross-platform conflicts: 15 (12 resolved, 3 open)**

---

## 5. Race Condition Analysis

Race conditions identified per platform where concurrent operations can produce incorrect, inconsistent, or unsafe states.

### Backend (BE) — 12 race conditions

| ID | Race Condition | Requirements | Severity | Mitigation | Status |
|---|---|---|---|---|---|
| RC-BE-01 | **Concurrent patient update (lost update)** — Two clinicians open the same patient record simultaneously. Both read version N, make different edits, and submit. The second write silently overwrites the first with no conflict detection. Neither `SUB-PR-0003-BE` nor the patient model implements optimistic locking. | SUB-PR-0003-BE | High | Add a `version` column (integer, auto-increment on update) to the patient model. The update endpoint must include the version in the request body. If the version in the database doesn't match, return 409 Conflict. This is standard optimistic concurrency control. | **Resolved** — SUB-PR-0003-BE updated to require optimistic locking via version column with 409 on mismatch. |
| RC-BE-02 | **Concurrent encounter status transition** — Two users simultaneously transition the same encounter from "scheduled" to "in_progress." Both read the current status as "scheduled," both pass the transition validation, and both write "in_progress." The audit trail shows two transitions but only one is semantically valid. | SUB-CW-0003-BE, SUB-CW-0007-BE | High | Use `SELECT ... FOR UPDATE` when reading encounter status before transitioning. This serializes concurrent transitions at the database row level. Alternatively, use an optimistic locking approach (version column) as described in RC-BE-01. | **Resolved** — SUB-CW-0003-BE and SUB-CW-0007-BE updated to require `SELECT ... FOR UPDATE` serialization. |
| RC-BE-03 | **Prescription saved before interaction check completes** — A physician submits a new prescription. The backend starts an async interaction check (SUB-MM-0001-BE) but also saves the prescription immediately (SUB-MM-0008-BE). If the interaction check finds a contraindication, the prescription is already persisted and potentially visible to pharmacists. | SUB-MM-0001-BE vs SUB-MM-0008-BE | Critical | The interaction check must complete before the prescription is committed to the database. Implement this as a synchronous pre-save hook: `validate → check interactions → save`. If the check finds a contraindicated interaction, reject the save. For major/moderate interactions, save with a "pending_review" status and require prescriber acknowledgment. | **Resolved** — SUB-MM-0001-BE updated with synchronous pre-save hook. SUB-MM-0008-BE updated to block prescription commit until interaction check completes. |
| RC-BE-04 | **Audit log timestamp ordering ambiguity** — Concurrent requests to different endpoints (e.g., patient read + encounter create) produce audit entries with identical or very close timestamps. When querying the audit log (SUB-RA-0003-BE), the order of operations is ambiguous. | SUB-PR-0005-BE, SUB-CW-0004-BE, SUB-MM-0004-BE | Low | Use a monotonically increasing sequence (database serial/bigserial on `audit_log.id`) as the primary ordering key rather than timestamp alone. The current schema already uses integer PK for audit_log, which provides this ordering. Document that ordering is by ID, not timestamp. | **Resolved** — Existing schema already provides monotonic ordering via integer PK. No requirements change needed; audit event catalog (PC-BE-03) formalizes this. |
| RC-BE-05 | **Duplicate email TOCTOU** — The patient service checks email uniqueness with a SELECT before INSERT. Between the check and the insert, another concurrent request may insert a patient with the same email. The check passes for both, but the second insert violates the unique constraint. | SUB-PR-0006-BE, SUB-PR-0003-BE | Medium | The database unique constraint on `email` is the authoritative enforcement. The service-layer pre-check is a UX optimization (fast feedback), not a safety mechanism. The service must catch `IntegrityError` from the database on insert/update and translate it to HTTP 409. Current implementation handles this correctly. | **Resolved** — SUB-PR-0006 and SUB-PR-0006-BE updated to specify IntegrityError → 409 as authoritative enforcement. |
| RC-BE-06 | **Patient deactivation during active encounter** — An administrator deactivates a patient (SUB-PR-0003-BE) while a physician has an in_progress encounter for that patient (SUB-CW-0003-BE). The encounter references a now-inactive patient. Should the encounter be auto-cancelled? Should deactivation be blocked? | SUB-PR-0003-BE vs SUB-CW-0003-BE | High | Block patient deactivation if the patient has any encounter in non-terminal status (scheduled or in_progress). Return 409 with a message listing the blocking encounter IDs. The administrator must first complete or cancel the open encounters, then deactivate. | **Resolved** — SUB-PR-0003 and SUB-PR-0003-BE updated to require blocking deactivation when non-terminal encounters exist (return 409). |
| RC-BE-07 | **Prescription status change during interaction check** — A pharmacist cancels a prescription (SUB-MM-0008-BE) while an interaction check (SUB-MM-0001-BE) is running against the patient's active medications. The interaction check may include or exclude the cancelled prescription depending on when the cancellation commits. | SUB-MM-0001-BE vs SUB-MM-0008-BE | Medium | The interaction check should read active medications within a single database transaction with `REPEATABLE READ` isolation. This provides a consistent snapshot regardless of concurrent status changes. The check result reflects the state at check-start time. | **Resolved** — SUB-MM-0001-BE updated to require `REPEATABLE READ` isolation for interaction checks. |
| RC-BE-08 | **Concurrent refill decrement** — Two pharmacy terminals simultaneously process a refill for the same prescription (SUB-MM-0009-BE). Both read `refills_remaining = 1`, both decrement to 0, and both dispense. The patient receives one extra fill. | SUB-MM-0009-BE | Critical | Use an atomic update: `UPDATE prescriptions SET refills_remaining = refills_remaining - 1 WHERE id = ? AND refills_remaining > 0`. Check the affected row count — if 0, the refill was already claimed. Do not read-then-write in application code. | **Resolved** — SUB-MM-0009 and SUB-MM-0009-BE updated to require atomic update with row-count check. |
| RC-BE-09 | **Concurrent prompt update (version conflict)** — Two administrators simultaneously edit the same prompt. Both read the current text, make different changes, and submit. SUB-PM-0004's auto-versioning means both edits produce new versions (N+1 and N+2) rather than overwriting each other. However, without `FOR UPDATE` serialization, both could read `MAX(version) = N` and attempt to create version `N+1`, causing a unique constraint violation. | SUB-PM-0004-BE | Medium | The `SELECT MAX(version) ... FOR UPDATE` serialization specified in SUB-PM-0004-BE prevents this race. The first transaction acquires the lock and creates version N+1; the second transaction waits, reads N+1, and creates version N+2. Both edits are preserved as separate versions. | **Resolved** — SUB-PM-0004-BE specifies `FOR UPDATE` serialization. Auto-versioning preserves both edits. |
| RC-BE-10 | **LLM comparison timeout under load** — Multiple administrators simultaneously request prompt version comparisons (SUB-PM-0007-BE). Each request calls the Anthropic Claude API. Under load, API responses may exceed the expected latency, consuming server threads/connections and degrading other endpoints. | SUB-PM-0007-BE | Medium | Apply a 30-second timeout on the LLM API call. Implement rate limiting on the comparison endpoint (e.g., 10 requests per minute per user). Return 504 Gateway Timeout if the LLM call exceeds 30 seconds. Return 429 Too Many Requests if rate limit is exceeded. | **Resolved** — SUB-PM-0007-BE specifies 30-second timeout and rate limiting. |
| RC-BE-11 | **Concurrent lesion upload for same patient and anatomical site** — Two clinicians simultaneously upload dermoscopic images for the same patient at the same anatomical site (SUB-PR-0013-BE). Both uploads create new `lesion_image` records. The longitudinal tracking system (SUB-PR-0016-BE, ADR-0019) computes `change_score` by comparing the current embedding against the most recent prior embedding. With near-simultaneous uploads, the "prior" reference is ambiguous — the second upload may use the first upload (captured seconds ago) as its prior, producing a meaningless near-zero change_score rather than comparing against the clinically relevant prior assessment. | SUB-PR-0016-BE, SUB-PR-0013-BE | Medium | Serialize lesion assessment creation per (patient_id, anatomical_site) using `SELECT ... FOR UPDATE` on the lesion identity row when computing change_score. The second upload waits for the first to complete, ensuring a consistent "prior" reference. Additionally, enforce a configurable minimum interval between assessments at the same site (default: 24 hours) — return 409 if a second upload occurs within the interval unless the clinician explicitly overrides. | Open |
| RC-BE-12 | **CDS circuit breaker during upload pipeline** — The lesion upload pipeline (SUB-PR-0013-BE) performs: validate image → encrypt with AES-256-GCM → store in PostgreSQL → forward to CDS service → receive classification → store results. If the CDS circuit breaker (ADR-0018) transitions from CLOSED to OPEN between the "store image" and "forward to CDS" steps, the encrypted image is persisted but no classification is generated. The endpoint returns 503 to the client. A client retry re-uploads the same image, creating a duplicate encrypted blob with no deduplication mechanism. | SUB-PR-0013-BE | Medium | Wrap the entire upload pipeline in a single database transaction. If the CDS call fails (timeout or circuit open), rollback the image storage — no orphaned blobs. The client retries the full upload. Additionally, implement an idempotency key: the upload request includes a client-generated UUID in an `X-Idempotency-Key` header. The backend deduplicates on this key — if the same key is retried, return the existing result (or retry the CDS call if the previous attempt failed at that stage). | Open |

### Web Frontend (WEB) — 2 race conditions

| ID | Race Condition | Requirements | Severity | Mitigation | Status |
|---|---|---|---|---|---|
| RC-WEB-01 | **Token refresh thundering herd** — Multiple API calls fail with 401 simultaneously (token expired). Each call independently triggers a token refresh via `lib/auth.ts`. Multiple refresh requests hit the backend concurrently, but only the first succeeds — subsequent ones may use an invalidated refresh token. | SUB-PR-0001-WEB, SUB-CW-0001-WEB, SUB-MM-0006-WEB, SUB-RA-0004-WEB | High | Implement a token refresh lock: a single Promise that all concurrent callers await. The first caller initiates the refresh; subsequent callers queue behind the same Promise and receive the new token when the refresh completes. Use a module-scoped `refreshPromise` variable. | **Resolved** — SUB-PR-0001-WEB updated to require token refresh lock via single Promise serialization. |
| RC-WEB-02 | **Stale form submission (lost update)** — A clinician opens a patient edit form, reads version N. Another clinician updates the same patient to version N+1. The first clinician submits their edit, unknowingly overwriting version N+1's changes. No optimistic concurrency check exists on the frontend. | SUB-PR-0003-WEB | Medium | Include the patient `version` (or `updated_at`) in the edit form's hidden state. On submission, the backend (per RC-BE-01) rejects the update with 409 if the version doesn't match. The frontend must handle 409 by showing a conflict resolution dialog or prompting the user to reload. | **Resolved** — SUB-PR-0003-WEB updated to include version in form state and handle 409 with conflict resolution dialog. |

### Android (AND) — 3 race conditions

| ID | Race Condition | Requirements | Severity | Mitigation | Status |
|---|---|---|---|---|---|
| RC-AND-01 | **Camera lifecycle race** — The user rapidly switches between wound assessment (SUB-PR-0009-AND), patient ID verification (SUB-PR-0010-AND), and document OCR (SUB-PR-0011-AND). CameraX's `unbind` from the previous feature may not complete before `bind` for the next feature. This causes `IllegalStateException` or a black camera preview. | SUB-PR-0009-AND, SUB-PR-0010-AND, SUB-PR-0011-AND | High | Use a `CameraSessionManager` with a state machine: `IDLE → BINDING → ACTIVE → UNBINDING → IDLE`. All camera operations go through this manager. Transitions are serialized via a coroutine `Mutex`. Feature switching requests queue behind the current unbind operation. | **Resolved** — SUB-PR-0012 defines CameraSessionManager. SUB-PR-0009/0010/0011-AND all reference it. |
| RC-AND-02 | **Offline-sync conflict** — The Android app supports offline data entry (SUB-PR-0003-AND, SUB-CW-0003-AND). While offline, a clinician creates or modifies records. When connectivity restores, the sync pushes local changes to the backend, which may conflict with changes made by other users during the offline period. | SUB-PR-0003-AND, SUB-CW-0003-AND | High | Implement last-write-wins with conflict detection: each sync request includes the `version` or `updated_at` from when the record was last fetched. The backend returns 409 for conflicts. The Android app maintains a conflict queue and presents a resolution UI showing local vs server versions. | **Resolved** — SUB-PR-0003-AND and SUB-CW-0003-AND updated with offline-sync conflict resolution requirements. |
| RC-AND-03 | **Offline TFLite vs server classification discrepancy** — SUB-PR-0013-AND performs on-device TFLite classification (MobileNetV3) when offline and syncs the image to the backend when connectivity restores. The backend re-classifies using EfficientNet-B4 (SUB-PR-0013-BE), which may produce a different top-1 prediction or significantly different confidence scores. If the clinician took action based on the on-device triage result (e.g., reassuring a patient that a lesion is benign) and the server later returns a higher-risk classification, the discrepancy creates a patient safety and liability concern. | SUB-PR-0013-AND | High | The on-device classification result must be displayed with a clear "preliminary triage" label and a warning that "server confirmation is pending." Store the on-device classification locally with a `confirmed = false` flag. When the server classification returns, compare results. If the top-1 prediction or risk level differs, fire a push notification to the clinician: "Classification updated for [patient] — please review." The patient-facing encounter record must never show the on-device result as a final classification. Ties to PC-AI-01 model parity requirements. | Open |

**Total race conditions: 17 (14 resolved, 3 open)**

---

## 6. Summary

Of 49 total conflicts and race conditions, 40 have been resolved at the requirements level. 9 new open conflicts were identified in v1.5 (2026-02-21) from the Dermatology CDS requirements (SUB-PR-0013–0016, SUB-RA-0008, SYS-REQ-0012). The requirements documents (SYS-REQ.md, SUB-PR.md, SUB-CW.md, SUB-MM.md, SUB-RA.md, SUB-PM.md) have been updated to incorporate each resolved conflict. Implementation of the updated requirements is tracked by the individual requirement statuses in each SUB-*.md file.

| Category | Count | Critical | High | Medium | Low | Resolved |
|---|---|---|---|---|---|---|
| Intra-domain conflicts | 17 | 0 | 7 | 8 | 2 | **14/17** |
| Cross-platform conflicts | 15 | 0 | 4 | 8 | 3 | **12/15** |
| Race conditions | 17 | 2 | 7 | 7 | 1 | **14/17** |
| **Total** | **49** | **2** | **18** | **23** | **6** | **40/49** |

### Open Conflicts — Dermatology CDS (9 open, resolve before implementation)

The following conflicts were introduced by SUB-PR-0013–0016 and SUB-RA-0008 (SYS-REQ-0012). Resolve these at the requirements level before beginning implementation of the Dermatology CDS feature.

**High — resolve before any derm implementation begins:**
1. **DC-PR-06** — Lesion audit trail traceability gap (SUB-PR-0013–0016 vs SYS-REQ-0003). Must add audit action strings and trace lesion endpoints to SYS-REQ-0003.
2. **DC-PR-07** — Encounter-patient cross-reference validation (SUB-PR-0013 vs SUB-CW-0008). Must validate encounter.patient_id matches upload patient_id.
3. **PC-AI-01** — Model version parity between server EfficientNet-B4 and mobile MobileNetV3 (SUB-PR-0013-AI vs SUB-PR-0013-AND). Must define compatibility matrix and label on-device results as preliminary.
4. **RC-AND-03** — Offline TFLite vs server classification discrepancy (SUB-PR-0013-AND). Must surface classification updates via push notification.

**Medium — resolve before platform-specific implementation:**
5. **DC-PR-05** — AI inference queuing scope expansion (SUB-PR-0012 vs SUB-PR-0013). Must add dermoscopy to CameraSessionManager priority order.
6. **PC-BE-08** — Encryption module path divergence (SUB-PR-0013-BE vs SUB-PR-0004-BE). Must unify on `services/encryption_service.py`.
7. **PC-AND-03** — Camera contention expansion for dermoscopy (SUB-PR-0013-AND). Must add camera configuration profiles.
8. **RC-BE-11** — Concurrent lesion upload for same patient/site (SUB-PR-0016-BE). Must serialize with `FOR UPDATE` and enforce minimum interval.
9. **RC-BE-12** — CDS circuit breaker during upload pipeline (SUB-PR-0013-BE). Must wrap pipeline in transaction and implement idempotency key.

### Implementation Priority (requirements resolved, code implementation pending)

The following items have been resolved in the requirements but require code changes. Prioritized by severity:

**Critical — implement before any production deployment:**
1. **RC-BE-03** — Synchronous pre-save interaction check (SUB-MM-0001-BE, SUB-MM-0008-BE).
2. **RC-BE-08** — Atomic refill decrement (SUB-MM-0009-BE).

**High — target next sprint:**
1. **DC-PR-01 / PC-BE-01** — Encryption migration to AES-256-GCM (SUB-PR-0004-BE).
2. **RC-BE-01** — Optimistic locking via version column (SUB-PR-0003-BE).
3. **RC-BE-02** — `SELECT ... FOR UPDATE` for encounter transitions (SUB-CW-0003-BE, SUB-CW-0007-BE).
4. **RC-BE-06** — Block deactivation during active encounters (SUB-PR-0003-BE).
5. **RC-WEB-01** — Token refresh lock (SUB-PR-0001-WEB).
6. **RC-AND-01 / PC-AND-01** — CameraSessionManager singleton (SUB-PR-0012, SUB-PR-0009/0010/0011-AND).
7. **RC-AND-02** — Offline-sync conflict resolution (SUB-PR-0003-AND, SUB-CW-0003-AND).

---

## Appendix A: Conflict Cross-Reference to Requirements

Quick lookup: which requirement IDs are involved in conflicts or race conditions.

| Requirement | Conflict/Race IDs |
|---|---|
| SYS-REQ-0001 | PC-BE-02, PC-BE-06, PC-WEB-01, PC-WEB-03, PC-AND-02, RC-WEB-01 |
| SYS-REQ-0002 | DC-PR-01, PC-BE-01, PC-BE-08 |
| SYS-REQ-0003 | PC-BE-03, PC-BE-07, DC-RA-01, RC-BE-04, DC-PR-06 |
| SYS-REQ-0005 | PC-BE-04, DC-RA-01 |
| SYS-REQ-0006 | DC-MM-01, PC-BE-05, RC-BE-03 |
| SYS-REQ-0011 | DC-PM-01, DC-PM-02, DC-PM-03, RC-BE-09, RC-BE-10 |
| SYS-REQ-0012 | DC-PR-05, DC-PR-06, DC-PR-07, PC-BE-08, PC-AND-03, PC-AI-01, RC-BE-11, RC-BE-12, RC-AND-03 |
| SUB-PR-0003 | DC-PR-02, DC-PR-04, RC-BE-01, RC-BE-06, RC-WEB-02, RC-AND-02 |
| SUB-PR-0004 | DC-PR-01, PC-BE-01, PC-BE-08 |
| SUB-PR-0006 | DC-PR-04, RC-BE-05 |
| SUB-PR-0009 | DC-PR-03, PC-AND-01, RC-AND-01, PC-AND-03 |
| SUB-PR-0010 | DC-PR-03, PC-AND-01, RC-AND-01, PC-AND-03 |
| SUB-PR-0011 | DC-PR-03, PC-AND-01, RC-AND-01, PC-AND-03 |
| SUB-PR-0012 | DC-PR-03, DC-PR-05, PC-AND-01, PC-AND-03, RC-AND-01 |
| SUB-PR-0013 | DC-PR-05, DC-PR-06, DC-PR-07, PC-BE-08, PC-AND-03, PC-AI-01, RC-BE-11, RC-BE-12, RC-AND-03 |
| SUB-PR-0014 | DC-PR-06 |
| SUB-PR-0015 | DC-PR-06 |
| SUB-PR-0016 | DC-PR-06, RC-BE-11 |
| SUB-CW-0003 | DC-CW-01, DC-CW-02, DC-CW-03, RC-BE-02, RC-BE-06, RC-AND-02 |
| SUB-CW-0005 | DC-CW-03 |
| SUB-CW-0007 | DC-CW-01, RC-BE-02 |
| SUB-CW-0008 | DC-PR-07 |
| SUB-MM-0001 | DC-MM-01, PC-BE-05, RC-BE-03, RC-BE-07 |
| SUB-MM-0003 | DC-MM-01, PC-BE-01 |
| SUB-MM-0007 | DC-MM-03 |
| SUB-MM-0008 | DC-MM-02, DC-MM-03, RC-BE-03, RC-BE-07 |
| SUB-MM-0009 | DC-MM-02, RC-BE-08 |
| SUB-PM-0001 | PC-BE-06, PC-WEB-03 |
| SUB-PM-0003 | DC-PM-01 |
| SUB-PM-0004 | DC-PM-02, RC-BE-09 |
| SUB-PM-0005 | PC-BE-07 |
| SUB-PM-0007 | DC-PM-03, RC-BE-10 |
| SUB-RA-0003 | DC-RA-01, RC-BE-04 |
| SUB-RA-0005 | DC-RA-01, PC-BE-04 |
