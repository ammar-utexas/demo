# Platform Requirements: Patient Records — Web Frontend (SUB-PR-WEB)

**Parent:** [SUB-PR (Domain)](../domain/SUB-PR.md)
**Platform:** Web Frontend (WEB) — 8 requirements

---

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
