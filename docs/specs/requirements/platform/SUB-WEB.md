# Platform Requirements: Web Frontend (SUB-WEB)

**Version:** 1.0
**Date:** 2026-02-21
**Platform:** Web Frontend (WEB) — 24 requirements across 5 domains
**Repository:** pms-frontend
**Technology:** Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS 3

---

## Summary

| Domain | Req Count | Status Breakdown |
|--------|-----------|-----------------|
| Patient Records (PR) | 8 | 1 Scaffolded, 7 Not Started |
| Clinical Workflow (CW) | 3 | 1 Scaffolded, 2 Not Started |
| Medication Management (MM) | 2 | 1 Scaffolded, 1 Not Started |
| Reporting & Analytics (RA) | 6 | 1 Scaffolded, 5 Not Started |
| Prompt Management (PM) | 5 | 5 Not Started |
| **Total** | **24** | |

---

## Patient Records (SUB-PR)

**Parent:** [SUB-PR (Domain)](../domain/SUB-PR.md)

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-PR-0001-WEB | SUB-PR-0001 | Auth guard and token management for patient pages. Guard must be parameterized (`requireRole(['admin', 'physician'])`) — role lists are subsystem-specific (PC-WEB-01). Must implement token refresh lock: a single Promise serializes concurrent refresh attempts to prevent thundering herd (RC-WEB-01). | `lib/auth.ts` | TST-PR-0001-WEB | Scaffolded |
| SUB-PR-0003-WEB | SUB-PR-0003 | Patient CRUD forms and list views. Edit form must include patient `version` in hidden state; on 409 response (optimistic lock conflict), display conflict resolution dialog prompting user to reload (RC-WEB-02). | `app/patients/` | TST-PR-0003-WEB | Not Started |
| SUB-PR-0007-WEB | SUB-PR-0007 | Patient search UI with filters | — | TST-PR-0007-WEB | Not Started |
| SUB-PR-0008-WEB | SUB-PR-0008 | Paginated patient list with navigation controls | — | TST-PR-0008-WEB | Not Started |
| SUB-PR-0013-WEB | SUB-PR-0013 | Lesion image upload component with drag-and-drop, anatomical site selector, and image preview. Accessible from encounter detail page at `/encounters/[id]/dermatology` | `components/dermatology/LesionUploader.tsx`, `app/encounters/[id]/dermatology/page.tsx` | TST-PR-0013-WEB | Not Started |
| SUB-PR-0014-WEB | SUB-PR-0014 | Similar Lesions Gallery component displaying top-10 ISIC reference image thumbnails with diagnosis labels and similarity scores | `components/dermatology/SimilarGallery.tsx` | TST-PR-0014-WEB | Not Started |
| SUB-PR-0015-WEB | SUB-PR-0015 | Risk assessment banner component with severity color coding (red/yellow/green), referral urgency, and contributing risk factors. Includes clinical disclaimer. | `components/dermatology/ClassificationResults.tsx` | TST-PR-0015-WEB | Not Started |
| SUB-PR-0016-WEB | SUB-PR-0016 | Lesion Change Timeline component showing chronological assessment history with change detection indicators for a given patient and anatomical site | `components/dermatology/LesionTimeline.tsx` | TST-PR-0016-WEB | Not Started |

---

## Clinical Workflow (SUB-CW)

**Parent:** [SUB-CW (Domain)](../domain/SUB-CW.md)

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-CW-0001-WEB | SUB-CW-0001 | Auth guard for encounter pages | `lib/auth.ts` | TST-CW-0001-WEB | Scaffolded |
| SUB-CW-0003-WEB | SUB-CW-0003 | Encounter lifecycle UI (list, create, status updates) | `app/encounters/` | TST-CW-0003-WEB | Not Started |
| SUB-CW-0006-WEB | SUB-CW-0006 | Encounter type selection in forms | `app/encounters/page.tsx` | TST-CW-0006-WEB | Not Started |

---

## Medication Management (SUB-MM)

**Parent:** [SUB-MM (Domain)](../domain/SUB-MM.md)

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-MM-0001-WEB | SUB-MM-0001 | Drug interaction warning display on medication page | `app/medications/page.tsx` | TST-MM-0001-WEB | Not Started |
| SUB-MM-0006-WEB | SUB-MM-0006 | Auth guard for medication pages | `lib/auth.ts` | TST-MM-0006-WEB | Scaffolded |

---

## Reporting & Analytics (SUB-RA)

**Parent:** [SUB-RA (Domain)](../domain/SUB-RA.md)

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-RA-0001-WEB | SUB-RA-0001 | Patient volume dashboard with date range controls. Must display a "last refreshed" timestamp and use a cache TTL. Dashboard data may lag real-time patient list data by up to the cache TTL (eventual consistency accepted) (PC-WEB-02). | `app/reports/page.tsx` | TST-RA-0001-WEB | Not Started |
| SUB-RA-0002-WEB | SUB-RA-0002 | Encounter summary dashboard with charts | `app/reports/page.tsx` | TST-RA-0002-WEB | Not Started |
| SUB-RA-0003-WEB | SUB-RA-0003 | Audit log query interface with filter controls | — | TST-RA-0003-WEB | Not Started |
| SUB-RA-0004-WEB | SUB-RA-0004 | Auth guard for report pages | `lib/auth.ts` | TST-RA-0004-WEB | Scaffolded |
| SUB-RA-0006-WEB | SUB-RA-0006 | Medication usage dashboard with charts | `app/reports/page.tsx` | TST-RA-0006-WEB | Not Started |
| SUB-RA-0008-WEB | SUB-RA-0008 | Dermatology analytics dashboard with classification volume charts, risk distribution pie chart, referral trend line chart, and model confidence histogram | `app/reports/dermatology/page.tsx` | TST-RA-0008-WEB | Not Started |

---

## Prompt Management (SUB-PM)

**Parent:** [SUB-PM (Domain)](../domain/SUB-PM.md)

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-PM-0001-WEB | SUB-PM-0001 | Auth guard for prompt management pages using parameterized `requireRole` (follows PC-WEB-01 / PC-WEB-03 precedent) | `lib/auth.ts`, `app/prompts/` | TST-PM-0001-WEB | Not Started |
| SUB-PM-0003-WEB | SUB-PM-0003 | Prompt CRUD forms: create form (name + text), list view, detail view, edit form. Display 409 conflict error on duplicate name submission. | `app/prompts/` | TST-PM-0003-WEB | Not Started |
| SUB-PM-0004-WEB | SUB-PM-0004 | Version indicator in prompt editor: display current version number, show "saving creates new version" notice before submission | `app/prompts/[id]/edit/` | TST-PM-0004-WEB | Not Started |
| SUB-PM-0006-WEB | SUB-PM-0006 | Version history list with pagination controls for each prompt | `app/prompts/[id]/versions/` | TST-PM-0006-WEB | Not Started |
| SUB-PM-0007-WEB | SUB-PM-0007 | Comparison UI: version selector (two dropdowns), trigger comparison, display natural-language diff summary returned by backend | `app/prompts/[id]/compare/` | TST-PM-0007-WEB | Not Started |
