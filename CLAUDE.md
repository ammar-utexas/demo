# Project Agent Instructions

## Repository Docs as Single Source of Truth

This project uses **markdown files in the `docs/` directory** as the central knowledge repository. All project context, decisions, and implementation details must be stored there — committed to the repo and pushed to GitHub.

### Directory Structure

```
docs/
├── architecture/        # Architectural Decision Records (ADRs)
├── features/            # Implementation details for completed features
├── bugs/                # Root cause analyses for non-trivial bugs
├── api/                 # API contracts, schemas, and interface docs
├── config/              # Dependencies, environment setup, and configuration
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
