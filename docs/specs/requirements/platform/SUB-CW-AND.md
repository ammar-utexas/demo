# Platform Requirements: Clinical Workflow — Android (SUB-CW-AND)

**Parent:** [SUB-CW (Domain)](../domain/SUB-CW.md)
**Platform:** Android (AND) — 3 requirements

---

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-CW-0001-AND | SUB-CW-0001 | Auth interceptor for encounter API calls | `data/api/AuthInterceptor.kt` | TST-CW-0001-AND | Scaffolded |
| SUB-CW-0003-AND | SUB-CW-0003 | Encounter lifecycle screens with Compose UI. Must implement offline-sync conflict resolution: sync requests include `version`/`updated_at`, backend 409 conflicts are queued and presented in a resolution UI (RC-AND-02). | `ui/encounters/` | TST-CW-0003-AND | Not Started |
| SUB-CW-0006-AND | SUB-CW-0006 | Encounter type selection in Compose forms | `ui/encounters/EncountersScreen.kt` | TST-CW-0006-AND | Not Started |
