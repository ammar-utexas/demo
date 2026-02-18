# Subsystem Requirements: Prompt Management (SUB-PM)

**Document ID:** PMS-SUB-PM-001
**Version:** 1.0
**Date:** 2026-02-18
**Parent:** [System Requirements](SYS-REQ.md)

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

### Backend (BE) — 7 requirements

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-PM-0001-BE | SUB-PM-0001 | Enforce JWT auth on all prompt API endpoints via shared `require_auth` middleware (follows PC-BE-02 / PC-BE-06 precedent) | `middleware/auth.py`, `routers/prompts.py` | TST-PM-0001-BE | Not Started |
| SUB-PM-0002-BE | SUB-PM-0002 | Enforce role-based access control on prompt API endpoints: admin for create/update/delete, admin+physician for read | `middleware/auth.py:require_role`, `routers/prompts.py` | TST-PM-0002-BE | Not Started |
| SUB-PM-0003-BE | SUB-PM-0003 | REST CRUD endpoints for prompts (`POST /prompts/`, `GET /prompts/`, `GET /prompts/{id}`, `PUT /prompts/{id}`, `DELETE /prompts/{id}`). Prompt name uniqueness enforced via DB unique constraint; service catches IntegrityError and returns 409. | `routers/prompts.py`, `services/prompt_service.py`, `models/prompt.py` | TST-PM-0003-BE | Not Started |
| SUB-PM-0004-BE | SUB-PM-0004 | Auto-versioning: on every prompt text save, insert a new row into `prompt_versions` with an auto-incremented version number. Use `SELECT MAX(version) FROM prompt_versions WHERE prompt_id = ? FOR UPDATE` to serialize concurrent version creation (DC-PM-02, RC-BE-09). Versions are immutable once created. | `services/prompt_service.py`, `models/prompt_version.py` | TST-PM-0004-BE | Not Started |
| SUB-PM-0005-BE | SUB-PM-0005 | Audit log all prompt operations using standardized action strings: PROMPT_CREATE, PROMPT_READ, PROMPT_UPDATE, PROMPT_DELETE, VERSION_CREATE, VERSION_COMPARE. Resource type: `prompt`. Follows audit event catalog pattern (PC-BE-03 / PC-BE-07). | `services/audit_service.py`, `routers/prompts.py` | TST-PM-0005-BE | Not Started |
| SUB-PM-0006-BE | SUB-PM-0006 | Paginated version history API endpoint (`GET /prompts/{id}/versions?page=1&size=20`). Returns versions ordered by version number descending with total count. | `routers/prompts.py`, `services/prompt_service.py` | TST-PM-0006-BE | Not Started |
| SUB-PM-0007-BE | SUB-PM-0007 | Version comparison API endpoint (`POST /prompts/{id}/versions/compare`). Accepts two version numbers, retrieves both version texts, calls Anthropic Claude API (`claude-sonnet-4-20250514`) with the managed comparison prompt, and returns the natural-language diff summary. 30-second timeout on LLM call; rate-limited to prevent abuse (RC-BE-10). Endpoint validates that both versions belong to the same prompt (DC-PM-03). | `routers/prompts.py`, `services/prompt_service.py`, `services/llm_service.py` | TST-PM-0007-BE | Not Started |

### Web Frontend (WEB) — 5 requirements

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-PM-0001-WEB | SUB-PM-0001 | Auth guard for prompt management pages using parameterized `requireRole` (follows PC-WEB-01 / PC-WEB-03 precedent) | `lib/auth.ts`, `app/prompts/` | TST-PM-0001-WEB | Not Started |
| SUB-PM-0003-WEB | SUB-PM-0003 | Prompt CRUD forms: create form (name + text), list view, detail view, edit form. Display 409 conflict error on duplicate name submission. | `app/prompts/` | TST-PM-0003-WEB | Not Started |
| SUB-PM-0004-WEB | SUB-PM-0004 | Version indicator in prompt editor: display current version number, show "saving creates new version" notice before submission | `app/prompts/[id]/edit/` | TST-PM-0004-WEB | Not Started |
| SUB-PM-0006-WEB | SUB-PM-0006 | Version history list with pagination controls for each prompt | `app/prompts/[id]/versions/` | TST-PM-0006-WEB | Not Started |
| SUB-PM-0007-WEB | SUB-PM-0007 | Comparison UI: version selector (two dropdowns), trigger comparison, display natural-language diff summary returned by backend | `app/prompts/[id]/compare/` | TST-PM-0007-WEB | Not Started |

### AI Infrastructure (AI) — 1 requirement

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-PM-0007-AI | SUB-PM-0007 | Anthropic Claude API integration for prompt version comparison. Uses `claude-sonnet-4-20250514` model. Prompt text is NOT PHI — external API calls are acceptable. The comparison template is itself a managed prompt bootstrapped via migration. | `services/llm_service.py` | TST-PM-0007-AI | Not Started |
