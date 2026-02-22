# ADR-0011: Vector Database Strategy

**Date:** 2026-02-21
**Status:** Accepted
**Deciders:** Development Team

---

## Context

The Dermatology CDS module (SYS-REQ-0012) requires vector similarity search to find ISIC reference images that are visually similar to a patient's skin lesion (SUB-PR-0014). The system generates 512-dimensional float32 embedding vectors from the penultimate layer of the classification model and must query a reference database of 10,000-50,000 pre-computed ISIC image embeddings to return the top-K most similar images by cosine distance.

Performance requirement: <200ms for top-10 similarity search against 50,000 reference vectors.

## Options Considered

1. **pgvector (PostgreSQL extension)** — Add vector similarity search directly to the existing PostgreSQL instance.
   - Pros: No new infrastructure, shared with existing PMS database, SQL-native queries, IVFFlat and HNSW indexing, good enough for 50K vectors.
   - Cons: Not optimized for billion-scale vector workloads, IVFFlat requires pre-defined list count, no GPU-accelerated search.

2. **Milvus** — Purpose-built distributed vector database.
   - Pros: Designed for vector search at scale, GPU-accelerated, supports hybrid search, rich query DSL.
   - Cons: Heavy infrastructure (etcd + MinIO + Milvus), overkill for 50K vectors, another service to deploy/monitor/backup.

3. **Qdrant** — Lightweight vector search engine.
   - Pros: Simple deployment (single binary), good performance, REST/gRPC API, filtering support.
   - Cons: Another service to manage, separate backup strategy, data duplication (metadata in both PostgreSQL and Qdrant).

4. **Weaviate** — AI-native vector database with built-in vectorizers.
   - Pros: Built-in module for image vectorization, GraphQL API, hybrid search.
   - Cons: Heavyweight, built-in vectorizers redundant (we have our own model), another infrastructure component.

5. **FAISS (in-memory)** — Facebook's similarity search library loaded in the CDS service process.
   - Pros: Fastest search (microseconds), no external dependency, trivial for 50K vectors.
   - Cons: In-memory only (lost on restart), no persistence without custom serialization, not queryable from backend, duplicates data management.

## Decision

Use **pgvector** (PostgreSQL vector extension) for all vector similarity search, leveraging the existing PostgreSQL instance shared with the PMS backend.

## Rationale

1. **No new infrastructure** — pgvector is a PostgreSQL extension installed via `CREATE EXTENSION vector`. No new services, ports, backup strategies, or monitoring dashboards.
2. **Scale matches our needs** — With 50,000 reference vectors and an IVFFlat index (100 lists), pgvector delivers <50ms query latency. Even at 200,000 vectors, pgvector with HNSW indexing stays under 100ms. Dedicated vector databases are designed for millions-to-billions of vectors.
3. **SQL-native joins** — Similarity search results can be joined with ISIC metadata (diagnosis, anatomical site, patient demographics) in a single SQL query, eliminating application-level data stitching.
4. **Transactional consistency** — Reference embeddings and their metadata are in the same database as patient data. Updates to the reference cache (ADR-0017) are transactional.
5. **Operational simplicity** — One database to back up, monitor, and tune. On Jetson Thor (ADR-0007), running Milvus alongside PostgreSQL would strain the 128 GB unified memory.
6. **Cosine distance support** — pgvector natively supports cosine distance (`<=>` operator), which is the standard metric for normalized image embeddings.

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| Milvus | Heavy infrastructure (etcd + MinIO), overkill for 50K vectors, complex on Jetson edge |
| Qdrant | Separate service, separate backup, data duplication with PostgreSQL |
| Weaviate | Heavyweight, built-in vectorizers redundant, over-engineered for our use case |
| FAISS in-memory | No persistence, not queryable from backend, data management complexity |

## Trade-offs

- **Performance ceiling** — pgvector is slower than dedicated vector databases at scale. If the reference cache grows beyond 500K vectors, we may need to re-evaluate. Current plan caps at 50K.
- **Index rebuild on insert** — IVFFlat indexes need periodic rebuilding as data distribution changes. Mitigated by using HNSW index type (available in pgvector 0.5+) which doesn't require rebuilding.
- **No GPU-accelerated search** — Unlike Milvus, pgvector runs on CPU only. Acceptable: 50K vectors searched in <50ms on CPU.

## Consequences

- PostgreSQL requires the `pgvector` extension (version 0.7+). The Docker Compose PostgreSQL image uses `pgvector/pgvector:pg16`.
- Two vector tables are created: `isic_reference_embeddings` (reference cache) and `patient_lesion_embeddings` (patient lesion vectors for longitudinal tracking).
- IVFFlat indexes are created with `vector_cosine_ops` for cosine distance search.
- The CDS service connects directly to PostgreSQL for similarity queries (shared database with backend).
- Database migrations (ADR-0021) manage vector table schema and index creation.
- If vector volume exceeds 500K, the team will re-evaluate dedicated vector DB options.

## References

- Related PRD: docs/experiments/18-PRD-ISICArchive-PMS-Integration.md (Section 5.3)
- Related Requirements: SYS-REQ-0012, SUB-PR-0014, SUB-PR-0014-AI
- Related ADRs: ADR-0008 (CDS Microservice), ADR-0017 (ISIC Reference Cache), ADR-0019 (Lesion Longitudinal Tracking), ADR-0021 (Database Migration)
