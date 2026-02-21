# ADR-0017: ISIC Reference Cache Management

**Date:** 2026-02-21
**Status:** Accepted
**Deciders:** Development Team

---

## Context

The Dermatology CDS module (SUB-PR-0014) provides similarity search by comparing patient lesion embeddings against a local cache of ISIC Archive reference images with pre-computed 512-dimensional embedding vectors. This reference cache must be populated initially (10,000-50,000 images), kept consistent with the model version used to generate embeddings, and updated when new ISIC data or model versions become available.

The ISIC Archive contains 400,000+ images available via REST API and AWS S3 Open Data bucket. The PMS only needs a representative subset, balanced across the 9 diagnostic categories.

## Options Considered

1. **Initial S3 bulk download + model-version-coupled embeddings + incremental API updates** — Download a representative subset from S3, compute embeddings with the current model, recompute when model changes, add new images via ISIC API.
   - Pros: Fast initial population (S3 bulk), embedding consistency with active model, incremental growth without full recompute.
   - Cons: S3 download requires AWS CLI, embedding recomputation is compute-intensive on model change.

2. **On-demand API fetching** — Fetch and embed ISIC images at query time (lazy population).
   - Pros: No upfront bulk download, always fresh data.
   - Cons: First query latency is unacceptable (>10s per image), requires internet access for every similarity search, violates offline-capable requirement.

3. **Pre-computed embeddings shipped with Docker image** — Bundle reference embeddings as a static database dump in the Docker image.
   - Pros: Zero setup for deployment, immediate availability.
   - Cons: Docker image grows by ~5 GB, embeddings are tied to a specific model version, updating requires image rebuild.

4. **External vector service with ISIC embeddings** — Use an ISIC-hosted embedding service.
   - Pros: No local storage needed, always up-to-date.
   - Cons: Doesn't exist, would require internet access (violates on-premises requirement), external dependency.

## Decision

Use **S3 bulk download for initial population**, **model-version-coupled embeddings** that are recomputed when the classification model changes, and **incremental updates** via the ISIC REST API for adding new reference images between model updates.

## Rationale

1. **Fast initial setup** — AWS S3 bulk download (`aws s3 sync`) retrieves 50,000 ISIC reference images in ~30 minutes (vs. days via individual API calls). The ISIC Archive S3 bucket is part of the AWS Open Data program (no AWS account charges for download).
2. **Model-version coupling** — Embeddings are meaningful only relative to the model that generated them. When the classification model changes (ADR-0013), all reference embeddings must be recomputed to maintain similarity search accuracy. The reference cache stores the model version that generated each embedding.
3. **Balanced category distribution** — The population script ensures balanced representation across 9 diagnostic categories, avoiding the ISIC dataset's heavy skew toward melanocytic nevi (~70% of images).
4. **Incremental growth** — Between model updates, new ISIC images (published annually) can be added incrementally via `isic-cli` or the REST API, with embeddings computed on insertion.
5. **Offline operation** — Once populated, the reference cache operates entirely offline. Similarity search requires no internet access.

## Cache Population Strategy

```
┌─────────────────────────────────────────┐
│ Initial Population (one-time)           │
│                                         │
│ 1. aws s3 sync from ISIC S3 bucket    │
│ 2. Filter to 50K representative images  │
│    (~5,500 per diagnostic category)     │
│ 3. Compute embeddings via CDS model     │
│ 4. Insert into isic_reference_embeddings│
│ 5. Build IVFFlat/HNSW pgvector index   │
│ 6. Record model_version in manifest     │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ Incremental Update (periodic)           │
│                                         │
│ 1. Query ISIC API for new images since  │
│    last sync date                       │
│ 2. Download new images                  │
│ 3. Compute embeddings with current model│
│ 4. Insert into isic_reference_embeddings│
│ 5. Rebuild index if >10% growth         │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ Model Version Change (annual)           │
│                                         │
│ 1. New model deployed (ADR-0013)        │
│ 2. Recompute ALL reference embeddings   │
│    with new model                       │
│ 3. Update model_version in all rows     │
│ 4. Rebuild pgvector index               │
│ 5. Validate with known similarity pairs │
└─────────────────────────────────────────┘
```

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| On-demand API fetching | 10s+ per query, requires internet, violates offline requirement |
| Embeddings in Docker image | 5 GB image size increase, tied to specific model, rebuild on update |
| External embedding service | Doesn't exist, internet dependency, external point of failure |
| Full 400K image cache | 80 GB storage requirement exceeds Jetson SSD budget, diminishing returns beyond 50K |

## Trade-offs

- **Embedding recomputation** — Model changes require recomputing all 50K embeddings (~4 hours on GPU, ~24 hours on CPU). Mitigation: model updates are annual; recomputation runs as a batch job during maintenance window.
- **S3 download requirement** — Initial setup needs internet access and AWS CLI. Mitigated by also supporting `isic-cli download` for environments without AWS CLI.
- **Category balance** — The ISIC dataset is heavily skewed. Active balancing may undersample common diagnoses. Mitigated by keeping extra nevi images in a secondary tier for completeness.
- **Storage** — 50K reference images + embeddings require ~10 GB. Acceptable for server/Jetson deployments.

## Consequences

- A `populate_cache.py` script handles initial S3 bulk download, category balancing, and embedding computation.
- The `isic_reference_embeddings` table includes a `model_version` column to track embedding provenance.
- A `cache-manifest.json` records: total images, per-category counts, model version, last sync date, S3 sync timestamp.
- Model update SOP (ADR-0013) includes a step to recompute reference embeddings.
- The CDS health endpoint reports reference cache status: `{"reference_cache": {"total": 50000, "model_version": "2024-v1"}}`.
- pgvector indexes are rebuilt after significant cache changes (>10% growth or model version change).

## References

- Related PRD: docs/experiments/18-PRD-ISICArchive-PMS-Integration.md (Section 5.5)
- Related Requirements: SYS-REQ-0012, SUB-PR-0014, SUB-PR-0014-AI
- Related ADRs: ADR-0011 (Vector Database), ADR-0013 (AI Model Lifecycle)
