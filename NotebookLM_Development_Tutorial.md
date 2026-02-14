# Using NotebookLM as a Development Power Tool

**How to Integrate NotebookLM CLI with AI Agents for Smarter Development Workflows**

Extended Edition: Claude Code + GitHub Spec Kit + NotebookLM for IEEE/DOD-Style Requirements Engineering — With SonarQube, CodeRabbit & Snyk for Continuous Code Quality and Security Monitoring

*Featuring a Healthcare Patient Management System Case Study*

Based on the video tutorial by AI Labs Pro — [Watch the original video on YouTube](https://youtu.be/eFCHwtufjJc)

---

## Table of Contents

### Compliance Evidence Storage Policy

- [Compliance Evidence Storage Policy](#compliance-evidence-storage-policy)

### PART I — NotebookLM Fundamentals

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Step 1: Install the NotebookLM CLI Tool](#step-1-install-the-notebooklm-cli-tool)
- [Step 2: Authenticate with Your Google Account](#step-2-authenticate-with-your-google-account)
- [Step 3: Second Brain for AI Agents](#step-3-set-up-notebooklm-as-a-second-brain-for-ai-agents)
- [Step 4: Enhanced Research Workflows](#step-4-enhanced-research-workflows)
- [Step 5: Codebase Understanding with RepoMix](#step-5-understand-codebases-with-notebooklm-and-repomix)
- [Step 6: Debugging Knowledge Base](#step-6-build-a-dedicated-debugging-knowledge-base)
- [Step 7: Cross-Tool Context Builder](#step-7-cross-tool-context-builder)
- [Step 8: Agent Navigation via Visualizations](#step-8-agent-navigation-via-visualizations)
- [Step 9: Grounded Security Audits](#step-9-grounded-security-audits)

### PART II — Requirements Engineering & Traceability

- [Step 10: Initialize GitHub Spec Kit](#step-10-initialize-github-spec-kit-for-spec-driven-development)
- [Step 11: System & Subsystem Requirements](#step-11-define-system-level-and-subsystem-level-requirements)
- [Step 12: Requirements Traceability Matrix](#step-12-build-the-requirements-traceability-matrix-rtm)
- [Step 13: Automated Test Coverage Tracking](#step-13-automated-test-coverage-tracking)
- [Step 14: Living Requirements Dashboard](#step-14-living-requirements-dashboard-with-notebooklm)

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

The **GitHub repository** is the authoritative, permanent source of truth for all compliance evidence. Every piece of evidence — test reports, quality scans, security results, traceability matrices, coverage reports, SBOMs, and review summaries — **must be committed to the repository** before being pushed to NotebookLM.

| Store | Role | Retention | Properties |
|-------|------|-----------|------------|
| **GitHub Repository** | Primary / System of Record | **Permanent** (git history) | Versioned, tamper-evident, auditable, satisfies HIPAA 6-year requirement |
| **GitHub Actions Artifacts** | Ephemeral CI output | **90 days** | Convenience only — never rely on as sole evidence store |
| **NotebookLM** | Secondary / Query Layer | Platform-dependent | Indexes repo evidence for natural-language querying; not a legal record |

### Evidence Commitment Rule

Every evidence-generating step in this tutorial must follow this sequence:

1. **Generate** the evidence artifact (report, scan result, matrix, etc.)
2. **`git add`** the artifact to staging
3. **`git commit`** with a descriptive message referencing requirement IDs
4. **Then** push to NotebookLM (which indexes the committed file)

> **Never push evidence to NotebookLM without first committing it to the repository.** NotebookLM is a convenience layer for querying — the repo is the legal record.

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

# PART I — NotebookLM Fundamentals

## Introduction

Google NotebookLM has evolved into a powerful knowledge management platform. When paired with its CLI (command-line interface), it becomes indispensable for modern AI-assisted development workflows.

This tutorial covers seventeen steps across three parts. Part I covers NotebookLM fundamentals (Steps 1–9). Part II extends into IEEE/DOD-style requirements engineering with GitHub Spec Kit (Steps 10–14). Part III adds SonarQube code quality gates, CodeRabbit AI-powered reviews, and Snyk continuous security monitoring — with all evidence archived in both GitHub and NotebookLM (Steps 15–17).

> **💡 Why This Combination?**
> NotebookLM provides grounded, citation-backed answers. GitHub Spec Kit provides structured specification management. Claude Code provides autonomous implementation. SonarQube, CodeRabbit, and Snyk provide continuous quality and security verification. Together, they create a complete pipeline where requirements are defined, implemented, reviewed, tested, and monitored with full traceability and evidence.

---

## Prerequisites

Before you begin, make sure you have the following ready:

- A Google account (for NotebookLM authentication)
- Node.js and npm installed (for CLIs and tooling)
- Claude Code CLI installed
- Git and GitHub CLI (`gh`) installed
- GitHub Spec Kit CLI (`specify`) — covered in Step 10
- SonarQube instance or SonarCloud account — covered in Step 15
- CodeRabbit account — covered in Step 16
- Snyk account and CLI — covered in Step 17

> **⚠️ Note:** The exact CLI package names and installation commands may vary as tools evolve. Check the official repositories for the latest instructions.

---

## Step 1: Install the NotebookLM CLI Tool

*Video reference: 0:32*

The NotebookLM CLI provides terminal access to create notebooks, add sources, query content, and generate visualizations — all without opening a browser.

### Installation

```bash
npm install -g notebooklm-cli
```

### Verify Installation

```bash
nlm-cli --help
```

This displays the available commands: `init` (install skills to your AI assistant), `update` (update to latest version), and `versions` (show version info).

> **💡 Tip:** If the command is not found after installation, ensure your npm global bin directory is in your system PATH. Note: the binary is `nlm-cli`, not `nlm`.

---

## Step 2: Authenticate and Install Skills

*Video reference: 1:01*

Before you can interact with NotebookLM, you need to install the NotebookLM Skills into your AI assistant and authenticate with your Google account.

### Install NotebookLM Skills

```bash
nlm-cli init --ai claude
```

This installs the NotebookLM Skills into Claude Code, enabling MCP-based notebook operations (creating notebooks, adding sources, generating learning materials). Supported AI assistants: `claude`, `cursor`, `windsurf`, `continue`.

### Authenticate

```bash
nlm login
```

This opens a browser window where you sign in with your Google account. Once authenticated, credentials are saved locally so you do not need to sign in again for subsequent sessions.

1. **Run the command above** — A browser window will open automatically.
2. **Sign in with Google** — Use the Google account associated with your NotebookLM.
3. **Return to your terminal** — The CLI confirms authentication was successful.

> **⚠️ Important:** All notebook operations (creating notebooks, adding sources, generating content) are performed through Claude Code's MCP tools (`notebooklm-mcp:*`), not via direct terminal commands. Querying notebooks is done through the NotebookLM web interface at [notebooklm.google.com](https://notebooklm.google.com).

---

## Step 3: Set Up NotebookLM as a Second Brain for AI Agents

*Video reference: 1:24*

This is the foundational workflow. The idea is to give your AI agent a persistent, structured knowledge base that survives context window resets and can be shared across sessions.

### A. Instruct Your Agent via a .md File

Create an instructions file (e.g., `CLAUDE.md` or `AGENTS.md`) that tells your AI agent to store all project knowledge in NotebookLM. Include directives like:

- Store all architectural decisions in the NotebookLM notebook
- After completing a feature, update the notebook with implementation details
- Use the notebook as the single source of truth for project context

### B. Create the Notebook

In Claude Code, ask it to create a notebook:

```
"Create a NotebookLM notebook titled 'Project: My App'."
```

Claude Code will use the `notebooklm-mcp:notebook_create` MCP tool. Save the returned notebook ID in your instructions file so the agent always knows which notebook to update.

### C. Automate Updates

In Claude Code, ask it to add sources:

```
"Add ./docs/feature-auth.md as a source to the 'Project: My App' notebook (<ID>)."
```

Claude Code will use the `notebooklm-mcp:source_add` MCP tool to upload the file.

> **💡 Best Practice:** Keep your notebook organized by topic. Use separate sources for architecture decisions, API documentation, feature specs, and meeting notes.

---

## Step 4: Enhanced Research Workflows

*Video reference: 2:36*

NotebookLM excels at research because it grounds answers in the sources you provide. Here is how to set up a research pipeline:

1. **Delegate the research topic** — Tell your AI agent what to research. It will find relevant sources and compile them.
2. **Create a research notebook** — The agent creates a new NotebookLM notebook and uploads all collected sources.
3. **Clear agent context** — Once sources are safely in NotebookLM, clear the agent's conversation context to avoid token bloat.
4. **Query the notebook** — Instead of re-reading all sources, query for specific findings through the NotebookLM web interface at [notebooklm.google.com](https://notebooklm.google.com):

> "What are the key findings on X?"

The response comes grounded in your uploaded sources with citations, ensuring high accuracy and traceability.

> **⚠️ Important:** Clearing agent context after uploading sources is crucial. It prevents the agent from working with stale or bloated context while still having full access to all research via NotebookLM queries.

---

## Step 5: Understand Codebases with NotebookLM and RepoMix

*Video reference: 3:52*

One of the most powerful use cases: turning an entire codebase into a queryable knowledge base.

### A. Clone the Repository

```bash
gh repo clone owner/repository-name
```

### B. Install and Run RepoMix

```bash
npm install -g repomix
repomix --output codebase.txt
```

### C. Create a Notebook and Add the Source

In Claude Code, ask it to create a notebook and add the source:

```
"Create a NotebookLM notebook titled 'Codebase: repo-name'
and add ./codebase.txt as a source."
```

Claude Code will use the `notebooklm-mcp:notebook_create` and `notebooklm-mcp:source_add` MCP tools.

### D. Visualize the Codebase

NotebookLM can generate visual representations of your codebase:

- Mind maps showing module relationships and dependencies
- Infographics summarizing architecture and data flow
- Data tables listing endpoints, models, or configuration

These visualizations can be viewed in the NotebookLM Studio interface and exported for use by agents.

> **💡 Tip:** For large codebases, consider using RepoMix with filters to focus on specific directories or file types.

---

## Step 6: Build a Dedicated Debugging Knowledge Base

*Video reference: 6:16*

Instead of relying on generic web searches for debugging, build a curated knowledge base that your agent consults first.

### A. Create a Debugging Notebook

In Claude Code, ask it to create the notebook:

```
"Create a NotebookLM notebook titled 'Debugging Handbook'."
```

### B. Add Curated Sources

- Official documentation for your tech stack
- Community forum solutions (Stack Overflow, GitHub Discussions)
- Relevant GitHub repository READMEs and issue threads
- Blog posts with proven solutions to common errors

In Claude Code, ask it to add sources:

```
"Add the following sources to the Debugging Handbook notebook (<ID>):
- URL: https://docs.example.com/troubleshooting
- File: ./debugging-notes.md"
```

Claude Code will use the `notebooklm-mcp:source_add` MCP tool for each source.

### C. Configure Agent Priority

Update your agent's instructions (e.g., in `CLAUDE.md`):

```markdown
When encountering a bug:
1. First, query the Debugging Handbook notebook
2. Only if no relevant solution is found, perform a web search
3. If you find a new solution, add it to the notebook for future use
```

> **💡 Pro Tip:** Have your agent automatically add successful debugging solutions back to the notebook. Over time, this creates a self-improving knowledge base tailored to your exact tech stack.

---

## Step 7: Cross-Tool Context Builder

*Video reference: 7:54*

NotebookLM notebooks can serve as a shared context layer accessible by multiple tools and team members.

### A. Push Documentation to NotebookLM

In Claude Code, ask it to create the notebook and add sources:

```
"Create a NotebookLM notebook titled 'App Documentation Hub'
and add the following files as sources:
- ./docs/api-reference.md
- ./docs/architecture.md
- ./docs/deployment-guide.md"
```

Claude Code will use `notebooklm-mcp:notebook_create` and `notebooklm-mcp:source_add` MCP tools.

### B. Enable Cross-Tool Access

Any agent or MCP-compatible tool with the notebook ID can manage this shared knowledge base. To query the notebook, use the NotebookLM web interface at [notebooklm.google.com](https://notebooklm.google.com):

> "How is authentication handled in this app?"

Claude Code, Cursor, Windsurf, or any MCP-compatible tool can add sources to the same notebook via `notebooklm-mcp:source_add`.

---

## Step 8: Agent Navigation via Visualizations

*Video reference: 9:02*

Visualizations are not just for humans. AI agents can use exported mind maps and structured data to navigate codebases more efficiently than crawling file systems.

### A. Generate Visualizations

- Mind maps showing module relationships (exportable as JSON)
- Infographics summarizing architecture layers
- Data tables mapping endpoints to their handlers

### B. Configure Agent to Use Visuals

```markdown
When navigating the codebase:
1. Check the mind map JSON for module structure
2. Consult the endpoint table for API routes
3. Only crawl the file system if the visualization data is insufficient
```

This approach is faster, uses fewer tokens, and gives the agent structured context rather than raw file contents.

---

## Step 9: Grounded Security Audits

*Video reference: 10:04*

Perform security audits where every finding is backed by authoritative sources, not just AI inference.

### A. Create a Security Handbook Notebook

In Claude Code, ask it to create the notebook:

```
"Create a NotebookLM notebook titled 'Security Handbook'."
```

### B. Add Security Sources

- OWASP cheat sheets and guidelines
- Security best practices for your specific tech stack
- CVE database entries relevant to your dependencies
- Custom security policies and compliance requirements

In Claude Code, ask it to add sources:

```
"Add the following sources to the Security Handbook notebook (<ID>):
- URL: https://cheatsheetseries.owasp.org/
- File: ./security/internal-policy.md"
```

Claude Code will use the `notebooklm-mcp:source_add` MCP tool for each source.

### C. Run Grounded Security Checks

Open the **Security Handbook** notebook at [notebooklm.google.com](https://notebooklm.google.com) and ask:

> "Review this code for SQL injection vulnerabilities and cite the relevant OWASP guidelines."

> **⚠️ Security Note:** While NotebookLM-grounded audits are valuable, they should complement — not replace — professional security reviews and automated scanning tools for production systems.

---

# PART II — Requirements Engineering & Traceability

## Claude Code + GitHub Spec Kit + NotebookLM

This section extends the NotebookLM workflow into a full **requirements engineering pipeline** using IEEE/DOD-style conventions. We use a **Healthcare Patient Management System (PMS)** as a running example, covering HIPAA compliance, HL7 FHIR interoperability, and FDA software validation requirements.

> **🟣 The Three-Tool Architecture**
> GitHub Spec Kit defines what to build (specifications). Claude Code builds it (implementation). NotebookLM remembers everything and provides grounded verification (knowledge base). Together they create an auditable chain from requirements through testing.

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

Create a `CLAUDE.md` at the repository root that links all three tools:

```markdown
# CLAUDE.md — Agent Instructions for PMS Development

## Development Methodology
This project uses Spec-Driven Development (SDD).
Always use /specify, /plan, /analyze before implementing.

## NotebookLM Integration
- Requirements Notebook: <NLM_REQ_ID>
- Architecture Notebook: <NLM_ARCH_ID>
- Test Evidence Notebook: <NLM_TEST_ID>
- Quality & Security Notebook: <NLM_QS_ID>

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
7. Archive → Push evidence to GitHub + NotebookLM
```

### C. Create NotebookLM Knowledge Bases

In Claude Code, ask it to create the notebooks:

```
"Create the following NotebookLM notebooks:
1. 'PMS: Requirements (IEEE 830)'
2. 'PMS: Architecture & Design'
3. 'PMS: Test Evidence & Traceability'
4. 'PMS: Quality & Security Evidence'
5. 'PMS: HIPAA & FDA Compliance'

Then add https://www.hhs.gov/hipaa/for-professionals/security/
as a source to the HIPAA & FDA Compliance notebook."
```

Claude Code will use `notebooklm-mcp:notebook_create` and `notebooklm-mcp:source_add` MCP tools.

> **💡 Best Practice:** Store all notebook IDs in your CLAUDE.md so every agent session can immediately access the right knowledge base.

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

### C. Push Requirements to NotebookLM

In Claude Code, ask it to add all requirement specs as sources:

```
"Add the following files as sources to the PMS: Requirements
notebook (<NLM_REQ_ID>):
- .specify/specs/system-requirements.md
- .specify/specs/sub-pr-requirements.md
- .specify/specs/sub-mm-requirements.md
- .specify/specs/sub-cw-requirements.md
- .specify/specs/sub-ra-requirements.md"
```

Claude Code will use the `notebooklm-mcp:source_add` MCP tool for each file.

> **💡 IEEE 830 Compliance:** Each requirement must be uniquely identifiable, unambiguous, verifiable, and traceable. The hierarchical ID scheme (SYS-REQ → SUB-XX) ensures every subsystem requirement traces back to a system-level need.

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

### D. Commit RTM and Push to NotebookLM

Commit the traceability matrix to the repository:

```bash
git add docs/traceability-matrix.md docs/traceability-matrix.json
git commit -m "evidence: add requirements traceability matrix

- Forward and backward traceability for all SYS-REQ and SUB requirements
- Maps requirements to design, source modules, tests, and verification status"
```

Then push the committed RTM to NotebookLM. In Claude Code:

```
"Add docs/traceability-matrix.md as a source to the PMS: Requirements
notebook (<NLM_REQ_ID>)."
```

Now anyone can query traceability through the NotebookLM web interface at [notebooklm.google.com](https://notebooklm.google.com). Open the **PMS: Requirements** notebook and ask:

> "Which subsystem requirements trace to SYS-REQ-0006 and what is their current test status?"

> **🔴 Regulatory Requirement:** For FDA-regulated medical software (IEC 62304), the traceability matrix is a mandatory deliverable. Storing it in NotebookLM ensures auditors and developers can query specific traceability chains on demand.

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
```

Then push the committed report to NotebookLM:

```
"Add docs/coverage-report.md as a source to the
PMS: Test Evidence notebook (<NLM_TEST_ID>)."
```

Claude Code will use `notebooklm-mcp:source_add` to upload the committed file.

### D. Coverage Summary Dashboard

| Subsystem | Total Reqs | Tested | Passing | Failing | No Tests | Coverage |
|-----------|-----------|--------|---------|---------|----------|----------|
| Patient Records (PR) | 12 | 11 | 10 | 1 | 1 | 91.7% |
| Clinical Workflow (CW) | 15 | 13 | 12 | 1 | 2 | 86.7% |
| Medication Mgmt (MM) | 8 | 7 | 6 | 1 | 1 | 87.5% |
| Reporting (RA) | 6 | 4 | 4 | 0 | 2 | 66.7% |
| **TOTAL** | **41** | **35** | **32** | **3** | **6** | **85.4%** |

> **⚠️ Gap Analysis:** Requirements with no tests (6 in this example) represent verification gaps. Claude Code can be directed to prioritize writing tests for these uncovered requirements.

---

## Step 14: Living Requirements Dashboard with NotebookLM

The final step of Part II ties everything together: NotebookLM becomes the living, queryable dashboard for your entire requirements engineering pipeline.

### A. Consolidate All Artifacts

> **Reminder:** Per the [Compliance Evidence Storage Policy](#compliance-evidence-storage-policy), all files listed below must already be committed to the repository before adding them as NotebookLM sources. If any are not yet committed, run `git add` and `git commit` first.

In Claude Code, ask it to add all artifacts as sources to their respective notebooks:

```
"Add the following sources to the appropriate NotebookLM notebooks:

PMS: Requirements notebook (<NLM_REQ_ID>):
- All files in .specify/specs/
- docs/traceability-matrix.md

PMS: Architecture & Design notebook (<NLM_ARCH_ID>):
- All files in .specify/plans/
- All files in docs/adr/

PMS: Test Evidence notebook (<NLM_TEST_ID>):
- docs/coverage-report.md
- All files in docs/test-evidence/

PMS: HIPAA & FDA Compliance notebook (<NLM_COMPLIANCE_ID>):
- docs/hipaa-assessment.md"
```

Claude Code will use the `notebooklm-mcp:source_add` MCP tool for each file.

### B. Query Patterns for Requirements Engineering

| Query Type | Example Question | Grounded In |
|------------|-----------------|-------------|
| Traceability | Which test cases verify SYS-REQ-0002 and are any failing? | RTM + Test Reports |
| Coverage Gap | Which subsystem requirements have no associated test cases? | RTM + Coverage Report |
| Impact Analysis | If we change SYS-REQ-0004, which subsystem requirements and tests are affected? | RTM + Specs |
| Compliance | Show all requirements related to HIPAA Security Rule audit trail provisions | Specs + HIPAA Docs |
| Design Rationale | Why did we choose event-driven architecture for the clinical alerts pipeline? | ADRs + Specs |
| Regression Risk | Which areas have the most failing tests and what requirements do they cover? | Test Reports + RTM |

### C. Automate the Update Cycle

Add to `CLAUDE.md`:

```markdown
## Post-Implementation Protocol
After completing any implementation task:
1. Run /analyze to verify spec consistency
2. Run tests and generate coverage-report.md
3. Update the traceability matrix
4. git add and git commit all updated evidence files
5. Push committed artifacts to NotebookLM
6. If a new architectural decision was made,
   create an ADR, commit it, and push to the architecture notebook
```

> **🟣 The Complete Pipeline:** Specify (GitHub Spec Kit) → Plan → Analyze → Implement (Claude Code) → Test → Trace → Store (NotebookLM) → Query & Verify. Every stage is documented, every decision is grounded, and every requirement is traceable from inception through verification.

---

# PART III — Code Quality, Reviews & Security Monitoring

This section closes the development loop by adding **continuous code quality verification** (SonarQube), **AI-powered peer review** (CodeRabbit), and **continuous security monitoring** (Snyk). Crucially, all output is stored as evidence in both **GitHub** (for developer workflow) and **NotebookLM** (for auditing and grounded queries).

> **🟢 The Evidence Pipeline Principle**
> Every tool in the pipeline produces artifacts. Every artifact is **committed to the GitHub repository** as the permanent system of record, then indexed in NotebookLM for long-term querying, audit preparation, and cross-tool grounded answers. Committed files in `docs/` — not ephemeral CI artifacts — are the authoritative evidence store. Nothing is lost; everything is versioned and tamper-evident.

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
| Reliability Rating | A | SYS-REQ-0006 (Alerts) | NotebookLM: Quality notebook |

### D. Commit and Push Quality Evidence to NotebookLM

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
```

Then push the committed report to NotebookLM:

```
"Add docs/quality-reports/quality-report-<TODAY>.md as a source
to the PMS: Quality & Security notebook (<NLM_QS_ID>)."
```

Claude Code will use `notebooklm-mcp:source_add` to upload the committed file.

To query historical quality trends, open the **PMS: Quality & Security** notebook at [notebooklm.google.com](https://notebooklm.google.com) and ask:

> "What is the trend in code coverage for the Medication Management subsystem over the last 5 reports?"

> **💡 Quality Gate as Gatekeeper:** Configure GitHub branch protection rules to require a passing SonarQube quality gate before merging PRs.

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
```

Then push the committed evidence to NotebookLM:

```
"Add docs/reviews/pr-<PR_NUMBER>-review-summary.md as a source
to the PMS: Quality & Security notebook (<NLM_QS_ID>)."
```

Claude Code will use `notebooklm-mcp:source_add` to upload the committed file.

### E. Review Metrics Dashboard

| Metric | Current Sprint | Previous Sprint | Trend |
|--------|---------------|-----------------|-------|
| PRs Reviewed | 24 | 18 | Increasing |
| Issues Found (Critical) | 3 | 7 | Improving |
| Issues Found (Suggestions) | 41 | 52 | Improving |
| HIPAA Violations Caught | 2 | 5 | Improving |
| Average Review Time | < 3 min | < 3 min | Stable |
| Requirement References | 87% | 62% | Improving |

> **💡 CodeRabbit + Claude Code Synergy:** When CodeRabbit identifies issues, Claude Code can be directed to fix them: "Fix all critical issues from the CodeRabbit review on PR #42, ensuring each fix references the associated requirement ID in the commit message."

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
```

Then push the committed SBOMs to NotebookLM:

```
"Add docs/sbom/sbom-cyclonedx.json as a source to the PMS: HIPAA & FDA
Compliance notebook (<NLM_COMPLIANCE_ID>)."
```

Claude Code will use `notebooklm-mcp:source_add` to upload the committed file.

### E. Commit and Push Security Evidence to NotebookLM

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
```

Then push the committed report to NotebookLM:

```
"Add docs/security/security-report-<TODAY>.md as a source
to the PMS: Quality & Security notebook (<NLM_QS_ID>)."
```

Claude Code will use `notebooklm-mcp:source_add` to upload the committed file.

```bash
# Continuous monitoring baseline
snyk monitor --json-file-output=snyk-monitor.json
```

To query security posture at any time, open the **PMS: Quality & Security** notebook at [notebooklm.google.com](https://notebooklm.google.com) and ask:

> "What critical vulnerabilities are currently unresolved and which requirements do they affect?"

> **🔴 HIPAA Compliance:** The HIPAA Security Rule requires covered entities to conduct risk analysis and implement security measures. Snyk scans, combined with the SBOM and vulnerability-to-requirement mapping, provide documentary evidence of ongoing security due diligence. Store all evidence with retention policies of at least 6 years per HIPAA requirements.

---

## Evidence Pipeline Architecture

All three tools (SonarQube, CodeRabbit, Snyk) feed into a dual-store evidence architecture.

### GitHub Evidence (Developer Workflow)

| Tool | GitHub Location | Retention | Access |
|------|----------------|-----------|--------|
| SonarQube | PR status checks + `docs/quality-reports/` (committed) | **Permanent** (git history) | Developers, CI/CD |
| CodeRabbit | PR review comments + `docs/reviews/` (committed) | **Permanent** (git history) | All PR participants |
| Snyk | Code Scanning alerts + `docs/security/` (committed) | **Permanent** (git history) | Security tab |
| Test Coverage | `docs/coverage-report.md` + `docs/test-evidence/` (committed) | **Permanent** (git history) | Developers, CI/CD |
| SBOM | `docs/sbom/` (committed) + Releases | **Permanent** (git history) | Compliance team |

### NotebookLM Evidence (Audit & Query)

| Notebook | Contents | Query Examples |
|----------|----------|----------------|
| PMS: Quality & Security | SonarQube reports, CodeRabbit summaries, Snyk reports, trend analyses | "Show quality trends for the last 3 sprints" |
| PMS: Requirements | SRS, RTM, specs, traceability, coverage reports | "Which requirements have failing tests?" |
| PMS: HIPAA Compliance | HIPAA assessment, SBOM, security audit evidence, encryption verification | "Show all evidence for HIPAA Security Rule compliance" |
| PMS: Test Evidence | Test reports, coverage dashboards, verification records | "What is the verification status of SYS-REQ-0003?" |

### Automated Evidence Sync (CI/CD Post-Step)

```yaml
# .github/workflows/evidence-sync.yml
name: Sync Evidence to NotebookLM
on:
  workflow_run:
    workflows: ['SonarQube Quality Gate',
                'CodeRabbit Review',
                'Snyk Security Scan']
    types: [completed]

jobs:
  sync-evidence:
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

      - name: Push to NotebookLM
        run: |
          # Use Claude Code to add the committed evidence summary via MCP
          claude --print "Add docs/evidence-summary.md as a source to \
            NotebookLM notebook $NLM_QS_ID using notebooklm-mcp:source_add"
        env:
          NLM_QS_ID: ${{ vars.NLM_QS_NOTEBOOK_ID }}
```

> **🟢 Repository-First, Dual-Store Benefit:** The GitHub repository is the permanent, authoritative evidence store (satisfying HIPAA's 6-year retention requirement via git history). NotebookLM indexes committed evidence for grounded, natural-language querying across the entire project history. Together, they ensure evidence is both actionable for developers and auditable for compliance teams — with the repo as the system of record.

---

## Summary & Next Steps

This tutorial covered seventeen steps across three parts for building a complete, auditable development pipeline:

| Part | Steps | Tools | Purpose |
|------|-------|-------|---------|
| I | 1–9 | NotebookLM CLI | Knowledge management, research, debugging, security audits |
| II | 10–14 | Spec Kit + Claude Code + NotebookLM | IEEE/DOD requirements, traceability matrices, test coverage |
| III | 15–17 | SonarQube + CodeRabbit + Snyk | Code quality gates, AI reviews, continuous security monitoring |

### Key Takeaways

- **GitHub Spec Kit** enforces structure: no implementation without an approved specification
- **Claude Code** automates implementation, test scaffolding, evidence generation, and remediation
- **NotebookLM** provides grounded truth: every answer cites your actual project artifacts
- **SonarQube** catches quality issues with enforceable gates before code merges
- **CodeRabbit** provides AI-powered reviews that reference your requirement IDs
- **Snyk** monitors dependencies, containers, and code for vulnerabilities continuously
- The **repository-first evidence pipeline** commits all evidence to GitHub (permanent, versioned, tamper-evident), then indexes it in NotebookLM for querying — satisfying HIPAA's 6-year retention requirement
- For **regulated industries**, this pipeline produces audit-ready documentation with full traceability and no reliance on ephemeral CI artifacts

### Next Steps

- Set up your CI/CD pipeline with all three quality/security workflows
- Configure CodeRabbit with requirement-aware review instructions
- Run your first Snyk scan and generate the initial SBOM
- Establish the evidence-sync workflow to keep NotebookLM current
- Create your compliance notebook and load regulatory guidance

---

For the foundational NotebookLM walkthrough, [watch the original video on YouTube](https://youtu.be/eFCHwtufjJc). For GitHub Spec Kit, visit [github.com/github/spec-kit](https://github.com/github/spec-kit). For Snyk, visit [snyk.io](https://snyk.io). For CodeRabbit, visit [coderabbit.ai](https://coderabbit.ai).
