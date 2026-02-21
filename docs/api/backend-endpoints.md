# Backend API Endpoints

**Base URL:** `http://localhost:8000`
**Docs:** `http://localhost:8000/docs` (Swagger UI)
**Last Updated:** 2026-02-21

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

## Lesions — Dermatology CDS (SUB-PR-0013, SUB-PR-0014, SUB-PR-0015, SUB-PR-0016)

All lesion endpoints require authentication and are gated behind feature flags (ADR-0020). When a feature flag is disabled, the endpoint returns `404 Not Found`. The backend forwards image data to the `pms-derm-cds` service (:8090) via HTTP with circuit breaking (ADR-0018). All endpoints currently return stub data until the CDS service is deployed.

| Method | Path | Description | Auth | Feature Flag |
|--------|------|-------------|------|-------------|
| POST | `/api/lesions/upload` | Upload dermoscopic image for AI classification | Yes | `DERM_CLASSIFICATION` |
| GET | `/api/lesions/history/{patient_id}` | Lesion classification history for a patient | Yes | `DERM_CLASSIFICATION` |
| POST | `/api/lesions/similar` | Find similar ISIC reference images | Yes | `DERM_SIMILARITY_SEARCH` |
| GET | `/api/lesions/{lesion_id}/timeline` | Longitudinal timeline for a specific lesion | Yes | `DERM_LONGITUDINAL_TRACKING` |
| GET | `/reports/dermatology` | Dermatology classification analytics | Yes | `DERM_REPORTING_DASHBOARD` |

### POST `/api/lesions/upload`

Upload a dermoscopic image for AI classification, risk scoring, and similarity search. The image is encrypted with AES-256-GCM (ADR-0010, ADR-0016) before storage.

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image` | file | Yes | JPEG or PNG dermoscopic image (max 20 MB) |
| `patient_id` | UUID | Yes | Patient to associate the lesion with |
| `encounter_id` | UUID | No | Encounter to link assessment to |
| `anatomical_site` | string | No | Body location (e.g., `back`, `scalp`, `trunk`, `lower_extremity`) |

**Response (200):**
```json
{
  "lesion_image_id": "uuid",
  "classification": {
    "predictions": [
      { "class": "melanocytic_nevus", "probability": 0.7234 },
      { "class": "melanoma", "probability": 0.1102 },
      { "class": "benign_keratosis", "probability": 0.0891 }
    ],
    "top_prediction": "melanocytic_nevus",
    "confidence": 0.7234,
    "model_name": "efficientnet_b4",
    "model_version": "isic-2024-v1"
  },
  "similar_images": [
    {
      "isic_id": "ISIC_0024306",
      "diagnosis": "melanocytic_nevus",
      "similarity_score": 0.9412,
      "image_url": "https://api.isic-archive.com/api/v2/images/ISIC_0024306/thumbnail",
      "metadata": { "age": 45, "sex": "male", "site": "back" }
    }
  ],
  "risk_assessment": {
    "risk_level": "low",
    "referral_urgency": "routine",
    "risk_factors": [],
    "malignant_probability": 0.1521
  }
}
```

**Error Responses:**
- `400` — Invalid image file (corrupt, wrong format, or too small)
- `422` — Image quality validation failed (blur, exposure). Body: `{"detail": "Image too blurry (score: 45.3, threshold: 100.0)."}`
- `503` — CDS service unavailable (circuit breaker open). Body: `{"detail": "CDS service unavailable", "cds_status": "circuit_open"}`

### GET `/api/lesions/history/{patient_id}`

Returns lesion classification history for a patient, ordered by most recent first.

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | 50 | Max results to return |

**Response (200):**
```json
[
  {
    "id": "uuid",
    "lesion_image_id": "uuid",
    "classified_at": "ISO 8601",
    "top_prediction": "melanocytic_nevus",
    "confidence": 0.7234,
    "risk_level": "low",
    "referral_urgency": "routine",
    "anatomical_site": "back",
    "model_version": "isic-2024-v1"
  }
]
```

### POST `/api/lesions/similar`

Find visually similar ISIC reference images for a dermoscopic image via pgvector cosine similarity (ADR-0011).

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image` | file | Yes | JPEG or PNG dermoscopic image |
| `top_k` | int | No | Number of results (default: 10, max: 50) |

**Response (200):**
```json
[
  {
    "isic_id": "ISIC_0024306",
    "diagnosis": "melanocytic_nevus",
    "similarity_score": 0.9412,
    "image_url": "https://api.isic-archive.com/api/v2/images/ISIC_0024306/thumbnail",
    "metadata": { "age": 45, "sex": "male", "site": "back" }
  }
]
```

### GET `/api/lesions/{lesion_id}/timeline`

Returns longitudinal timeline for a persistent lesion, including change detection scores (ADR-0019).

**Response (200):**
```json
{
  "lesion_id": "uuid",
  "patient_id": "uuid",
  "anatomical_site": "back",
  "status": "active",
  "assessments": [
    {
      "lesion_image_id": "uuid",
      "captured_at": "ISO 8601",
      "top_prediction": "melanocytic_nevus",
      "confidence": 0.7234,
      "risk_level": "low",
      "change_score": null
    },
    {
      "lesion_image_id": "uuid",
      "captured_at": "ISO 8601",
      "top_prediction": "melanocytic_nevus",
      "confidence": 0.6890,
      "risk_level": "medium",
      "change_score": 0.35
    }
  ]
}
```

### GET `/reports/dermatology`

Dermatology classification analytics report (SUB-RA-0008).

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `start_date` | date | 30 days ago | Report start date |
| `end_date` | date | today | Report end date |

**Response (200):**
```json
{
  "report": "dermatology",
  "period": { "start": "YYYY-MM-DD", "end": "YYYY-MM-DD" },
  "classification_volume": {
    "total": 142,
    "by_diagnosis": { "melanocytic_nevus": 68, "melanoma": 12, "basal_cell_carcinoma": 8 }
  },
  "risk_distribution": { "low": 98, "medium": 32, "high": 12 },
  "referral_trends": { "routine": 98, "expedited": 32, "urgent": 12 },
  "model_confidence": { "mean": 0.74, "median": 0.78, "p95": 0.93 }
}
```

---

## Dermatology CDS Service (Internal — :8090)

The `pms-derm-cds` service (ADR-0008) runs on port 8090 and is called by the PMS backend only. It is **not** exposed to clients directly.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | CDS service health check |
| POST | `/classify` | Classify a dermoscopic image |
| POST | `/similar` | Find similar ISIC reference images |

See [ISICArchive Setup Guide](../experiments/18-ISICArchive-PMS-Developer-Setup-Guide.md) for full CDS API details.

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
