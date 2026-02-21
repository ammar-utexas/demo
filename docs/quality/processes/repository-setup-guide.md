# Repository Setup Guide

**Date:** 2026-02-21
**Purpose:** Step-by-step guide to bootstrap a new repository with the same documentation-as-source-of-truth process used in this project.

---

## Prerequisites

Before starting, ensure you have:

- **Git** installed and a GitHub (or equivalent) account
- **A text editor** or IDE with markdown preview support
- **A clear project scope** — at minimum, a one-paragraph description of what the system does, who uses it, and what regulations apply
- **Regulatory context** — know whether ISO 13485, ISO 14971, HIPAA, 21 CFR Part 11, or other standards apply (this determines whether Steps 6–7 are needed)

---

## Step 1: Root Files

Create the repository and add the three root-level files.

```bash
mkdir my-project && cd my-project
git init
```

### 1a. `CLAUDE.md`

This is the agent instruction file. It tells AI agents (and human contributors) where documentation lives and how it is organized. Copy the structure from the reference project's `CLAUDE.md`, adapting the directory descriptions and rules to your project.

Key sections to include:

| Section | Purpose |
|---------|---------|
| Repository Docs as Single Source of Truth | Declares `docs/` as the canonical knowledge store |
| Directory Structure | Full tree of all `docs/` subdirectories |
| What to Store | Describes what goes in each directory |
| When to Update Docs | Triggers for documentation changes |
| Rules | The six rules (never rely on memory, read before you build, etc.) |

### 1b. `README.md`

Standard project README with: project name, one-paragraph description, quick start instructions, and a link to `docs/index.md` for full documentation.

### 1c. `.gitignore`

Add language-specific ignores for your stack plus:

```
# OS
.DS_Store
Thumbs.db

# Editor
.idea/
.vscode/
*.swp

# Environment
.env
.env.local
```

---

## Step 2: Directory Skeleton

Create the full `docs/` directory tree. Every directory listed here maps to a section in `CLAUDE.md`.

```bash
mkdir -p docs/{architecture,api,bugs,config,domain,experiments,features,platform,quality/{audits,capa,processes,risk-management,standards},specs/{requirements/{domain,platform}},testing/evidence}
```

This produces:

```
docs/
├── architecture/        # Architecture Decision Records (ADRs)
├── api/                 # API contracts, schemas, interface docs
├── bugs/                # Root cause analyses for non-trivial bugs
├── config/              # Dependencies, environment setup, configuration
├── domain/              # Documentation views by business domain
├── experiments/         # POC evaluations, tool integration trials
├── features/            # Product requirements, implementation details
├── platform/            # Documentation views by deployment platform
├── quality/
│   ├── audits/          # Audit records
│   ├── capa/            # Corrective and preventive actions
│   ├── processes/       # Development processes, governance, working instructions
│   ├── risk-management/ # Risk analyses (ISO 14971)
│   └── standards/       # Regulatory standards (e.g., ISO 13485)
├── specs/
│   ├── requirements/
│   │   ├── domain/      # Domain-level subsystem requirements
│   │   └── platform/    # Platform-specific requirements
│   └── ...              # System spec, versions, compatibility matrix
└── testing/
    └── evidence/        # Test run records
```

---

## Step 3: Foundation Documents

These are the minimum files to create on day 1. Each file establishes a convention that all later work builds on.

### 3a. `docs/index.md` — Table of Contents

The TOC links to every other document. Start with section headers for each directory and placeholder text. Update this file every time you add or remove a doc.

Sections to include:

```markdown
# Project Knowledge Base

- [Documentation Workflow](documentation-workflow.md)

## Architecture Decisions
<!-- Links to ADRs -->

## Features
<!-- Links to feature docs -->

## Bug Fixes
_No bug fixes documented yet._

## API Contracts
<!-- Links to API docs -->

## Configuration & Dependencies
<!-- Links to config docs -->

## Release Management
<!-- Links to release docs -->

## Experiments & Tool Evaluations
<!-- Links to experiment docs -->

## Documentation Views
### By Domain
### By Platform

## Specifications & Requirements
<!-- Links to SYS-REQ, domain, and platform requirement docs -->

## Testing & Traceability
<!-- Links to testing strategy and traceability matrix -->

## Quality Management
<!-- Links to governance, processes, standards -->
```

### 3b. `docs/documentation-workflow.md` — Workflow Steps

This file defines how features flow through the documentation system. Model it on the 10-step workflow:

| Step | Name | When |
|------|------|------|
| 1 | Research & Discovery | New technology or feature evaluated |
| 2 | Architecture Decision | Technology choice or design approach recorded |
| 3 | System Requirements | New capability requires a formal requirement |
| 4 | Subsystem Decomposition | System requirement broken into domain/platform requirements |
| 5 | Governance, Quality & Risk | Conflict analysis (5a) and risk assessment (5b) |
| 6 | Testing & Traceability | Test coverage tracking for new requirements |
| 7 | Development & Implementation | Actual code written (speckit cycle) |
| 8 | Configuration & Deployment | Dependencies, feature flags, environment changes |
| 9 | Verification & Evidence | Full test suite, evidence, pre-release gate |
| 10 | Release | Release evidence (10a) and version/publish (10b) |

For each step, include:
- **When** — trigger condition
- **Checklist** — ordered list of actions
- **Files Modified** — which docs are touched
- **AI Agent Prompt** — a reusable prompt for AI-assisted execution

Include a **Quick Reference** table mapping steps to files and a **File Inventory** table listing all files by directory.

### 3c. `docs/specs/system-spec.md` — System Specification

Define your system at the highest level. Sections to include:

| Section | Content |
|---------|---------|
| Purpose | One-paragraph system description |
| Scope | Components table (name, repository, technology) |
| System Context | Mermaid diagram showing components and external systems |
| Subsystem Decomposition | Table of subsystem codes, names, scopes |
| User Roles | Table of roles and access levels |
| Regulatory Constraints | Applicable regulations |
| Quality Attributes | Targets and verification methods |
| Requirement ID Convention | Format table (see below) |
| Platform Codes | Table mapping codes to repositories |
| Traceability Policy | How requirements trace to design, code, and tests |

#### Requirement ID Convention

Adopt this convention from day 1 — it is referenced everywhere else:

| Level | Format | Example |
|-------|--------|---------|
| System | `SYS-REQ-XXXX` | SYS-REQ-0001 |
| Subsystem (Domain) | `SUB-{code}-XXXX` | SUB-PR-0001 |
| Platform | `SUB-{code}-XXXX-{platform}` | SUB-PR-0003-BE |
| Test Case (Domain) | `TST-{code}-XXXX` | TST-PR-0001 |
| Test Case (Platform) | `TST-{code}-XXXX-{platform}` | TST-PR-0003-BE |
| Test Run | `RUN-{YYYY-MM-DD}-{NNN}` | RUN-2026-02-15-001 |

Replace `{code}` with your subsystem codes (e.g., PR, CW, MM) and `{platform}` with your platform codes (e.g., BE, WEB, AND, AI).

### 3d. `docs/specs/requirements/SYS-REQ.md` — System Requirements

Start with your first 3–5 system-level requirements. Each entry needs:

- **Req ID** (`SYS-REQ-XXXX`)
- **Title** — short name
- **Priority** — High / Medium / Low
- **Status** — Not Started / Scaffolded / Implemented / Verified
- **Rationale** — why this requirement exists
- **Acceptance Criteria** — 3–7 numbered, testable criteria
- **Decomposes To** — which domain requirements it will produce

Use a summary table at the top and detailed sections below.

### 3e. `docs/testing/testing-strategy.md` — Test Strategy

Define testing conventions before any code is written. Include:

1. **Testing Levels** — Unit, Integration, System (pyramid diagram)
2. **Test Naming Convention** — `TST-{code}-XXXX-{platform}` format with platform codes
3. **Requirement Annotations** — how to link tests to requirements in each language (e.g., `# @requirement SUB-MM-0001` in Python, `// @requirement SUB-PR-0003` in TypeScript)
4. **Subsystem Testing** — commands per repository
5. **System-Level Testing** — full-stack test setup
6. **Test Run Record Format** — template for `RUN-YYYY-MM-DD-NNN.md` files containing date, repo, commit, branch, runner, and per-test results table
7. **Consistency Verification** — pre-release check that every requirement has a test and every test has a recent pass

### 3f. `docs/testing/traceability-matrix.md` — Traceability Matrix (Template)

Start with an empty structure containing:

- **Forward Traceability** table: SYS-REQ → subsystem requirements → modules → test cases → status
- **Backward Traceability** table: test case ID → description → repository → test function → traces to → last result → run ID
- **Coverage Summary** table: subsystem → domain reqs → platform reqs → tests → coverage %
- **Test Run Log**: initially empty

### 3g. `docs/quality/processes/requirements-governance.md` — Governance

Define governance procedures:

1. **Requirement lifecycle** — statuses and transitions (Not Started → Scaffolded → Implemented → Verified)
2. **Conflict analysis categories**:
   - Domain Conflicts (`DC-{code}-NN`) — contradictions between subsystem requirements
   - Platform Conflicts (`PC-{platform}-NN`) — implementation tensions across platforms
   - Race Conditions (`RC-{platform}-NN`) — concurrency issues in multi-platform scenarios
3. **Resolution process** — how conflicts are documented and resolved
4. **Branching & release strategy** — feature branching rules and merge requirements

### 3h. `docs/config/project-setup.md` — Development Environment

Document how to set up a development environment from scratch:

- Clone instructions
- Prerequisites (language runtimes, databases, Docker)
- Install steps per component
- Run commands
- Common troubleshooting

### 3i. `docs/config/dependencies.md` — Dependency Decisions

For each dependency, record:

| Field | Content |
|-------|---------|
| Name | Library/framework name |
| Version | Pinned version |
| Purpose | Why it is needed |
| Alternatives Rejected | What else was considered |
| Rationale | Why this one was chosen |

---

## Step 4: Architecture Decision Records

### 4a. ADR-0001: Repository-Based Knowledge Management

Your first ADR should document the decision to use this documentation process itself. This makes the process self-documenting.

File: `docs/architecture/0001-repo-based-knowledge-management.md`

Template:

```markdown
# ADR-0001: Use Repository-Based Knowledge Management

**Date:** YYYY-MM-DD
**Status:** Accepted

## Context
[Why you need a knowledge management approach]

## Decision
Use markdown files in a `docs/` directory as the single source of truth for all project context, decisions, and implementation details.

## Rationale
- Version-controlled alongside code
- No external tool dependency
- AI agents can read and update docs directly
- Searchable with standard text tools

## Consequences
- Every decision must be documented in `docs/`
- `docs/index.md` must be updated when files are added/removed
- Team members must read relevant docs before starting work
```

### 4b. ADR-0002: First Technology Decision

Your second ADR should be a real technology decision for the project (e.g., choice of backend framework, database, frontend framework). Follow the same template: Context, Options Considered, Decision, Rationale, Consequences.

ADR naming convention: `NNNN-short-title.md` (zero-padded 4-digit number, kebab-case title).

---

## Step 5: Requirements Decomposition Setup

Create template files for your domain and platform subsystems.

### 5a. Identify Your Subsystems

Based on your system specification, list your subsystem codes. Examples:

| Code | Subsystem |
|------|-----------|
| PR | Patient Records |
| CW | Clinical Workflow |
| MM | Medication Management |
| RA | Reporting & Analytics |
| PM | Prompt Management |

Replace these with your project's actual subsystems.

### 5b. Identify Your Platforms

Based on your architecture, list your platform codes:

| Platform Code | Platform | Repository |
|---------------|----------|------------|
| BE | Backend API | my-project-backend |
| WEB | Web Frontend | my-project-frontend |
| AND | Android App | my-project-android |
| AI | AI Infrastructure | my-project-ai |

### 5c. Create Domain Requirement Templates

For each subsystem, create `docs/specs/requirements/domain/SUB-{code}.md`:

```markdown
# Subsystem Requirements: {Subsystem Name} (SUB-{CODE})

**Version:** 0.1
**Date:** YYYY-MM-DD
**Parent:** [SYS-REQ](../SYS-REQ.md)

## Requirements

| Req ID | Title | Priority | Status | Parent SYS-REQ |
|--------|-------|----------|--------|----------------|
| SUB-{CODE}-0001 | ... | High | Not Started | SYS-REQ-XXXX |

## Platform Decomposition

| Domain Req | BE | WEB | AND | AI |
|------------|----|----|-----|-----|
| SUB-{CODE}-0001 | SUB-{CODE}-0001-BE | SUB-{CODE}-0001-WEB | — | — |
```

### 5d. Create Platform Requirement Templates

For each subsystem + platform combination, create `docs/specs/requirements/platform/SUB-{code}-{PLATFORM}.md`:

```markdown
# Platform Requirements: {Subsystem} — {Platform} (SUB-{CODE}-{PLATFORM})

**Version:** 0.1
**Date:** YYYY-MM-DD

## Requirements

| Req ID | Description | Parent Domain Req | Module(s) | Test Case ID | Status |
|--------|-------------|-------------------|-----------|-------------|--------|
| SUB-{CODE}-0001-{PLATFORM} | ... | SUB-{CODE}-0001 | ... | TST-{CODE}-0001-{PLATFORM} | Not Started |
```

Only create platform files for subsystem + platform combinations that apply to your project.

---

## Step 6: Quality & DHF Setup

> **Skip this step** if your project is not a medical device and does not require ISO 13485 compliance. See [Appendix C: Customization Points](#appendix-c-customization-points).

### 6a. DHF Directory Structure

Create the 10 DHF sub-folders mapping to ISO 13485 Clause 7.3:

```bash
mkdir -p docs/quality/DHF/{01-design-planning,02-design-input,03-design-output,04-design-review,05-design-verification,06-design-validation,07-design-transfer,08-design-changes,09-risk-management,10-release-evidence}
```

| Folder | ISO Clause | Contents |
|--------|-----------|----------|
| `01-design-planning/` | 7.3.2 | Documentation workflow, system spec |
| `02-design-input/` | 7.3.3 | SYS-REQ, domain requirement files |
| `03-design-output/` | 7.3.4 | API docs, ADRs |
| `04-design-review/` | 7.3.5 | Requirements governance |
| `05-design-verification/` | 7.3.6 | Testing strategy, traceability matrix |
| `06-design-validation/` | 7.3.7 | User acceptance testing records |
| `07-design-transfer/` | 7.3.8 | Release process, compatibility matrix |
| `08-design-changes/` | 7.3.9 | ADRs (dual purpose with 03) |
| `09-risk-management/` | ISO 14971 | Risk assessment files |
| `10-release-evidence/` | 4.2.5/7.3.2 | Per-release conformity records |

### 6b. `docs/quality/DHF/DHF-index.md`

Create the DHF master index with:

1. **Purpose** — declares this as the design history file per ISO 13485
2. **ISO 13485 Clause 7.3 Traceability Matrix** — table mapping clauses to DHF folders and artifacts
3. **Gap Analysis** — table of missing deliverables with priority
4. **Refresh Process** — describes when and how DHF copies are updated (Step 10a)
5. **File Manifest** — table of folder → file count → source directory

---

## Step 7: Documentation Views

Documentation views provide alternative entry points organized by business domain or deployment platform, without duplicating content.

### 7a. `docs/domain/index.md`

List all business domain views. Each domain view is a markdown file that aggregates links to relevant ADRs, requirements, experiments, and config docs.

```markdown
# Documentation by Domain

Browse documentation organized by business/functional domain.

- [Domain A](domain-a.md)
- [Domain B](domain-b.md)
- ...
```

Create one file per domain that links to (not copies) existing docs.

### 7b. `docs/platform/index.md`

Same approach but organized by deployment platform:

```markdown
# Documentation by Platform

Browse documentation organized by deployment platform.

- [Backend/Server](backend-server.md)
- [Web Frontend](web-frontend.md)
- [Android](android.md)
- ...
```

---

## Step 8: First Commit & Branching

### 8a. Initial Commit

Stage and commit everything:

```bash
git add -A
git commit -m "docs: bootstrap documentation-as-source-of-truth structure

Create docs/ directory skeleton with 11+ subdirectories, foundation
documents (index, workflow, system spec, requirements, testing strategy,
traceability matrix, governance), ADR-0001, and domain/platform templates.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

### 8b. Push to Remote

```bash
git remote add origin <your-repo-url>
git push -u origin main
```

### 8c. Branching Strategy

Adopt a branching strategy from day 1. The recommended approach:

- **`main`** — always deployable, documentation complete
- **`feature/{name}`** — one branch per feature, follows the 10-step workflow
- **Merge rule** — feature branches merge to main only after Steps 1–10 are complete
- **PR requirement** — all merges to main require a pull request with documentation review

Document this in `docs/quality/processes/requirements-governance.md` under a "Branching & Release Strategy" section.

---

## Appendix A: Naming Conventions

All naming conventions used across the documentation system:

| Artifact | Convention | Example |
|----------|-----------|---------|
| System Requirement | `SYS-REQ-XXXX` | SYS-REQ-0001 |
| Domain Requirement | `SUB-{code}-XXXX` | SUB-PR-0001 |
| Platform Requirement | `SUB-{code}-XXXX-{platform}` | SUB-PR-0003-BE |
| Test Case (Domain) | `TST-{code}-XXXX` | TST-PR-0001 |
| Test Case (Platform) | `TST-{code}-XXXX-{platform}` | TST-PR-0003-BE |
| Test Run Record | `RUN-{YYYY-MM-DD}-{NNN}` | RUN-2026-02-15-001 |
| ADR | `NNNN-short-title.md` | 0001-repo-based-knowledge-management.md |
| Experiment | `NN-{Type}-{Name}.md` | 18-PRD-ISICArchive-PMS-Integration.md |
| Risk Assessment | `RA-{code}-{feature}.md` | RA-PR-DermatologyCDS.md |
| Release Evidence | `DHF-release-{YYYY-MM-DD}-v{X.Y.Z}-{tag}.md` | DHF-release-2026-02-21-v0.2.0-arch.md |
| Domain Conflict | `DC-{code}-NN` | DC-PR-01 |
| Platform Conflict | `PC-{platform}-NN` | PC-BE-01 |
| Race Condition | `RC-{platform}-NN` | RC-AND-01 |
| Feature Flag | `FF_{SUBSYSTEM}_{FEATURE}` | FF_PR_DERM_CDS |

---

## Appendix B: File Inventory Checklist

Complete list of files to create, grouped by directory. Check each off as you create it.

### Root (3 files)

- [ ] `CLAUDE.md`
- [ ] `README.md`
- [ ] `.gitignore`

### `docs/` root (2 files)

- [ ] `docs/index.md`
- [ ] `docs/documentation-workflow.md`

### `docs/specs/` (1 + templates)

- [ ] `docs/specs/system-spec.md`
- [ ] `docs/specs/subsystem-versions.md` (can start empty)
- [ ] `docs/specs/release-compatibility-matrix.md` (can start empty)

### `docs/specs/requirements/` (1 + domain + platform templates)

- [ ] `docs/specs/requirements/SYS-REQ.md`
- [ ] `docs/specs/requirements/domain/SUB-{code}.md` (one per subsystem)
- [ ] `docs/specs/requirements/platform/SUB-{code}-{PLATFORM}.md` (one per subsystem + platform)

### `docs/testing/` (2 files)

- [ ] `docs/testing/testing-strategy.md`
- [ ] `docs/testing/traceability-matrix.md`

### `docs/quality/processes/` (1+ files)

- [ ] `docs/quality/processes/requirements-governance.md`

### `docs/config/` (2+ files)

- [ ] `docs/config/project-setup.md`
- [ ] `docs/config/dependencies.md`

### `docs/architecture/` (2+ files)

- [ ] `docs/architecture/0001-repo-based-knowledge-management.md`
- [ ] `docs/architecture/0002-{your-first-tech-decision}.md`

### `docs/api/` (1 file)

- [ ] `docs/api/backend-endpoints.md` (or equivalent API reference — can start as template)

### `docs/domain/` (1+ files)

- [ ] `docs/domain/index.md`
- [ ] One view file per business domain

### `docs/platform/` (1+ files)

- [ ] `docs/platform/index.md`
- [ ] One view file per platform

### `docs/quality/DHF/` (11 files — ISO 13485 only)

- [ ] `docs/quality/DHF/DHF-index.md`
- [ ] `docs/quality/DHF/01-design-planning/` (folder)
- [ ] `docs/quality/DHF/02-design-input/` (folder)
- [ ] `docs/quality/DHF/03-design-output/` (folder)
- [ ] `docs/quality/DHF/04-design-review/` (folder)
- [ ] `docs/quality/DHF/05-design-verification/` (folder)
- [ ] `docs/quality/DHF/06-design-validation/` (folder)
- [ ] `docs/quality/DHF/07-design-transfer/` (folder)
- [ ] `docs/quality/DHF/08-design-changes/` (folder)
- [ ] `docs/quality/DHF/09-risk-management/` (folder)
- [ ] `docs/quality/DHF/10-release-evidence/` (folder)

**Minimum total for day 1:** ~15 markdown files + 3 root files + directory skeleton.

---

## Appendix C: Customization Points

Not every project needs every part of this system. Here is what to adjust based on your context.

### Non-medical-device projects

If your project does **not** require ISO 13485 compliance:

- **Skip Step 6 entirely** — no DHF folder, no `DHF-index.md`
- **Skip Step 5b** (Risk Assessment) — or simplify it to an informal risk register without ISO 14971 format
- **Skip Step 10a** (Release Evidence) — or replace with a simpler release notes process
- **Remove** `docs/quality/DHF/`, `docs/quality/risk-management/`, `docs/quality/standards/`, `docs/quality/audits/`, `docs/quality/capa/`
- **Keep** `docs/quality/processes/` — governance and conflict analysis are useful for any multi-team project

### Single-platform projects

If your project has only one deployable component (e.g., a web app with no mobile):

- **Use a two-tier decomposition** — System (SYS-REQ) → Subsystem (SUB-{code}) only
- **Skip platform requirement files** — no `docs/specs/requirements/platform/` directory
- **Simplify test naming** — use `TST-{code}-XXXX` without platform suffix
- **Skip** `docs/platform/` views (or make them a single file)

### Projects without AI/ML components

- Remove the `AI` platform code
- Remove AI-related subsystems from templates
- Skip edge deployment documentation (`docs/config/jetson-deployment.md`)

### Small teams (1–3 developers)

- Conflict analysis (Step 5a) can be informal — a section in governance rather than individual conflict IDs
- Documentation views (Step 7) can be deferred until the docs/ directory exceeds 30 files
- Experiments directory can be skipped if all technology choices are already made

### Adapting the 10-step workflow

The workflow steps are sequential for a reason (each step's output feeds the next), but not all steps are needed for every change:

| Change Type | Steps Required |
|-------------|---------------|
| New feature (full) | All 10 steps |
| Bug fix | 5a (governance check) → 7 (implement) → 9 (verify) |
| Documentation only | Update relevant docs → 10b (version & publish) |
| Dependency update | 8 (config) → 9 (verify) → 10b (version & publish) |
| New experiment/POC | 1 (research) only |
| Architecture decision | 2 (ADR) only |
