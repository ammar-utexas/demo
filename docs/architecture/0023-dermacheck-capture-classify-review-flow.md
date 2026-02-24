# ADR-0023: DermaCheck Capture-Classify-Review Flow (Journey 1)

**Date:** 2026-02-24
**Status:** Accepted
**Deciders:** Development Team

---

## Context

Journey 1 (DermaCheck — Skin Lesion Capture, Classification, and Review) is the primary clinical workflow for AI-assisted dermatology triage in the PMS. The server-side orchestration is defined in ADR-0022 (parallel fan-out pipeline inside the CDS service). However, the client-side architecture — how the Android app and Next.js frontend implement the end-to-end capture-classify-review flow — has not been formalized.

Journey 1 spans seven steps from the physician's perspective (PRD Section 4.1):

1. **Patient Selection** — Select patient from the patient list
2. **DermaCheck Entry** — Tap a branded "DermaCheck" button to enter the CDS workflow
3. **Camera Capture** — Photograph the skin lesion via `CameraSessionManager`
4. **Notes / Dictation** — Add clinical notes (anatomical site, concerns, observations)
5. **Upload & AI Processing** — Upload image + notes to `POST /api/lesions`, which triggers the full CDS pipeline (EfficientNet-B4 classification, Gemma 3 narrative, pgvector similarity search, risk scoring)
6. **Results Display** — View top-3 classification, clinical narrative, risk level, and similar ISIC reference images
7. **Clinician Action** — Save to encounter, discard, or capture another lesion

Key decisions needed:

- How should the DermaCheck workflow be entered — as a dedicated branded flow or as a generic image assessment tool?
- How should the Android camera be integrated — reusable singleton or per-use instantiation?
- How should the Lesion API be designed — multipart upload or base64 encoding?
- Should the client wait synchronously for full results or poll asynchronously?
- How should clinician actions (Save/Discard/Add Another) be modeled — as a state machine or ad-hoc navigation?

## Options Considered

### Entry Point Design

1. **Branded "DermaCheck" entry point** — A dedicated, visually distinct button on the patient record screen that launches a purpose-built dermatology CDS workflow with its own navigation stack.
   - Pros: Clear clinical intent, discoverable branding, dedicated UX optimized for the dermoscopy workflow, feature-flag controllable (ADR-0020).
   - Cons: Additional navigation surface, tightly coupled to the dermatology CDS module.

2. **Generic "Add Image" with classification toggle** — Extend the existing patient image upload with a "Classify with AI" checkbox.
   - Pros: Reuses existing upload UI, simpler navigation.
   - Cons: Less discoverable, generic UX not optimized for dermoscopy workflow, harder to feature-flag independently, mixes clinical CDS with passive image storage.

3. **Encounter-level "Clinical Tools" menu** — Add DermaCheck as one option in a dropdown menu of clinical decision support tools.
   - Pros: Scalable to future CDS tools, consistent entry pattern.
   - Cons: Extra navigation step (tap menu → select tool), less prominent for the primary CDS feature, dropdown menus are poor for touch interfaces.

### Camera Integration (Android)

1. **CameraSessionManager singleton with CameraProfile** — A reusable singleton (`CameraSessionManager`) configured with a dermoscopy-specific `CameraProfile` that sets resolution, focus mode, exposure, and overlay guidance.
   - Pros: Consistent camera behavior across the app, dermoscopy-optimized settings, reusable for other imaging features (e.g., wound assessment), memory-efficient (single camera instance).
   - Cons: Singleton lifecycle management complexity, must handle configuration switching between profiles.

2. **Per-use CameraX instance** — Create a new CameraX session each time the camera is needed, passing configuration inline.
   - Pros: Simple lifecycle, no shared state.
   - Cons: Camera startup latency on each use (~500ms), duplicated configuration, inconsistent settings if hardcoded in multiple places.

3. **System camera intent** — Launch the system camera via `ACTION_IMAGE_CAPTURE` intent.
   - Pros: Zero camera code, works on all devices.
   - Cons: No control over resolution/focus/exposure, no dermoscopy overlay guidance, inconsistent behavior across OEMs, cannot enforce quality requirements (ADR-0014).

### Lesion API Upload Pattern

1. **Multipart form-data upload** — `POST /api/lesions` accepts `multipart/form-data` with the image as a file part and metadata (patient_id, encounter_id, anatomical_site, clinical_notes) as form fields.
   - Pros: Standard HTTP file upload, streaming upload (no full base64 in memory), compatible with browser `<input type="file">` and Android `MultipartBody`.
   - Cons: Slightly more complex request construction than JSON.

2. **Base64-encoded JSON body** — `POST /api/lesions` accepts a JSON body with the image as a base64-encoded string field.
   - Pros: Pure JSON request, simpler API contract.
   - Cons: 33% size overhead from base64 encoding (3 MB image → 4 MB payload), entire payload must be buffered in memory before sending, not streamable.

3. **Two-step upload (presigned URL)** — First request creates a lesion record and returns a presigned upload URL; second request uploads the image directly to storage.
   - Pros: Decouples metadata from binary upload, supports large files, resumable uploads.
   - Cons: Two round-trips, more complex client logic, presigned URLs add infrastructure for on-premises deployment (no S3).

### Client Processing Model

1. **Synchronous blocking wait** — The client sends the upload request and waits for the full `DermaCheckResult` response (classification + narrative + risk + similar images) in a single HTTP round-trip. A loading indicator shows progress.
   - Pros: Simple client logic, single request/response, atomic result display, no polling infrastructure.
   - Cons: Long request duration (~2–5s), must handle HTTP timeout carefully, client blocked during processing.

2. **Async upload with polling** — The client uploads the image, receives a job ID immediately, then polls `GET /api/lesions/{id}/status` until processing completes.
   - Pros: Non-blocking upload, client can show progress stages, graceful timeout handling.
   - Cons: Polling infrastructure, multiple HTTP requests, more complex client state management, added latency from polling interval.

3. **WebSocket streaming** — The client opens a WebSocket connection, sends the image, and receives partial results as each AI stage completes.
   - Pros: Real-time progressive rendering, lowest perceived latency.
   - Cons: WebSocket infrastructure, complex client-side partial UI updates, error handling for mid-stream failures, harder to test (ADR-0022 rejected this for the same reasons).

### Clinician Action Model

1. **Explicit state machine** — The post-results screen presents three mutually exclusive actions as a state machine: **Save** (persist to encounter → return to patient record), **Discard** (delete image and results → return to patient record), **Add Another** (return to camera capture within the same encounter). State transitions are explicit and logged.
   - Pros: Clear workflow boundaries, auditable state transitions, prevents accidental data loss (discard requires confirmation), encounter-scoped session for multi-capture.
   - Cons: Rigid flow, clinician must explicitly choose an action before proceeding.

2. **Auto-save with undo** — Results are automatically saved to the encounter immediately. The clinician can undo (delete) within a configurable window (e.g., 30s).
   - Pros: Faster workflow, no explicit save step.
   - Cons: Images stored before clinician review, undo window creates ambiguity, harder to audit, auto-persisting PHI before review raises HIPAA concerns.

3. **Draft/pending state** — Results are saved as "draft" by default. The clinician explicitly "finalizes" or "deletes" drafts later.
   - Pros: No data loss, clinician can review later.
   - Cons: Accumulates draft records, clinician burden to clean up, stale drafts consume encrypted storage, unclear when drafts become part of the medical record.

## Decision

1. **Branded "DermaCheck" entry point** (Option 1) — A dedicated button on the patient record launches the DermaCheck flow.
2. **CameraSessionManager singleton with CameraProfile** (Option 1) — Reusable singleton with a dermoscopy-specific profile.
3. **Multipart form-data upload** (Option 1) — Standard multipart upload for `POST /api/lesions`.
4. **Synchronous blocking wait** (Option 1) — Client waits for the full `DermaCheckResult` in a single round-trip.
5. **Explicit state machine** (Option 1) — Save/Discard/Add Another as explicit clinician-driven actions.

## Rationale

### Branded Entry Point
- **Discoverability** — Primary care clinicians encountering a suspicious lesion need to find the CDS tool immediately. A branded button ("DermaCheck") on the patient record is faster than navigating menus or toggling checkboxes.
- **Feature-flag aligned** — DermaCheck is controlled by the `DERM_CDS_ENABLED` feature flag (ADR-0020). A dedicated entry point can be shown/hidden cleanly, unlike a checkbox buried in an existing upload flow.
- **Regulatory clarity** — As a clinical decision support tool, DermaCheck has distinct intended use and regulatory implications. A branded entry point makes it clear when the clinician is invoking AI-assisted classification vs. uploading a passive photo.

### CameraSessionManager Singleton
- **Dermoscopy optimization** — The `CameraProfile` configures auto-focus mode (macro), resolution (minimum 380x380 for EfficientNet-B4 input per ADR-0014), and an overlay guide ring to help the clinician center the dermoscope. These settings would be duplicated across call sites without a shared profile.
- **Reusability** — The same `CameraSessionManager` can be configured with different `CameraProfile` instances for wound assessment (Vision Capabilities), document scanning, or patient ID capture — only the profile changes.
- **Memory efficiency** — The Android Camera2/CameraX API is resource-intensive. A singleton ensures at most one camera session is active, preventing memory leaks from orphaned sessions.

### Multipart Upload
- **No base64 overhead** — A typical dermoscopic image is 2–4 MB. Base64 adds 33% overhead (2.7–5.3 MB) and requires the entire payload in memory. Multipart streams the file, reducing peak memory on both client and server.
- **Browser compatibility** — The Next.js frontend (Journey 7) uses a standard `<input type="file">` with `FormData`, which maps directly to multipart. Base64 would require client-side encoding before submission.
- **FastAPI native support** — FastAPI's `UploadFile` parameter handles multipart natively with streaming, temp file management, and automatic cleanup.

### Synchronous Blocking Wait
- **Clinical workflow fit** — The physician captures an image and needs results before deciding to save, discard, or capture another lesion. Polling or background processing would require the physician to navigate away and return later, breaking the clinical flow.
- **Latency budget** — The full pipeline completes in 2–5s (ADR-0022). This is within acceptable waiting time for a synchronous HTTP request with a loading indicator. Polling would add polling-interval latency on top.
- **Simplicity** — One request, one response. No job queue, no polling endpoint, no WebSocket server. The Backend is a thin proxy to the CDS service (ADR-0022), and the CDS returns a complete `DermaCheckResult` payload.
- **Timeout handling** — The Backend sets a 10s timeout on the CDS call (ADR-0018). If the CDS returns a degraded result (e.g., Gemma 3 timed out), the client still receives a valid response with the `degraded` flag set to `true`.

### Explicit State Machine
- **Patient safety** — Auto-saving unreviewed AI classifications to the medical record is risky. The physician must explicitly choose to persist results after reviewing them.
- **Audit trail** — Each state transition (capture → processing → results → save/discard) is logged with a timestamp and user identity. This supports the audit logging requirement (PRD Section 7.1).
- **Multi-capture support** — "Add Another" returns to the camera within the same encounter session, allowing the physician to capture multiple lesions (up to the session limit) without re-entering the DermaCheck flow. The state machine tracks which lesions have been saved vs. pending.
- **Discard safety** — Discard requires a confirmation dialog to prevent accidental deletion of results. Discarded images are securely deleted from encrypted storage (ADR-0010).

## Client State Machine

```
                        ┌──────────────────────┐
                        │   Patient Record     │
                        │   (DermaCheck btn)   │
                        └──────────┬───────────┘
                                   │ tap "DermaCheck"
                                   ▼
                        ┌──────────────────────┐
                   ┌───>│   Camera Capture     │
                   │    │   (CameraSession     │
                   │    │    Manager)           │
                   │    └──────────┬───────────┘
                   │               │ image captured
                   │               ▼
                   │    ┌──────────────────────┐
                   │    │   Notes / Dictation  │
                   │    │   (optional)         │
                   │    └──────────┬───────────┘
                   │               │ submit
                   │               ▼
                   │    ┌──────────────────────┐
                   │    │   Processing         │
                   │    │   (loading spinner)  │
                   │    │   POST /api/lesions  │
                   │    └──────────┬───────────┘
                   │               │ results received
                   │               ▼
                   │    ┌──────────────────────┐
                   │    │   Results Display    │
                   │    │   - top-3 classif.   │
                   │    │   - narrative        │
                   │    │   - risk level       │
                   │    │   - similar images   │
                   │    └──┬─────┬─────┬───────┘
                   │       │     │     │
                   │  Save │     │     │ Add Another
                   │       │     │     └───────────┐
                   │       │     │ Discard          │
                   │       │     ▼                  │
                   │       │  ┌───────────┐         │
                   │       │  │ Confirm?  │         │
                   │       │  └──┬────┬───┘         │
                   │       │  Yes│    │No            │
                   │       │     │    └──> (back     │
                   │       │     │      to results)  │
                   │       ▼     ▼                   │
                   │    ┌──────────────┐             │
                   │    │ Patient      │             │
                   │    │ Record       │             │
                   │    │ (updated)    │             │
                   │    └──────────────┘             │
                   │                                 │
                   └─────────────────────────────────┘
```

## Lesion API Contract

**Endpoint:** `POST /api/lesions`
**Content-Type:** `multipart/form-data`

| Field | Type | Required | Description |
|---|---|---|---|
| `image` | file (JPEG/PNG) | Yes | Dermoscopic image, min 224x224px |
| `patient_id` | UUID | Yes | Patient record ID |
| `encounter_id` | UUID | Yes | Current encounter ID |
| `anatomical_site` | string | No | Body location (e.g., "left_forearm") |
| `clinical_notes` | string | No | Free-text clinical observations |
| `prior_lesion_id` | UUID | No | Reference to prior lesion for longitudinal comparison (Journey 2) |

**Response:** `DermaCheckResult` (see ADR-0022 for full schema)

**Clinician Actions:**

| Action | Method | Endpoint | Effect |
|---|---|---|---|
| Save | `POST` | `/api/lesions/{id}/save` | Persist classification + image to encounter record |
| Discard | `DELETE` | `/api/lesions/{id}` | Securely delete image (AES key destruction) and classification |
| Add Another | Client-side | N/A | Navigate back to camera capture, same encounter session |

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| Generic image upload + classify toggle | Less discoverable, mixed intent with passive image storage, harder to feature-flag |
| System camera intent | No control over dermoscopy-optimized settings, inconsistent across OEMs, cannot enforce quality gates |
| Base64-encoded JSON | 33% payload overhead, full buffering in memory, no streaming |
| Async polling | Breaks clinical flow (physician must wait anyway), added complexity for marginal benefit given 2–5s latency |
| WebSocket streaming | Complex partial rendering, harder error handling, Android UI complexity (rejected in ADR-0022) |
| Auto-save with undo | PHI persisted before review, undo window ambiguity, HIPAA concerns |
| Draft/pending state | Stale draft accumulation, unclear record status, clinician burden to finalize |

## Trade-offs

- **Synchronous wait blocks the UI for 2–5s** — The physician cannot navigate during processing. Mitigated by a clear loading indicator with estimated time, and the `degraded` flag in the response allows partial results if a non-critical stage (e.g., Gemma 3 narrative) times out.
- **Singleton CameraSessionManager adds lifecycle complexity** — The singleton must handle Activity/Fragment lifecycle events (pause/resume/destroy) without leaking resources. Mitigated by tying the session to a Lifecycle-aware component and releasing camera resources in `onPause()`.
- **Explicit state machine limits workflow flexibility** — The physician cannot skip directly from results to patient record without choosing Save or Discard. This is intentional — it prevents orphaned AI results in an ambiguous state and ensures every classification is either persisted or explicitly discarded.
- **Multipart upload is slightly more complex than JSON** — Both Android (`MultipartBody.Builder`) and Next.js (`FormData`) have native multipart support, so the implementation complexity is minimal. The server's FastAPI `UploadFile` handles cleanup automatically.

## Consequences

- The Android app implements a `DermaCheckActivity` (or Compose navigation graph) with screens for capture, notes, processing, and results — following the state machine above.
- The `CameraSessionManager` singleton is initialized once per app lifecycle and configured with a `DermoscopyCameraProfile` that sets macro auto-focus, minimum 380x380 resolution, and an overlay guide ring.
- The `POST /api/lesions` endpoint in the PMS Backend accepts `multipart/form-data`, encrypts the image (ADR-0010), forwards to the CDS service (ADR-0022), and returns the assembled `DermaCheckResult`.
- The Backend acts as a thin proxy: validate input → encrypt image → forward to CDS → persist result → return to client.
- The client renders results atomically (waits for the full `DermaCheckResult` rather than progressive updates), consistent with ADR-0022.
- Discard triggers secure deletion: the encrypted image is deleted from `lesion_images`, the encryption key reference is destroyed (ADR-0016), and the classification record is removed.
- "Add Another" preserves the encounter context (encounter_id, patient_id) and returns to the camera capture screen, allowing batch capture within a single clinical visit.
- The Next.js frontend (Journey 7) follows the same API contract and clinician action model, using a file upload widget instead of `CameraSessionManager`.
- All state transitions are audit-logged with user identity, timestamp, and action type (PRD Section 7.1).

## References

- Related PRD: docs/experiments/18-PRD-ISICArchive-PMS-Integration.md (Section 4.1: Journey 1)
- Related Feature Doc: docs/features/18-PRD-ISICArchive-PMS-Integration.docx (Journey 1: DermaCheck)
- Related Requirements: SYS-REQ-0012, SUB-PR-0013-AND, SUB-PR-0013-BE, SUB-PR-0013-WEB
- Related ADRs: ADR-0008 (CDS Microservice), ADR-0010 (Image Storage), ADR-0014 (Image Preprocessing), ADR-0015 (Risk Scoring), ADR-0016 (Encryption Key Management), ADR-0018 (Inter-Service Communication), ADR-0020 (Feature Flags), ADR-0022 (Workflow Orchestration)
