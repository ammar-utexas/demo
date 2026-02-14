# PMS Developer Working Instructions

**Patient Management System — Development Process Guide**

Version 1.0 | Last Updated: February 2026

---

## Table of Contents

- [Section 1: First-Time Setup](#section-1-first-time-setup)
- [Section 2: Implementing a Feature](#section-2-implementing-a-feature-over-multiple-days)
- [Section 3: A Day in the Life](#section-3-a-day-in-the-life-of-a-pms-developer)

---

# Section 1: First-Time Setup

*Complete these steps once when joining the PMS team or setting up a new machine.*

## 1.1 System Prerequisites

Before starting, ensure your machine meets these requirements:

- **Operating System:** macOS 13+, Ubuntu 22.04+, or Windows 11 with WSL2
- **RAM:** Minimum 16 GB (recommended 32 GB for running SonarQube locally)
- **Disk:** At least 50 GB free space
- **Internet:** Stable connection (required for NotebookLM, Snyk, CodeRabbit)

## 1.2 Install Core Development Tools

### Node.js and npm

```bash
# Install Node.js 20 LTS (recommended via nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
nvm install 20
nvm use 20
node --version   # Should show v20.x.x
npm --version    # Should show 10.x.x
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

# Authenticate
claude auth login
# Follow the browser prompt to sign in with your Anthropic account
```

### GitHub Spec Kit

```bash
npm install -g @github/specify

# Verify
specify check
```

### NotebookLM CLI

```bash
npm install -g notebooklm-cli

# Verify
nlm --help
```

### Authenticate with NotebookLM

```bash
nlm auth
# A browser window opens — sign in with your company Google Workspace account
# Credentials are saved locally for future sessions
```

> **🔑 Access Request:** If you do not have access to the PMS NotebookLM notebooks, request access from the Tech Lead by providing your Google Workspace email. The following notebooks require read/write access:
>
> | Notebook | ID | Purpose |
> |----------|----|---------|
> | PMS: Requirements (IEEE 830) | `<NLM_REQ_ID>` | System & subsystem requirements |
> | PMS: Architecture & Design | `<NLM_ARCH_ID>` | ADRs, design docs, architecture |
> | PMS: Test Evidence & Traceability | `<NLM_TEST_ID>` | Test reports, RTM, coverage |
> | PMS: Quality & Security Evidence | `<NLM_QS_ID>` | SonarQube, CodeRabbit, Snyk reports |
> | PMS: HIPAA & FDA Compliance | `<NLM_COMPLIANCE_ID>` | Regulatory evidence, SBOM |

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
# ✓ NotebookLM authentication
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

The repository root contains a `CLAUDE.md` file that instructs Claude Code how to work with this project. Read this file to understand the development workflow, requirement ID conventions, and NotebookLM notebook references. Do not modify `CLAUDE.md` without Tech Lead approval.

## 1.6 Access Checklist

Before you start working on features, confirm you have:

- [ ] GitHub repository access (push to feature branches, create PRs)
- [ ] NotebookLM access to all five PMS notebooks
- [ ] SonarQube/SonarCloud access to the pms-healthcare project
- [ ] CodeRabbit reviews appearing on your test PR
- [ ] Snyk access to the pms-healthcare organization
- [ ] Local development environment running (`npm run dev`)
- [ ] All tests passing (`npm test`)
- [ ] Read the `CLAUDE.md` file completely
- [ ] Read the `CONTRIBUTING.md` file for coding standards

---

# Section 2: Implementing a Feature Over Multiple Days

*This section walks through the complete lifecycle of implementing a feature using the PMS Spec-Driven Development process.*

**Example Feature:** *Add real-time medication interaction alerts that notify prescribers when a new prescription conflicts with the patient's active medications (relates to SYS-REQ-0006, SUB-MM-0001, SUB-MM-0002).*

---

## Day 1: Specification & Planning

### Morning: Understand the Requirement

1. **Query NotebookLM for context:**

```bash
nlm notebook query --notebook <NLM_REQ_ID> \
  --question "What are the detailed requirements for medication
  interaction checking? Include SYS-REQ-0006 and all related
  SUB-MM requirements."
```

2. **Review the traceability matrix** to understand what already exists:

```bash
nlm notebook query --notebook <NLM_REQ_ID> \
  --question "What is the current implementation status of
  SUB-MM-0001 and SUB-MM-0002 in the traceability matrix?"
```

3. **Check architecture decisions:**

```bash
nlm notebook query --notebook <NLM_ARCH_ID> \
  --question "What architectural decisions have been made about
  the clinical alerts pipeline and drug interaction checking?"
```

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

8. **Run /analyze to validate consistency:**

```bash
/analyze
# This checks that specs, plans, and tasks are aligned
# Fix any issues flagged by the analyzer
```

9. **Commit the specification and plan:**

```bash
git add .specify/
git commit -m "spec: add medication interaction alerts specification

Relates to: SYS-REQ-0006, SUB-MM-0001, SUB-MM-0002
Spec-Kit phase: Specify + Plan"
```

10. **Push spec to NotebookLM:**

```bash
nlm source add --notebook <NLM_REQ_ID> \
  --file .specify/specs/medication-interaction-alerts.md
nlm source add --notebook <NLM_ARCH_ID> \
  --file .specify/plans/medication-interaction-alerts-plan.md
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
- NotebookLM updated with spec and plan

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

4. **Push evidence to NotebookLM:**

```bash
nlm source add --notebook <NLM_TEST_ID> \
  --file docs/coverage-report.md
nlm source add --notebook <NLM_REQ_ID> \
  --file docs/traceability-matrix.md
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

13. **Push final evidence to NotebookLM:**

```bash
# Get the merged PR review data
gh pr view <PR_NUMBER> --comments --json comments \
  > docs/reviews/pr-<PR_NUMBER>-review.json

claude
# "Summarize the CodeRabbit review and SonarQube results for
# PR #<PR_NUMBER>. Map findings to requirement IDs. Generate
# docs/reviews/pr-<PR_NUMBER>-evidence-summary.md"

nlm source add --notebook <NLM_QS_ID> \
  --file docs/reviews/pr-<PR_NUMBER>-evidence-summary.md
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

# Query NotebookLM for context on the requirements involved
nlm notebook query --notebook <NLM_REQ_ID> \
  --question "What are the requirements and acceptance criteria
  for <FEATURE_NAME>?"
```

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

### Query NotebookLM Before Coding

Before writing code, always check what already exists:

```bash
# Check for existing patterns you should follow
nlm notebook query --notebook <NLM_ARCH_ID> \
  --question "What design patterns are used for <SIMILAR_FEATURE>
  and what architectural constraints apply?"

# Check debugging knowledge for known issues
nlm notebook query --notebook <NLM_QS_ID> \
  --question "Are there known issues or gotchas related to
  <TECHNOLOGY_OR_MODULE> in the PMS codebase?"
```

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

1. **Check the debugging notebook first:**

```bash
nlm notebook query --notebook <NLM_QS_ID> \
  --question "Has anyone encountered <ERROR_MESSAGE_OR_ISSUE>
  in the PMS project? What was the solution?"
```

2. **If no solution found, solve it and add the solution back:**

```bash
# After solving the issue
claude
# "Document the bug I just fixed: <DESCRIPTION>.
# Generate a debugging note for docs/debugging/<ISSUE>.md
# that includes the error message, root cause, and fix."

nlm source add --notebook <NLM_QS_ID> \
  --file docs/debugging/<ISSUE>.md
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

### Push Updated Evidence to NotebookLM

```bash
# If you updated the RTM or coverage report
nlm source add --notebook <NLM_REQ_ID> \
  --file docs/traceability-matrix.md

# If you created or updated an architecture decision
nlm source add --notebook <NLM_ARCH_ID> \
  --file docs/adr/<NEW_DECISION>.md
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
| 10:00 AM | Feature work: query NotebookLM → implement → test | P2 |
| 12:00 PM | Lunch break | — |
| 1:00 PM | Check CI results, continue feature work | P2 |
| 3:00 PM | Run tests and local quality scans | — |
| 4:00 PM | Follow up on PR reviews | P0 |
| 4:30 PM | Commit all changes, push, update RTM, update NotebookLM | — |

---

## Quick Reference: Common Commands

```bash
# === NotebookLM ===
nlm notebook query --notebook <ID> --question "..."   # Query a notebook
nlm source add --notebook <ID> --file <FILE>           # Add source

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

*For the complete development process tutorial, see the [NotebookLM Development Tutorial](./NotebookLM_Development_Tutorial.md).*
