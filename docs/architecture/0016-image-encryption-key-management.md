# ADR-0016: Encryption Key Management

**Date:** 2026-02-21
**Status:** Accepted
**Deciders:** Development Team

---

## Context

The PMS already encrypts patient SSNs using AES-256 (SYS-REQ-0002) with a key loaded from an environment variable. The Dermatology CDS module (ADR-0010) adds a second encryption use case: patient dermoscopic images stored as AES-256-GCM encrypted BYTEA in PostgreSQL. This creates a key management question: should image encryption use the same key as SSN encryption, a separate key, or a more sophisticated key management approach?

Additionally, if the encryption key ever needs to be rotated (e.g., key compromise, compliance audit), all encrypted data must be re-encrypted with the new key. With potentially 50,000+ encrypted images, key rotation must be practical.

## Options Considered

1. **Unified key management with versioned-envelope approach** — A single key hierarchy with a Key Encryption Key (KEK) that wraps per-purpose Data Encryption Keys (DEKs). Each encrypted blob includes the DEK version used.
   - Pros: Supports key rotation without re-encrypting all data at once, separate DEKs for SSN and images, enterprise-grade pattern.
   - Cons: More complex than a single flat key, requires version metadata in encrypted blobs.

2. **Single shared key for all encryption** — Reuse the existing SSN encryption key for images.
   - Pros: Simplest implementation, no new key management.
   - Cons: Compromising one key exposes all PHI (SSNs + images), no key rotation path, violates principle of least privilege.

3. **Separate keys per data type** — One key for SSNs, another for images, both from environment variables.
   - Pros: Isolation between data types, compromise of one key doesn't expose the other.
   - Cons: Multiple environment variables, no key rotation support, keys must be coordinated across services.

4. **External key management service (HashiCorp Vault)** — Dedicated KMS for key generation, rotation, and access control.
   - Pros: Enterprise-grade, automatic rotation, audit trail, access policies.
   - Cons: Significant infrastructure addition, must run on-premises for Jetson deployment, operational complexity.

## Decision

Use a **unified key management approach with versioned-envelope encryption** — a single Key Encryption Key (KEK) wraps purpose-specific Data Encryption Keys (DEKs), and each encrypted blob includes the DEK version for rotation support.

## Rationale

1. **Key isolation** — Separate DEKs for SSN encryption and image encryption mean compromising one DEK doesn't expose the other data type.
2. **Key rotation** — The KEK can be rotated independently. New data is encrypted with the current DEK version. Old data is re-encrypted lazily (on next read) or in batch, tracked by version number.
3. **Versioned ciphertext** — Each encrypted blob starts with a 1-byte version prefix, then the 12-byte nonce, then ciphertext. The version byte identifies which DEK was used, enabling graceful migration.
4. **Backward compatible** — Existing SSN encryption can be migrated to this scheme incrementally. Current SSN ciphertext (no version prefix) is treated as version 0.
5. **On-premises friendly** — Unlike HashiCorp Vault, this requires no additional infrastructure. The KEK is loaded from an environment variable, and DEKs are derived deterministically or stored encrypted in a keyring table.
6. **Shared across services** — Both the PMS backend and the CDS service can derive DEKs from the same KEK, enabling the backend to encrypt images that the CDS service can read if needed.

## Key Hierarchy

```
┌──────────────────────────────────────────┐
│  KEK (Key Encryption Key)                │
│  Source: Environment variable            │
│  Algorithm: AES-256                      │
│  Rotation: Manual, requires re-wrapping  │
└──────────────────────────────────────────┘
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌─────────────────────┐
│  DEK-SSN v1     │  │  DEK-IMG v1         │
│  Purpose: SSN   │  │  Purpose: Images    │
│  AES-256-GCM    │  │  AES-256-GCM        │
│  Wrapped by KEK │  │  Wrapped by KEK     │
└─────────────────┘  └─────────────────────┘

Ciphertext format:
[version: 1 byte][nonce: 12 bytes][ciphertext + GCM tag]
```

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| Single shared key | Key compromise exposes all PHI, no key rotation path |
| Separate env var keys | No rotation support, multiple env vars to coordinate |
| HashiCorp Vault | Infrastructure overhead, must run on-premises for Jetson, overkill for current scale |
| AWS KMS / GCP KMS | Cloud dependency violates on-premises PHI requirement |

## Trade-offs

- **Complexity vs flat key** — The versioned-envelope approach is more complex than a single environment variable. Justified by key rotation support and data type isolation, which are compliance requirements for medical software.
- **KEK as single point** — The KEK in an environment variable is still a single secret. Mitigation: restrict access to the environment configuration, rotate KEK annually, re-wrap DEKs on rotation.
- **No hardware security module** — Keys are stored in software (environment variables, database keyring table). For production deployments with higher security requirements, a future ADR can add HSM support.

## Consequences

- A `key_manager.py` module in the backend provides `encrypt(purpose, plaintext)` and `decrypt(purpose, ciphertext)` functions.
- The `purpose` parameter selects the DEK (e.g., `"ssn"`, `"image"`).
- DEKs are generated once and stored in a `encryption_keys` table, wrapped by the KEK.
- The CDS service accesses the same key infrastructure for any image decryption needs.
- Encrypted blobs include a version prefix byte for forward-compatible key rotation.
- Existing SSN encryption is migrated to the new scheme (version 0 = legacy format, version 1+ = new format).
- Key rotation SOP: generate new DEK version → new writes use new version → batch re-encrypt old data → retire old version.

## References

- Related PRD: docs/experiments/18-PRD-ISICArchive-PMS-Integration.md (Section 6.1)
- Related Requirements: SYS-REQ-0002 (PHI encryption), SYS-REQ-0012
- Related ADRs: ADR-0003 (Backend Tech Stack), ADR-0010 (Image Storage)
