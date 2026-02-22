# Risk Assessment: DermaCheck Workflow Orchestration

**Document ID:** PMS-RA-DERM-001
**Subsystem:** SUB-PR (Patient Records) + SUB-CW (Clinical Workflow)
**Feature:** SYS-REQ-0013 — DermaCheck Pipeline Orchestration
**Date:** 2026-02-21
**Author:** AI Agent (reviewed by Ammar Darkazanli)
**Standard:** ISO 14971:2019 — Application of risk management to medical devices
**Related QMS:** ISO 13485:2016 Clause 7.1 (Planning of product realization), Clause 7.3.3 (Design and development inputs)

---

## Scope

This risk assessment covers the DermaCheck capture-classify-review pipeline (SYS-REQ-0013), which decomposes into:

- **SUB-PR-0017** — Pipeline orchestration (parallel fan-out, graceful degradation, atomic DermaCheckResult)
  - SUB-PR-0017-BE (Backend thin proxy)
  - SUB-PR-0017-AI (CDS service parallel fan-out via `asyncio.gather`)
- **SUB-CW-0009** — Encounter workflow (capture → upload → review → save/discard)
  - SUB-CW-0009-BE (Encounter-lesion association API)
  - SUB-CW-0009-WEB (Web DermaCheck workflow UI)
  - SUB-CW-0009-AND (Android DermaCheck workflow UI)

**Architecture references:** ADR-0022 (orchestration), ADR-0018 (inter-service communication), ADR-0015 (risk scoring), ADR-0008 (CDS microservice), ADR-0014 (image preprocessing), ADR-0020 (feature flags)

**Governance cross-references:** DC-PR-06 (audit trail), DC-PR-07 (encounter-patient validation), PC-AI-01 (model parity), RC-BE-11 (concurrent upload), RC-BE-12 (circuit breaker orphans)

---

## Risk Acceptability Matrix

| Probability / Severity | 1 (Negligible) | 2 (Minor) | 3 (Moderate) | 4 (Major) | 5 (Catastrophic) |
|---|---|---|---|---|---|
| **5 (Frequent)** | 5 | 10 | 15 | 20 | 25 |
| **4 (Probable)** | 4 | 8 | 12 | 16 | 20 |
| **3 (Occasional)** | 3 | 6 | 9 | 12 | 15 |
| **2 (Remote)** | 2 | 4 | 6 | 8 | 10 |
| **1 (Improbable)** | 1 | 2 | 3 | 4 | 5 |

Risk levels: **1–4 = Acceptable** (green), **5–9 = ALARP** (yellow), **10–25 = Unacceptable** (red)

---

## Risk Register

### Clinical Safety

| Risk ID | Description | Related Req(s) | Severity | Probability | Risk Level | Mitigation | Residual Risk |
|---|---|---|---|---|---|---|---|
| RISK-DERM-001 | **Melanoma misclassification** — EfficientNet-B4 produces a false-negative classification for melanoma (e.g., classifies as benign nevus), leading the physician to reassure the patient instead of referring to dermatology. Delayed diagnosis of melanoma is a life-threatening outcome. | SUB-PR-0017-AI, SUB-PR-0013, SYS-REQ-0012 | 5 (Catastrophic) | 2 (Remote) | **10 (Unacceptable)** | (1) Risk scoring engine uses high-sensitivity thresholds that intentionally over-refer (ADR-0015: melanoma threshold ≥0.2 for medium risk). (2) Clinical disclaimer: "Clinical Decision Support Only — does not replace clinical judgment." (3) Similar ISIC images provide visual cross-check evidence. (4) Model validated against ISIC holdout set with >95% melanoma sensitivity target (SUB-PR-0013-AI). (5) Physician is the final decision-maker — system assists, does not diagnose. | S5 × P1 = **5 (ALARP)** |
| RISK-DERM-002 | **Risk scoring threshold misconfiguration** — Administrator adjusts configurable thresholds (ADR-0015) to values that under-refer high-risk lesions (e.g., raising melanoma threshold from 0.2 to 0.5), increasing missed referrals. | SUB-PR-0017-AI, SUB-PR-0015 | 4 (Major) | 2 (Remote) | **8 (ALARP)** | (1) Default thresholds intentionally over-refer (ADR-0015). (2) Threshold changes require administrator role (SUB-PR-0002). (3) All configuration changes audit-logged (SYS-REQ-0003). (4) Reporting dashboard (SUB-RA-0008) tracks referral rate trends — anomaly detection for sudden drops. | S4 × P1 = **4 (Acceptable)** |
| RISK-DERM-003 | **Hallucinated clinical narrative** — Gemma 3 generates a clinical narrative containing medically incorrect or fabricated guidance (e.g., suggesting a benign diagnosis for a high-confidence melanoma classification), misleading the physician. | SUB-PR-0017-AI | 4 (Major) | 3 (Occasional) | **12 (Unacceptable)** | (1) Narrative is labeled "AI-generated clinical summary — verify against classification data." (2) Classification and risk score are deterministic (ADR-0015) and serve as primary decision inputs; narrative is supplementary context only. (3) Narrative is a non-critical parallel stage — physicians can proceed without it (ADR-0022 graceful degradation). (4) Physician reviews all results before save/discard decision (SUB-CW-0009). (5) Narrative does not appear in the risk score calculation — clinical action is driven by classification + risk, not narrative. | S4 × P2 = **8 (ALARP)** |
| RISK-DERM-004 | **Degraded result interpreted as complete** — Physician acts on a degraded DermaCheckResult (missing risk score or similar images) without noticing the `degraded` flag, making a clinical decision without the full context. | SUB-PR-0017, SUB-CW-0009-WEB, SUB-CW-0009-AND | 4 (Major) | 2 (Remote) | **8 (ALARP)** | (1) `degraded` flag in DermaCheckResult (ADR-0022). (2) Web UI displays "Risk score unavailable" / "Similar images unavailable" banners for null fields (SUB-CW-0009-WEB). (3) Android UI displays degradation indicators (SUB-CW-0009-AND). (4) Classification (the primary decision input) is always present when response returns successfully — EfficientNet-B4 failure is a hard error (HTTP 500). | S4 × P1 = **4 (Acceptable)** |
| RISK-DERM-005 | **Non-dermoscopic image uploaded** — Physician uploads an irrelevant image (selfie, document photo, non-skin image), and the model returns a spurious classification that appears clinically meaningful. | SUB-CW-0009-WEB, SUB-CW-0009-AND, SUB-PR-0013 | 3 (Moderate) | 3 (Occasional) | **9 (ALARP)** | (1) Image quality validation pipeline (ADR-0014) with blur/exposure quality gates — rejects unsuitable images with 422. (2) CameraSessionManager applies dermoscopy-specific CameraProfile (SUB-PR-0012, PC-AND-03). (3) Clinical disclaimer on all results. (4) Physician review step before save (SUB-CW-0009). (5) Anatomical site selector provides context guidance. | S3 × P2 = **6 (ALARP)** |
| RISK-DERM-006 | **Low-quality dermoscopic image passes quality gates** — Android camera produces a marginally acceptable image (motion blur, poor focus) that passes ADR-0014 quality gates but produces an unreliable classification with misleading confidence. | SUB-CW-0009-AND, SUB-PR-0013-AND | 3 (Moderate) | 2 (Remote) | **6 (ALARP)** | (1) CameraSessionManager applies macro focus mode, high resolution, clinical white balance via CameraProfile (PC-AND-03). (2) Image quality gates reject images below threshold (ADR-0014). (3) Low confidence scores naturally signal unreliable classification. (4) Similar images gallery provides visual cross-reference. | S3 × P1 = **3 (Acceptable)** |

### Data Integrity

| Risk ID | Description | Related Req(s) | Severity | Probability | Risk Level | Mitigation | Residual Risk |
|---|---|---|---|---|---|---|---|
| RISK-DERM-007 | **Encounter-patient PHI cross-contamination** — Lesion assessment uploaded with an `encounter_id` belonging to Patient A but `patient_id` for Patient B, linking a dermoscopic image to the wrong patient's encounter. HIPAA violation. | SUB-CW-0009-BE, SUB-PR-0013-BE | 5 (Catastrophic) | 1 (Improbable) | **5 (ALARP)** | (1) SUB-PR-0013-BE validates encounter-patient consistency — returns 422 on mismatch (DC-PR-07, resolved). (2) SUB-CW-0008 enforces encounter-patient FK constraint at DB level. (3) Client UIs derive encounter_id from navigation context (URL/screen arg), not manual entry. | S5 × P1 = **5 (ALARP)** |
| RISK-DERM-008 | **Audit trail incomplete for pipeline stages** — DermaCheck pipeline executes classification, narrative, similarity, and risk scoring, but audit log captures only the overall request — not per-stage latency, degradation status, or model version. Violates HIPAA §164.312(b) audit controls. | SUB-PR-0017-BE, SYS-REQ-0003, SYS-REQ-0013 | 3 (Moderate) | 2 (Remote) | **6 (ALARP)** | (1) SUB-PR-0017-BE requires `DERMACHECK_PIPELINE` audit action with model_version, per-stage latency, and degraded status in metadata (DC-PR-06). (2) SUB-PR-0005-BE scope includes all lesion operations. (3) Audit event catalog extended with derm-specific actions (DC-PR-06, resolved). | S3 × P1 = **3 (Acceptable)** |
| RISK-DERM-009 | **Orphaned encrypted image blob** — CDS circuit breaker opens between "store encrypted image" and "forward to CDS" steps. Image is persisted but no classification generated. Client retry creates a duplicate blob. | SUB-PR-0017-BE | 2 (Minor) | 2 (Remote) | **4 (Acceptable)** | (1) Single DB transaction wrapping entire pipeline — rollback on CDS failure (RC-BE-12, resolved). (2) `X-Idempotency-Key` header for retry deduplication (RC-BE-12, resolved). | S2 × P1 = **2 (Acceptable)** |
| RISK-DERM-010 | **Model version mismatch in stored results** — DermaCheckResult records a model_version string that doesn't match the model actually used for classification, creating false audit traceability. | SUB-PR-0017-AI, SUB-PR-0013-AI | 3 (Moderate) | 1 (Improbable) | **3 (Acceptable)** | (1) `model-manifest.json` (ADR-0013) is the single source of truth. (2) Model version read at service startup and included in every response. (3) Audit trail records model version per pipeline execution. | S3 × P1 = **3 (Acceptable)** |
| RISK-DERM-011 | **PHI egress via Gemma 3 narrative stage** — Patient dermoscopic image or identifiable PHI is sent to the Gemma 3 AI Gateway, which could be an external service, violating HIPAA. | SUB-PR-0017-AI | 5 (Catastrophic) | 1 (Improbable) | **5 (ALARP)** | (1) Gemma 3 receives classification probabilities + clinical notes context only, NOT the raw image (ADR-0022 pipeline flow). (2) AI Gateway runs on-premises within Docker internal network (ADR-0008). (3) No external API calls involving patient images — ONNX Runtime inference is local to CDS. (4) Image encryption at rest (ADR-0010, ADR-0016). (5) Network policy restricts CDS egress to internal services only. | S5 × P1 = **5 (ALARP)** |
| RISK-DERM-012 | **Lesion saved to wrong encounter** — UI navigation error or race condition causes a DermaCheck result to be persisted against the wrong encounter, creating an incorrect clinical record. | SUB-CW-0009-WEB, SUB-CW-0009-AND, SUB-CW-0009-BE | 3 (Moderate) | 2 (Remote) | **6 (ALARP)** | (1) Encounter ID derived from navigation context (URL path `/encounters/[id]/dermatology` on web, screen argument on Android). (2) Backend validates encounter-patient consistency (DC-PR-07). (3) Encounter detail screen displays patient name for visual confirmation. | S3 × P1 = **3 (Acceptable)** |
| RISK-DERM-013 | **Discarded assessment leaves orphaned PHI** — Physician captures and classifies a lesion then discards the result, but the encrypted image and classification are already stored in PostgreSQL. | SUB-CW-0009-BE, SUB-CW-0009-AND, SUB-CW-0009-WEB | 2 (Minor) | 3 (Occasional) | **6 (ALARP)** | (1) "Discard" action soft-deletes the lesion record (marks inactive, not hard-deleted). (2) HIPAA requires 6-year PHI retention minimum — deletion is not required even for discarded records. (3) Audit trail records the discard action for compliance. (4) Images remain encrypted at rest (ADR-0010). | S2 × P2 = **4 (Acceptable)** |

### Availability

| Risk ID | Description | Related Req(s) | Severity | Probability | Risk Level | Mitigation | Residual Risk |
|---|---|---|---|---|---|---|---|
| RISK-DERM-014 | **CDS service unavailable** — The `pms-derm-cds` Docker container is down (crash, OOM, deployment), blocking all DermaCheck workflows across all clients. Single point of failure for the dermatology feature. | SUB-PR-0017-BE, SUB-PR-0017-AI | 3 (Moderate) | 2 (Remote) | **6 (ALARP)** | (1) Circuit breaker returns fast 503 instead of hanging (ADR-0018: 5 consecutive failures → open, 30s recovery). (2) Feature flag `DERM_CLASSIFICATION` (ADR-0020) disables DermaCheck gracefully when CDS is down — endpoints return 404 instead of 503. (3) Docker health checks + container restart policy. (4) Android on-device TFLite provides offline preliminary triage (SUB-PR-0013-AND). | S3 × P1 = **3 (Acceptable)** |
| RISK-DERM-015 | **Pipeline exceeds 5-second latency target** — Under concurrent load or on CPU-only hardware, the DermaCheck pipeline exceeds the SYS-REQ-0013 acceptance criterion of <5s end-to-end, degrading clinical workflow efficiency. | SUB-PR-0017-AI, SYS-REQ-0013 | 2 (Minor) | 3 (Occasional) | **6 (ALARP)** | (1) Parallel fan-out minimizes wall-clock time to max(narrative, similarity, risk) after classification (ADR-0022). (2) Per-stage timeouts: Gemma 3 = 5s, similarity = 2s, risk = 1s. (3) Overall 10s CDS timeout from backend (ADR-0018). (4) Graceful degradation returns partial results if slow stages timeout. (5) GPU inference recommended for production. | S2 × P2 = **4 (Acceptable)** |
| RISK-DERM-016 | **Backend timeout exceeds client timeout** — Backend-to-CDS 10s timeout + processing overhead exceeds the client HTTP timeout, causing client-side timeout before the server responds. Physician sees a generic network error. | SUB-PR-0017-BE, SUB-CW-0009-AND, SUB-CW-0009-WEB | 2 (Minor) | 2 (Remote) | **4 (Acceptable)** | (1) Client timeout configured ≥15s (backend 10s + overhead). (2) Android Retrofit and Web fetch timeout aligned. (3) `X-Idempotency-Key` allows safe retry (RC-BE-12). | S2 × P1 = **2 (Acceptable)** |

### Concurrency

| Risk ID | Description | Related Req(s) | Severity | Probability | Risk Level | Mitigation | Residual Risk |
|---|---|---|---|---|---|---|---|
| RISK-DERM-017 | **asyncio.gather exception kills pipeline** — An unhandled exception in one parallel stage (Gemma 3, similarity, or risk) propagates through `asyncio.gather()`, terminating the entire pipeline including the successfully completed classification. | SUB-PR-0017-AI | 3 (Moderate) | 3 (Occasional) | **9 (ALARP)** | (1) Use `asyncio.gather(return_exceptions=True)` to capture per-stage exceptions without propagation. (2) Graceful degradation table (ADR-0022): non-critical stage exception → null field + `degraded = true`. (3) Per-stage try/except with asyncio.timeout wrapping. (4) EfficientNet-B4 runs before fan-out — its result is already captured. | S3 × P1 = **3 (Acceptable)** |
| RISK-DERM-018 | **Concurrent uploads exhaust CDS resources** — Multiple physicians submit DermaCheck requests simultaneously during a busy clinic session, exhausting CDS service GPU/CPU, connection pool, or memory, causing cascading failures for all users. | SUB-PR-0017-AI, SUB-PR-0017-BE | 3 (Moderate) | 2 (Remote) | **6 (ALARP)** | (1) Backend connection pool sizing: default 10 concurrent connections to CDS (ADR-0018, tunable via env). (2) Circuit breaker prevents cascade failure — opens after 5 consecutive failures. (3) Per-stage timeouts cap resource holding time. (4) ONNX Runtime inference bounded by available GPU/CPU cores. | S3 × P1 = **3 (Acceptable)** |
| RISK-DERM-019 | **Concurrent lesion uploads produce ambiguous longitudinal baseline** — Two clinicians simultaneously upload dermoscopic images for the same patient at the same anatomical site. The second upload uses the first (captured seconds ago) as its "prior" for change detection, producing a meaningless near-zero change_score. | SUB-PR-0017-BE, SUB-PR-0016-BE | 3 (Moderate) | 2 (Remote) | **6 (ALARP)** | (1) `SELECT ... FOR UPDATE` serialization per (patient_id, anatomical_site) on lesion identity row (RC-BE-11, resolved). (2) Configurable 24h minimum interval between assessments at same site — 409 if violated unless clinician overrides (RC-BE-11). (3) Change_score computation serialized via FOR UPDATE (SUB-PR-0016-BE). | S3 × P1 = **3 (Acceptable)** |
| RISK-DERM-020 | **Token expiry during long pipeline execution** — The JWT token expires during the 10s+ DermaCheck pipeline execution. The backend accepts the request (token valid at start), but subsequent audit logging or result persistence uses an expired user context. | SUB-PR-0017-BE, SUB-PR-0001 | 2 (Minor) | 2 (Remote) | **4 (Acceptable)** | (1) JWT validation occurs at request start in middleware — the entire request executes within a single authenticated context. (2) Token refresh is a client concern (RC-WEB-01, PC-AND-02); the server validates once per request. (3) Default session timeout is 30 minutes (SYS-REQ-0001) — far exceeds pipeline duration. | S2 × P1 = **2 (Acceptable)** |

---

## Summary

| Metric | Count |
|---|---|
| **Total risks identified** | **20** |
| Acceptable (1–4) before mitigation | 4 |
| ALARP (5–9) before mitigation | 14 |
| Unacceptable (10–25) before mitigation | 2 |

### After Mitigation (Residual Risk)

| Residual Level | Count | Risk IDs |
|---|---|---|
| **Acceptable (1–4)** | **15** | RISK-DERM-002, 004, 006, 008, 009, 010, 012, 013, 014, 015, 016, 017, 018, 019, 020 |
| **ALARP (5–9)** | **5** | RISK-DERM-001 (5), 003 (8), 005 (6), 007 (5), 011 (5) |
| **Unacceptable (10–25)** | **0** | — |
| **Residual unacceptable risks** | **0** | Must be 0 before release |

### Residual ALARP Justification

The 5 residual ALARP risks are accepted under the following rationale:

| Risk ID | Residual | Acceptance Rationale |
|---|---|---|
| RISK-DERM-001 | 5 | Melanoma misclassification is inherent to any AI-assisted diagnostic tool. Mitigated by >95% melanoma sensitivity target, over-referral bias in risk scoring, and explicit "CDS only" labeling. The system augments — not replaces — physician judgment. Residual risk is comparable to clinical practice without AI assistance. |
| RISK-DERM-003 | 8 | LLM hallucination is a known property of generative models. Narrative is positioned as supplementary context only — not a clinical recommendation. Classification and risk score (both deterministic) drive clinical action. Narrative can be disabled via feature flag without impacting core functionality. |
| RISK-DERM-005 | 6 | Non-dermoscopic image upload is a user error scenario. Quality gates (ADR-0014) reject most unsuitable images. Clinical disclaimer and physician review step provide final safeguard. Classification confidence scores naturally reflect poor-quality inputs. |
| RISK-DERM-007 | 5 | PHI cross-contamination via encounter-patient mismatch is prevented by server-side validation (422 on mismatch, DC-PR-07) and DB FK constraints. Residual risk covers edge cases in the validation logic itself; accepted because validation is a mandatory server-side check that cannot be bypassed. |
| RISK-DERM-011 | 5 | PHI egress prevention relies on architectural controls (on-premises AI Gateway, Docker network isolation, CDS sends classification probabilities not images). Residual risk covers misconfiguration of network policy; accepted because deployment validation (ADR-0008) verifies network isolation. |

---

## Traceability to Governance Mitigations

The following resolved conflicts from [requirements-governance.md](../processes/requirements-governance.md) serve as existing mitigations referenced in this risk assessment:

| Governance ID | Description | Risks Mitigated |
|---|---|---|
| DC-PR-06 | Lesion audit trail traceability — derm-specific audit actions added | RISK-DERM-008 |
| DC-PR-07 | Encounter-patient cross-reference validation — 422 on mismatch | RISK-DERM-007, RISK-DERM-012 |
| PC-AI-01 | Model version parity — ≥90% agreement, preliminary triage labeling | RISK-DERM-001 |
| PC-AND-03 | Camera contention expansion — CameraProfile for dermoscopy | RISK-DERM-006 |
| RC-BE-11 | Concurrent lesion upload — FOR UPDATE serialization, 24h interval | RISK-DERM-019 |
| RC-BE-12 | CDS circuit breaker — single-transaction rollback, idempotency key | RISK-DERM-009, RISK-DERM-016 |
| RC-AND-03 | Offline classification discrepancy — preliminary triage labeling | RISK-DERM-001 |

---

## Regulatory Mapping

| Regulatory Requirement | Risk IDs | Compliance Status |
|---|---|---|
| HIPAA §164.312(b) — Audit Controls | RISK-DERM-008 | Mitigated via SUB-PR-0017-BE audit requirements |
| HIPAA §164.312(a)(2)(iv) — Encryption of ePHI | RISK-DERM-011, RISK-DERM-013 | Mitigated via ADR-0010 (AES-256-GCM), ADR-0016 (key management) |
| HIPAA §164.312(a)(1) — Access Controls | RISK-DERM-007, RISK-DERM-012 | Mitigated via encounter-patient validation (DC-PR-07) |
| HIPAA §164.306(a) — Contingency Planning | RISK-DERM-014, RISK-DERM-017 | Mitigated via circuit breaker (ADR-0018), graceful degradation (ADR-0022) |
| ISO 13485 §7.3.3 — Design Inputs (risk) | All | This document fulfills the risk assessment input requirement |
| ISO 13485 §7.3.4 — Design Outputs | All | Mitigations trace to specific requirements and ADRs |
| ISO 14971 §4.4 — Risk Analysis | All 20 risks | Severity and probability estimated per risk acceptability matrix |
| ISO 14971 §5 — Risk Evaluation | All 20 risks | Evaluated against acceptability criteria (Acceptable/ALARP/Unacceptable) |
| ISO 14971 §6 — Risk Control | 16 risks ≥ ALARP | Mitigations specified with residual risk re-evaluation |

---

## References

- [SYS-REQ-0013](../../specs/requirements/SYS-REQ.md) — DermaCheck Workflow Orchestration
- [SUB-PR-0017](../../specs/requirements/domain/SUB-PR.md) — Pipeline orchestration domain requirement
- [SUB-CW-0009](../../specs/requirements/domain/SUB-CW.md) — Encounter workflow domain requirement
- [ADR-0022](../../architecture/0022-dermacheck-workflow-orchestration.md) — Parallel fan-out pipeline
- [ADR-0018](../../architecture/0018-inter-service-communication.md) — Backend-to-CDS communication
- [ADR-0015](../../architecture/0015-risk-scoring-engine.md) — Risk scoring engine
- [ADR-0014](../../architecture/0014-image-preprocessing-pipeline.md) — Image preprocessing and quality gates
- [ADR-0020](../../architecture/0020-derm-cds-feature-flags.md) — Feature flag strategy
- [ADR-0008](../../architecture/0008-derm-cds-microservice-architecture.md) — CDS microservice architecture
- [Requirements Governance](../processes/requirements-governance.md) — Resolved conflicts and race conditions
