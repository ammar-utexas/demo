# Platform Requirements: Android (SUB-AND)

**Version:** 1.0
**Date:** 2026-02-21
**Platform:** Android (AND) — 19 requirements across 4 domains
**Repository:** pms-android
**Technology:** Kotlin, Jetpack Compose, Hilt (DI), Retrofit (HTTP), Room (local DB), DataStore (preferences), offline-first architecture

---

## Summary

| Domain | Req Count | Status Breakdown |
|--------|-----------|-----------------|
| Patient Records (PR) | 8 | 1 Scaffolded, 7 Not Started |
| Clinical Workflow (CW) | 4 | 1 Scaffolded, 3 Not Started |
| Medication Management (MM) | 2 | 1 Scaffolded, 1 Not Started |
| Reporting & Analytics (RA) | 5 | 1 Scaffolded, 4 Not Started |
| **Total** | **19** | |

---

## Patient Records (SUB-PR)

**Parent:** [SUB-PR (Domain)](../domain/SUB-PR.md)

| Platform Req ID | Parent | SYS-REQ | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|---|
| SUB-PR-0001-AND | SUB-PR-0001 | SYS-REQ-0001 | Auth interceptor for patient API calls. Must implement token refresh synchronization via Kotlin `Mutex` — first caller refreshes, subsequent callers wait and reuse the new token (PC-AND-02). | `data/api/AuthInterceptor.kt` | TST-PR-0001-AND | Scaffolded |
| SUB-PR-0003-AND | SUB-PR-0003 | — | Patient CRUD screens with Compose UI. Must implement offline-sync conflict resolution: sync requests include `version`/`updated_at`, backend 409 conflicts are queued and presented in a resolution UI showing local vs server versions (RC-AND-02). | `ui/patients/` | TST-PR-0003-AND | Not Started |
| SUB-PR-0007-AND | SUB-PR-0007 | — | Patient search screen with filters | — | TST-PR-0007-AND | Not Started |
| SUB-PR-0008-AND | SUB-PR-0008 | — | Paginated patient list with lazy loading | — | TST-PR-0008-AND | Not Started |
| SUB-PR-0009-AND | SUB-PR-0009 | — | Camera capture for wound assessment with on-device inference. Camera access must go through CameraSessionManager singleton (SUB-PR-0012, PC-AND-01, RC-AND-01). | — | TST-PR-0009-AND | Not Started |
| SUB-PR-0010-AND | SUB-PR-0010 | — | Camera capture for patient ID verification. Camera access must go through CameraSessionManager singleton (SUB-PR-0012, PC-AND-01, RC-AND-01). | — | TST-PR-0010-AND | Not Started |
| SUB-PR-0011-AND | SUB-PR-0011 | — | Document scanner for OCR capture. Camera access must go through CameraSessionManager singleton (SUB-PR-0012, PC-AND-01, RC-AND-01). | — | TST-PR-0011-AND | Not Started |
| SUB-PR-0013-AND | SUB-PR-0013 | SYS-REQ-0012, SYS-REQ-0003 | Camera capture for dermoscopic images with on-device TFLite classification (MobileNetV3) for offline skin lesion triage. Camera access must go through CameraSessionManager singleton with a dermoscopy-specific `CameraProfile` (macro focus mode, high resolution, clinical white balance) applied during the BINDING phase (SUB-PR-0012, PC-AND-01, PC-AND-03, RC-AND-01). On-device classification results must be displayed with a "preliminary triage — pending server confirmation" label and stored with `confirmed = false` flag (PC-AI-01, RC-AND-03). When connectivity restores, results are synced to backend for server reclassification. If the server top-1 prediction or risk level differs from the on-device result, fire a push notification to the clinician: "Classification updated for [patient] — please review." The patient-facing encounter record must never show the on-device result as a final classification. | `ui/dermatology/LesionCaptureScreen.kt`, `data/ml/LesionClassifier.kt`, `data/sync/LesionSyncWorker.kt` | TST-PR-0013-AND | Not Started |

---

## Clinical Workflow (SUB-CW)

**Parent:** [SUB-CW (Domain)](../domain/SUB-CW.md)

| Platform Req ID | Parent | SYS-REQ | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|---|
| SUB-CW-0001-AND | SUB-CW-0001 | SYS-REQ-0001 | Auth interceptor for encounter API calls | `data/api/AuthInterceptor.kt` | TST-CW-0001-AND | Scaffolded |
| SUB-CW-0003-AND | SUB-CW-0003 | — | Encounter lifecycle screens with Compose UI. Must implement offline-sync conflict resolution: sync requests include `version`/`updated_at`, backend 409 conflicts are queued and presented in a resolution UI (RC-AND-02). | `ui/encounters/` | TST-CW-0003-AND | Not Started |
| SUB-CW-0006-AND | SUB-CW-0006 | — | Encounter type selection in Compose forms | `ui/encounters/EncountersScreen.kt` | TST-CW-0006-AND | Not Started |
| SUB-CW-0009-AND | SUB-CW-0009 | SYS-REQ-0013 | DermaCheck encounter workflow on Android: from encounter detail screen, physician taps "DermaCheck" to open camera capture (via CameraSessionManager with dermoscopy CameraProfile per SUB-PR-0012), uploads image to backend, receives and displays `DermaCheckResult` (classification, narrative, risk score, similar images), and taps "Save to Encounter" or "Discard". Must handle `degraded` responses by showing "unavailable" indicators for missing fields. Supports "Add Another Lesion" to capture multiple lesions within the same encounter. Results rendered atomically — waits for full response, no progressive rendering. | `ui/dermatology/DermaCheckScreen.kt`, `ui/dermatology/DermaCheckViewModel.kt`, `ui/encounters/EncounterDetailScreen.kt` | TST-CW-0009-AND | Not Started |

---

## Medication Management (SUB-MM)

**Parent:** [SUB-MM (Domain)](../domain/SUB-MM.md)

| Platform Req ID | Parent | SYS-REQ | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|---|
| SUB-MM-0001-AND | SUB-MM-0001 | SYS-REQ-0006 | Drug interaction warning display on medications screen | `ui/medications/MedicationsScreen.kt` | TST-MM-0001-AND | Not Started |
| SUB-MM-0006-AND | SUB-MM-0006 | SYS-REQ-0001 | Auth interceptor for medication API calls | `data/api/AuthInterceptor.kt` | TST-MM-0006-AND | Scaffolded |

---

## Reporting & Analytics (SUB-RA)

**Parent:** [SUB-RA (Domain)](../domain/SUB-RA.md)

| Platform Req ID | Parent | SYS-REQ | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|---|
| SUB-RA-0001-AND | SUB-RA-0001 | — | Patient volume report screen | `ui/reports/ReportsScreen.kt` | TST-RA-0001-AND | Not Started |
| SUB-RA-0002-AND | SUB-RA-0002 | — | Encounter summary report screen | `ui/reports/ReportsScreen.kt` | TST-RA-0002-AND | Not Started |
| SUB-RA-0003-AND | SUB-RA-0003 | SYS-REQ-0003 | Audit log query screen with filters | — | TST-RA-0003-AND | Not Started |
| SUB-RA-0004-AND | SUB-RA-0004 | SYS-REQ-0001 | Auth interceptor for report API calls | `data/api/AuthInterceptor.kt` | TST-RA-0004-AND | Scaffolded |
| SUB-RA-0006-AND | SUB-RA-0006 | — | Medication usage report screen | `ui/reports/ReportsScreen.kt` | TST-RA-0006-AND | Not Started |
