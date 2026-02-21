# Platform Requirements: Prompt Management — Backend (SUB-PM-BE)

**Parent:** [SUB-PM (Domain)](../domain/SUB-PM.md)
**Platform:** Backend (BE) — 7 requirements

---

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-PM-0001-BE | SUB-PM-0001 | Enforce JWT auth on all prompt API endpoints via shared `require_auth` middleware (follows PC-BE-02 / PC-BE-06 precedent) | `middleware/auth.py`, `routers/prompts.py` | TST-PM-0001-BE | Not Started |
| SUB-PM-0002-BE | SUB-PM-0002 | Enforce role-based access control on prompt API endpoints: admin for create/update/delete, admin+physician for read | `middleware/auth.py:require_role`, `routers/prompts.py` | TST-PM-0002-BE | Not Started |
| SUB-PM-0003-BE | SUB-PM-0003 | REST CRUD endpoints for prompts (`POST /prompts/`, `GET /prompts/`, `GET /prompts/{id}`, `PUT /prompts/{id}`, `DELETE /prompts/{id}`). Prompt name uniqueness enforced via DB unique constraint; service catches IntegrityError and returns 409. | `routers/prompts.py`, `services/prompt_service.py`, `models/prompt.py` | TST-PM-0003-BE | Not Started |
| SUB-PM-0004-BE | SUB-PM-0004 | Auto-versioning: on every prompt text save, insert a new row into `prompt_versions` with an auto-incremented version number. Use `SELECT MAX(version) FROM prompt_versions WHERE prompt_id = ? FOR UPDATE` to serialize concurrent version creation (DC-PM-02, RC-BE-09). Versions are immutable once created. | `services/prompt_service.py`, `models/prompt_version.py` | TST-PM-0004-BE | Not Started |
| SUB-PM-0005-BE | SUB-PM-0005 | Audit log all prompt operations using standardized action strings: PROMPT_CREATE, PROMPT_READ, PROMPT_UPDATE, PROMPT_DELETE, VERSION_CREATE, VERSION_COMPARE. Resource type: `prompt`. Follows audit event catalog pattern (PC-BE-03 / PC-BE-07). | `services/audit_service.py`, `routers/prompts.py` | TST-PM-0005-BE | Not Started |
| SUB-PM-0006-BE | SUB-PM-0006 | Paginated version history API endpoint (`GET /prompts/{id}/versions?page=1&size=20`). Returns versions ordered by version number descending with total count. | `routers/prompts.py`, `services/prompt_service.py` | TST-PM-0006-BE | Not Started |
| SUB-PM-0007-BE | SUB-PM-0007 | Version comparison API endpoint (`POST /prompts/{id}/versions/compare`). Accepts two version numbers, retrieves both version texts, calls Anthropic Claude API (`claude-sonnet-4-20250514`) with the managed comparison prompt, and returns the natural-language diff summary. 30-second timeout on LLM call; rate-limited to prevent abuse (RC-BE-10). Endpoint validates that both versions belong to the same prompt (DC-PM-03). | `routers/prompts.py`, `services/prompt_service.py`, `services/llm_service.py` | TST-PM-0007-BE | Not Started |
