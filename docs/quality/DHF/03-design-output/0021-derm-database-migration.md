# ADR-0021: Database Migration Strategy

**Date:** 2026-02-21
**Status:** Accepted
**Deciders:** Development Team

---

## Context

The Dermatology CDS module introduces several new database objects: tables (`lesion_images`, `lesion_classifications`, `isic_reference_embeddings`, `patient_lesion_embeddings`, `lesion_records`, `derm_audit_log`), the pgvector extension, and IVFFlat/HNSW indexes. These must be created in a controlled, repeatable manner across development, QA, staging, production, and Jetson edge environments.

The existing PMS backend uses Alembic for database migrations (ADR-0003). The Dermatology CDS service also connects to the same PostgreSQL instance for pgvector queries. The question is whether the derm-specific tables should be managed by the backend's Alembic migrations or by raw SQL scripts owned by the CDS service.

## Options Considered

1. **Alembic-managed migrations (in PMS backend)** — Add derm tables as new Alembic migration files in the existing backend migration chain.
   - Pros: Single migration toolchain, version-controlled, rollback support, integrated with backend deployment, team already familiar with Alembic.
   - Cons: CDS-specific tables managed by the backend (cross-service ownership), pgvector extension creation requires superuser (Alembic runs as app user).

2. **Raw SQL scripts in CDS service** — Standalone SQL files (`init_db.sql`) executed manually or via entrypoint script.
   - Pros: CDS owns its own schema, simple SQL files, easy to understand.
   - Cons: No version control for schema changes, no rollback, no migration history, manual execution error-prone, doesn't integrate with backend deployment pipeline.

3. **Separate Alembic instance in CDS service** — CDS has its own Alembic configuration managing only derm tables.
   - Pros: CDS owns its own migrations, version-controlled, rollback support.
   - Cons: Two Alembic instances against one database, migration ordering conflicts, duplicate migration infrastructure.

4. **Flyway or Liquibase** — Alternative migration tool alongside Alembic.
   - Pros: Established tools with good PostgreSQL support.
   - Cons: Another tool in the stack, team unfamiliar, Java dependency (Flyway/Liquibase), conflicts with Alembic.

## Decision

Use **Alembic-managed migrations in the PMS backend** for all dermatology database objects, with the pgvector extension created via a migration that runs with elevated privileges during initial setup.

## Rationale

1. **Single migration chain** — All database schema changes (patient records, encounters, medications, AND dermatology) are in one Alembic migration chain with clear ordering. No risk of competing migrations or out-of-order execution.
2. **Version-controlled rollback** — Alembic's `downgrade` capability enables rolling back derm schema changes without affecting other tables. Raw SQL scripts don't support this.
3. **Team familiarity** — The development team already writes and reviews Alembic migrations for core PMS tables. No new tooling to learn.
4. **CI/CD integration** — The existing deployment pipeline runs `alembic upgrade head` as part of backend deployment. Derm migrations execute automatically in the same step.
5. **Cross-environment consistency** — The same Alembic migration chain runs in dev, QA, staging, production, and Jetson edge, ensuring identical schema everywhere.
6. **pgvector extension handling** — The `CREATE EXTENSION IF NOT EXISTS vector` statement is idempotent and can be the first step in the derm migration. If it requires superuser, the initial setup SOP grants extension creation privilege to the migration user.

## Migration Plan

```
Existing Alembic chain:
  001_initial_schema.py          (patients, encounters, medications)
  002_add_audit_logging.py       (audit_log table)
  003_add_encryption_fields.py   (SSN encryption columns)
  ...

New derm migrations (appended):
  00X_create_pgvector_extension.py
    - CREATE EXTENSION IF NOT EXISTS vector

  00X_create_lesion_tables.py
    - lesion_records (persistent lesion identity)
    - lesion_images (encrypted image storage)
    - lesion_classifications (AI classification results)
    - derm_audit_log (HIPAA audit trail)

  00X_create_vector_tables.py
    - isic_reference_embeddings (ISIC cache with vector(512))
    - patient_lesion_embeddings (patient vectors for tracking)
    - IVFFlat indexes on both tables

  00X_add_lesion_change_tracking.py
    - Add change_score column to patient_lesion_embeddings
    - Add lesion_record_id FK to lesion_images
    - Add status column to lesion_records
```

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| Raw SQL scripts in CDS | No version control, no rollback, manual execution, no migration history |
| Separate Alembic in CDS | Two migration instances against one DB, ordering conflicts, duplication |
| Flyway/Liquibase | New tool, team unfamiliar, Java dependency, conflicts with existing Alembic |
| Schema per service | PostgreSQL schema isolation adds query complexity, pgvector indexes don't span schemas efficiently |

## Trade-offs

- **Cross-service ownership** — The backend's Alembic manages tables used primarily by the CDS service. This creates a soft dependency: CDS schema changes require a backend migration. Mitigated by: migrations are just DDL, they don't import backend Python code, and the CDS team can author migrations in the backend repo.
- **pgvector superuser requirement** — `CREATE EXTENSION` typically requires superuser. Mitigated by: running this once during initial setup (not on every deploy), granting `CREATE` privilege on the database to the migration user, or using the pgvector Docker image which pre-installs the extension.
- **Migration testing** — Derm migrations must be tested against a database with pgvector installed. CI pipeline needs a pgvector-enabled PostgreSQL image for migration tests.

## Consequences

- All dermatology tables are defined as Alembic migration files in `pms-backend/alembic/versions/`.
- The Docker Compose PostgreSQL image is changed to `pgvector/pgvector:pg16` to pre-install the extension.
- Migration files follow the existing naming convention with descriptive slugs.
- The CDS service does NOT run migrations — it assumes the schema exists (created by backend migrations).
- `alembic upgrade head` in CI/CD creates all tables including derm tables.
- Rollback: `alembic downgrade` to the pre-derm revision removes all derm tables and indexes.
- The setup guide (docs/experiments/18-ISICArchive-PMS-Developer-Setup-Guide.md) references running migrations before starting the CDS service.

## References

- Related PRD: docs/experiments/18-PRD-ISICArchive-PMS-Integration.md
- Related Requirements: SYS-REQ-0012
- Related ADRs: ADR-0003 (Backend Tech Stack — Alembic), ADR-0010 (Image Storage), ADR-0011 (Vector Database)
