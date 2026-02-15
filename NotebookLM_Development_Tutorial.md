# Development Pipeline Tutorial

**How to Build an Auditable Development Pipeline with AI Agents**

Extended Edition: Claude Code + GitHub Spec Kit for IEEE/DOD-Style Requirements Engineering — With SonarQube, CodeRabbit & Snyk for Continuous Code Quality and Security Monitoring

*Featuring a Healthcare Patient Management System Case Study*

Based on the video tutorial by AI Labs Pro — [Watch the original video on YouTube](https://youtu.be/eFCHwtufjJc)

---

## Table of Contents

### Compliance Evidence Storage Policy

- [Compliance Evidence Storage Policy](#compliance-evidence-storage-policy)

### PART I — Knowledge Management Fundamentals

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Step 1: Set Up the docs/ Knowledge Base](#step-1-set-up-the-docs-knowledge-base)
- [Step 2: Configure Your AI Agent](#step-2-configure-your-ai-agent)
- [Step 3: Second Brain for AI Agents](#step-3-set-up-docs-as-a-second-brain-for-ai-agents)
- [Step 4: Enhanced Research Workflows](#step-4-enhanced-research-workflows)
- [Step 5: Codebase Understanding with RepoMix](#step-5-understand-codebases-with-repomix)
- [Step 6: Debugging Knowledge Base](#step-6-build-a-dedicated-debugging-knowledge-base)
- [Step 7: Cross-Tool Context Builder](#step-7-cross-tool-context-builder)
- [Step 8: Agent Navigation via Visualizations](#step-8-agent-navigation-via-visualizations)
- [Step 9: Grounded Security Audits](#step-9-grounded-security-audits)

### PART II — Requirements Engineering & Traceability

- [Step 10: Initialize GitHub Spec Kit](#step-10-initialize-github-spec-kit-for-spec-driven-development)
- [Step 11: System & Subsystem Requirements](#step-11-define-system-level-and-subsystem-level-requirements)
- [Step 12: Requirements Traceability Matrix](#step-12-build-the-requirements-traceability-matrix-rtm)
- [Step 13: Automated Test Coverage Tracking](#step-13-automated-test-coverage-tracking)
- [Step 14: Living Requirements Dashboard](#step-14-living-requirements-dashboard)

### PART III — Code Quality, Reviews & Security Monitoring

- [Step 15: SonarQube Code Quality Gates](#step-15-sonarqube-code-quality-gates-with-evidence-archival)
- [Step 16: CodeRabbit AI-Powered PR Reviews](#step-16-coderabbit-ai-powered-pull-request-reviews)
- [Step 17: Snyk Continuous Security Monitoring](#step-17-snyk-continuous-security-monitoring)
- [Evidence Pipeline Architecture](#evidence-pipeline-architecture)
- [Summary & Next Steps](#summary--next-steps)

---

## Compliance Evidence Storage Policy

> **This policy applies to all evidence workflows described in this tutorial.**

### Authoritative Evidence Store

The **GitHub repository** is the authoritative, permanent source of truth for all compliance evidence. Every piece of evidence — test reports, quality scans, security results, traceability matrices, coverage reports, SBOMs, and review summaries — **must be committed to the repository**.

| Store | Role | Retention | Properties |
|-------|------|-----------|------------|
| **GitHub Repository** | Primary / System of Record | **Permanent** (git history) | Versioned, tamper-evident, auditable, satisfies HIPAA 6-year requirement |
| **GitHub Actions Artifacts** | Ephemeral CI output | **90 days** | Convenience only — never rely on as sole evidence store |
| **`docs/` directory** | Queryable documentation layer | **Permanent** (committed to repo) | Markdown files committed alongside the code for easy reading and agent access |

### Evidence Commitment Rule

Every evidence-generating step in this tutorial must follow this sequence:

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

### Retention Comparison

| Evidence Type | Before (Artifact-Only) | After (Repository-First) |
|---------------|----------------------|--------------------------|
| SonarQube results | 90-day artifact | **Permanent** — committed to `docs/quality-reports/` |
| Snyk scan results | 90-day artifact | **Permanent** — committed to `docs/security/` |
| Test coverage | 90-day artifact | **Permanent** — committed to `docs/test-evidence/` |
| SBOM files | 90-day artifact | **Permanent** — committed to `docs/sbom/` |
| CodeRabbit reviews | PR comments (permanent) | PR comments + committed summary in `docs/reviews/` |
| /analyze output | Not stored | **Permanent** — committed to `docs/analyze/` |
| Evidence summaries | Not stored | **Permanent** — committed to `docs/evidence-summary.md` |

---

# PART I — Knowledge Management Fundamentals

## Introduction

A well-organized knowledge base is essential for modern AI-assisted development workflows. By storing all project knowledge as markdown files in a `docs/` directory within your repository, you ensure that documentation is version-controlled, always available, and directly accessible by AI agents and developers alike.

This tutorial covers seventeen steps across three parts. Part I covers knowledge management fundamentals using the `docs/` directory (Steps 1-9). Part II extends into IEEE/DOD-style requirements engineering with GitHub Spec Kit (Steps 10-14). Part III adds SonarQube code quality gates, CodeRabbit AI-powered reviews, and Snyk continuous security monitoring — with all evidence archived in the repository (Steps 15-17).

> **Why This Combination?**
> The `docs/` directory provides a reliable, version-controlled knowledge base. GitHub Spec Kit provides structured specification management. Claude Code provides autonomous implementation. SonarQube, CodeRabbit, and Snyk provide continuous quality and security verification. Together, they create a complete pipeline where requirements are defined, implemented, reviewed, tested, and monitored with full traceability and evidence.

---

## Prerequisites

Before you begin, make sure you have the following ready:

- Node.js and npm installed (for CLIs and tooling)
- Claude Code CLI installed
- Git and GitHub CLI (`gh`) installed
- GitHub Spec Kit CLI (`specify`) — covered in Step 10
- SonarQube instance or SonarCloud account — covered in Step 15
- CodeRabbit account — covered in Step 16
- Snyk account and CLI — covered in Step 17

> **Note:** The exact CLI package names and installation commands may vary as tools evolve. Check the official repositories for the latest instructions.

---

## Step 1: Set Up the docs/ Knowledge Base

The `docs/` directory in your repository serves as the central knowledge base for the entire project. All architectural decisions, implementation details, debugging notes, and compliance evidence live here.

### A. Create the Directory Structure

```bash
mkdir -p docs/{architecture,features,bugs,api,config,adr,security,quality-reports,reviews,test-evidence,sbom,analyze,debugging}
```

### B. Create the Index File

Create `docs/index.md` as the table of contents for your knowledge base:

```markdown
# Project Knowledge Base

This directory is the single source of truth for all project context,
decisions, and implementation details.

## Architecture Decisions
- [ADR-0001: Example Decision](architecture/0001-example-decision.md)

## Features
<!-- Add links to feature docs as they are completed -->

## Bug Fixes
<!-- Add links to bug analyses as they are resolved -->

## API Contracts
<!-- Add links to API docs as they are defined -->

## Configuration & Dependencies
<!-- Add links to config docs as they are established -->
```

### C. Commit the Initial Structure

```bash
git add docs/
git commit -m "docs: initialize docs/ knowledge base structure

- Directory structure for all project documentation
- Index file as table of contents"
git push
```

> **Best Practice:** Keep your `docs/index.md` updated as new documentation is added. This serves as the entry point for both developers and AI agents.

---

## Step 2: Configure Your AI Agent

Create an instructions file (`CLAUDE.md`) that tells your AI agent to use the `docs/` directory as its knowledge base.

### A. Create CLAUDE.md

```markdown
# CLAUDE.md — Agent Instructions

## Knowledge Management
- The `docs/` directory is the single source of truth for all project knowledge
- Always read relevant docs before starting work
- After completing a feature, update the docs with implementation details
- Never rely solely on conversation memory — persist decisions to docs/

## Documentation Rules
1. Read before you build — check docs/ for existing context
2. Keep docs focused — one topic per file
3. Update, don't duplicate — if a doc exists, update it
4. Docs are authoritative — they override any assumptions
5. Commit and push — every doc change must be committed
```

### B. Commit and Push

```bash
git add CLAUDE.md
git commit -m "docs: add AI agent instructions (CLAUDE.md)"
git push
```

---

## Step 3: Set Up docs/ as a Second Brain for AI Agents

This is the foundational workflow. The idea is to give your AI agent a persistent, structured knowledge base that survives context window resets and can be shared across sessions.

### A. Store Architectural Decisions

When making architecture decisions, create Architecture Decision Records (ADRs):

```bash
# In Claude Code:
"Create an ADR for the decision to use PostgreSQL over MongoDB.
Save it as docs/adr/0001-use-postgresql.md with the standard
ADR template: Context, Options Considered, Decision, Rationale,
Consequences."
```

### B. Store Implementation Details

After implementing a feature, document key details:

```bash
# In Claude Code:
"Document the authentication implementation.
Save it as docs/features/authentication.md covering:
architecture, key modules, configuration, and known limitations."
```

### C. Automate Updates

Add to your `CLAUDE.md`:

```markdown
## Post-Implementation Protocol
After completing any implementation task:
1. Update or create the relevant doc in docs/
2. Update docs/index.md with the new link
3. Commit and push the changes
```

> **Best Practice:** Keep your docs organized by topic. Use separate files for architecture decisions, API documentation, feature specs, and debugging notes.

---

## Step 4: Enhanced Research Workflows

The `docs/` directory excels at research because it provides grounded, traceable context that any agent or developer can reference.

1. **Delegate the research topic** — Tell your AI agent what to research. It will find relevant sources and compile them.
2. **Save research findings** — The agent saves compiled research as markdown in `docs/`:

```bash
# In Claude Code:
"Research the best practices for HIPAA-compliant data encryption.
Save your findings to docs/research/hipaa-encryption-practices.md
with citations and recommendations."
```

3. **Reference in future sessions** — Instead of re-researching, agents and developers read the saved findings directly from `docs/`.

> **Tip:** Committing research to the repo means it's version-controlled. If recommendations change, update the file and the git history preserves the full evolution.

---

## Step 5: Understand Codebases with RepoMix

One of the most powerful use cases: turning an entire codebase into a structured knowledge document.

### A. Clone the Repository

```bash
gh repo clone owner/repository-name
```

### B. Install and Run RepoMix

```bash
npm install -g repomix
repomix --output codebase.txt
```

### C. Generate Documentation from the Codebase

In Claude Code:

```
"Analyze codebase.txt and generate:
1. docs/architecture/system-overview.md — module relationships and dependencies
2. docs/api/endpoints.md — all API endpoints with their handlers
3. docs/architecture/data-flow.md — data flow through the system"
```

### D. Commit the Documentation

```bash
git add docs/architecture/ docs/api/
git commit -m "docs: generate codebase documentation from RepoMix analysis"
git push
```

> **Tip:** For large codebases, consider using RepoMix with filters to focus on specific directories or file types.

---

## Step 6: Build a Dedicated Debugging Knowledge Base

Instead of relying on generic web searches for debugging, build a curated knowledge base that your agent consults first.

### A. Create the Debugging Directory

```bash
mkdir -p docs/debugging
```

### B. Document Solutions as You Find Them

When you fix a bug, document the solution:

```bash
# In Claude Code:
"Document the fix for the database connection timeout issue.
Save it as docs/debugging/db-connection-timeout.md with:
- Error message
- Root cause
- Solution
- Prevention tips"
```

### C. Configure Agent Priority

Update your `CLAUDE.md`:

```markdown
When encountering a bug:
1. First, check docs/debugging/ for known solutions
2. Only if no relevant solution is found, perform a web search
3. If you find a new solution, save it to docs/debugging/ for future use
```

> **Pro Tip:** Over time, this creates a self-improving knowledge base tailored to your exact tech stack.

---

## Step 7: Cross-Tool Context Builder

The `docs/` directory serves as a shared context layer accessible by multiple tools and team members.

### A. Centralize Documentation

```bash
docs/
├── api/
│   └── api-reference.md       # API endpoints and contracts
├── architecture/
│   └── system-overview.md     # System architecture
├── config/
│   └── deployment-guide.md    # Deployment configuration
└── index.md                   # Table of contents
```

### B. Enable Cross-Tool Access

Any AI agent with repository access can read the `docs/` directory:

- **Claude Code** reads docs directly from the filesystem
- **GitHub Copilot** can reference docs in pull request context
- **CI/CD pipelines** can validate documentation completeness
- **New team members** can onboard by reading `docs/index.md`

---

## Step 8: Agent Navigation via Visualizations

Visualizations are not just for humans. AI agents can use structured documentation to navigate codebases more efficiently than crawling file systems.

### A. Generate Structured Navigation Files

In Claude Code:

```
"Generate docs/architecture/module-map.md listing all modules,
their responsibilities, key files, and dependencies."

"Generate docs/api/endpoint-table.md as a markdown table mapping
every API endpoint to its handler file and HTTP method."
```

### B. Configure Agent to Use Navigation Files

```markdown
When navigating the codebase:
1. Check docs/architecture/module-map.md for module structure
2. Consult docs/api/endpoint-table.md for API routes
3. Only crawl the file system if the documentation is insufficient
```

This approach is faster, uses fewer tokens, and gives the agent structured context rather than raw file contents.

---

## Step 9: Grounded Security Audits

Perform security audits where every finding is backed by authoritative sources, not just AI inference.

### A. Create Security Reference Documentation

```bash
# In Claude Code:
"Create docs/security/security-handbook.md covering:
- OWASP Top 10 checklist for our tech stack
- Security best practices for Node.js/TypeScript
- Our custom security policies and compliance requirements"
```

### B. Add Security Sources

- OWASP cheat sheets and guidelines
- Security best practices for your specific tech stack
- Custom security policies and compliance requirements

### C. Run Grounded Security Checks

In Claude Code:

```
"Review src/auth/ for security vulnerabilities. Cross-reference
your findings with docs/security/security-handbook.md and cite
the relevant OWASP guidelines. Save the audit report to
docs/security/audit-<DATE>.md."
```

> **Security Note:** While docs-grounded audits are valuable, they should complement — not replace — professional security reviews and automated scanning tools for production systems.

---

# PART II — Requirements Engineering & Traceability

## Claude Code + GitHub Spec Kit

This section extends the `docs/` workflow into a full **requirements engineering pipeline** using IEEE/DOD-style conventions. We use a **Healthcare Patient Management System (PMS)** as a running example, covering HIPAA compliance, HL7 FHIR interoperability, and FDA software validation requirements.

> **The Three-Tool Architecture**
> GitHub Spec Kit defines what to build (specifications). Claude Code builds it (implementation). The `docs/` directory remembers everything and provides the knowledge base. Together they create an auditable chain from requirements through testing.

---

## Case Study: Healthcare Patient Management System

Throughout Part II and Part III, we build the requirements structure for a PMS with these characteristics:

- Multi-facility healthcare organization serving 50+ clinics
- HIPAA-compliant patient data handling with audit trails
- HL7 FHIR R4 interoperability for EHR data exchange
- Role-based access control (physicians, nurses, administrators, billing)
- Real-time clinical alerts and medication interaction checking

The system decomposes into four subsystems:

| Subsystem | Prefix | Scope |
|-----------|--------|-------|
| Patient Records | SUB-PR | Demographics, medical history, documents, consent |
| Clinical Workflow | SUB-CW | Scheduling, encounters, orders, referrals |
| Medication Management | SUB-MM | Prescriptions, interactions, formulary, dispensing |
| Reporting & Analytics | SUB-RA | Clinical dashboards, compliance reports, audit logs |

---

## Step 10: Initialize GitHub Spec Kit for Spec-Driven Development

GitHub Spec Kit is an open-source toolkit that puts structure and intent at the heart of AI-assisted software development. It establishes a four-phase gated development process: Specify, Plan, Tasks, and Implement.

### A. Install and Initialize Spec Kit

```bash
# Install the Specify CLI
npm install -g @github/specify

# Initialize in your project root
cd patient-management-system
specify init
```

This creates two key directories:

- `.github/` — Agent prompts and slash command definitions
- `.specify/` — Specifications, technical plans, task breakdowns, and helper scripts

### B. Configure Claude Code Integration

Create a `CLAUDE.md` at the repository root that links all tools:

```markdown
# CLAUDE.md — Agent Instructions for PMS Development

## Development Methodology
This project uses Spec-Driven Development (SDD).
Always use /specify, /plan, /analyze before implementing.

## Knowledge Base
All project documentation lives in the `docs/` directory.
Read relevant docs before starting any work.

## Requirements Convention (IEEE 830 / DOD-STD-498)
- System requirements: SYS-REQ-XXXX
- Subsystem requirements: SUB-{code}-XXXX

## Workflow
1. /specify → Define requirements
2. /plan → Technical implementation plan
3. /analyze → Validate consistency
4. Implement → Claude Code writes code
5. Review → SonarQube + CodeRabbit
6. Scan → Snyk security monitoring
7. Archive → Commit evidence to docs/
```

### C. Create Knowledge Base Structure

Set up the `docs/` directory with subdirectories for all evidence types:

```bash
mkdir -p docs/{architecture,adr,features,security,quality-reports,reviews,test-evidence,sbom,analyze,debugging}
```

Create `docs/index.md` as the central table of contents and commit:

```bash
git add docs/
git commit -m "docs: initialize knowledge base structure for PMS"
git push
```

> **Best Practice:** Keep `docs/index.md` updated as you add documentation, so every agent session can immediately find the right knowledge.

---

## Step 11: Define System-Level and Subsystem-Level Requirements

Using the GitHub Spec Kit `/specify` command, Claude Code generates structured requirements at two levels following IEEE 830 / DOD-STD-498 conventions.

### A. System-Level Requirements (SYS-REQ)

```bash
/specify

# Prompt: "Define system-level requirements for a HIPAA-compliant
# Patient Management System supporting 50+ clinics with HL7 FHIR
# interoperability, role-based access, and real-time clinical alerts."
```

| Req ID | Description | Priority | Verification |
|--------|-------------|----------|--------------|
| SYS-REQ-0001 | Authenticate all users via MFA before granting access to patient data | Critical | Test / Demo |
| SYS-REQ-0002 | Encrypt all patient data at rest (AES-256) and in transit (TLS 1.3) | Critical | Inspection |
| SYS-REQ-0003 | Maintain complete audit trail of all data access and modifications | Critical | Test |
| SYS-REQ-0004 | Support HL7 FHIR R4 for patient data exchange with external EHRs | High | Test / Demo |
| SYS-REQ-0005 | Enforce RBAC with minimum four roles: physician, nurse, admin, billing | Critical | Test |
| SYS-REQ-0006 | Generate real-time clinical alerts for critical lab values within 30 seconds | High | Test |
| SYS-REQ-0007 | Support 500+ concurrent users with response times under 2 seconds | High | Test |

### B. Subsystem-Level Requirements (SUB-XX)

Example decomposition for the Medication Management subsystem:

| Req ID | Parent | Description | Verification |
|--------|--------|-------------|--------------|
| SUB-MM-0001 | SYS-REQ-0006 | Check new prescriptions against active medications within 5 seconds | Test |
| SUB-MM-0002 | SYS-REQ-0006 | Classify drug interactions: contraindicated, major, moderate, minor | Test |
| SUB-MM-0003 | SYS-REQ-0002 | Encrypt all prescription data using AES-256 | Inspection |
| SUB-MM-0004 | SYS-REQ-0003 | Log all prescription events with prescriber ID and timestamp | Test |
| SUB-MM-0005 | SYS-REQ-0004 | Support FHIR R4 MedicationRequest and MedicationDispense resources | Test / Demo |

### C. Commit Requirements to the Repository

```bash
git add .specify/specs/
git commit -m "spec: define system and subsystem requirements

- SYS-REQ-0001 through SYS-REQ-0007
- SUB-PR, SUB-CW, SUB-MM, SUB-RA decompositions
Follows IEEE 830 / DOD-STD-498 conventions"
git push
```

> **IEEE 830 Compliance:** Each requirement must be uniquely identifiable, unambiguous, verifiable, and traceable. The hierarchical ID scheme (SYS-REQ → SUB-XX) ensures every subsystem requirement traces back to a system-level need.

---

## Step 12: Build the Requirements Traceability Matrix (RTM)

The Requirements Traceability Matrix is the backbone of auditable software development. It links every requirement to its design artifacts, source code, and test cases.

### A. Use Claude Code to Generate the RTM

```bash
# In Claude Code:
"Build a requirements traceability matrix for the PMS project.
Map each SYS-REQ to its child SUB requirements, design documents,
source modules, test case IDs, and verification status.
Output as both markdown and a structured JSON file."
```

### B. Forward Traceability (Requirements → Implementation)

This view answers: "Has every requirement been implemented and tested?"

| System Req | Subsystem Reqs | Source Module(s) | Test Case(s) | Status |
|------------|----------------|------------------|--------------|--------|
| SYS-REQ-0001 (MFA) | SUB-PR-0001, SUB-CW-0001 | src/auth/mfa/, src/auth/rbac/ | TC-AUTH-001, TC-AUTH-002, TC-AUTH-003 | Verified |
| SYS-REQ-0002 (Encryption) | SUB-MM-0003, SUB-PR-0004 | src/crypto/, src/db/encryption/ | TC-SEC-001, TC-SEC-002 | Verified |
| SYS-REQ-0006 (Alerts) | SUB-MM-0001, SUB-MM-0002, SUB-CW-0005 | src/alerts/, src/medications/interactions/ | TC-MED-001, TC-MED-002, TC-ALT-001 | In Progress |

### C. Backward Traceability (Tests → Requirements)

This view answers: "Does every test verify a real requirement?"

| Test Case | Description | Traces To | Result | Evidence |
|-----------|-------------|-----------|--------|----------|
| TC-AUTH-001 | Verify MFA login with valid TOTP | SYS-REQ-0001, SUB-PR-0001 | PASS | test-report-auth-001.html |
| TC-AUTH-002 | Verify MFA rejects expired TOTP | SYS-REQ-0001, SUB-PR-0001 | PASS | test-report-auth-002.html |
| TC-SEC-001 | Verify AES-256 encryption at rest | SYS-REQ-0002, SUB-MM-0003 | PASS | encryption-audit.pdf |
| TC-MED-001 | Drug interaction check < 5 sec | SYS-REQ-0006, SUB-MM-0001 | PASS | perf-test-med-001.json |
| TC-MED-002 | Interaction severity classification | SYS-REQ-0006, SUB-MM-0002 | FAIL | bug-report-MM-042.md |

### D. Commit the RTM

```bash
git add docs/traceability-matrix.md docs/traceability-matrix.json
git commit -m "evidence: add requirements traceability matrix

- Forward and backward traceability for all SYS-REQ and SUB requirements
- Maps requirements to design, source modules, tests, and verification status"
git push
```

Now anyone can review traceability by reading `docs/traceability-matrix.md`:

> "Which subsystem requirements trace to SYS-REQ-0006 and what is their current test status?"

> **Regulatory Requirement:** For FDA-regulated medical software (IEC 62304), the traceability matrix is a mandatory deliverable. Storing it in the repository ensures auditors and developers can query specific traceability chains on demand.

---

## Step 13: Automated Test Coverage Tracking

With requirements and traceability in place, ensure every requirement has adequate test coverage and that results flow back into the knowledge base.

### A. Define Test-to-Requirement Mapping in Spec Kit

```bash
/speckit.tasks

# Prompt: "Generate test tasks for all SUB-MM requirements.
# Each test task must reference the requirement ID,
# specify the test type (unit/integration/system),
# and define pass/fail criteria."
```

### B. Claude Code Generates Test Scaffolding

```typescript
// test/medications/interaction-check.test.ts
// @requirement SUB-MM-0001
// @requirement SUB-MM-0002
// @verification-method Test
// @priority Critical

describe('Drug Interaction Checker', () => {
  test('checks interactions within 5 seconds', async () => {
    // SUB-MM-0001: Performance requirement
    const start = Date.now();
    const result = await checkInteractions(prescription);
    expect(Date.now() - start).toBeLessThan(5000);
  });

  test('classifies severity levels', () => {
    // SUB-MM-0002: Classification requirement
    const result = classifyInteraction(drugA, drugB);
    expect(['contraindicated', 'major',
      'moderate', 'minor']).toContain(result.severity);
  });
});
```

### C. Coverage Report Generation

```bash
# Run tests and generate coverage report
npm test -- --reporter=json > test-results.json
```

In Claude Code:

```
"Parse test-results.json and cross-reference with
docs/traceability-matrix.md. Generate a coverage report
showing: requirements with passing tests, requirements with
failing tests, and requirements with no tests. Save it as
docs/coverage-report.md."
```

Commit the coverage report to the repository:

```bash
git add docs/coverage-report.md test-results.json
git commit -m "evidence: generate requirement test coverage report

- Cross-referenced test results with traceability matrix
- Coverage summary by subsystem with gap analysis"
git push
```

### D. Coverage Summary Dashboard

| Subsystem | Total Reqs | Tested | Passing | Failing | No Tests | Coverage |
|-----------|-----------|--------|---------|---------|----------|----------|
| Patient Records (PR) | 12 | 11 | 10 | 1 | 1 | 91.7% |
| Clinical Workflow (CW) | 15 | 13 | 12 | 1 | 2 | 86.7% |
| Medication Mgmt (MM) | 8 | 7 | 6 | 1 | 1 | 87.5% |
| Reporting (RA) | 6 | 4 | 4 | 0 | 2 | 66.7% |
| **TOTAL** | **41** | **35** | **32** | **3** | **6** | **85.4%** |

> **Gap Analysis:** Requirements with no tests (6 in this example) represent verification gaps. Claude Code can be directed to prioritize writing tests for these uncovered requirements.

---

## Step 14: Living Requirements Dashboard

The final step of Part II ties everything together: the `docs/` directory becomes the living, queryable dashboard for your entire requirements engineering pipeline.

### A. Consolidate All Artifacts

> **Reminder:** Per the [Compliance Evidence Storage Policy](#compliance-evidence-storage-policy), all artifacts must be committed to the repository.

In Claude Code, consolidate artifacts into the `docs/` directory:

```
"Organize the following artifacts into docs/:

docs/ directory structure:
- .specify/specs/ → requirements specifications
- docs/traceability-matrix.md → RTM
- docs/adr/ → architecture decision records
- docs/coverage-report.md → test coverage
- docs/test-evidence/ → test execution reports

Ensure docs/index.md links to all of these."
```

### B. Query Patterns for Requirements Engineering

| Query Type | How to Find the Answer | Look In |
|------------|----------------------|---------|
| Traceability | Which test cases verify SYS-REQ-0002 and are any failing? | `docs/traceability-matrix.md` |
| Coverage Gap | Which subsystem requirements have no associated test cases? | `docs/coverage-report.md` |
| Impact Analysis | If we change SYS-REQ-0004, which subsystem requirements and tests are affected? | `docs/traceability-matrix.md` + `.specify/specs/` |
| Compliance | Show all requirements related to HIPAA Security Rule audit trail provisions | `.specify/specs/` + `docs/security/` |
| Design Rationale | Why did we choose event-driven architecture for the clinical alerts pipeline? | `docs/adr/` |
| Regression Risk | Which areas have the most failing tests and what requirements do they cover? | `docs/test-evidence/` + `docs/traceability-matrix.md` |

### C. Automate the Update Cycle

Add to `CLAUDE.md`:

```markdown
## Post-Implementation Protocol
After completing any implementation task:
1. Run /analyze to verify spec consistency
2. Run tests and generate coverage-report.md
3. Update the traceability matrix
4. git add and git commit all updated evidence files
5. git push to the remote repository
6. If a new architectural decision was made,
   create an ADR and commit it
```

> **The Complete Pipeline:** Specify (GitHub Spec Kit) → Plan → Analyze → Implement (Claude Code) → Test → Trace → Store (docs/) → Review & Verify. Every stage is documented, every decision is grounded, and every requirement is traceable from inception through verification.

---

# PART III — Code Quality, Reviews & Security Monitoring

This section closes the development loop by adding **continuous code quality verification** (SonarQube), **AI-powered peer review** (CodeRabbit), and **continuous security monitoring** (Snyk). Crucially, all output is stored as evidence in the **GitHub repository** for auditing and traceability.

> **The Evidence Pipeline Principle**
> Every tool in the pipeline produces artifacts. Every artifact is **committed to the GitHub repository** as the permanent system of record. Committed files in `docs/` — not ephemeral CI artifacts — are the authoritative evidence store. Nothing is lost; everything is versioned and tamper-evident.

---

## Step 15: SonarQube Code Quality Gates with Evidence Archival

SonarQube performs static code analysis across 30+ languages, measuring code quality metrics like bugs, vulnerabilities, code smells, coverage, and duplication. It enforces quality gates that must pass before code merges.

### A. Configure SonarQube for the PMS Project

Create a `sonar-project.properties` file in the repository root:

```properties
sonar.projectKey=pms-healthcare
sonar.projectName=Patient Management System
sonar.sources=src
sonar.tests=test
sonar.language=ts
sonar.javascript.lcov.reportPaths=coverage/lcov.info
sonar.qualitygate.wait=true
```

### B. GitHub Actions Workflow for SonarQube

```yaml
# .github/workflows/sonarqube.yml
name: SonarQube Quality Gate
on:
  push:
    branches: [main, develop]
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  sonarqube:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run Tests with Coverage
        run: npm test -- --coverage

      - name: SonarQube Scan
        uses: SonarSource/sonarqube-scan-action@v2
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ vars.SONAR_HOST_URL }}

      - name: Quality Gate Check
        id: quality-gate
        uses: SonarSource/sonarqube-quality-gate-action@master
        timeout-minutes: 5
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ vars.SONAR_HOST_URL }}

      - name: Archive SonarQube Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: sonarqube-report-${{ github.sha }}
          path: .sonarqube/
          retention-days: 90

      - name: Commit SonarQube Evidence
        if: always()
        run: |
          mkdir -p docs/quality-reports
          cp -r .sonarqube/ docs/quality-reports/sonarqube-${{ github.sha }}/
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add docs/quality-reports/
          git commit -m "evidence(ci): archive SonarQube results for ${{ github.sha }}

          - Quality gate status and metrics committed to docs/quality-reports/
          - Permanent evidence per Compliance Evidence Storage Policy" || true
          git push || true
```

### C. Map Quality Metrics to Requirements

| Quality Metric | Threshold | Traces To | Evidence Location |
|---------------|-----------|-----------|-------------------|
| Security Hotspots | 0 critical | SYS-REQ-0002 (Encryption) | GitHub: Code Scanning alerts |
| Code Coverage | > 80% | All SUB-*-* requirements | GitHub: Actions artifact |
| Duplicated Lines | < 3% | SYS-REQ-0007 (Performance) | SonarQube dashboard |
| Bugs | 0 blockers | All SYS-REQ-* | GitHub: PR status check |
| Reliability Rating | A | SYS-REQ-0006 (Alerts) | `docs/quality-reports/` |

### D. Commit and Archive Quality Evidence

After each CI run, use Claude Code to export and generate quality evidence:

```
"Extract the SonarQube quality gate results from .sonarqube/
and generate a quality-report.md with metrics, findings, and
requirement traceability mappings. Save it as
docs/quality-reports/quality-report-<TODAY>.md."
```

Commit the quality report to the repository:

```bash
git add docs/quality-reports/quality-report-<TODAY>.md
git commit -m "evidence: SonarQube quality report for <TODAY>

- Quality gate metrics and findings with requirement traceability
Relates to: SYS-REQ-0002, SYS-REQ-0007"
git push
```

To review historical quality trends, read through the reports in `docs/quality-reports/`.

> **Quality Gate as Gatekeeper:** Configure GitHub branch protection rules to require a passing SonarQube quality gate before merging PRs.

---

## Step 16: CodeRabbit AI-Powered Pull Request Reviews

CodeRabbit provides AI-driven code review that goes beyond static analysis. It understands context, identifies logic issues, suggests improvements, and provides line-by-line feedback on every pull request.

### A. Install and Configure CodeRabbit

```bash
# Install CLI
curl -fsSL https://cli.coderabbit.ai/install.sh | sh

# Local review (e.g., before pushing)
coderabbit review --plain
coderabbit review --type uncommitted --plain
coderabbit review --base main --plain
```

### B. GitHub Actions Integration

```yaml
# .github/workflows/coderabbit.yml
name: CodeRabbit Review
on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  pull-requests: write
  contents: read

jobs:
  coderabbit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: CodeRabbit Review
        uses: coderabbitai/github-action@latest
        env:
          CODERABBIT_TOKEN: ${{ secrets.CODERABBIT_TOKEN }}
```

### C. Configure Requirement-Aware Reviews

Create a `.coderabbit.yaml` that instructs CodeRabbit to check against your requirements:

```yaml
reviews:
  instructions: |
    This is a HIPAA-compliant healthcare application.
    When reviewing code, verify:
    1. All patient data access includes audit logging (SYS-REQ-0003)
    2. Encryption is applied to PHI fields (SYS-REQ-0002)
    3. RBAC checks precede data access (SYS-REQ-0005)
    4. Drug interaction checks meet 5-second SLA (SUB-MM-0001)
    5. FHIR resource handling follows R4 spec (SYS-REQ-0004)
    Reference requirement IDs in your feedback.
```

### D. Evidence Collection from PR Reviews

CodeRabbit posts reviews directly as GitHub PR comments, creating a permanent audit trail. Additionally, extract, commit, and archive review summaries:

```bash
# Extract review evidence using GitHub CLI
gh pr view <PR_NUMBER> --comments --json comments \
  > docs/reviews/pr-<PR_NUMBER>-review.json
```

In Claude Code:

```
"Summarize the CodeRabbit review from
docs/reviews/pr-<PR_NUMBER>-review.json.
Map each finding to a requirement ID.
Generate docs/reviews/pr-<PR_NUMBER>-review-summary.md."
```

Commit the review evidence to the repository:

```bash
git add docs/reviews/pr-<PR_NUMBER>-review.json \
       docs/reviews/pr-<PR_NUMBER>-review-summary.md
git commit -m "evidence: archive CodeRabbit review for PR #<PR_NUMBER>

- Review findings mapped to requirement IDs
- Summary with remediation status"
git push
```

### E. Review Metrics Dashboard

| Metric | Current Sprint | Previous Sprint | Trend |
|--------|---------------|-----------------|-------|
| PRs Reviewed | 24 | 18 | Increasing |
| Issues Found (Critical) | 3 | 7 | Improving |
| Issues Found (Suggestions) | 41 | 52 | Improving |
| HIPAA Violations Caught | 2 | 5 | Improving |
| Average Review Time | < 3 min | < 3 min | Stable |
| Requirement References | 87% | 62% | Improving |

> **CodeRabbit + Claude Code Synergy:** When CodeRabbit identifies issues, Claude Code can be directed to fix them: "Fix all critical issues from the CodeRabbit review on PR #42, ensuring each fix references the associated requirement ID in the commit message."

---

## Step 17: Snyk Continuous Security Monitoring

Snyk provides continuous vulnerability scanning across three dimensions: open-source dependencies, container images, and your own source code (SAST). For a healthcare system handling PHI, this is not optional — it is a compliance requirement.

### A. Install and Authenticate Snyk

```bash
# Install Snyk CLI
npm install -g snyk

# Authenticate
snyk auth

# Initial scan of the project
snyk test --json-file-output=snyk-results.json
snyk code test --json-file-output=snyk-code-results.json
```

### B. Comprehensive GitHub Actions Pipeline

```yaml
# .github/workflows/snyk-security.yml
name: Snyk Security Scan
on:
  push:
    branches: [main, develop]
  pull_request:
  schedule:
    - cron: '0 6 * * 1'  # Weekly Monday scan

jobs:
  snyk-dependencies:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: snyk/actions/node@master
        continue-on-error: true
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: >-
            --severity-threshold=medium
            --json-file-output=snyk-deps.json
            --sarif-file-output=snyk-deps.sarif

      - name: Upload SARIF to Code Scanning
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: snyk-deps.sarif
          category: snyk-dependencies

      - name: Archive Results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: snyk-deps-${{ github.sha }}
          path: snyk-deps.json
          retention-days: 90

      - name: Commit Snyk Dependency Results
        if: always()
        run: |
          mkdir -p docs/security
          cp snyk-deps.json docs/security/snyk-deps-${{ github.sha }}.json
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add docs/security/
          git commit -m "evidence(ci): archive Snyk dependency scan for ${{ github.sha }}

          - Dependency vulnerability results committed to docs/security/
          - Permanent evidence per Compliance Evidence Storage Policy" || true
          git push || true

  snyk-code:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Snyk Code (SAST)
        uses: snyk/actions/node@master
        continue-on-error: true
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          command: code test
          args: --sarif-file-output=snyk-code.sarif

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: snyk-code.sarif
          category: snyk-code

  snyk-container:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t pms:latest .
      - uses: snyk/actions/docker@master
        continue-on-error: true
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          image: pms:latest
          args: >-
            --json-file-output=snyk-container.json
            --sarif-file-output=snyk-container.sarif

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: snyk-container.sarif
          category: snyk-container

      - name: Archive Container Results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: snyk-container-${{ github.sha }}
          path: snyk-container.json
          retention-days: 90

      - name: Commit Snyk Container Results
        if: always()
        run: |
          mkdir -p docs/security
          cp snyk-container.json docs/security/snyk-container-${{ github.sha }}.json
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add docs/security/
          git commit -m "evidence(ci): archive Snyk container scan for ${{ github.sha }}

          - Container vulnerability results committed to docs/security/
          - Permanent evidence per Compliance Evidence Storage Policy" || true
          git push || true
```

### C. Map Vulnerabilities to Requirements

| Snyk Finding | Severity | Traces To | Status | Evidence |
|--------------|----------|-----------|--------|----------|
| CVE-2025-XXXXX: SQL Injection in ORM | Critical | SYS-REQ-0002, SUB-PR-0004 | Remediated | snyk-deps.json + PR #67 |
| Insecure deserialization in FHIR parser | High | SYS-REQ-0004, SUB-MM-0005 | In Progress | snyk-code.sarif |
| Container base image: 3 high vulns | High | SYS-REQ-0007 (Availability) | Tracking | snyk-container.json |
| Outdated crypto dependency | Medium | SYS-REQ-0002 (Encryption) | Remediated | snyk-deps.json + PR #71 |
| Hardcoded credential in test fixture | Medium | SYS-REQ-0001 (MFA/Auth) | Remediated | snyk-code.sarif + PR #72 |

### D. Generate SBOM for Compliance

For FDA/HIPAA compliance, generate a Software Bill of Materials:

```bash
# Generate SBOM in CycloneDX format
snyk sbom --format cyclonedx > docs/sbom/sbom-cyclonedx.json

# Generate SBOM in SPDX format
snyk sbom --format spdx > docs/sbom/sbom-spdx.json
```

Commit the SBOM files to the repository:

```bash
git add docs/sbom/
git commit -m "evidence: generate SBOM for FDA/HIPAA compliance

- CycloneDX and SPDX format Software Bill of Materials
- Permanent evidence per Compliance Evidence Storage Policy"
git push
```

### E. Commit and Archive Security Evidence

After each security scan, use Claude Code to generate the security report:

```
"Analyze snyk-deps.json, snyk-code.sarif, and
snyk-container.json. Generate a security-report.md that:
1. Lists all findings by severity
2. Maps each to the relevant SYS-REQ/SUB requirement
3. Notes remediation status and PR references
4. Compares with previous report for trend analysis
Save it as docs/security/security-report-<TODAY>.md."
```

Commit the security report to the repository:

```bash
git add docs/security/security-report-<TODAY>.md
git commit -m "evidence: Snyk security report for <TODAY>

- Vulnerability findings by severity with requirement traceability
- Remediation status and trend analysis
Relates to: SYS-REQ-0001, SYS-REQ-0002"
git push
```

To review security posture at any time, read `docs/security/` for the latest reports.

```bash
# Continuous monitoring baseline
snyk monitor --json-file-output=snyk-monitor.json
```

> **HIPAA Compliance:** The HIPAA Security Rule requires covered entities to conduct risk analysis and implement security measures. Snyk scans, combined with the SBOM and vulnerability-to-requirement mapping, provide documentary evidence of ongoing security due diligence. Store all evidence with retention policies of at least 6 years per HIPAA requirements.

---

## Evidence Pipeline Architecture

All three tools (SonarQube, CodeRabbit, Snyk) feed into a repository-first evidence architecture.

### GitHub Evidence (Developer Workflow)

| Tool | GitHub Location | Retention | Access |
|------|----------------|-----------|--------|
| SonarQube | PR status checks + `docs/quality-reports/` (committed) | **Permanent** (git history) | Developers, CI/CD |
| CodeRabbit | PR review comments + `docs/reviews/` (committed) | **Permanent** (git history) | All PR participants |
| Snyk | Code Scanning alerts + `docs/security/` (committed) | **Permanent** (git history) | Security tab |
| Test Coverage | `docs/coverage-report.md` + `docs/test-evidence/` (committed) | **Permanent** (git history) | Developers, CI/CD |
| SBOM | `docs/sbom/` (committed) + Releases | **Permanent** (git history) | Compliance team |

### Automated Evidence Sync (CI/CD Post-Step)

```yaml
# .github/workflows/evidence-sync.yml
name: Generate Evidence Summary
on:
  workflow_run:
    workflows: ['SonarQube Quality Gate',
                'CodeRabbit Review',
                'Snyk Security Scan']
    types: [completed]

jobs:
  generate-summary:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Download Artifacts
        uses: actions/download-artifact@v4

      - name: Generate Evidence Summary
        run: |
          claude --print "Compile all scan results from artifacts/
            into a unified evidence-summary.md with:
            1. SonarQube quality gate status and metrics
            2. CodeRabbit review findings summary
            3. Snyk vulnerability counts by severity
            4. Requirement traceability for all findings
            5. Comparison with previous evidence summary
            Save to docs/evidence-summary.md"

      - name: Commit Evidence Summary
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add docs/evidence-summary.md
          git commit -m "evidence(ci): unified evidence summary for workflow run

          - Compiled SonarQube, CodeRabbit, and Snyk results
          - Requirement traceability and trend analysis
          - Permanent evidence per Compliance Evidence Storage Policy" || true
          git push || true
```

> **Repository-First Benefit:** The GitHub repository is the permanent, authoritative evidence store (satisfying HIPAA's 6-year retention requirement via git history). The `docs/` directory provides easy access for both developers and AI agents. Together, they ensure evidence is both actionable for developers and auditable for compliance teams — with the repo as the system of record.

---

## Summary & Next Steps

This tutorial covered seventeen steps across three parts for building a complete, auditable development pipeline:

| Part | Steps | Tools | Purpose |
|------|-------|-------|---------|
| I | 1-9 | docs/ directory | Knowledge management, research, debugging, security audits |
| II | 10-14 | Spec Kit + Claude Code + docs/ | IEEE/DOD requirements, traceability matrices, test coverage |
| III | 15-17 | SonarQube + CodeRabbit + Snyk | Code quality gates, AI reviews, continuous security monitoring |

### Key Takeaways

- **`docs/` directory** provides a reliable, version-controlled knowledge base accessible by all agents and developers
- **GitHub Spec Kit** enforces structure: no implementation without an approved specification
- **Claude Code** automates implementation, test scaffolding, evidence generation, and remediation
- **SonarQube** catches quality issues with enforceable gates before code merges
- **CodeRabbit** provides AI-powered reviews that reference your requirement IDs
- **Snyk** monitors dependencies, containers, and code for vulnerabilities continuously
- The **repository-first evidence pipeline** commits all evidence to GitHub (permanent, versioned, tamper-evident) — satisfying HIPAA's 6-year retention requirement
- For **regulated industries**, this pipeline produces audit-ready documentation with full traceability and no reliance on ephemeral CI artifacts

### Next Steps

- Set up your CI/CD pipeline with all three quality/security workflows
- Configure CodeRabbit with requirement-aware review instructions
- Run your first Snyk scan and generate the initial SBOM
- Establish the evidence-sync workflow to keep `docs/evidence-summary.md` current
- Create your compliance documentation in `docs/security/`

---

For the foundational walkthrough, [watch the original video on YouTube](https://youtu.be/eFCHwtufjJc). For GitHub Spec Kit, visit [github.com/github/spec-kit](https://github.com/github/spec-kit). For Snyk, visit [snyk.io](https://snyk.io). For CodeRabbit, visit [coderabbit.ai](https://coderabbit.ai).
