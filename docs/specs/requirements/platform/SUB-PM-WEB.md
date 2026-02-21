# Platform Requirements: Prompt Management — Web Frontend (SUB-PM-WEB)

**Parent:** [SUB-PM (Domain)](../domain/SUB-PM.md)
**Platform:** Web Frontend (WEB) — 5 requirements

---

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-PM-0001-WEB | SUB-PM-0001 | Auth guard for prompt management pages using parameterized `requireRole` (follows PC-WEB-01 / PC-WEB-03 precedent) | `lib/auth.ts`, `app/prompts/` | TST-PM-0001-WEB | Not Started |
| SUB-PM-0003-WEB | SUB-PM-0003 | Prompt CRUD forms: create form (name + text), list view, detail view, edit form. Display 409 conflict error on duplicate name submission. | `app/prompts/` | TST-PM-0003-WEB | Not Started |
| SUB-PM-0004-WEB | SUB-PM-0004 | Version indicator in prompt editor: display current version number, show "saving creates new version" notice before submission | `app/prompts/[id]/edit/` | TST-PM-0004-WEB | Not Started |
| SUB-PM-0006-WEB | SUB-PM-0006 | Version history list with pagination controls for each prompt | `app/prompts/[id]/versions/` | TST-PM-0006-WEB | Not Started |
| SUB-PM-0007-WEB | SUB-PM-0007 | Comparison UI: version selector (two dropdowns), trigger comparison, display natural-language diff summary returned by backend | `app/prompts/[id]/compare/` | TST-PM-0007-WEB | Not Started |
