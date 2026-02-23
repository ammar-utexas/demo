# ADR-0022: DermaCheck Core Workflow Orchestration

**Date:** 2026-02-21
**Status:** Accepted
**Deciders:** Development Team

---

## Context

Journey 1 (DermaCheck — Skin Lesion Capture, Classification, and Review) is the primary end-to-end dermatology CDS workflow on Android. A physician captures a dermoscopic image, the system runs four AI processing stages (EfficientNet-B4 classification, Gemma 3 clinical narrative, pgvector similarity search, risk scoring), and returns results for the physician to save, discard, or continue capturing.

The four AI stages have different latency profiles and dependencies:

| Stage | Service | Latency | Depends On |
|---|---|---|---|
| EfficientNet-B4 classification | DermCDS (:8090) | ~500ms–2s | Image only |
| Gemma 3 clinical narrative | AI Gateway (:8001) | ~1–3s | Classification result + patient context |
| pgvector similarity search | PostgreSQL (pgvector) | ~100–200ms | Image embedding (from classification model) |
| Risk score calculation | DermCDS (:8090) | ~10ms | Classification probabilities + patient history |

The question is how to orchestrate these four stages within the `POST /api/lesions` request lifecycle to minimize total latency while respecting data dependencies, and how to handle the handoff between the PMS Backend (:8000) and the DermCDS Service (:8090).

## Options Considered

1. **Parallel fan-out with dependency graph** — The Backend sends the image to the CDS service once. The CDS service runs classification first (produces both probabilities and the 512-dim embedding), then fans out in parallel: Gemma 3 narrative (needs classification), similarity search (needs embedding), and risk scoring (needs classification + patient history). Results are assembled and returned in a single response.
   - Pros: Minimizes total latency (parallel stages run concurrently after classification), single round-trip from Backend to CDS, CDS owns the orchestration logic.
   - Cons: CDS must call the AI Gateway for Gemma 3 (cross-service call from CDS to Gateway), CDS must query PostgreSQL for patient history (shared DB access).

2. **Sequential pipeline** — Backend calls CDS for classification, waits, then calls AI Gateway for narrative, then calls CDS for similarity, then computes risk. Each stage returns before the next begins.
   - Pros: Simple linear flow, each call is independent, easy to debug.
   - Cons: Total latency is sum of all stages (~4–8s), exceeds the 5s target (Section 7.2). Physician waits longer than necessary.

3. **Backend-orchestrated parallel calls** — Backend sends the image to CDS, receives classification + embedding. Backend then makes three parallel calls: CDS for similarity search, AI Gateway for Gemma 3, and CDS for risk scoring. Backend assembles final response.
   - Pros: Backend controls all orchestration, CDS stays stateless and focused on inference, no cross-service calls from CDS.
   - Cons: Two round-trips to CDS (classify then similarity+risk), Backend must manage parallel HTTP calls and timeout handling, more network hops.

4. **Streaming/SSE response** — CDS streams partial results as each stage completes. Android app progressively renders: classification first, then similar images, then narrative, then risk score.
   - Pros: Perceived latency is low (first results appear in ~1s), physician can start reviewing while remaining stages complete.
   - Cons: Complex client-side state management, Android must handle partial UI updates, error handling for mid-stream failures is difficult, harder to test.

## Decision

Use **parallel fan-out with dependency graph inside the CDS service** (Option 1). The PMS Backend makes a single HTTP call to the CDS service's `/classify` endpoint. The CDS service internally orchestrates the four stages: classification runs first, then similarity search, Gemma 3 narrative, and risk scoring run in parallel. The CDS service returns the assembled result in one response.

## Rationale

1. **Meets latency target** — Classification takes ~1–2s. The three parallel stages (similarity ~200ms, Gemma 3 ~1–3s, risk ~10ms) run concurrently after classification completes. Total wall-clock time: ~2–5s, within the 5s target (Section 7.2).
2. **Single round-trip** — The Backend makes one HTTP call to the CDS service. No multi-call orchestration in the Backend, no partial failure assembly. The CDS service returns a complete `DermaCheckResult` payload or an error.
3. **CDS owns AI logic** — The CDS service (ADR-0008) is the domain owner for all AI processing. Keeping orchestration inside the CDS means the Backend doesn't need to understand classification dependencies or embedding extraction — it just sends an image and gets results.
4. **Embedding reuse** — The 512-dim embedding is a byproduct of the EfficientNet-B4 forward pass (extracted from the penultimate layer). Running classification and embedding extraction in the same process avoids recomputing or serializing the embedding across network boundaries.
5. **Simpler error handling** — If any parallel stage fails, the CDS service can return partial results with a degradation flag (e.g., narrative unavailable if Gemma 3 times out) rather than forcing the Backend to handle partial HTTP responses from multiple services.

## Pipeline Execution Flow

```
Backend                          CDS Service (:8090)                AI Gateway (:8001)     PostgreSQL
  |                                    |                                  |                     |
  |  POST /classify                    |                                  |                     |
  |  {image, patient_id, notes}        |                                  |                     |
  |----------------------------------->|                                  |                     |
  |                                    |                                  |                     |
  |                          1. EfficientNet-B4 classify                  |                     |
  |                             → probabilities[9]                        |                     |
  |                             → embedding[512]                          |                     |
  |                                    |                                  |                     |
  |                          2. Fan-out (parallel):                       |                     |
  |                                    |                                  |                     |
  |                                    |------ Gemma 3 narrative -------->|                     |
  |                                    |       {classification, context}  |                     |
  |                                    |                                  |                     |
  |                                    |------ pgvector similarity -------|-------------------->|
  |                                    |       {embedding, top_k=10}      |                     |
  |                                    |                                  |                     |
  |                                    |------ Risk score calc -----------|                     |
  |                                    |       {probabilities, history}   |                     |
  |                                    |                                  |                     |
  |                                    |<-------- narrative -------------|                     |
  |                                    |<-------- Top-K matches ---------|---------------------|
  |                                    |<-------- risk level ------------|                     |
  |                                    |                                  |                     |
  |                          3. Assemble DermaCheckResult                 |                     |
  |                                    |                                  |                     |
  |  {classification, narrative,       |                                  |                     |
  |   risk_score, similar_images}      |                                  |                     |
  |<-----------------------------------|                                  |                     |
```

## Request / Response Contract

**Request:** `POST /classify`

```json
{
  "image": "<base64 JPEG/PNG>",
  "patient_id": "uuid",
  "encounter_id": "uuid",
  "anatomical_site": "left_forearm",
  "clinical_notes": "Patient noticed growth over 3 months..."
}
```

**Response:** `DermaCheckResult`

```json
{
  "classification": {
    "top_3": [
      {"category": "melanoma", "confidence": 0.72},
      {"category": "melanocytic_nevi", "confidence": 0.18},
      {"category": "basal_cell_carcinoma", "confidence": 0.05}
    ],
    "all_probabilities": {"melanoma": 0.72, "...": "..."}
  },
  "narrative": "Given the patient's age and the lesion's dermoscopic features...",
  "risk_score": {
    "level": "high",
    "referral_urgency": "urgent",
    "contributing_factors": ["melanoma_confidence_above_70", "lesion_growth_reported"]
  },
  "similar_images": [
    {
      "isic_id": "ISIC_0024306",
      "diagnosis": "melanoma",
      "similarity_score": 0.94,
      "metadata": {"age": 55, "sex": "male", "anatomical_site": "back"}
    }
  ],
  "embedding_id": "uuid",
  "model_version": "efficientnet-b4-isic2024-v1.2",
  "degraded": false
}
```

The `degraded` flag is `true` if a parallel stage (e.g., Gemma 3) timed out — the response is still valid but missing that field's content.

## Graceful Degradation

| Stage Failure | Behavior |
|---|---|
| Gemma 3 timeout (> 5s) | Return result with `narrative: null`, `degraded: true`. Classification and risk score are still valid. |
| pgvector query failure | Return result with `similar_images: []`, `degraded: true`. |
| Risk scoring failure | Return result with `risk_score: null`, `degraded: true`. Classification is still valid. |
| EfficientNet-B4 failure | Return HTTP 500 — classification is the critical path, no result without it. |

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| Sequential pipeline | Total latency ~4–8s exceeds 5s target; unnecessary serialization of independent stages |
| Backend-orchestrated parallel | Two round-trips to CDS, Backend takes on AI orchestration responsibility, more network hops |
| Streaming/SSE | Complex client-side partial rendering, harder error handling, Android UI complexity |
| Message queue (Redis/RabbitMQ) | Overkill for synchronous clinical workflow; physician expects results before proceeding |

## Trade-offs

- **CDS cross-service call to AI Gateway** — The CDS service calls the AI Gateway (:8001) for Gemma 3 narrative. This means the CDS has an outbound HTTP dependency beyond the Backend. Mitigated by: timeout + graceful degradation (narrative is non-critical), circuit breaker pattern (ADR-0018).
- **CDS direct PostgreSQL access** — The CDS reads patient history from PostgreSQL for risk scoring and writes embeddings. This creates a shared-database coupling with the Backend. Mitigated by: CDS only accesses its own tables (`lesion_embeddings`, `isic_reference_embeddings`) plus read-only access to `patients` for age/history (ADR-0021).
- **Single point of failure** — If the CDS service is down, the entire DermaCheck workflow fails. Mitigated by: health checks, container restart policy, feature flag (ADR-0020) that disables DermaCheck gracefully when CDS is unavailable.

## Consequences

- The PMS Backend's `POST /api/lesions` endpoint is a thin proxy: validate input, forward to CDS, persist the `DermaCheckResult` to PostgreSQL, return to the Android client.
- The CDS service's `/classify` endpoint owns all AI orchestration: classification → parallel fan-out → result assembly.
- `asyncio.gather()` is used inside the CDS service to run Gemma 3, similarity search, and risk scoring concurrently after classification completes.
- Timeout per parallel stage: Gemma 3 = 5s, similarity = 2s, risk = 1s. Overall CDS timeout from Backend = 10s (ADR-0018).
- The Android client renders results atomically — it waits for the full `DermaCheckResult` rather than progressive updates.
- The `DermaCheckResult` schema is versioned and included in the CDS service's OpenAPI spec.
- The `degraded` flag enables the Android UI to show "Narrative unavailable" or "Similar images unavailable" without blocking the physician from reviewing classification and risk.

## References

- Related PRD: docs/experiments/18-PRD-ISICArchive-PMS-Integration.md (Section 4.1: Journey 1)
- Related Feature Doc: docs/features/18-PRD-ISICArchive-PMS-Integration.docx (Journey 1: DermaCheck)
- Related Requirements: SYS-REQ-0012, SUB-PR-0013-AND
- Related ADRs: ADR-0008 (CDS Microservice), ADR-0009 (AI Inference Runtime), ADR-0011 (Vector Database — pgvector), ADR-0018 (Inter-Service Communication), ADR-0020 (Feature Flags)
