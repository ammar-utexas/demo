# ADR-0003: Backend Tech Stack — FastAPI with Async SQLAlchemy

**Date:** 2026-02-15
**Status:** Accepted

## Context

The PMS backend needs to serve REST APIs for patient records, clinical workflows, medication management, and reporting. It must be HIPAA-compliant, supporting encryption at rest, audit logging, and role-based access control.

## Options Considered

1. **Django + DRF** — Mature, batteries-included, sync by default.
   - Pros: Built-in admin, ORM, auth.
   - Cons: Heavier, sync-first, less ergonomic for async workloads.

2. **FastAPI + SQLAlchemy async** — Modern, async-native, Pydantic-integrated.
   - Pros: Native async, automatic OpenAPI docs, Pydantic v2 validation, high performance.
   - Cons: Less built-in (no admin panel), requires manual auth setup.

3. **Flask + SQLAlchemy** — Lightweight, flexible.
   - Pros: Simple, well-known.
   - Cons: No async by default, manual schema validation, no auto-generated docs.

## Decision

Use **FastAPI with async SQLAlchemy + asyncpg**.

## Key Dependencies

| Library | Purpose |
|---|---|
| FastAPI | Web framework with auto OpenAPI docs |
| SQLAlchemy 2.0 (async) | ORM with async session support |
| asyncpg | PostgreSQL async driver |
| Pydantic v2 | Request/response validation |
| pydantic-settings | Environment configuration |
| python-jose | JWT token creation/verification |
| bcrypt | Password hashing |
| Alembic | Database migrations |

## Architecture

Layered architecture with clear separation:

```
routers/    → HTTP endpoint definitions (thin)
services/   → Business logic (testable without HTTP)
models/     → SQLAlchemy ORM models
schemas/    → Pydantic request/response models
middleware/ → Cross-cutting concerns (audit, auth)
```

## HIPAA Compliance Features

- **SYS-REQ-0001**: JWT-based authentication with RBAC middleware
- **SYS-REQ-0002**: AES encryption service for PHI fields (SSN)
- **SYS-REQ-0003**: Audit logging middleware + service for all data access
- **SYS-REQ-0005**: Role-based access control via `require_role()` dependency

## Consequences

- All database operations must use async sessions.
- PHI fields must be encrypted via `encryption_service` before persistence.
- Every state-changing endpoint must produce an audit log entry.
