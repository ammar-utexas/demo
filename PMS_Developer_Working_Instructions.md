# PMS Developer Working Instructions

**Patient Management System — Development Process Guide**

Version 1.1 | Last Updated: February 2026

---

## Table of Contents

- [Compliance Evidence Storage Policy](#compliance-evidence-storage-policy)
- [Section 1: First-Time Setup](#section-1-first-time-setup)
- [Section 2: Implementing a Feature](#section-2-implementing-a-feature-over-multiple-days)
- [Section 3: A Day in the Life](#section-3-a-day-in-the-life-of-a-pms-developer)

---

## Compliance Evidence Storage Policy

> **This policy applies to all PMS developers and CI/CD pipelines.**

### Authoritative Evidence Store

The **GitHub repository** is the authoritative, permanent source of truth for all compliance evidence. Every piece of evidence — test reports, quality scans, security results, traceability matrices, coverage reports, and review summaries — **must be committed to the repository**.

- **GitHub repo** = permanent, versioned, tamper-evident (git history provides an immutable audit trail)
- **`docs/` directory** = queryable documentation layer (markdown files committed alongside the code)

### Evidence Commitment Rule

Every evidence-generating step must follow this sequence:

1. **Generate** the evidence artifact (report, scan result, matrix, etc.)
2. **`git add`** the artifact to staging
3. **`git commit`** with a descriptive message referencing requirement IDs
4. **`git push`** to the remote repository

### Evidence Directory Structure

All compliance evidence resides under `docs/` in the repository:

```
docs/
├── analyze/                  # /analyze consistency reports
├── quality-reports/          # SonarQube quality gate results
├── security/                 # Snyk scan results and security reports
├── reviews/                  # CodeRabbit and PR review evidence
├── test-evidence/            # Test execution reports
├── sbom/                     # Software Bill of Materials (CycloneDX, SPDX)
├── adr/                      # Architecture Decision Records
├── traceability-matrix.md    # Requirements Traceability Matrix
├── coverage-report.md        # Requirement test coverage report
└── evidence-summary.md       # Unified evidence summary (CI-generated)
```

### Retention

HIPAA requires a minimum **6-year retention period** for compliance documentation. GitHub's permanent git history satisfies this requirement. GitHub Actions artifacts (90-day retention) are **not** a substitute for committed evidence files.

---

# Section 1: First-Time Setup

*Complete these steps once when joining the PMS team or setting up a new machine.*

## 1.1 System Prerequisites

Before starting, ensure your machine meets these requirements:

- **Operating System:** macOS 13+, Ubuntu 22.04+, or Windows 11 with WSL2
- **RAM:** Minimum 16 GB (recommended 32 GB for running SonarQube locally)
- **Disk:** At least 50 GB free space
- **Internet:** Stable connection (required for Snyk, CodeRabbit)

## 1.2 Install Core Development Tools

### Node.js and npm

```bash
# Install Node.js 24 LTS (recommended via nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
nvm install 24
nvm use 24
node --version   # Should show v24.x.x
npm --version    # Should show 11.x.x
```

### Git

```bash
# macOS
brew install git

# Ubuntu
sudo apt update && sudo apt install git

# Configure your identity
git config --global user.name "Your Name"
git config --global user.email "your.email@company.com"
```

### GitHub CLI

```bash
# macOS
brew install gh

# Ubuntu
sudo apt install gh

# Authenticate
gh auth login
# Select: GitHub.com → HTTPS → Login with a web browser
```

### Docker

```bash
# macOS
brew install --cask docker
# Launch Docker Desktop from Applications

# Ubuntu
sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER
# Log out and back in for group membership to take effect
```

## 1.3 Install Development Pipeline Tools

### Claude Code CLI

```bash
# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Verify
claude --version
# Launch Claude Code and follow the authentication prompt on first run
```

### GitHub Spec Kit

```bash
npm install -g @github/specify

# Verify
specify check
```

### SonarQube

```bash
# For SonarCloud (hosted):
# 1. Go to https://sonarcloud.io and sign in with your GitHub account
# 2. Request access to the "pms-healthcare" project from your Tech Lead
# 3. Generate a personal token: My Account → Security → Generate Token
# 4. Save the token — you'll need it for local scans

# For local scanning:
npm install -g sonarqube-scanner

# Set environment variables (add to ~/.bashrc or ~/.zshrc)
export SONAR_TOKEN="your-personal-token"
export SONAR_HOST_URL="https://sonarcloud.io"  # or your org's SonarQube URL
```

### CodeRabbit

```bash
# Install CLI
curl -fsSL https://cli.coderabbit.ai/install.sh | sh

# CodeRabbit GitHub App should already be installed on the PMS repo.
# If you don't see CodeRabbit reviews on your PRs, contact the Tech Lead.
```

### Snyk

```bash
npm install -g snyk

# Authenticate
snyk auth
# Follow the browser prompt to sign in

# Verify you have access to the PMS organization
snyk test --org=pms-healthcare
```

## 1.4 Clone and Set Up the Repository

```bash
# Clone the PMS repository
gh repo clone your-org/patient-management-system
cd patient-management-system

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local
# Edit .env.local with your local database credentials and API keys
```

### Verify the Setup

```bash
# Run the verification script
npm run verify-setup

# This checks:
# ✓ Node.js version
# ✓ Docker running
# ✓ Database connection
# ✓ All CLI tools installed
# ✓ Snyk authentication
# ✓ SonarQube connectivity
```

### Run Tests to Confirm Everything Works

```bash
# Run the full test suite
npm test

# Run with coverage (used by SonarQube)
npm test -- --coverage

# Start the development server
npm run dev
# Application should be available at http://localhost:3000
```

## 1.5 Configure Your Editor / IDE

### VS Code (Recommended Extensions)

- **ESLint** — Code linting
- **Prettier** — Code formatting
- **SonarLint** — Real-time SonarQube feedback
- **Snyk Security** — Real-time vulnerability alerts
- **GitLens** — Enhanced Git integration

### CLAUDE.md Awareness

The repository root contains a `CLAUDE.md` file that instructs Claude Code how to work with this project. Read this file to understand the development workflow, requirement ID conventions, and the `docs/` directory structure. Do not modify `CLAUDE.md` without Tech Lead approval.

## 1.6 Access Checklist

Before you start working on features, confirm you have:

- [ ] GitHub repository access (push to feature branches, create PRs)
- [ ] SonarQube/SonarCloud access to the pms-healthcare project
- [ ] CodeRabbit reviews appearing on your test PR
- [ ] Snyk access to the pms-healthcare organization
- [ ] Local development environment running (`npm run dev`)
- [ ] All tests passing (`npm test`)
- [ ] Read the `CLAUDE.md` file completely
- [ ] Read the `CONTRIBUTING.md` file for coding standards
- [ ] Read the `docs/` directory structure and `docs/index.md`

---

# Section 2: Implementing a Feature Over Multiple Days

*This section walks through the complete lifecycle of implementing a feature using the PMS Spec-Driven Development process.*

**Example Feature:** *Add real-time medication interaction alerts that notify prescribers when a new prescription conflicts with the patient's active medications (relates to SYS-REQ-0006, SUB-MM-0001, SUB-MM-0002).*

---

## Day 1: Specification & Planning

### Morning: Understand the Requirement

1. **Read the relevant docs for context:**

Read the requirements documentation in `docs/` to understand:

> What are the detailed requirements for medication interaction checking? Include SYS-REQ-0006 and all related SUB-MM requirements.

2. **Review the traceability matrix** to understand what already exists:

Check `docs/traceability-matrix.md` for the current implementation status of SUB-MM-0001 and SUB-MM-0002.

3. **Check architecture decisions:**

Read the architecture documentation in `docs/architecture/` and `docs/adr/` to understand:

> What architectural decisions have been made about the clinical alerts pipeline and drug interaction checking?

### Afternoon: Create the Specification

4. **Create a feature branch:**

```bash
git checkout -b feature/medication-interaction-alerts
```

5. **Run /specify in Claude Code:**

```bash
claude
# In Claude Code:
/specify
# Prompt: "Create a specification for real-time medication
# interaction alerts. Must check new prescriptions against
# active medications within 5 seconds (SUB-MM-0001), classify
# severity as contraindicated/major/moderate/minor (SUB-MM-0002),
# and notify the prescriber via an in-app alert with one-click
# override capability. Must comply with SYS-REQ-0003 (audit trail)
# and SYS-REQ-0002 (encryption)."
```

6. **Review the generated spec** in `.specify/specs/` and refine as needed.

7. **Run /plan to generate the technical plan:**

```bash
/plan
# Prompt: "Create a technical implementation plan for the
# medication interaction alerts specification."
```

8. **Run /analyze to validate consistency and save the output:**

```bash
/analyze
# This checks that specs, plans, and tasks are aligned
# Fix any issues flagged by the analyzer
```

Save the `/analyze` output as evidence:

```bash
# Save the /analyze report to the evidence directory
# (Claude Code can generate this file from the /analyze output)
claude
# "Save the /analyze output to docs/analyze/medication-interaction-alerts-analyze.md"
```

9. **Commit the specification, plan, and analysis evidence:**

```bash
git add .specify/ docs/analyze/
git commit -m "spec: add medication interaction alerts specification

- Specification, technical plan, and /analyze consistency report
Relates to: SYS-REQ-0006, SUB-MM-0001, SUB-MM-0002
Spec-Kit phase: Specify + Plan + Analyze"
```

### End of Day 1: Status Update

Push your branch and create a draft PR:

```bash
git push -u origin feature/medication-interaction-alerts
gh pr create --draft \
  --title "feat: medication interaction alerts (SYS-REQ-0006)" \
  --body "## Specification Phase
- Spec created and validated with /analyze
- Technical plan generated

## Requirements
- SYS-REQ-0006: Real-time clinical alerts within 30 seconds
- SUB-MM-0001: Interaction check within 5 seconds
- SUB-MM-0002: Severity classification

## Status: Day 1/3 — Specification Complete"
```

---

## Day 2: Implementation

### Morning: Core Implementation

1. **Pull latest and sync:**

```bash
git checkout feature/medication-interaction-alerts
git pull origin develop --rebase
```

2. **Generate tasks from the plan:**

```bash
claude
/speckit.tasks
# This breaks the plan into small, testable implementation tasks
```

3. **Implement with Claude Code:**

```bash
claude
# "Implement task 1: Create the DrugInteractionChecker service
# per the specification in .specify/specs/medication-interaction-alerts.md.
# Ensure all functions include audit logging (SYS-REQ-0003) and
# encrypt PHI fields (SYS-REQ-0002). Add @requirement annotations
# in JSDoc comments."
```

4. **Write tests alongside implementation:**

```bash
# "Write tests for the DrugInteractionChecker service.
# Each test must include @requirement annotations mapping to
# SUB-MM-0001 and SUB-MM-0002. Include performance tests
# verifying the 5-second SLA."
```

5. **Run tests locally:**

```bash
npm test -- --testPathPattern=medications
npm test -- --coverage
```

### Afternoon: Continue Implementation and Local Scans

6. **Continue implementing remaining tasks** from `/speckit.tasks`.

7. **Run CodeRabbit locally before pushing:**

```bash
coderabbit review --type uncommitted --plain
# Review suggestions and fix critical issues
```

8. **Run Snyk locally to catch vulnerabilities early:**

```bash
snyk test
snyk code test
# Fix any critical or high severity issues before pushing
```

9. **Run SonarQube locally (optional but recommended):**

```bash
sonar-scanner
# Check for quality gate issues
```

10. **Commit progress with requirement references:**

```bash
git add src/medications/ test/medications/
git commit -m "feat(medications): implement drug interaction checker

- DrugInteractionChecker service with severity classification
- Real-time check completes within 5 seconds (SUB-MM-0001)
- Severity levels: contraindicated, major, moderate, minor (SUB-MM-0002)
- Full audit logging on all interaction checks (SYS-REQ-0003)
- PHI encryption for prescription data (SYS-REQ-0002)

Requirement coverage: SUB-MM-0001, SUB-MM-0002, SUB-MM-0003, SUB-MM-0004"

git push
```

### End of Day 2: Status Update

Update the draft PR description with implementation progress.

---

## Day 3: Testing, Review & Evidence

### Morning: Complete Testing and Evidence

1. **Run the full test suite with coverage:**

```bash
npm test -- --coverage --reporter=json > test-results.json
```

2. **Update the traceability matrix:**

```bash
claude
# "Update docs/traceability-matrix.md to include the medication
# interaction alerts. Map SUB-MM-0001 and SUB-MM-0002 to the new
# source modules and test cases. Mark verification status."
```

3. **Generate coverage report:**

```bash
claude
# "Cross-reference test-results.json with docs/traceability-matrix.md.
# Generate docs/coverage-report.md showing requirement test coverage
# for all SUB-MM requirements."
```

4. **Commit evidence to the repository:**

```bash
git add docs/traceability-matrix.md docs/coverage-report.md test-results.json
git commit -m "evidence: update RTM and coverage report for medication alerts

- Updated traceability matrix with SUB-MM-0001, SUB-MM-0002 mappings
- Generated requirement test coverage report
Relates to: SYS-REQ-0006, SUB-MM-0001, SUB-MM-0002"

git push
```

### Midday: Mark PR as Ready for Review

5. **Run final local checks:**

```bash
npm test -- --coverage
snyk test
coderabbit review --plain
```

6. **Mark the PR as ready:**

```bash
gh pr ready
```

7. **The CI pipeline will automatically run:**
   - SonarQube quality gate analysis
   - CodeRabbit AI-powered review
   - Snyk dependency and code scanning
   - Unit and integration tests

### Afternoon: Address Review Feedback

8. **Review CodeRabbit comments** on the PR and address each finding.

9. **Check SonarQube quality gate status** in the PR checks.

10. **Review Snyk alerts** in the GitHub Security tab.

11. **Make fixes and push:**

```bash
git add .
git commit -m "fix(medications): address review feedback

- Fixed audit log format per CodeRabbit suggestion (SYS-REQ-0003)
- Added missing input validation per SonarQube finding
- Updated dependency per Snyk advisory"

git push
```

12. **Once approved, merge via squash merge:**

```bash
gh pr merge --squash
```

### Post-Merge: Archive Evidence

13. **Archive and commit PR review evidence:**

```bash
# Get the merged PR review data
gh pr view <PR_NUMBER> --comments --json comments \
  > docs/reviews/pr-<PR_NUMBER>-review.json
```

In Claude Code:

```
"Summarize the CodeRabbit review and SonarQube results for
PR #<PR_NUMBER>. Map findings to requirement IDs. Generate
docs/reviews/pr-<PR_NUMBER>-evidence-summary.md."
```

Commit the evidence to the repository:

```bash
git add docs/reviews/pr-<PR_NUMBER>-review.json \
       docs/reviews/pr-<PR_NUMBER>-evidence-summary.md
git commit -m "evidence: archive PR #<PR_NUMBER> review and quality results

- CodeRabbit review summary with requirement mappings
- SonarQube quality gate results
Relates to: <REQUIREMENT_IDS>"

git push
```

14. **Update CLAUDE.md if any architectural decisions were made.**

---

# Section 3: A Day in the Life of a PMS Developer

*A typical development day following the PMS process, from morning priorities to end-of-day commits.*

---

## 8:30 AM — Start of Day: Triage & Priorities

### Check Notifications and Assignments

```bash
# Check for PR review requests
gh pr list --search "review-requested:@me"

# Check assigned issues
gh issue list --assignee @me --state open

# Check Snyk alerts (new vulnerabilities overnight)
snyk test --json | jq '.vulnerabilities | length'
```

### Review the Board

Check the sprint board for your assigned tasks, noting priorities:

1. **P0 — Blocking PRs** that need your review (other developers are waiting)
2. **P1 — Critical bug fixes** or security remediations
3. **P2 — Feature work** from your current sprint assignment
4. **P3 — Technical debt** and documentation improvements

---

## 8:45 AM — Review Other Developers' PRs (Priority #1)

Reviewing PRs first unblocks your teammates. For each PR:

### Quick Context Check

```bash
# View PR details
gh pr view <PR_NUMBER>

# Check if CI passed
gh pr checks <PR_NUMBER>
```

Read the relevant docs for context on the requirements involved. Check `docs/` for the requirements and acceptance criteria related to the feature under review.

### Review Checklist

For each PR, verify:

- [ ] **Specification alignment** — Does the code match the spec in `.specify/specs/`?
- [ ] **Requirement annotations** — Are `@requirement` tags present in tests and code?
- [ ] **HIPAA compliance** — Is PHI encrypted? Are audit logs in place?
- [ ] **Test coverage** — Are all requirements covered by tests?
- [ ] **SonarQube gate** — Did it pass? Any new issues introduced?
- [ ] **CodeRabbit findings** — Were critical findings addressed?
- [ ] **Snyk results** — Any new vulnerabilities? Are they acceptable?

### Provide Feedback

```bash
# Approve if everything looks good
gh pr review <PR_NUMBER> --approve -b "LGTM. Requirement coverage verified for SUB-CW-003. HIPAA audit logging confirmed."

# Or request changes with specific references
gh pr review <PR_NUMBER> --request-changes -b "Missing audit logging on the DELETE endpoint (SYS-REQ-0003). Also, SUB-CW-003 requires input validation on the referral code field — see the spec in .specify/specs/clinical-workflow-referrals.md."
```

---

## 9:30 AM — Address Any Critical Issues (Priority #2)

### Check for Urgent Snyk Alerts

```bash
# Check for critical vulnerabilities
snyk test --severity-threshold=critical

# If critical vulns found, create a hotfix branch
git checkout -b hotfix/snyk-critical-<CVE_ID>
```

### Check SonarQube for Regressions

Review the SonarQube dashboard for any quality gate failures on the develop branch. If failures exist, prioritize fixing them.

---

## 10:00 AM — Feature Work (Priority #3)

### Sync and Start

```bash
# Pull latest develop
git checkout develop && git pull

# Switch to your feature branch
git checkout feature/your-current-feature
git rebase develop
```

### Read the Docs Before Coding

Before writing code, always check what already exists. Read the relevant documentation in `docs/`:

- Check `docs/architecture/` and `docs/adr/` for:

  > What design patterns are used for \<SIMILAR_FEATURE\> and what architectural constraints apply?

- Check `docs/security/` and `docs/quality-reports/` for:

  > Are there known issues or gotchas related to \<TECHNOLOGY_OR_MODULE\> in the PMS codebase?

### Implement Using the Spec-Driven Process

Follow the Day 2 implementation process from Section 2. Key reminders:

- Always reference requirement IDs in code comments and commit messages
- Write tests alongside implementation, not after
- Run local scans (CodeRabbit, Snyk) before pushing
- Commit frequently with meaningful messages

---

## 12:00 PM — Lunch Break

Step away from the screen. The CI pipeline works while you rest.

---

## 1:00 PM — Continue Feature Work

### Check CI Results from Morning Push

```bash
# Check if your morning push triggered any failures
gh pr checks <YOUR_PR_NUMBER>

# If CodeRabbit posted a review, address it
gh pr view <YOUR_PR_NUMBER> --comments
```

### Continue Implementation

Resume where you left off. If you encounter a bug or unexpected behavior:

1. **Check the docs first:**

Read `docs/security/` and `docs/quality-reports/` for any previously documented issues related to the error.

2. **If no solution found, solve it and document the solution:**

In Claude Code:

```
"Document the bug I just fixed: <DESCRIPTION>.
Generate a debugging note for docs/debugging/<ISSUE>.md
that includes the error message, root cause, and fix."
```

Commit the debugging documentation:

```bash
git add docs/debugging/<ISSUE>.md
git commit -m "docs: add debugging note for <ISSUE>

- Error message, root cause, and fix documented
Relates to: <REQUIREMENT_ID_IF_APPLICABLE>"

git push
```

---

## 3:00 PM — Testing & Quality Check

### Run Your Tests

```bash
# Run tests for the modules you changed
npm test -- --testPathPattern=<YOUR_MODULE>

# Run full suite if your changes may have broader impact
npm test -- --coverage
```

### Local Quality Scans

```bash
# Quick CodeRabbit check on uncommitted changes
coderabbit review --type uncommitted --plain

# Snyk check for any new dependencies you added
snyk test

# If you added a new npm package, verify it's safe:
snyk test --json | jq '.vulnerabilities[] | select(.severity=="critical" or .severity=="high")'
```

---

## 4:00 PM — Follow Up on Reviews

### Check on PRs You Reviewed This Morning

```bash
# See if authors addressed your feedback
gh pr list --search "reviewed-by:@me is:open"
```

### Re-review and Approve if Fixed

If the author addressed your feedback, re-review and approve promptly. Don't be the bottleneck.

---

## 4:30 PM — End-of-Day Wrap-Up

### Commit All Work in Progress

**Never leave uncommitted changes overnight.** Even if a feature is incomplete, commit your progress:

```bash
# Stage your changes
git add src/medications/ test/medications/ docs/

# Commit with a clear WIP message including requirement context
git commit -m "wip(medications): interaction alert UI component

- Completed: alert notification panel (SUB-MM-0001)
- In progress: override workflow with reason capture
- Next: wire up to WebSocket for real-time delivery

Requirement progress: SUB-MM-0001 (80%), SUB-MM-0002 (60%)"
```

### Push to Remote

```bash
git push
```

### Update the Traceability Matrix (if implementation changed)

If you completed implementation of any requirement today:

```bash
claude
# "Update docs/traceability-matrix.md to reflect that
# SUB-MM-0001 now has source module src/medications/interaction-checker.ts
# and test case TC-MED-001. Mark status as 'In Verification'."
```

### Commit Updated Evidence

If the traceability matrix or any ADRs were updated today, commit them:

```bash
git add docs/traceability-matrix.md docs/adr/
git commit -m "evidence: end-of-day RTM and ADR updates

- Updated traceability matrix with today's implementation progress
- Added/updated ADRs for architectural decisions made today
Relates to: <REQUIREMENT_IDS>"

git push
```

### Update Your Sprint Status

Leave a brief status update on your Jira ticket or sprint board noting what you accomplished and what's next.

### Quick Standup Prep

Jot down for tomorrow's standup:

- **Done today:** What you completed (with requirement IDs)
- **Doing tomorrow:** What you'll work on next
- **Blockers:** Anything preventing progress

---

## Daily Checklist Summary

| Time | Activity | Priority |
|------|----------|----------|
| 8:30 AM | Triage notifications, check Snyk alerts | — |
| 8:45 AM | Review teammates' PRs | P0 |
| 9:30 AM | Address critical bugs / security remediations | P1 |
| 10:00 AM | Feature work: read docs/ → implement → test | P2 |
| 12:00 PM | Lunch break | — |
| 1:00 PM | Check CI results, continue feature work | P2 |
| 3:00 PM | Run tests and local quality scans | — |
| 4:00 PM | Follow up on PR reviews | P0 |
| 4:30 PM | Commit all changes, push, update RTM | — |

---

## Quick Reference: Common Commands

```bash
# === GitHub Spec Kit ===
/specify                    # Define specifications
/plan                       # Generate technical plan
/analyze                    # Validate consistency
/speckit.tasks              # Break into implementation tasks

# === Code Quality ===
coderabbit review --plain                   # Local AI review
coderabbit review --type uncommitted        # Review uncommitted only
sonar-scanner                               # Local SonarQube scan

# === Security ===
snyk test                                   # Dependency scan
snyk code test                              # SAST scan
snyk test --severity-threshold=critical     # Critical only
snyk sbom --format cyclonedx                # Generate SBOM

# === Git Workflow ===
gh pr create --draft --title "feat: ..." --body "..."   # Create draft PR
gh pr ready                                              # Mark ready for review
gh pr checks <NUMBER>                                    # Check CI status
gh pr review <NUMBER> --approve -b "..."                 # Approve PR
gh pr merge --squash                                     # Merge via squash
```

---

*For the complete development process tutorial, see the [Developer Documentation](./docs/index.md).*
