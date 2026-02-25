# Platform Requirements: Web Frontend (SUB-WEB)

**Version:** 1.2
**Date:** 2026-02-23
**Platform:** Web Frontend (WEB) — 35 requirements across 6 domains
**Repository:** pms-frontend
**Technology:** Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS 3

---

## Summary

| Domain | Req Count | Status Breakdown |
|--------|-----------|-----------------|
| Patient Records (PR) | 8 | 1 Scaffolded, 7 Not Started |
| Clinical Workflow (CW) | 4 | 1 Scaffolded, 3 Not Started |
| Medication Management (MM) | 2 | 1 Scaffolded, 1 Not Started |
| Reporting & Analytics (RA) | 6 | 1 Scaffolded, 5 Not Started |
| Prompt Management (PM) | 5 | 5 Not Started |
| Authentication & User Mgmt (AU) | 10 | 10 Not Started |
| **Total** | **35** | |

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
| SUB-CW-0009-WEB | SUB-CW-0009 | DermaCheck workflow within encounter detail page: Lesion Image Capture Widget (file upload / USB dermoscope), anatomical site selector, classification results panel displaying `DermaCheckResult` (top-3 predictions, confidence chart, clinical narrative, risk level with severity color coding), similar lesions gallery, and save/discard action buttons. Accessible at `/encounters/[id]/dermatology`. Must handle `degraded` responses by showing "Narrative unavailable" or "Similar images unavailable" banners without blocking the physician from reviewing classification and risk. | `app/encounters/[id]/dermatology/page.tsx`, `components/dermatology/DermaCheckWorkflow.tsx` | TST-CW-0009-WEB | Not Started |

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

---

## Authentication & User Management (SUB-AU)

**Parent:** [SUB-AU (Domain)](../SUB-AU.md)

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-AU-0001-WEB | SUB-AU-0001 | Login page with OAuth provider buttons (Google, Microsoft, GitHub). Clicking a button redirects to `GET /auth/oauth/{provider}/authorize`. Handle callback redirect and store returned JWT. | `app/login/`, `lib/auth.ts` | TST-AU-0001-WEB | Verified |
| SUB-AU-0002-WEB | SUB-AU-0002 | Email/password login form on login page. Password reset request form (`/forgot-password`) and password reset form (`/reset-password?token=...`). Display validation errors from backend. | `app/login/`, `app/forgot-password/`, `app/reset-password/` | TST-AU-0002-WEB | Verified |
| SUB-AU-0003-WEB | SUB-AU-0003 | JWT token storage (httpOnly cookie or secure storage), auth guard with parameterized `requireRole` (follows PC-WEB-01). Token refresh with single-Promise lock to prevent thundering herd (RC-WEB-01). Logout clears tokens and redirects to login. | `lib/auth.ts`, `middleware.ts` | TST-AU-0003-WEB | Verified |
| SUB-AU-0004-WEB | SUB-AU-0004 | Display account lockout message on login form when backend returns lockout error. Show remaining lockout duration if provided. | `app/login/` | TST-AU-0004-WEB | Verified |
| SUB-AU-0006-WEB | SUB-AU-0006 | User management admin pages: paginated user list, create user form (email, name, role selection), user detail/edit form, deactivate/reactivate toggle, resend invite button. All pages guarded by `requireRole(['admin'])`. | `app/admin/users/` | TST-AU-0006-WEB | Verified |
| SUB-AU-0007-WEB | SUB-AU-0007 | Invite acceptance page (`/invite/accept?token=...`): validate token, display set-password form with complexity requirements, submit to activate account. Show error for expired/invalid tokens. | `app/invite/` | TST-AU-0007-WEB | Verified |
| SUB-AU-0008-WEB | SUB-AU-0008 | Multi-role selection in user create/edit forms (checkbox group for admin, clinician, sales, lab-staff). Display assigned roles in user list and detail views. At least one role must be selected (client-side validation). | `app/admin/users/` | TST-AU-0008-WEB | Verified |
| SUB-AU-0009-WEB | SUB-AU-0009 | Navigation and route visibility based on user's roles from JWT claims. Hide menu items and routes the user has no role to access. Redirect unauthorized access attempts to a 403 page. | `components/navigation/`, `middleware.ts` | TST-AU-0009-WEB | Verified |
| SUB-AU-0015-WEB | SUB-AU-0015 | Current user profile page (`/profile`): display user name, email, and assigned roles from `GET /users/me`. Available to all authenticated users. | `app/profile/` | TST-AU-0015-WEB | Verified |
| SUB-AU-0016-WEB | SUB-AU-0016 | Auth bypass in frontend auth context: when `NEXT_PUBLIC_AUTH_BYPASS_ENABLED=true`, skip login redirect and inject a mock user into the auth context with role from `NEXT_PUBLIC_AUTH_BYPASS_ROLE` (default `admin`), email from `NEXT_PUBLIC_AUTH_BYPASS_EMAIL` (default `dev@localhost`), and name from `NEXT_PUBLIC_AUTH_BYPASS_NAME` (default `Dev User`). Display a persistent banner ("Auth Bypass Active — Development Mode") in the application header. The banner must be visually prominent (yellow/warning) and non-dismissible. | `lib/auth.ts`, `components/layout/Header.tsx` | TST-AU-0016-WEB | Verified |
