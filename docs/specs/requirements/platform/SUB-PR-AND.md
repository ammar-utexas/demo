# Platform Requirements: Patient Records — Android (SUB-PR-AND)

**Parent:** [SUB-PR (Domain)](../domain/SUB-PR.md)
**Platform:** Android (AND) — 8 requirements

---

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-PR-0001-AND | SUB-PR-0001 | Auth interceptor for patient API calls. Must implement token refresh synchronization via Kotlin `Mutex` — first caller refreshes, subsequent callers wait and reuse the new token (PC-AND-02). | `data/api/AuthInterceptor.kt` | TST-PR-0001-AND | Scaffolded |
| SUB-PR-0003-AND | SUB-PR-0003 | Patient CRUD screens with Compose UI. Must implement offline-sync conflict resolution: sync requests include `version`/`updated_at`, backend 409 conflicts are queued and presented in a resolution UI showing local vs server versions (RC-AND-02). | `ui/patients/` | TST-PR-0003-AND | Not Started |
| SUB-PR-0007-AND | SUB-PR-0007 | Patient search screen with filters | — | TST-PR-0007-AND | Not Started |
| SUB-PR-0008-AND | SUB-PR-0008 | Paginated patient list with lazy loading | — | TST-PR-0008-AND | Not Started |
| SUB-PR-0009-AND | SUB-PR-0009 | Camera capture for wound assessment with on-device inference. Camera access must go through CameraSessionManager singleton (SUB-PR-0012, PC-AND-01, RC-AND-01). | — | TST-PR-0009-AND | Not Started |
| SUB-PR-0010-AND | SUB-PR-0010 | Camera capture for patient ID verification. Camera access must go through CameraSessionManager singleton (SUB-PR-0012, PC-AND-01, RC-AND-01). | — | TST-PR-0010-AND | Not Started |
| SUB-PR-0011-AND | SUB-PR-0011 | Document scanner for OCR capture. Camera access must go through CameraSessionManager singleton (SUB-PR-0012, PC-AND-01, RC-AND-01). | — | TST-PR-0011-AND | Not Started |
| SUB-PR-0013-AND | SUB-PR-0013 | Camera capture for dermoscopic images with on-device TFLite classification (MobileNetV3) for offline skin lesion triage. Camera access must go through CameraSessionManager singleton (SUB-PR-0012, PC-AND-01, RC-AND-01). Results synced to backend when connectivity is available. | `ui/dermatology/LesionCaptureScreen.kt`, `data/ml/LesionClassifier.kt` | TST-PR-0013-AND | Not Started |
