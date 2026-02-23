# ADR-0010: Patient Image Storage Strategy

**Date:** 2026-02-21
**Status:** Accepted
**Deciders:** Development Team

---

## Context

The Dermatology CDS module (SYS-REQ-0012) captures and stores patient dermoscopic images for classification, longitudinal tracking, and clinical review. These images are Protected Health Information (PHI) and must be encrypted at rest per HIPAA Security Rule requirements. The existing PMS already encrypts patient SSNs using AES-256 in the backend encryption service.

Patient images are typically 1-5 MB JPEG files. The system must store up to 50 images per patient over time (longitudinal tracking), and the total volume could reach 10,000-50,000 images across all patients.

## Options Considered

1. **AES-256-GCM encrypted BYTEA in PostgreSQL** — Store encrypted image bytes directly in a PostgreSQL `BYTEA` column.
   - Pros: Single backup strategy, transactional consistency with patient records, no separate storage infrastructure, encryption at the application layer.
   - Cons: PostgreSQL not optimized for large binary storage, database size grows with image volume, backup/restore slower with large BLOBs.

2. **Encrypted filesystem with PostgreSQL metadata** — Store encrypted images on disk (or Docker volume), with file paths in PostgreSQL.
   - Pros: Filesystem optimized for large files, PostgreSQL stays lean, can use OS-level encryption (LUKS/dm-crypt).
   - Cons: Two systems to back up, file path references can become stale, no transactional consistency between metadata and file.

3. **PostgreSQL Large Objects (lo)** — Use PostgreSQL's built-in large object facility.
   - Pros: Handles large files better than BYTEA, streaming support.
   - Cons: Large objects bypass row-level security, harder to encrypt at application layer, non-standard API, orphaned objects require vacuuming.

4. **Object storage (MinIO/S3-compatible)** — Self-hosted MinIO for on-premises object storage.
   - Pros: Purpose-built for binary objects, S3 API compatibility, server-side encryption.
   - Cons: Additional infrastructure component, another service to deploy/monitor, overkill for the expected volume.

## Decision

Store patient dermoscopic images as **AES-256-GCM encrypted BYTEA** in PostgreSQL, with encryption performed at the application layer before persistence.

## Rationale

1. **Transactional consistency** — Image storage, classification results, and audit logs are in the same transaction. No orphaned files or stale references.
2. **Single backup strategy** — PostgreSQL `pg_dump` captures everything. No separate file backup pipeline needed.
3. **Encryption alignment** — Reuses the same AES-256-GCM pattern established for SSN encryption (SYS-REQ-0002), with key management extended to cover image data (ADR-0016).
4. **Volume is manageable** — At 3 MB average per encrypted image and 50,000 total images, the storage requirement is ~150 GB. PostgreSQL handles this comfortably with modern hardware and tablespace management.
5. **Deployment simplicity** — On Jetson Thor (ADR-0007), adding a MinIO service or separate filesystem encryption layer increases complexity. PostgreSQL BYTEA works with the existing docker-compose stack.
6. **HIPAA compliance** — Application-layer encryption means images are encrypted before they reach PostgreSQL. Even database administrators or backup operators cannot access raw patient images without the encryption key.

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| Encrypted filesystem + metadata | Two backup systems, stale file references, no transactional consistency |
| PostgreSQL Large Objects | Bypass row-level security, non-standard API, harder to encrypt at app layer |
| MinIO/S3 object storage | Additional infrastructure for our volume, overkill for on-premises single-clinic deployment |
| Unencrypted storage with disk-level encryption | Does not meet defense-in-depth requirement; DB admins could access images |

## Trade-offs

- **Database size** — PostgreSQL grows with image volume. Mitigation: configurable retention policy, tablespace on separate NVMe, periodic archival of old images.
- **Query performance** — Large BYTEA columns slow down `SELECT *` queries. Mitigation: images are in a dedicated `lesion_images` table, never joined in list queries; image retrieval is always by primary key.
- **Backup time** — Full backups are slower with large BLOBs. Mitigation: incremental backups via WAL archiving, image table can be backed up separately with `pg_dump --table`.
- **Memory pressure** — Large images in BYTEA can pressure PostgreSQL shared buffers. Mitigation: images are stored encrypted (opaque bytes, not indexed), and retrieval uses streaming cursors.

## Consequences

- The `lesion_images` table stores encrypted image bytes in a `BYTEA NOT NULL` column (`image_data`).
- Application-layer encryption uses AES-256-GCM with a 12-byte nonce prepended to the ciphertext (nonce || ciphertext || GCM tag).
- The encryption key is managed via the unified key management approach (ADR-0016).
- Image upload endpoints in the backend encrypt before `INSERT`, decrypt on retrieval via `SELECT`.
- An `image_hash` column (SHA-256 of plaintext) enables deduplication without decryption.
- PostgreSQL storage is monitored for growth; alerts fire if `lesion_images` exceeds configurable thresholds.

## References

- Related PRD: docs/experiments/18-PRD-ISICArchive-PMS-Integration.md (Section 6.1)
- Related Requirements: SYS-REQ-0002 (PHI encryption), SYS-REQ-0012, SUB-PR-0013-BE
- Related ADRs: ADR-0003 (Backend Tech Stack), ADR-0016 (Encryption Key Management)
