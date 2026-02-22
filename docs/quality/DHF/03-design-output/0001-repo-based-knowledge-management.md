# ADR-0001: Use Repository-Based Knowledge Management

**Date:** 2026-02-15
**Status:** Accepted

## Context

We needed a centralized way for AI agents and developers to store and retrieve project knowledge — architectural decisions, implementation details, bug analyses, and configuration docs.

Initially, we evaluated NotebookLM as the knowledge store. However, we encountered authentication and API reliability issues that made it impractical:
- The `notebooklm` CLI's `add-text` and `add-file` commands failed to persist sources.
- Google's 2-Step Verification and passkey requirements made automated browser auth difficult.
- The dependency on an external service introduced fragility into the workflow.

## Options Considered

1. **NotebookLM** — AI-powered notebook with built-in Q&A over sources.
   - Pros: Natural language querying, automatic summarization.
   - Cons: Unreliable CLI, authentication complexity, external dependency, not version-controlled.

2. **Markdown files in the repo** — Store docs in a `docs/` directory, committed to Git.
   - Pros: Version-controlled, always available, no auth needed, works offline, reviewable in PRs.
   - Cons: No built-in Q&A; requires manual organization.

3. **Wiki (GitHub Wiki or Notion)** — External wiki tool.
   - Pros: Rich editing, search.
   - Cons: Separate from code, not version-controlled with the codebase, additional tool dependency.

## Decision

Use **markdown files in the repo** (`docs/` directory) as the single source of truth.

## Rationale

- **Reliability**: No external service dependencies. If the repo is accessible, the docs are accessible.
- **Version control**: Every change is tracked, reviewable, and revertible through Git.
- **Colocation**: Documentation lives alongside the code it describes.
- **Simplicity**: Standard markdown requires no special tooling.

## Consequences

- Developers and agents must manually organize and maintain the `docs/` directory.
- The `docs/index.md` file must be kept up to date as a table of contents.
- No natural language querying — agents must read files directly to find context.
