# Project Agent Instructions

## Repository Docs as Single Source of Truth

This project uses **markdown files in the `docs/` directory** as the central knowledge repository. All project context, decisions, and implementation details must be stored there — committed to the repo and pushed to GitHub.

### Directory Structure

```
docs/
├── architecture/        # Architectural Decision Records (ADRs)
├── api/                 # API contracts, schemas, and interface docs
├── bugs/                # Root cause analyses for non-trivial bugs
├── config/              # Dependencies, environment setup, and configuration
├── domain/              # Documentation views organized by business domain
├── experiments/         # POC evaluations and tool integration trials
├── features/            # Product requirements / PRDs and implementation details
├── platform/            # Documentation views organized by deployment platform
├── quality/             # Quality Management System (ISO 13485)
│   ├── audits/          # Audit records
│   ├── capa/            # Corrective and preventive actions
│   ├── processes/       # Development processes, governance, working instructions
│   ├── risk-management/ # Risk analyses
│   └── standards/       # Regulatory standards (e.g., ISO 13485)
├── specs/               # System and subsystem specifications
│   ├── requirements/    # Three-tier requirements decomposition
│   │   ├── SYS-REQ.md  # System requirements (top level)
│   │   ├── domain/      # Domain-level subsystem requirements (SUB-PR, SUB-CW, etc.)
│   │   └── platform/    # Platform-specific requirements (SUB-PR-BE, SUB-PR-WEB, etc.)
│   └── ...              # System spec, subsystem versions, compatibility matrix
├── testing/             # Test strategy, traceability matrix, evidence
│   ├── evidence/        # Test run records
│   └── ...              # testing-strategy.md, traceability-matrix.md
└── index.md             # Table of contents linking to all docs
```

### What to Store

**Architectural Decisions** (`docs/architecture/`)
- Record every architectural decision as a new markdown file immediately when made.
- Use the naming convention: `NNNN-short-title.md` (e.g., `0001-chose-jwt-over-sessions.md`).
- Include: context, options considered, rationale, and trade-offs.

**Implementation Details** (`docs/features/`)
- After completing a feature or significant change, add a markdown file summarizing:
  - What was built and why
  - Key files and components involved
  - Any non-obvious design choices
  - Known limitations or follow-up work

**Bug Fixes and Incidents** (`docs/bugs/`)
- Document root cause analysis for non-trivial bugs.
- Include what was tried, what failed, and what ultimately resolved the issue.

**API Contracts and Interfaces** (`docs/api/`)
- Store API schemas, interface definitions, and integration details.
- Update these whenever contracts change.

**Dependencies and Configuration** (`docs/config/`)
- Record decisions about dependencies (why chosen, alternatives rejected).
- Document environment-specific configuration and setup steps.

**Quality Management** (`docs/quality/`)
- Store audit records, CAPA reports, and development process documentation.
- Keep governance procedures and conflict analyses in `quality/processes/`.
- Store risk management artifacts in `quality/risk-management/`.
- Regulatory standards (e.g., ISO 13485) go in `quality/standards/`.

**Specifications & Requirements** (`docs/specs/`)
- System specification and subsystem requirement documents live here.
- All requirement files (SYS-REQ, SUB-*) go in `specs/requirements/`.
- Subsystem versions and release compatibility matrices stay at the specs level.

**Testing & Traceability** (`docs/testing/`)
- Store the testing strategy and traceability matrix here.
- Test run evidence (RUN-*.md records) goes in `testing/evidence/`.
- Update the traceability matrix whenever requirement or test status changes.

**Experiments & POC Evaluations** (`docs/experiments/`)
- Document proof-of-concept evaluations and tool integration trials.
- Use numbered prefixes for grouping related experiments (e.g., `00-Tambo-*`, `05-OpenClaw-*`).

### When to Update Docs

- **Before starting work**: Read relevant docs in `docs/` for existing context.
- **After completing a feature**: Add implementation details to `docs/features/`.
- **After an architectural decision**: Record it in `docs/architecture/` immediately — do not defer.
- **After resolving a bug**: Document the root cause and fix in `docs/bugs/`.
- **When onboarding context changes**: Update or replace outdated docs.
- **Always update `docs/index.md`** when adding or removing a doc file.

### Rules

1. **Never rely on memory alone.** If a decision or implementation detail matters, it goes in `docs/`.
2. **Read before you build.** Check `docs/` for existing context before starting any non-trivial task.
3. **Keep docs focused.** One topic per file — don't dump everything into a single document.
4. **Update, don't duplicate.** If context has changed, update the existing file rather than adding a conflicting one.
5. **Docs are authoritative.** When there is a conflict between `docs/` and other sources (comments, memory), the docs win.
6. **Commit and push.** Every doc change must be committed and pushed to GitHub so the repo stays the source of truth.
