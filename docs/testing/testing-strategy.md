# Testing Strategy

**Document ID:** PMS-TST-STRATEGY-001
**Version:** 1.2
**Date:** 2026-02-16

---

## 1. Testing Levels

The PMS uses a three-level testing pyramid, each level mapped to requirements:

```
         ┌──────────┐
         │  System  │   End-to-end, cross-component
         │  Tests   │   Traces to: SYS-REQ-*
         ├──────────┤
         │Integration│  API + database, cross-module
         │  Tests    │  Traces to: SUB-*-* (multi-module)
         ├──────────┤
         │   Unit   │   Single function/class
         │  Tests   │   Traces to: SUB-*-* (single req)
         └──────────┘
```

| Level | Scope | Runs In | Frequency | Traces To |
|---|---|---|---|---|
| Unit | Single function, class, or component | Each repo (`pytest`, `vitest`, `./gradlew test`) | Every commit | Individual SUB-*-* requirements |
| Integration | API endpoints with test database | pms-backend (pytest + httpx) | Every PR | Multiple SUB-*-* requirements |
| System | Full stack: backend + frontend/Android | CI pipeline (Docker Compose) | Nightly + pre-release | SYS-REQ-* requirements |

---

## 2. Test Naming Convention

Test IDs follow this format:

```
TST-{domain}-{NNNN}-{platform}       # Platform-scoped test (preferred)
TST-{domain}-{NNNN}-{platform}-{a}   # Platform-scoped sub-case (e.g., TST-PR-0003-BE-a)
TST-{domain}-{NNNN}                  # Domain-level test (legacy, still valid)
TST-SYS-{NNNN}                       # System-level tests
TST-AUTH-{NNNN}                       # Cross-cutting auth tests
```

Platform codes: `BE` (Backend), `WEB` (Web Frontend), `AND` (Android), `AI` (AI Infrastructure).

> **Deprecation notice (v1.2):** The flat `TST-FE-{NNNN}` and `TST-AND-{NNNN}` prefixes are deprecated. New tests should use platform-scoped IDs (e.g., `TST-PR-0001-WEB` instead of `TST-FE-0001`). Existing test IDs are preserved with alias mappings in the [Traceability Matrix](traceability-matrix.md#test-id-migration-note).

Every test file must include requirement annotations:

### Python (pms-backend)

```python
# @requirement SUB-MM-0001
# @requirement SUB-MM-0002
# @verification-method Test

def test_interaction_check_within_5_seconds(client):
    """TST-MM-0001: Drug interaction check completes within 5 seconds."""
    ...
```

### TypeScript (pms-frontend)

```typescript
// @requirement SUB-PR-0003
// @verification-method Test

describe("Patient list", () => {
  it("TST-PR-0003: returns empty list when no patients exist", async () => {
    ...
  });
});
```

### Kotlin (pms-android)

```kotlin
/**
 * @requirement SUB-PR-0003
 * @verification-method Test
 */
@Test
fun `TST-AND-0001 PatientEntity roundtrip mapping`() { ... }
```

---

## 3. Requirement-to-Test Mapping Process

### When Implementing a Requirement

1. **Read** the requirement in `docs/specs/requirements/SUB-*.md`.
2. **Implement** the feature using speckit: `/specify` → `/plan` → `/speckit.tasks`.
3. **Write test(s)** with `@requirement` annotation linking to the **platform requirement ID** (e.g., `SUB-PR-0003-BE`). Use the `TST-{domain}-{NNNN}-{platform}` naming convention for new test IDs.
4. **Update** the Platform Decomposition table in the subsystem requirements doc.
5. **Update** the Backward Traceability section in `docs/testing/traceability-matrix.md`.

### When Running Tests

1. **Run** the test suite and capture results.
2. **Record** a new Test Run Log entry in the traceability matrix.
3. **Update** the "Last Result" and "Run ID" for each affected test case.
4. **Regenerate** the Coverage Summary.
5. **Commit** all evidence: `git add docs/specs/ docs/testing/ && git commit -m "evidence: test run RUN-YYYY-MM-DD-NNN"`.

---

## 4. Subsystem Testing (Per Repository)

### pms-backend

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=pms --cov-report=html

# Run specific subsystem
pytest tests/test_patients.py -v         # SUB-PR
pytest tests/test_encounters.py -v       # SUB-CW
pytest tests/test_medications.py -v      # SUB-MM
pytest tests/test_auth.py -v             # SYS-REQ-0001
```

### pms-frontend

```bash
# Run all tests
npm run test:run

# Run with coverage
npx vitest run --coverage

# Run specific test file
npx vitest run __tests__/auth.test.ts
```

### pms-android

```bash
# Unit tests
./gradlew test

# Instrumented tests (requires emulator)
./gradlew connectedAndroidTest
```

---

## 5. System-Level Testing

System tests verify end-to-end behavior across components. They run against the full stack (backend + database + client).

### Environment Setup

```bash
# Start the full stack
docker compose up -d

# Run system tests
pytest tests/system/ -v --base-url=http://localhost:8000
```

### System Test Cases

| Test ID | Requirement | Description | Components |
|---|---|---|---|
| TST-SYS-0001 | SYS-REQ-0001 | Login via API, use token to access patient data, verify rejection without token | Backend + DB |
| TST-SYS-0002 | SYS-REQ-0002 | Create patient with SSN, verify SSN is encrypted in DB, verify decryption on read | Backend + DB |
| TST-SYS-0003 | SYS-REQ-0003 | Perform CRUD operations, verify audit_logs table has complete entries for each | Backend + DB |
| TST-SYS-0005 | SYS-REQ-0005 | Login as each role, verify access granted/denied per RBAC rules | Backend + DB |
| TST-SYS-0006 | SYS-REQ-0006 | Create a prescription with known interaction, verify warning returned within 5s | Backend + DB |
| TST-SYS-0007 | SYS-REQ-0007 | Run load test with 500 concurrent requests, verify p99 < 2s | Backend + DB |
| TST-SYS-0008 | SYS-REQ-0008 | Build and serve frontend, navigate all pages, verify no console errors | Frontend + Backend |
| TST-SYS-0009 | SYS-REQ-0009 | Build Android APK, launch on emulator, verify all screens render | Android + Backend |
| TST-SYS-0010 | SYS-REQ-0010 | Build all Dockerfiles, verify containers start and health checks pass | All repos |

---

## 6. Test Run Records

Every test execution produces a **run record** committed to the repository:

```
docs/test-evidence/
├── RUN-2026-02-15-001.md      # Backend initial scaffold tests
├── RUN-2026-02-15-002.md      # Frontend initial scaffold tests
└── ...
```

### Run Record Format

```markdown
# Test Run: RUN-YYYY-MM-DD-NNN

| Field | Value |
|---|---|
| Date | YYYY-MM-DD HH:MM UTC |
| Repository | pms-backend / pms-frontend / pms-android |
| Commit | SHA |
| Branch | main / feature/... |
| Runner | local / CI (GitHub Actions) |

## Results

| Test Case | Requirement | Result | Duration |
|---|---|---|---|
| TST-PR-0003 | SUB-PR-0003 | PASS | 0.01s |
| ... | ... | ... | ... |

## Summary

- Total: N
- Passed: N
- Failed: N
- Skipped: N
```

---

## 7. Consistency Verification

Before any release, run the consistency check:

1. **Every requirement** in `SYS-REQ.md` and `SUB-*.md` must appear in the traceability matrix.
2. **Every test case** in the traceability matrix must exist in the codebase.
3. **Every requirement** must have at least one test case (coverage = 100%).
4. **Every test case** must have a recent run record with a PASS result.

Use `/analyze` in speckit to automate this check:

```bash
/analyze
# "Verify that all requirements in docs/specs/requirements/ are covered
# by test cases in the traceability matrix. Flag any requirements with
# no tests or with failing tests."
```

Commit the analysis output as evidence:

```bash
git add docs/analyze/
git commit -m "evidence: consistency verification for release candidate"
git push
```
