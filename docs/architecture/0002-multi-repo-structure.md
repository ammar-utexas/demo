# ADR-0002: Multi-Repository Structure with Shared Docs Submodule

**Date:** 2026-02-15
**Status:** Accepted

## Context

The Patient Management System (PMS) requires three client/server applications: a Python/FastAPI backend, a Next.js web frontend, and a Kotlin/Compose Android app — plus an AI platform hosting dermatology clinical decision support and other AI services. We needed to decide how to organize the codebase.

## Options Considered

1. **Monorepo** — All three projects in a single repository.
   - Pros: Atomic commits across projects, single CI pipeline.
   - Cons: Large repo, mixed toolchains (Python + Node + Gradle), complex CI matrix, tight coupling.

2. **Separate repos with shared docs submodule** — One repo per project, docs shared via Git submodule.
   - Pros: Independent deployment cycles, focused CI per language, clean separation of concerns, shared knowledge base.
   - Cons: Cross-repo changes require multiple PRs, submodule requires manual sync.

3. **Separate repos, no shared docs** — Fully independent repositories.
   - Pros: Maximum independence.
   - Cons: Duplicated documentation, no single source of truth, knowledge fragmentation.

## Decision

Use **separate repositories with a shared docs submodule** (Option 2).

### Repository Layout

| Repository | Purpose | Tech Stack |
|---|---|---|
| `ammar-utexas/demo` | Shared docs + project knowledge base | Markdown |
| `ammar-utexas/pms-backend` | REST API server | Python, FastAPI, SQLAlchemy |
| `ammar-utexas/pms-frontend` | Web application | Next.js, React, TypeScript |
| `ammar-utexas/pms-android` | Android mobile app | Kotlin, Jetpack Compose |
| `ammar-utexas/pms-ai` | AI platform (Dermatology CDS, AI Gateway) | Python, FastAPI, ONNX Runtime, pgvector |

Each project repo includes `docs/` as a Git submodule pointing to `ammar-utexas/demo`.

## Rationale

- **Independent release cycles**: Backend, frontend, Android, and AI platform can be deployed independently.
- **Focused CI/CD**: Each repo has a single language toolchain, simplifying build pipelines.
- **Shared knowledge**: The `docs/` submodule ensures all repos have access to the same architecture decisions, API contracts, and feature documentation.
- **Team scalability**: Different team members can own different repos without merge conflicts across languages.
- **AI isolation**: AI services (dermatology CDS, AI gateway, shared model infrastructure) live in a dedicated repository, keeping ML dependencies and GPU-heavy Docker images separate from the core backend API.

## Consequences

- Cross-cutting changes (e.g., new API endpoint) require updates in multiple repos.
- The `docs/` submodule must be updated in each repo after changes to the demo repo.
- API contracts in `docs/api/` serve as the canonical interface between frontend and backend.
