# ADR-0018: Backend-to-CDS Communication

**Date:** 2026-02-21
**Status:** Accepted
**Deciders:** Development Team

---

## Context

The PMS backend (FastAPI :8000) and the Dermatology CDS service (FastAPI :8090) are separate Docker containers (ADR-0008) that communicate over the internal Docker network. The backend forwards patient dermoscopic images to the CDS for classification and similarity search, then returns results to the client.

This inter-service communication must be reliable (CDS downtime shouldn't crash the backend), performant (minimize overhead in the <5s pipeline budget), and observable (failures must be logged and reported).

## Options Considered

1. **HTTP client pooling with circuit breaking, timeout, and error propagation** — Use `httpx.AsyncClient` with connection pooling, configurable timeouts, circuit breaker pattern, and structured error propagation.
   - Pros: Simple HTTP/1.1, Swagger-documented APIs, connection reuse, graceful degradation, familiar debugging tools.
   - Cons: Higher per-request overhead than gRPC (~1ms), no streaming for large responses.

2. **gRPC with protobuf** — Binary protocol with schema-defined contracts.
   - Pros: Lower latency (~0.5ms vs ~1ms), binary serialization, streaming support, code generation.
   - Cons: Protobuf schema management overhead, harder to debug (not human-readable), multipart file upload is awkward in gRPC.

3. **Message queue (RabbitMQ/Redis Streams)** — Asynchronous message-based communication.
   - Pros: Decoupled, retry built-in, back-pressure handling.
   - Cons: Async response model requires polling or callbacks, adds infrastructure, classification is a synchronous request-response pattern (clinician waits for result).

4. **Direct database sharing** — Backend writes images to PostgreSQL, CDS polls for new images.
   - Pros: No inter-service network call.
   - Cons: Polling latency, tight coupling through shared tables, no request-response pattern, classification results delayed.

## Decision

Use **HTTP communication with `httpx.AsyncClient` connection pooling**, circuit breaking, configurable timeouts, and structured error propagation between the PMS backend and the Dermatology CDS service.

## Rationale

1. **Request-response fit** — Lesion classification is inherently synchronous: the clinician uploads an image and waits for results. HTTP request-response is the natural pattern.
2. **Connection pooling** — `httpx.AsyncClient` with keep-alive connections reuses TCP connections across requests, reducing connection setup overhead for burst classification workloads (clinic sessions).
3. **Circuit breaking** — If the CDS service is down or slow, the circuit breaker opens after N consecutive failures, returning a fast error to the clinician rather than blocking. This prevents backend thread exhaustion during CDS outages.
4. **Timeout configuration** — Per-endpoint timeouts account for different latencies: `/classify` (10s), `/similar` (5s), `/health` (2s). The 10s classify timeout accommodates CPU-only inference while staying within the 5s user-facing budget on GPU.
5. **Swagger compatibility** — Both services expose Swagger/OpenAPI docs, enabling interactive testing and auto-generated client code.
6. **Structured errors** — CDS errors propagate with context to the frontend: `{"detail": "CDS service unavailable", "cds_status": "circuit_open", "fallback": "retry_in_30s"}`.

## Communication Pattern

```
┌──────────────┐         ┌──────────────────┐
│ PMS Backend  │  HTTP   │ Dermatology CDS  │
│   :8000      │────────→│    :8090         │
│              │         │                  │
│ httpx pool   │         │ /classify        │
│ circuit brk  │         │ /similar         │
│ timeout cfg  │         │ /health          │
│ retry logic  │         │                  │
└──────────────┘         └──────────────────┘

Timeout Configuration:
  /health  → 2s  (quick probe)
  /classify → 10s (model inference)
  /similar  → 5s  (pgvector search)

Circuit Breaker:
  failure_threshold: 5 consecutive failures
  recovery_timeout: 30 seconds
  half_open_requests: 1
```

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| gRPC | Multipart file upload awkward, harder debugging, schema overhead, marginal latency gain (~0.5ms) |
| Message queue (RabbitMQ) | Wrong pattern for synchronous classification, additional infrastructure, polling latency |
| Direct database sharing | No request-response pattern, polling latency, tight schema coupling |
| Unix domain socket | Doesn't work across Docker containers without shared volumes |

## Trade-offs

- **Network hop latency** — HTTP adds ~1-5ms per request. Negligible against the 2-10s inference time.
- **Connection pool sizing** — Too small: requests queue. Too large: wasted resources. Default: 10 connections, tunable via environment variable.
- **Circuit breaker sensitivity** — 5 failures may be too sensitive (temporary network blip) or too lenient (5 clinicians get errors). Tunable per deployment.
- **No streaming** — Large similarity search results (10 images with metadata) are returned as a single JSON response. Acceptable for current payload sizes (<100 KB).

## Consequences

- A `cds_client.py` module in the backend wraps all CDS communication with connection pooling, timeout, circuit breaking, and structured error handling.
- The `httpx.AsyncClient` is created at application startup (lifespan) and shared across requests.
- Circuit breaker state is tracked in-memory (acceptable for single-instance backend).
- CDS health is probed every 30s by the backend; circuit breaker state reflects the probe result.
- All CDS communication is logged at INFO level with request duration; errors are logged at ERROR with full context.
- Feature flags (ADR-0020) control whether the backend calls the CDS or returns stubs.
- If the CDS is unavailable and the circuit is open, the lesion upload endpoint returns HTTP 503 with a user-friendly message.

## References

- Related PRD: docs/experiments/18-PRD-ISICArchive-PMS-Integration.md (Section 3.1)
- Related Requirements: SYS-REQ-0012, SUB-PR-0013-BE
- Related ADRs: ADR-0008 (CDS Microservice), ADR-0020 (Feature Flags)
