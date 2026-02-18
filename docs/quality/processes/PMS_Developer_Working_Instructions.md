# PMS Developer Working Instructions

**Patient Management System — Development Process Guide**

Version 2.1 | Last Updated: February 2026

---

## Table of Contents

- [Compliance Evidence Storage Policy](#compliance-evidence-storage-policy)
- [Section 1: Project Structure & First-Time Setup](#section-1-project-structure--first-time-setup)
- [Section 2: The Four-Phase Development Process](#section-2-the-four-phase-development-process)
- [Section 3: Implementing a Feature (Worked Example)](#section-3-implementing-a-feature-worked-example)
- [Section 4: A Day in the Life](#section-4-a-day-in-the-life-of-a-pms-developer)
- [Quick Reference](#quick-reference)
- [Troubleshooting](#troubleshooting)

---

## Compliance Evidence Storage Policy

> **This policy applies to all PMS developers and CI/CD pipelines.**

### Authoritative Evidence Store

The **GitHub repository** is the authoritative, permanent source of truth for all compliance evidence. Every piece of evidence — test reports, quality scans, security results, traceability matrices, coverage reports, and review summaries — **must be committed to the repository**.

- **GitHub repos** = permanent, versioned, tamper-evident (git history provides an immutable audit trail)
- **`docs/` submodule** = shared documentation layer (markdown files accessible from all repos)

### Evidence Commitment Rule

Every evidence-generating step must follow this sequence:

1. **Generate** the evidence artifact (report, scan result, matrix, etc.)
2. **`git add`** the artifact to staging
3. **`git commit`** with a descriptive message referencing requirement IDs
4. **`git push`** to the remote repository

### Retention

HIPAA requires a minimum **6-year retention period** for compliance documentation. GitHub's permanent git history satisfies this requirement. GitHub Actions artifacts (90-day retention) are **not** a substitute for committed evidence files.

---

# Section 1: Project Structure & First-Time Setup

## 1.1 Multi-Repository Architecture

The PMS is split across three implementation repositories plus a shared documentation repository:

```
GitHub Organization
├── demo (docs)            # Shared documentation, specs, and requirements
├── pms-backend            # Python/FastAPI REST API
├── pms-frontend           # Next.js/TypeScript web UI
└── pms-android            # Kotlin/Jetpack Compose mobile app
```

Each implementation repo includes the `demo` repo as a Git submodule at `docs/`, so all three repos share the same specifications, requirements, and traceability matrix.

### Key Directories in `docs/` (the shared submodule)

```
docs/
├── specs/                           # Specifications & requirements
│   ├── system-spec.md               # System-level specification
│   ├── requirements/
│   │   ├── SYS-REQ.md              # System requirements (SYS-REQ-0001–0010)
│   │   ├── SUB-PR.md               # Patient Records subsystem requirements
│   │   ├── SUB-CW.md               # Clinical Workflow subsystem requirements
│   │   ├── SUB-MM.md               # Medication Management subsystem requirements
│   │   ├── SUB-RA.md               # Reporting & Analytics subsystem requirements
│   │   └── traceability-matrix.md  # RTM: forward + backward traceability
│   └── testing-strategy.md          # Test levels, naming, run records
├── architecture/                    # Architecture Decision Records (ADRs)
├── features/                        # Implementation details
├── api/                             # API contracts
├── config/                          # Setup guides, dependencies
├── test-evidence/                   # Test run records (RUN-YYYY-MM-DD-NNN.md)
└── index.md                         # Table of contents
```

## 1.2 System Prerequisites

- **Operating System:** macOS 13+, Ubuntu 22.04+, or Windows 11 with WSL2
- **RAM:** Minimum 16 GB
- **Disk:** At least 50 GB free space

## 1.3 Install Core Development Tools

### Python (pms-backend)

```bash
# Install Python 3.12+ (recommended via pyenv)
pyenv install 3.12
pyenv global 3.12
python --version   # Should show 3.12.x
```

### Node.js (pms-frontend)

```bash
# Install Node.js 24 LTS (recommended via nvm)
nvm install 24
nvm use 24
node --version   # Should show v24.x.x
```

### Android Development (pms-android)

```bash
# Install Android Studio (includes SDK, emulator, Gradle)
# macOS: brew install --cask android-studio
# Or download from https://developer.android.com/studio
```

### Common Tools

```bash
# Git
brew install git   # macOS
git config --global user.name "Your Name"
git config --global user.email "your.email@company.com"

# GitHub CLI
brew install gh
gh auth login

# Docker
brew install --cask docker   # macOS

# Claude Code CLI
npm install -g @anthropic-ai/claude-code

# GitHub Spec Kit
npm install -g @github/specify
```

## 1.4 Clone All Repositories

```bash
# Clone the docs repo (also used standalone for spec work)
gh repo clone ammar-utexas/demo
cd demo && cd ..

# Clone each implementation repo (docs submodule included)
gh repo clone ammar-utexas/pms-backend
cd pms-backend && git submodule update --init --recursive && cd ..

gh repo clone ammar-utexas/pms-frontend
cd pms-frontend && git submodule update --init --recursive && cd ..

gh repo clone ammar-utexas/pms-android
cd pms-android && git submodule update --init --recursive && cd ..
```

> **Known Issue: Submodule URL Mismatch**
>
> The `.gitmodules` files in each implementation repo reference the docs submodule using a custom SSH host alias (`git@github.com-utexas:ammar-utexas/demo.git`). If your SSH config does not include a `github.com-utexas` host entry, `git submodule update --init --recursive` will fail with:
>
> ```
> ssh: Could not resolve hostname github.com-utexas: nodename nor servname provided, or not known
> ```
>
> **Fix:** Override the submodule URL locally in each repo before initializing:
>
> ```bash
> # Run this in each implementation repo (pms-backend, pms-frontend, pms-android)
> git config submodule.docs.url git@github.com:utexas-demo/demo.git
> git submodule update --init --recursive
> ```
>
> If you use multiple GitHub accounts with SSH host aliases (see [Troubleshooting: SSH Multi-Account Setup](#ssh-multi-account-setup)), replace `github.com` with your alias (e.g., `github.com-julmak`).

## 1.5 Set Up Each Project

### Start PostgreSQL via Docker

The backend requires a PostgreSQL database. Start one before setting up the backend:

```bash
# Ensure Docker Desktop is running first (macOS: open -a Docker)
docker run -d \
  --name pms-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=pms \
  -p 5432:5432 \
  postgres:16

# Wait for PostgreSQL to be ready
docker exec pms-postgres pg_isready -U postgres

# Create the test database (required by pytest — see tests/conftest.py)
docker exec pms-postgres psql -U postgres -c "CREATE DATABASE pms_test;"
```

> **Important:** The test suite connects to a separate `pms_test` database (hardcoded in `tests/conftest.py`), not the main `pms` database. If you skip this step, all backend tests will fail with:
>
> ```
> asyncpg.exceptions.InvalidCatalogNameError: database "pms_test" does not exist
> ```

### pms-backend

```bash
cd pms-backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Edit .env with your local database credentials

# Verify
pytest -v                                    # All tests pass
python -m uvicorn pms.main:app --reload      # http://localhost:8000/docs
```

> **Known Issue: pydantic-settings `extra` Fields Error**
>
> With newer versions of pydantic-settings (v2.13+), both `Settings` and `FeatureFlags` classes read from the same `.env` file but reject each other's variables. You will see errors like:
>
> ```
> pydantic_core._pydantic_core.ValidationError: 5 validation errors for FeatureFlags
> database_url
>   Extra inputs are not permitted
> ```
>
> **Fix:** Add `"extra": "ignore"` to the `model_config` in both files:
>
> - `src/pms/config.py` — change `model_config` to:
>   ```python
>   model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}
>   ```
> - `src/pms/feature_flags.py` — change `model_config` to:
>   ```python
>   model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}
>   ```

### pms-frontend

```bash
cd pms-frontend
npm install
cp .env.example .env.local
# Edit .env.local with NEXT_PUBLIC_API_URL=http://localhost:8000

# Verify
npm run test:run     # All tests pass
npm run dev          # http://localhost:3000
```

### pms-android

```bash
cd pms-android
# Open in Android Studio, sync Gradle, run on emulator
./gradlew test       # Unit tests
```

## 1.6 Access Checklist

- [ ] GitHub repository access to all four repos
- [ ] Local development environment running for backend + frontend
- [ ] All tests passing in pms-backend (`pytest`) and pms-frontend (`npm run test:run`)
- [ ] Read `CLAUDE.md` in each repo
- [ ] Read `docs/specs/system-spec.md` for system context
- [ ] Read `docs/specs/testing-strategy.md` for test conventions
- [ ] Read `docs/index.md` for full documentation map

---

# Section 2: The Four-Phase Development Process

The PMS follows a specification-first development process. Every feature flows through four phases before it is considered complete.

```
┌─────────────────────────────────────────────────────────┐
│  Phase 1: SPECIFY                                       │
│  Define system & subsystem requirements                 │
│  Output: SYS-REQ.md, SUB-*.md                          │
├─────────────────────────────────────────────────────────┤
│  Phase 2: VERIFY CONSISTENCY                            │
│  Check traceability, run /analyze                       │
│  Output: traceability-matrix.md, /analyze report        │
├─────────────────────────────────────────────────────────┤
│  Phase 3: IMPLEMENT                                     │
│  Use speckit to implement subsystem requirements        │
│  Output: Source code with @requirement annotations      │
├─────────────────────────────────────────────────────────┤
│  Phase 4: TEST & TRACE                                  │
│  Write tests, run them, record results, update RTM      │
│  Output: Test files, RUN-*.md records, updated RTM      │
└─────────────────────────────────────────────────────────┘
```

## Phase 1: Specify

**Goal:** Define what the system must do before writing any code.

1. **System-level requirements** are defined in `docs/specs/requirements/SYS-REQ.md`. These are high-level, cross-cutting requirements (authentication, encryption, audit, RBAC, performance, etc.).

2. **Subsystem-level requirements** are defined in `docs/specs/requirements/SUB-*.md`. Each subsystem (PR, CW, MM, RA) has its own requirements file that decomposes the system requirements into testable, implementable units.

3. Each subsystem requirement must:
   - Have a unique ID (e.g., `SUB-MM-0001`)
   - Reference its parent system requirement (if applicable)
   - Specify a verification method (Test, Inspection, Demo)
   - Be unambiguous and testable

### Using speckit to specify

```bash
claude
/specify
# "Define subsystem requirements for patient search and pagination.
# Parent: SYS-REQ-0007 (Performance).
# Must support search by last name, DOB, or ID (SUB-PR-0007).
# Must return paginated results, default 20 per page (SUB-PR-0008)."
```

## Phase 2: Verify Consistency

**Goal:** Ensure all requirements are traceable and the matrix is complete.

1. **Update the traceability matrix** in `docs/specs/requirements/traceability-matrix.md`:
   - Forward traceability: SYS-REQ → SUB-* → module → test case → status
   - Backward traceability: test case → requirement(s) → last result → run ID

2. **Run /analyze** to check consistency:

```bash
claude
/analyze
# "Verify that all requirements in docs/specs/requirements/ are covered
# by test cases in the traceability matrix. Flag any requirements with
# no tests or with failing tests."
```

3. **Save the /analyze output** as evidence:

```bash
git add docs/analyze/
git commit -m "evidence: consistency verification for <feature>"
git push
```

## Phase 3: Implement

**Goal:** Write the code that satisfies the subsystem requirements.

1. **Create a feature branch:**

```bash
git checkout -b feature/<description>
```

2. **Use speckit to plan and generate tasks:**

```bash
claude
/plan
# "Create a technical implementation plan for SUB-PR-0007 and SUB-PR-0008
# (patient search and pagination)."

/speckit.tasks
# This breaks the plan into small, testable implementation tasks
```

3. **Implement with Claude Code**, ensuring:
   - Every source module references the requirement it satisfies
   - Audit logging is included for data access (SYS-REQ-0003)
   - PHI fields are encrypted (SYS-REQ-0002)
   - RBAC checks are in place (SYS-REQ-0005)

4. **Update the Implementation Mapping** table in the relevant `SUB-*.md` file:

```markdown
| SUB-PR-0007 | `routers/patients.py:search` | `app/patients/page.tsx` | `ui/patients/` | TST-PR-0007 |
```

## Phase 4: Test & Trace

**Goal:** Every requirement has a test. Every test run is recorded. The RTM is always current.

### Write Tests

Every test must include requirement annotations:

**Python (pms-backend):**
```python
# @requirement SUB-PR-0007
# @verification-method Test

def test_patient_search_by_last_name(client):
    """TST-PR-0007: Patient search returns results matching last name."""
    ...
```

**TypeScript (pms-frontend):**
```typescript
// @requirement SUB-PR-0007
// @verification-method Test

it("TST-FE-0004: patient search filters by last name", async () => {
  ...
});
```

**Kotlin (pms-android):**
```kotlin
/**
 * @requirement SUB-PR-0007
 * @verification-method Test
 */
@Test
fun `TST-AND-0003 patient search filters by last name`() { ... }
```

### Run Tests and Record Results

```bash
# pms-backend
cd pms-backend
pytest -v

# pms-frontend
cd pms-frontend
npm run test:run

# pms-android
cd pms-android
./gradlew test
```

### Create a Test Run Record

After each test execution, create a run record in `docs/test-evidence/`:

```markdown
# Test Run: RUN-YYYY-MM-DD-NNN

| Field | Value |
|---|---|
| Date | YYYY-MM-DD HH:MM UTC |
| Repository | pms-backend |
| Commit | <SHA> |
| Branch | feature/<description> |
| Runner | local |

## Results

| Test Case | Requirement | Result | Duration |
|---|---|---|---|
| TST-PR-0007 | SUB-PR-0007 | PASS | 0.03s |

## Summary

- Total: 1
- Passed: 1
- Failed: 0
- Skipped: 0
```

### Update the Traceability Matrix

1. Add new test cases to the **Backward Traceability** table.
2. Update **Last Result** and **Run ID** columns for each test case.
3. Add a row to the **Test Run Log**.
4. Recalculate the **Coverage Summary**.

### Commit All Evidence

```bash
git add docs/specs/ docs/test-evidence/
git commit -m "evidence: test run RUN-YYYY-MM-DD-NNN

- Test results for SUB-PR-0007, SUB-PR-0008
- Updated traceability matrix and coverage summary"
git push
```

## Process Summary

| Phase | Input | Activities | Output | Tools |
|---|---|---|---|---|
| 1. Specify | Business need | Define SYS-REQ, decompose to SUB-* | Requirements docs | `/specify` |
| 2. Verify | Requirements | Check traceability, run /analyze | Updated RTM, /analyze report | `/analyze` |
| 3. Implement | Verified requirements | Plan, generate tasks, write code | Source code with annotations | `/plan`, `/speckit.tasks` |
| 4. Test & Trace | Implementation | Write tests, run, record results | Test files, run records, updated RTM | `pytest`, `vitest`, `gradlew test` |

---

# Section 3: Implementing a Feature (Worked Example)

**Example:** *Add drug interaction alerts that notify prescribers when a new prescription conflicts with the patient's active medications (SYS-REQ-0006, SUB-MM-0001, SUB-MM-0002).*

---

## Day 1: Specify & Verify

### Morning: Understand the Requirements

1. **Read the system-level requirement:**

```bash
# Read docs/specs/requirements/SYS-REQ.md
# Find SYS-REQ-0006: "Generate real-time clinical alerts..."
```

2. **Read the subsystem requirements:**

```bash
# Read docs/specs/requirements/SUB-MM.md
# Find SUB-MM-0001: "Drug interaction check within 5 seconds"
# Find SUB-MM-0002: "Classify interaction severity"
```

3. **Check the traceability matrix** for current status:

```bash
# Read docs/specs/requirements/traceability-matrix.md
# Check coverage for SUB-MM-0001 and SUB-MM-0002
```

### Afternoon: Create Specification & Verify Consistency

4. **Create a feature branch:**

```bash
git checkout -b feature/medication-interaction-alerts
```

5. **Run /specify to create the specification:**

```bash
claude
/specify
# "Create a specification for real-time medication interaction alerts.
# Must check new prescriptions against active medications within 5 seconds
# (SUB-MM-0001), classify severity as contraindicated/major/moderate/minor
# (SUB-MM-0002). Must comply with SYS-REQ-0003 (audit trail) and
# SYS-REQ-0002 (encryption)."
```

6. **Run /analyze to verify consistency:**

```bash
/analyze
# "Verify that SUB-MM-0001 and SUB-MM-0002 are in the traceability matrix
# and have corresponding test case IDs assigned."
```

7. **Commit specification and analysis evidence:**

```bash
git add .specify/ docs/analyze/
git commit -m "spec: medication interaction alerts specification

Relates to: SYS-REQ-0006, SUB-MM-0001, SUB-MM-0002"
git push -u origin feature/medication-interaction-alerts
```

---

## Day 2: Implement

### Morning: Plan and Code

1. **Generate tasks from the plan:**

```bash
claude
/plan
# "Create a technical implementation plan for the medication
# interaction alerts specification."

/speckit.tasks
# Breaks the plan into small, testable implementation tasks
```

2. **Implement in pms-backend:**

```bash
claude
# "Implement the DrugInteractionChecker service per SUB-MM-0001
# and SUB-MM-0002. Add @requirement annotations. Include audit
# logging (SYS-REQ-0003)."
```

3. **Update the Implementation Mapping** in `docs/specs/requirements/SUB-MM.md`:

```markdown
| SUB-MM-0001 | `services/interaction_checker.py` | — | — | TST-MM-0001 |
| SUB-MM-0002 | `services/interaction_checker.py` | — | — | TST-MM-0002 |
```

### Afternoon: Continue Implementation

4. **Implement frontend components** in pms-frontend (if applicable).
5. **Implement Android screens** in pms-android (if applicable).
6. **Commit progress:**

```bash
git add src/ tests/ docs/specs/
git commit -m "feat(medications): implement drug interaction checker

- Interaction check within 5 seconds (SUB-MM-0001)
- Severity classification (SUB-MM-0002)
- Audit logging on all checks (SYS-REQ-0003)"
git push
```

---

## Day 3: Test & Trace

### Morning: Write and Run Tests

1. **Write tests with requirement annotations:**

```python
# tests/test_medications.py

# @requirement SUB-MM-0001
# @verification-method Test

def test_interaction_check_within_5_seconds(client):
    """TST-MM-0001: Drug interaction check completes within 5 seconds."""
    start = time.time()
    response = client.get("/medications/interactions", params={"drugs": ["warfarin", "aspirin"]})
    assert time.time() - start < 5.0
    assert response.status_code == 200

# @requirement SUB-MM-0002
# @verification-method Test

def test_interaction_severity_classification(client):
    """TST-MM-0002: Drug interactions are classified by severity."""
    response = client.get("/medications/interactions", params={"drugs": ["warfarin", "aspirin"]})
    data = response.json()
    assert data[0]["severity"] in ["contraindicated", "major", "moderate", "minor"]
```

2. **Run the tests:**

```bash
pytest tests/test_medications.py -v
```

3. **Create the test run record** in `docs/test-evidence/RUN-YYYY-MM-DD-NNN.md`.

4. **Update the traceability matrix:**
   - Add TST-MM-0001 and TST-MM-0002 to the backward traceability table
   - Update Last Result and Run ID columns
   - Add a row to the Test Run Log
   - Recalculate the Coverage Summary

5. **Commit all evidence:**

```bash
git add tests/ docs/specs/ docs/test-evidence/
git commit -m "evidence: test run RUN-YYYY-MM-DD-NNN

- TST-MM-0001: PASS (SUB-MM-0001)
- TST-MM-0002: PASS (SUB-MM-0002)
- Updated traceability matrix and coverage summary"
git push
```

### Afternoon: PR & Review

6. **Create the pull request:**

```bash
gh pr create --title "feat: medication interaction alerts (SYS-REQ-0006)" --body "## Summary
- Drug interaction checker with severity classification
- Tests with full requirement traceability

## Requirements Covered
- SUB-MM-0001: Interaction check within 5 seconds
- SUB-MM-0002: Severity classification

## Evidence
- Test run: RUN-YYYY-MM-DD-NNN
- Traceability matrix updated
- /analyze consistency verified"
```

---

# Section 4: A Day in the Life of a PMS Developer

## 8:30 AM — Triage & Priorities

```bash
# Check for PR review requests
gh pr list --search "review-requested:@me"

# Check assigned issues
gh issue list --assignee @me --state open
```

**Priority order:**
1. **P0** — Blocking PRs (unblock teammates first)
2. **P1** — Critical bugs or security issues
3. **P2** — Feature work (current sprint)
4. **P3** — Technical debt, documentation

## 8:45 AM — Review PRs

For each PR, verify:

- [ ] **Requirement annotations** — `@requirement` tags present in tests and code
- [ ] **Traceability** — New test cases added to the RTM
- [ ] **Test run record** — Evidence committed for test execution
- [ ] **HIPAA compliance** — PHI encrypted, audit logs in place
- [ ] **Implementation Mapping** — `SUB-*.md` updated with source modules

## 10:00 AM — Feature Work

### Sync All Repos

```bash
# Update docs submodule in your working repo
cd pms-backend
git submodule update --remote docs
```

### Follow the Four-Phase Process

1. **Read** the relevant requirements in `docs/specs/requirements/`
2. **Verify** the traceability matrix is current
3. **Implement** using `/plan` → `/speckit.tasks` → Claude Code
4. **Test** with requirement annotations, record results, update RTM

## 3:00 PM — Testing & Quality

```bash
# Run all backend tests
cd pms-backend && pytest -v --cov=pms

# Run all frontend tests
cd pms-frontend && npm run test:run

# Run quality scans
snyk test
coderabbit review --type uncommitted --plain
```

## 4:30 PM — End-of-Day Wrap-Up

1. **Commit all work** (even WIP) with requirement references
2. **Push to remote**
3. **Update the RTM** if any requirement status changed
4. **Commit evidence** (test runs, /analyze reports, RTM updates)

```bash
git add docs/specs/ docs/test-evidence/
git commit -m "evidence: end-of-day RTM and test updates

- Updated traceability matrix with today's progress
Relates to: <REQUIREMENT_IDS>"
git push
```

---

## Quick Reference

### Test Commands

```bash
# pms-backend
pytest -v                                    # Run all tests
pytest --cov=pms --cov-report=html           # With coverage
pytest tests/test_patients.py -v             # Specific subsystem

# pms-frontend
npm run test:run                             # Run all tests
npx vitest run --coverage                    # With coverage
npx vitest run __tests__/auth.test.ts        # Specific test

# pms-android
./gradlew test                               # Unit tests
./gradlew connectedAndroidTest               # Instrumented tests
```

### Speckit Commands (in Claude Code)

```bash
/specify                    # Define specifications
/plan                       # Generate technical plan
/analyze                    # Validate consistency
/speckit.tasks              # Break into implementation tasks
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/<description>

# Update docs submodule
git submodule update --remote docs

# Commit with requirement references
git commit -m "feat(<subsystem>): <description>

Relates to: SUB-XX-NNNN, SYS-REQ-NNNN"

# Create PR
gh pr create --title "feat: <title>" --body "..."
```

### Requirement ID Conventions

| Pattern | Scope | Example |
|---|---|---|
| `SYS-REQ-NNNN` | System-level requirement | SYS-REQ-0001 (MFA) |
| `SUB-PR-NNNN` | Patient Records subsystem | SUB-PR-0003 (CRUD) |
| `SUB-CW-NNNN` | Clinical Workflow subsystem | SUB-CW-0003 (Encounters) |
| `SUB-MM-NNNN` | Medication Management subsystem | SUB-MM-0001 (Interactions) |
| `SUB-RA-NNNN` | Reporting & Analytics subsystem | SUB-RA-0001 (Dashboards) |
| `TST-{subsystem}-NNNN` | Test case ID | TST-MM-0001 |
| `RUN-YYYY-MM-DD-NNN` | Test run record | RUN-2026-02-15-001 |

---

*For the complete development pipeline tutorial, see the [Development Pipeline Tutorial](./Development_Pipeline_Tutorial.md). For project documentation, see [docs/index.md](./docs/index.md).*

---

## Troubleshooting

### SSH Multi-Account Setup

If you use multiple GitHub accounts (e.g., a personal and a work account), you need separate SSH keys and host aliases in `~/.ssh/config` so Git knows which key to use for each account.

**1. Generate a new SSH key for the target account:**

```bash
ssh-keygen -t ed25519 -C "your.email@example.com" -f ~/.ssh/id_ed25519_yourname
```

**2. Add a host alias to `~/.ssh/config`:**

```
Host github.com-yourname
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_yourname
    IdentitiesOnly yes
```

**3. Add the public key to GitHub:**

- Copy the contents of `~/.ssh/id_ed25519_yourname.pub`
- Go to https://github.com/settings/keys → **New SSH key** → paste and save

**4. Test the connection:**

```bash
ssh -T git@github.com-yourname
# Expected: "Hi yourname! You've successfully authenticated..."
```

**5. Update all repo remotes to use your alias:**

```bash
cd pms-backend  && git remote set-url origin git@github.com-yourname:utexas-demo/pms-backend.git
cd pms-frontend && git remote set-url origin git@github.com-yourname:utexas-demo/pms-frontend.git
cd pms-android  && git remote set-url origin git@github.com-yourname:utexas-demo/pms-android.git
cd demo         && git remote set-url origin git@github.com-yourname:utexas-demo/demo.git
```

**6. Update the docs submodule URL in each implementation repo:**

```bash
# Run in each of: pms-backend, pms-frontend, pms-android
git config submodule.docs.url git@github.com-yourname:utexas-demo/demo.git
```

### Docker / PostgreSQL Issues

| Problem | Solution |
|---|---|
| `docker: Cannot connect to the Docker daemon` | Start Docker Desktop: `open -a Docker` (macOS) |
| `port 5432 already in use` | Another PostgreSQL is running. Stop it: `docker stop pms-postgres` or check `lsof -i :5432` |
| `database "pms_test" does not exist` | Create it: `docker exec pms-postgres psql -U postgres -c "CREATE DATABASE pms_test;"` |
| Tests pass but dev server fails to connect to DB | Ensure Docker container is running: `docker ps --filter "name=pms-postgres"` |

### pydantic-settings Validation Errors

If you see `Extra inputs are not permitted` errors when running `pytest` or starting the backend, add `"extra": "ignore"` to `model_config` in both `src/pms/config.py` and `src/pms/feature_flags.py`. See the note in [Section 1.5](#15-set-up-each-project) for details.

### Submodule Initialization Fails

If `git submodule update --init --recursive` fails with a hostname resolution error, the `.gitmodules` file uses a custom SSH alias. Override the URL locally:

```bash
git config submodule.docs.url git@github.com:utexas-demo/demo.git
git submodule update --init --recursive
```

See the note in [Section 1.4](#14-clone-all-repositories) for details.
