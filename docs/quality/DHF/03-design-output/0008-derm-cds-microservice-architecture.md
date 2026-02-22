# ADR-0008: CDS Microservice Architecture

**Date:** 2026-02-21
**Status:** Accepted
**Deciders:** Development Team

---

## Context

The PMS is adding AI-powered dermatology clinical decision support (SYS-REQ-0012) that requires deep learning inference (EfficientNet-B4), image embedding generation, pgvector similarity search, and risk scoring. These capabilities have heavy Python dependencies (PyTorch, ONNX Runtime, torchvision) and different scaling characteristics than the existing FastAPI backend, which handles CRUD operations for patient records, encounters, and medications.

The question is whether to embed the AI inference pipeline directly into the existing `pms-backend` FastAPI application or to deploy it as a separate Docker service.

## Options Considered

1. **Separate Docker service (`pms-derm-cds` on :8090)** — Dedicated FastAPI container with its own Dockerfile, dependencies, and lifecycle.
   - Pros: Independent scaling, isolated dependency tree (PyTorch/ONNX ~2 GB don't bloat backend), independent restarts during model updates, clear failure boundary.
   - Cons: Network hop latency (~1-5ms), additional container to manage, requires inter-service communication patterns.

2. **Embed into existing FastAPI monolith** — Add AI endpoints as new routers in `pms-backend`.
   - Pros: Simpler deployment (one container), no network hop, shared auth/DB infrastructure.
   - Cons: PyTorch/ONNX adds ~2 GB to backend image, model loading blocks backend startup, GPU OOM in inference crashes the entire backend, coupled release cycles.

3. **Serverless functions (AWS Lambda / Cloud Run)** — Deploy inference as stateless cloud functions.
   - Pros: Auto-scaling, no container management.
   - Cons: Patient images would leave the premises (HIPAA violation for our deployment model), cold start latency (~10s for model load), cannot use Jetson GPU.

## Decision

Deploy the Dermatology CDS as a **separate Docker service** (`pms-derm-cds`) listening on port 8090, communicating with the PMS backend over the internal Docker network via HTTP.

## Rationale

1. **Dependency isolation** — PyTorch 2.x, ONNX Runtime, torchvision, and Pillow add ~2 GB to the container image. Keeping these separate means the lean FastAPI backend (~200 MB) stays fast to build and deploy.
2. **Fault isolation** — An OOM during GPU inference or a model loading failure crashes only the CDS container, not the entire PMS backend serving patient records.
3. **Independent scaling** — Classification workloads are bursty (batch clinic sessions). The CDS service can scale independently or be allocated GPU resources without affecting backend CPU allocation.
4. **Model update lifecycle** — Model weights are updated annually (post-ISIC Challenge). Redeploying the CDS container with new weights doesn't require restarting the backend or disrupting active sessions.
5. **Consistent with edge deployment** — On Jetson Thor, the CDS runs as a separate container in the docker-compose stack (ADR-0007), matching the same architecture as development and staging environments.
6. **On-premises compliance** — Unlike serverless options, the Docker service runs entirely within the clinic network, ensuring patient images never leave the premises.

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| Embed into FastAPI monolith | PyTorch dependency bloat, coupled failure modes, model loading blocks backend startup |
| Serverless functions | Patient images would egress to cloud (HIPAA risk), cold start latency unacceptable for clinical workflow |
| gRPC instead of HTTP | Added complexity for minimal latency gain (~1ms) on internal Docker network; HTTP provides simpler debugging with Swagger docs |
| Sidecar container pattern | Unnecessary coupling; the CDS service has its own lifecycle and may serve multiple backend instances in future |

## Trade-offs

- **Network latency** — HTTP call from backend to CDS adds ~1-5ms. Acceptable given total pipeline target is <5s.
- **Operational complexity** — One more container to monitor. Mitigated by health checks, docker-compose orchestration, and circuit breaking (ADR-0018).
- **Shared database** — Both services connect to the same PostgreSQL instance. The CDS service only reads/writes its own tables (isic_reference_embeddings, patient_lesion_embeddings), reducing coupling.

## Consequences

- The `pms-derm-cds` service is defined in `docker-compose.yml` with its own Dockerfile, build context, and volume mounts for model weights and reference cache.
- The PMS backend communicates with the CDS service via HTTP client (httpx) with connection pooling and timeout configuration (ADR-0018).
- The CDS service exposes `/classify`, `/similar`, and `/health` endpoints.
- Model weights are stored in a Docker volume (`derm-models`) and loaded at container startup.
- The CDS service is feature-flagged (ADR-0020) and returns stubs until models are deployed.

## References

- Related PRD: docs/experiments/18-PRD-ISICArchive-PMS-Integration.md
- Related Requirements: SYS-REQ-0012, SUB-PR-0013, SUB-PR-0014, SUB-PR-0015, SUB-PR-0016
- Related ADRs: ADR-0003 (Backend Tech Stack), ADR-0007 (Jetson Edge Deployment), ADR-0018 (Inter-Service Communication)
