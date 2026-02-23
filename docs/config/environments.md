# Environment Configuration

**Related ADR:** [ADR-0006: Release Management Strategy](../architecture/0006-release-management-strategy.md)

---

## Environment Overview

| Environment | Purpose | Deploy Trigger | Data | Feature Flag Control |
|---|---|---|---|---|
| Dev | Development and integration testing | Auto on merge to `main` | Synthetic | Developers toggle freely |
| QA | Regression and acceptance testing | Manual trigger from CI | Synthetic | QA team approval for changes |
| Staging | Pre-production validation | RC tag deploy | Sanitized production copy | Product owner approval |
| Production | Live system | Manual promotion | Real PHI | Change control board approval |

## Dev Environment

- **URL pattern:** `*.dev.pms.internal`
- **Deploy trigger:** Automatic on every merge to `main` (CI must pass)
- **Database:** Synthetic test data, seeded on deploy
- **Feature flags:** All flags freely toggled by developers for testing
- **Access:** Development team only
- **HIPAA controls:** Relaxed (synthetic data, no PHI)
- **Logging:** Verbose, debug-level

## QA Environment

- **URL pattern:** `*.qa.pms.internal`
- **Deploy trigger:** Manual trigger from CI pipeline (select branch/tag)
- **Database:** Synthetic test data matching production schema
- **Feature flags:** Changes require QA team lead approval
- **Access:** QA team + development team (read-only for devs)
- **HIPAA controls:** Standard (synthetic data, but production-like configuration)
- **Logging:** Info-level, structured JSON

## Staging Environment

- **URL pattern:** `*.staging.pms.internal`
- **Deploy trigger:** RC tag deployment (e.g., `v0.2.0-rc.1`)
- **Database:** Sanitized copy of production data (PHI removed/anonymized)
- **Feature flags:** Changes require product owner approval
- **Access:** Product owner + QA lead + tech lead
- **HIPAA controls:** Full (production-equivalent configuration)
- **Logging:** Info-level, structured JSON, audit trail enabled

## Production Environment

- **URL pattern:** `*.pms.utexas.edu`
- **Deploy trigger:** Manual promotion after change control board approval
- **Database:** Real PHI, encrypted at rest (AES-256), TLS 1.3 in transit
- **Feature flags:** Changes require change control board approval
- **Access:** All authorized users per RBAC policy
- **HIPAA controls:** Full — encryption, audit logging, access controls, breach notification
- **Logging:** Info-level, structured JSON, immutable audit trail, 6-year retention

## Environment Variables by Environment

| Variable | Dev | QA | Staging | Prod |
|---|---|---|---|---|
| `DEBUG` | `true` | `false` | `false` | `false` |
| `DATABASE_URL` | Local PostgreSQL | QA PostgreSQL | Staging RDS | Prod RDS |
| `SECRET_KEY` | Dev key | Rotated monthly | Rotated monthly | Rotated monthly |
| `ENCRYPTION_KEY` | Dev key | Per-env key | Per-env key | HSM-managed |
| `LOG_LEVEL` | `DEBUG` | `INFO` | `INFO` | `INFO` |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | QA backend URL | Staging backend URL | Prod backend URL |
| `NEXT_PUBLIC_AUTH_BYPASS_ENABLED` | `true` (optional) | **never** | **never** | **never** |
| `NEXT_PUBLIC_AUTH_BYPASS_ROLE` | `admin` (optional) | — | — | — |
| `NEXT_PUBLIC_AUTH_BYPASS_EMAIL` | `dev@localhost` (optional) | — | — | — |
| `NEXT_PUBLIC_AUTH_BYPASS_NAME` | `Dev User` (optional) | — | — | — |
| `FEATURE_*` | Per developer | QA-controlled | PO-controlled | CCB-controlled |

> **Warning:** `NEXT_PUBLIC_AUTH_BYPASS_ENABLED` must **never** be set to `true` outside local development. The `NEXT_PUBLIC_` prefix exposes these values in the browser bundle. The frontend displays a non-dismissible yellow warning banner when bypass mode is active (SUB-AU-0016).

## Jetson Thor (Edge)

- **Hardware:** NVIDIA Jetson Thor T5000 (ARM64, Blackwell GPU, 128 GB LPDDR5X)
- **OS:** Ubuntu 24.04 LTS (JetPack 7.x)
- **Deploy trigger:** Manual `docker compose up` on-device
- **Database:** Local PostgreSQL in Docker, persistent volume, encrypted at rest
- **Feature flags:** Locally configured in `.env` on the Jetson
- **Access:** Android clients on local Wi-Fi 7 network only
- **HIPAA controls:** Full — all PHI stays on-device, no cloud egress, AES-256 encryption, audit logging
- **Logging:** Info-level, structured JSON, local audit trail
- **GPU:** CUDA 13, TensorRT 10.13 — used for vision inference (wound assessment, patient ID, OCR)
- **Network:** Wi-Fi 7 (802.11be), static IP recommended for stable client connections
- **Ports:** Backend :8000, Frontend :3000, PostgreSQL :5432 (internal only)

## Promotion Flow

```
Dev ──[CI pass]──→ QA ──[QA sign-off]──→ Staging ──[CCB approval]──→ Prod
```

Each promotion copies the exact same container image/build artifact — no rebuilds between environments. Only environment variables and feature flag states differ.
