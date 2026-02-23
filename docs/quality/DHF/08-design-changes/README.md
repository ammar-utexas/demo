# 08 — Design Changes (ISO 13485:2016 Clause 7.3.9)

Architecture Decision Records (ADRs) serve as both **design output** (Clause 7.3.4) and **design change records** (Clause 7.3.9). Each ADR documents the context, options considered, decision rationale, and consequences of a design change.

## Deliverables

The ADR files are located in:

```
docs/quality/DHF/03-design-output/
├── 0001-repo-based-knowledge-management.md
├── 0002-multi-repo-structure.md
├── 0003-backend-tech-stack.md
├── ...
└── 0021-derm-database-migration.md
```

> **Why not duplicated here?** ADRs are inherently change records — they document _what changed_ and _why_. Duplicating them into a separate folder adds maintenance burden without traceability value. The DHF-index.md traceability matrix maps Clause 7.3.9 to the `03-design-output/` folder.

## Cross-Reference

- **DHF Index:** [../DHF-index.md](../DHF-index.md) — Clause 7.3.9 row
- **Source files:** `docs/architecture/0001–0021`
- **DHF copies:** `docs/quality/DHF/03-design-output/`
