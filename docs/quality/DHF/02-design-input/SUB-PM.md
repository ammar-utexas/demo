# Subsystem Requirements: Prompt Management (SUB-PM)

**Document ID:** PMS-SUB-PM-001
**Version:** 1.0
**Date:** 2026-02-18
**Parent:** [System Requirements](../SYS-REQ.md)

---

## Scope

The Prompt Management subsystem provides centralized CRUD, automatic versioning, audit logging, and LLM-powered comparison for AI prompts used across the PMS (OpenClaw skills, MiniMax M2.5 agents, clinical document drafting). Prompt management is an administrative activity performed via the web frontend; no Android platform requirements are defined in v1.0 (can be added later via governance procedure 2.1).

## Requirements

| Req ID | Parent | Description | Verification | Status |
|---|---|---|---|---|
| SUB-PM-0001 | SYS-REQ-0001 | Require authenticated session for all prompt management operations | Test | Not Started |
| SUB-PM-0002 | SYS-REQ-0005 | Enforce RBAC: administrator can create, update, and delete prompts; administrator and physician can read prompts | Test | Not Started |
| SUB-PM-0003 | SYS-REQ-0011 | Support CRUD operations for prompts (name + text). Prompt names must be unique; the database unique constraint is authoritative and the service layer must handle IntegrityError and return HTTP 409 (mirrors SUB-PR-0006 pattern, see DC-PM-01). | Test | Not Started |
| SUB-PM-0004 | SYS-REQ-0011 | Auto-versioning: every text save creates a new immutable version. Version numbers are serialized via `SELECT MAX(version) ... FOR UPDATE` to prevent concurrent conflicts (see DC-PM-02). | Test | Not Started |
| SUB-PM-0005 | SYS-REQ-0003 | Log all prompt operations (create, update, delete, read, version_create, version_compare) to the audit trail with user_id, action, resource_type, resource_id, timestamp, and IP address | Test | Not Started |
| SUB-PM-0006 | SYS-REQ-0011 | Provide paginated version history listing for each prompt (default: 20 per page, ordered by version descending) | Test | Not Started |
| SUB-PM-0007 | SYS-REQ-0011 | LLM-powered version comparison: given two versions of the same prompt, generate a natural-language diff summary via Anthropic Claude API. The comparison template is itself stored as a managed prompt, bootstrapped via database migration (see DC-PM-03). | Test | Not Started |

## Design Decisions

1. **No Android (AND) requirements** — prompt management is an admin activity, not a mobile clinical workflow. Can be added later via governance procedure 2.1.
2. **LLM provider** — Anthropic Claude API (already configured for OpenClaw). Model: `claude-sonnet-4-20250514` for cost-effective comparison. Prompt text is NOT PHI, so external API calls are acceptable.
3. **Version serialization** — `SELECT MAX(version) ... FOR UPDATE` prevents concurrent version number conflicts (mirrors RC-BE-01 pattern).
4. **Prompt name uniqueness** — DB unique constraint is authoritative; service catches IntegrityError and returns 409 (mirrors SUB-PR-0006 pattern).
5. **Comparison prompt as managed prompt** — the LLM comparison template is itself stored as a managed prompt, bootstrapped via migration.

## Platform Decomposition

| Platform | File | Req Count |
|----------|------|-----------|
| Backend (BE) | [SUB-PM-BE](../platform/SUB-PM-BE.md) | 7 |
| Web Frontend (WEB) | [SUB-PM-WEB](../platform/SUB-PM-WEB.md) | 5 |
| AI Infrastructure (AI) | [SUB-PM-AI](../platform/SUB-PM-AI.md) | 1 |
