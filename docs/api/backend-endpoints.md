# Backend API Endpoints

**Base URL:** `http://localhost:8000`
**Docs:** `http://localhost:8000/docs` (Swagger UI)
**Last Updated:** 2026-02-16

## Authentication

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/auth/token` | Login, returns JWT | No |

### POST `/auth/token`

**Request:**
```json
{ "username": "string", "password": "string" }
```

**Response (200):**
```json
{ "access_token": "string", "token_type": "bearer" }
```

---

## Patients (SUB-PR)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/patients/` | List all patients | Yes |
| POST | `/patients/` | Create a patient | Yes |
| GET | `/patients/{id}` | Get patient by ID | Yes |
| PATCH | `/patients/{id}` | Update patient | Yes |

### Patient Object

```json
{
  "id": "uuid",
  "first_name": "string",
  "last_name": "string",
  "date_of_birth": "YYYY-MM-DD",
  "gender": "string",
  "email": "string | null",
  "phone": "string | null",
  "address": "string | null",
  "created_at": "ISO 8601",
  "updated_at": "ISO 8601"
}
```

### POST `/patients/` — Create

**Request:**
```json
{
  "first_name": "string",
  "last_name": "string",
  "date_of_birth": "YYYY-MM-DD",
  "gender": "string",
  "email": "string | null",
  "phone": "string | null",
  "address": "string | null",
  "ssn": "string | null"
}
```

Note: SSN is encrypted at rest (SYS-REQ-0002) and never returned in responses.

---

## Encounters (SUB-CW)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/encounters/` | List all encounters | Yes |
| POST | `/encounters/` | Create an encounter | Yes |
| GET | `/encounters/{id}` | Get encounter by ID | Yes |
| PATCH | `/encounters/{id}` | Update encounter | Yes |

### Encounter Object

```json
{
  "id": "uuid",
  "patient_id": "uuid",
  "encounter_type": "office_visit | telehealth | emergency | follow_up",
  "status": "scheduled | in_progress | completed | cancelled",
  "reason": "string | null",
  "notes": "string | null",
  "scheduled_at": "ISO 8601 | null",
  "started_at": "ISO 8601 | null",
  "completed_at": "ISO 8601 | null",
  "created_at": "ISO 8601"
}
```

---

## Medications (SUB-MM)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/medications/` | List all medications | Yes |
| POST | `/medications/` | Add a medication | Yes |
| POST | `/medications/prescriptions` | Create a prescription | Yes |
| GET | `/medications/interactions/{patient_id}` | Check drug interactions | Yes |

### Medication Object

```json
{
  "id": "uuid",
  "name": "string",
  "generic_name": "string | null",
  "drug_class": "string | null",
  "description": "string | null",
  "created_at": "ISO 8601"
}
```

### Prescription Object

```json
{
  "id": "uuid",
  "patient_id": "uuid",
  "medication_id": "uuid",
  "dosage": "string",
  "frequency": "string",
  "refills_remaining": 0,
  "status": "active | completed | cancelled",
  "prescribed_at": "ISO 8601"
}
```

### Interaction Warning

```json
{
  "medication_a": "string",
  "medication_b": "string",
  "severity": "high | medium | low",
  "description": "string"
}
```

---

## Reports (SUB-RA)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/reports/patient-volume` | Patient volume analytics | Yes |
| GET | `/reports/encounter-summary` | Encounter summary analytics | Yes |
| GET | `/reports/medication-usage` | Medication usage analytics | Yes |

All report endpoints currently return stub data:
```json
{ "report": "report_name", "data": [] }
```

---

## Vision (SUB-PR-0009, SUB-PR-0010, SUB-PR-0011)

All vision endpoints require authentication and are gated behind feature flags. When a feature flag is disabled, the endpoint returns `501 Not Implemented`. All endpoints currently return stub data until TensorRT models are deployed.

| Method | Path | Description | Auth | Feature Flag |
|--------|------|-------------|------|-------------|
| POST | `/vision/wound-assessment` | AI wound severity assessment | Yes | `FEATURE_SUB_PR_0009_WOUND_ASSESSMENT` |
| POST | `/vision/patient-id-verify` | Patient identity verification via photo | Yes | `FEATURE_SUB_PR_0010_PATIENT_ID_VERIFY` |
| POST | `/vision/document-ocr` | Document text extraction via OCR | Yes | `FEATURE_SUB_PR_0011_DOCUMENT_OCR` |

### POST `/vision/wound-assessment`

**Request:** `multipart/form-data` with `file` (image upload)

**Response (200):**
```json
{
  "severity": "mild | moderate | severe | critical",
  "area_percentage": 12.5,
  "description": "string",
  "confidence": 0.87
}
```

### POST `/vision/patient-id-verify`

**Request:** `multipart/form-data` with `file` (image upload) + query param `patient_id` (UUID)

**Response (200):**
```json
{
  "match": true,
  "confidence": 0.94
}
```

### POST `/vision/document-ocr`

**Request:** `multipart/form-data` with `file` (image upload)

**Response (200):**
```json
{
  "extracted_text": "string",
  "fields": {
    "patient_name": "string",
    "date_of_birth": "string",
    "insurance_id": "string"
  }
}
```

---

## Health

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/health` | Health check | No |

**Response:** `{ "status": "ok" }`

---

## Common Patterns

- **Authentication**: Bearer token in `Authorization` header.
- **IDs**: All entity IDs are UUIDs.
- **Timestamps**: ISO 8601 with timezone (`2024-01-15T10:30:00+00:00`).
- **Errors**: Standard FastAPI error responses (`{"detail": "message"}`).
- **Feature flags**: Vision endpoints return `501` when their flag is disabled.
- **Stub endpoints**: Most endpoints return placeholder data. See [Initial Project Scaffolds](../features/initial-project-scaffolds.md) for details.
