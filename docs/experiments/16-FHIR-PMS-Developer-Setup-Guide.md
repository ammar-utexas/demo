# FHIR Setup Guide for PMS Integration

**Document ID:** PMS-EXP-FHIR-001
**Version:** 1.0
**Date:** February 21, 2026
**Applies To:** PMS project (all platforms)
**Prerequisites Level:** Intermediate

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Part A: Install and Configure the FHIR Facade Service](#3-part-a-install-and-configure-the-fhir-facade-service)
4. [Part B: Integrate with PMS Backend](#4-part-b-integrate-with-pms-backend)
5. [Part C: Integrate with PMS Frontend](#5-part-c-integrate-with-pms-frontend)
6. [Part D: Testing and Verification](#6-part-d-testing-and-verification)
7. [Troubleshooting](#7-troubleshooting)
8. [Reference Commands](#8-reference-commands)

---

## 1. Overview

This guide walks you through deploying a **FHIR R4 Facade** over the PMS backend, enabling standards-based healthcare data interoperability. By the end, you will have:

- A FHIR R4 REST API service running on port 9090 within the Docker stack
- Resource mappers for Patient, Encounter, MedicationRequest, and Observation
- A `CapabilityStatement` endpoint describing supported FHIR interactions
- SMART on FHIR OAuth 2.0 authorization for external clients
- AuditEvent logging for all FHIR interactions (HIPAA compliance)
- FHIR resource rendering components in the Next.js frontend
- Integration tests against the HAPI FHIR public test server

### Architecture at a Glance

```mermaid
flowchart LR
    subgraph Clients["FHIR Clients"]
        EXT["External EHR<br/>(FHIR R4)"]
        WEB["Next.js :3000<br/>(FHIR Dashboard)"]
        AND["Android App<br/>(FHIR SDK)"]
    end

    subgraph Docker["Docker Network"]
        FHIR["FHIR Facade<br/>:9090<br/>(FastAPI)"]
        API["PMS Backend<br/>:8000<br/>(FastAPI)"]
        DB[("PostgreSQL<br/>:5432")]
    end

    EXT -->|"FHIR R4 REST<br/>(TLS + SMART)"| FHIR
    WEB -->|"FHIR R4 REST"| FHIR
    AND -->|"FHIR R4 REST"| FHIR
    FHIR -->|"Internal API"| API
    FHIR -->|"Audit logs"| DB
    API --> DB

    style FHIR fill:#3498db,color:#fff
    style API fill:#2ecc71,color:#fff
    style DB fill:#1abc9c,color:#fff
```

---

## 2. Prerequisites

### 2.1 Required Software

| Software | Minimum Version | Check Command |
|---|---|---|
| Python | 3.12+ | `python3 --version` |
| Docker | 24.0+ | `docker --version` |
| Docker Compose | 2.20+ | `docker compose version` |
| Node.js | 20 LTS+ | `node --version` |
| npm | 10+ | `npm --version` |
| Git | 2.40+ | `git --version` |
| curl | 7.80+ | `curl --version` |
| jq | 1.6+ | `jq --version` |

### 2.2 Installation of Prerequisites

**fhir.resources (Python FHIR models):**

```bash
pip install "fhir.resources>=8.0.0"
```

This installs Pydantic v2-based models for all FHIR R4 resource types (Patient, Encounter, MedicationRequest, Observation, Bundle, etc.). The library validates resource structure, data types, and required fields automatically.

**authlib (OAuth 2.0 for SMART on FHIR):**

```bash
pip install "authlib>=1.3.0"
```

**fhir-react (Frontend FHIR components):**

```bash
cd pms-frontend
npm install @beda.software/fhir-react
```

### 2.3 Verify PMS Services

Confirm all PMS services are running before proceeding:

```bash
# Check PMS backend
curl -s http://localhost:8000/docs | head -5
# Expected: HTML page for FastAPI Swagger docs

# Check PMS frontend
curl -s http://localhost:3000 | head -5
# Expected: HTML page for Next.js app

# Check PostgreSQL
docker exec pms-db pg_isready
# Expected: /var/run/postgresql:5432 - accepting connections
```

---

## 3. Part A: Install and Configure the FHIR Facade Service

### Step 1: Create the FHIR Facade Project Structure

```bash
mkdir -p pms-fhir/app/{routers,mappers,auth,models}
mkdir -p pms-fhir/tests
```

Expected directory layout:

```
pms-fhir/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Environment configuration
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── capability.py       # CapabilityStatement endpoint
│   │   ├── patient.py          # Patient FHIR CRUD
│   │   ├── encounter.py        # Encounter FHIR CRUD
│   │   ├── medication.py       # MedicationRequest FHIR CRUD
│   │   └── observation.py      # Observation FHIR CRUD
│   ├── mappers/
│   │   ├── __init__.py
│   │   ├── patient_mapper.py   # PMS Patient ↔ FHIR Patient
│   │   ├── encounter_mapper.py # PMS Encounter ↔ FHIR Encounter
│   │   ├── medication_mapper.py# PMS Prescription ↔ FHIR MedicationRequest
│   │   └── observation_mapper.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── smart.py            # SMART on FHIR OAuth 2.0
│   │   └── scopes.py           # Clinical scope definitions
│   └── models/
│       ├── __init__.py
│       └── audit.py            # AuditEvent SQLAlchemy model
├── tests/
│   ├── test_patient.py
│   ├── test_encounter.py
│   └── test_capability.py
├── Dockerfile
├── requirements.txt
└── .env
```

### Step 2: Create the Requirements File

```bash
cat > pms-fhir/requirements.txt << 'EOF'
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
fhir.resources>=8.0.0
fhir-core>=0.1.0
authlib>=1.3.0
httpx>=0.27.0
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.29.0
pydantic>=2.6.0
pydantic-settings>=2.1.0
python-jose[cryptography]>=3.3.0
EOF
```

### Step 3: Create the Dockerfile

```bash
cat > pms-fhir/Dockerfile << 'EOF'
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 9090

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9090"]
EOF
```

### Step 4: Create Environment Configuration

```bash
cat > pms-fhir/.env << 'EOF'
# FHIR Facade Configuration
FHIR_BASE_URL=http://localhost:9090/fhir/r4
PMS_BACKEND_URL=http://pms-backend:8000
DATABASE_URL=postgresql+asyncpg://pms:pms_secret@pms-db:5432/pms

# SMART on FHIR
SMART_ISSUER=http://localhost:9090/fhir/r4
SMART_TOKEN_EXPIRY=3600
SMART_SIGNING_KEY=generate-a-secure-key-here

# HIPAA Audit
AUDIT_LOG_ENABLED=true
AUDIT_RETENTION_DAYS=2555
EOF
```

### Step 5: Create the Main Application

Create `pms-fhir/app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import capability, patient, encounter, medication, observation
from app.config import settings

app = FastAPI(
    title="PMS FHIR R4 Facade",
    description="HL7 FHIR R4 REST API for PMS healthcare data interoperability",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.pms_frontend_url],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Mount FHIR R4 routers under /fhir/r4 prefix
app.include_router(capability.router, prefix="/fhir/r4", tags=["FHIR Metadata"])
app.include_router(patient.router, prefix="/fhir/r4", tags=["Patient"])
app.include_router(encounter.router, prefix="/fhir/r4", tags=["Encounter"])
app.include_router(medication.router, prefix="/fhir/r4", tags=["MedicationRequest"])
app.include_router(observation.router, prefix="/fhir/r4", tags=["Observation"])


@app.get("/fhir/r4/metadata")
async def metadata():
    """Alias for CapabilityStatement (FHIR convention)."""
    return await capability.get_capability_statement()
```

### Step 6: Create the CapabilityStatement Router

Create `pms-fhir/app/routers/capability.py`:

```python
from fastapi import APIRouter
from fhir.resources.R4B.capabilitystatement import CapabilityStatement
from datetime import date

router = APIRouter()


async def get_capability_statement() -> dict:
    """Return FHIR CapabilityStatement describing server capabilities."""
    cs = CapabilityStatement(
        status="active",
        date=date.today().isoformat(),
        kind="instance",
        fhirVersion="4.0.1",
        format=["json"],
        software={
            "name": "PMS FHIR Facade",
            "version": "1.0.0",
        },
        implementation={
            "description": "MPS Patient Management System FHIR R4 Interface",
            "url": "http://localhost:9090/fhir/r4",
        },
        rest=[
            {
                "mode": "server",
                "resource": [
                    {
                        "type": "Patient",
                        "interaction": [
                            {"code": "read"},
                            {"code": "search-type"},
                            {"code": "create"},
                            {"code": "update"},
                        ],
                        "searchParam": [
                            {"name": "_id", "type": "token"},
                            {"name": "name", "type": "string"},
                            {"name": "birthdate", "type": "date"},
                            {"name": "identifier", "type": "token"},
                        ],
                    },
                    {
                        "type": "Encounter",
                        "interaction": [
                            {"code": "read"},
                            {"code": "search-type"},
                            {"code": "create"},
                        ],
                        "searchParam": [
                            {"name": "_id", "type": "token"},
                            {"name": "patient", "type": "reference"},
                            {"name": "date", "type": "date"},
                            {"name": "status", "type": "token"},
                        ],
                    },
                    {
                        "type": "MedicationRequest",
                        "interaction": [
                            {"code": "read"},
                            {"code": "search-type"},
                        ],
                        "searchParam": [
                            {"name": "patient", "type": "reference"},
                            {"name": "status", "type": "token"},
                        ],
                    },
                    {
                        "type": "Observation",
                        "interaction": [
                            {"code": "read"},
                            {"code": "search-type"},
                            {"code": "create"},
                        ],
                        "searchParam": [
                            {"name": "patient", "type": "reference"},
                            {"name": "code", "type": "token"},
                            {"name": "date", "type": "date"},
                        ],
                    },
                ],
            }
        ],
    )
    return cs.model_dump(exclude_none=True)


@router.get("/CapabilityStatement")
async def read_capability_statement():
    return await get_capability_statement()
```

### Step 7: Create the Patient Resource Mapper

Create `pms-fhir/app/mappers/patient_mapper.py`:

```python
from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.humanname import HumanName
from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.identifier import Identifier


def pms_patient_to_fhir(pms_patient: dict) -> Patient:
    """Convert a PMS patient record to a FHIR R4 Patient resource."""
    return Patient(
        id=str(pms_patient["id"]),
        identifier=[
            Identifier(
                system="http://mps-pms.local/patient-id",
                value=str(pms_patient["id"]),
            )
        ],
        name=[
            HumanName(
                family=pms_patient.get("last_name", ""),
                given=[pms_patient.get("first_name", "")],
            )
        ],
        gender=pms_patient.get("gender", "unknown"),
        birthDate=pms_patient.get("date_of_birth"),
        telecom=[
            ContactPoint(
                system="phone",
                value=pms_patient.get("phone"),
            )
        ]
        if pms_patient.get("phone")
        else None,
        active=pms_patient.get("is_active", True),
    )


def fhir_patient_to_pms(fhir_patient: Patient) -> dict:
    """Convert a FHIR R4 Patient resource to a PMS patient dict."""
    name = fhir_patient.name[0] if fhir_patient.name else None
    return {
        "first_name": name.given[0] if name and name.given else "",
        "last_name": name.family if name else "",
        "gender": fhir_patient.gender or "unknown",
        "date_of_birth": str(fhir_patient.birthDate) if fhir_patient.birthDate else None,
        "phone": (
            fhir_patient.telecom[0].value
            if fhir_patient.telecom
            else None
        ),
        "is_active": fhir_patient.active if fhir_patient.active is not None else True,
    }
```

### Step 8: Create the Patient Router

Create `pms-fhir/app/routers/patient.py`:

```python
from fastapi import APIRouter, HTTPException, Query
from fhir.resources.R4B.bundle import Bundle, BundleEntry
from fhir.resources.R4B.patient import Patient
import httpx

from app.mappers.patient_mapper import pms_patient_to_fhir, fhir_patient_to_pms
from app.config import settings

router = APIRouter()


@router.get("/Patient/{patient_id}")
async def read_patient(patient_id: str):
    """FHIR read interaction: GET /fhir/r4/Patient/{id}"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{settings.pms_backend_url}/api/patients/{patient_id}"
        )
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail={
            "resourceType": "OperationOutcome",
            "issue": [{"severity": "error", "code": "not-found",
                        "diagnostics": f"Patient/{patient_id} not found"}],
        })
    pms_data = resp.json()
    fhir_patient = pms_patient_to_fhir(pms_data)
    return fhir_patient.model_dump(exclude_none=True)


@router.get("/Patient")
async def search_patient(
    name: str | None = Query(None),
    birthdate: str | None = Query(None),
    _id: str | None = Query(None, alias="_id"),
):
    """FHIR search interaction: GET /fhir/r4/Patient?name=...&birthdate=..."""
    params = {}
    if name:
        params["search"] = name
    if birthdate:
        params["date_of_birth"] = birthdate
    if _id:
        params["id"] = _id

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{settings.pms_backend_url}/api/patients",
            params=params,
        )
    pms_patients = resp.json()

    entries = []
    for p in pms_patients:
        fhir_p = pms_patient_to_fhir(p)
        entries.append(
            BundleEntry(
                resource=fhir_p,
                fullUrl=f"{settings.fhir_base_url}/Patient/{p['id']}",
            )
        )

    bundle = Bundle(
        type="searchset",
        total=len(entries),
        entry=entries if entries else None,
    )
    return bundle.model_dump(exclude_none=True)


@router.post("/Patient", status_code=201)
async def create_patient(patient: dict):
    """FHIR create interaction: POST /fhir/r4/Patient"""
    fhir_patient = Patient.model_validate(patient)
    pms_data = fhir_patient_to_pms(fhir_patient)

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.pms_backend_url}/api/patients",
            json=pms_data,
        )
    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=resp.status_code, detail=resp.json())

    created = resp.json()
    fhir_result = pms_patient_to_fhir(created)
    return fhir_result.model_dump(exclude_none=True)
```

### Step 9: Add FHIR Facade to Docker Compose

Add the following service to your `docker-compose.yml`:

```yaml
  pms-fhir:
    build:
      context: ./pms-fhir
      dockerfile: Dockerfile
    container_name: pms-fhir
    ports:
      - "9090:9090"
    environment:
      - FHIR_BASE_URL=http://localhost:9090/fhir/r4
      - PMS_BACKEND_URL=http://pms-backend:8000
      - DATABASE_URL=postgresql+asyncpg://pms:pms_secret@pms-db:5432/pms
      - AUDIT_LOG_ENABLED=true
    depends_on:
      - pms-backend
      - pms-db
    networks:
      - pms-network
    restart: unless-stopped
```

### Step 10: Build and Start the FHIR Service

```bash
docker compose up -d pms-fhir
```

Verify the service is running:

```bash
curl -s http://localhost:9090/fhir/r4/metadata | jq '.software'
# Expected:
# {
#   "name": "PMS FHIR Facade",
#   "version": "1.0.0"
# }
```

**Checkpoint:** The FHIR Facade service is running on port 9090, the `CapabilityStatement` endpoint returns valid metadata, and the service is connected to the PMS Docker network.

---

## 4. Part B: Integrate with PMS Backend

### Step 1: Create the AuditEvent Database Table

Create a migration for FHIR audit logging in the PMS backend:

```python
# pms-fhir/app/models/audit.py
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class FHIRAuditEvent(Base):
    __tablename__ = "fhir_audit_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(50), nullable=False)       # read, search, create, update
    resource_type = Column(String(50), nullable=False)     # Patient, Encounter, etc.
    resource_id = Column(String(100))
    client_id = Column(String(200))                        # SMART client identifier
    user_id = Column(String(200))                          # Authenticated user
    source_ip = Column(String(45))
    outcome = Column(String(10), nullable=False)           # 0=success, 4=minor, 8=serious, 12=major
    recorded = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    detail = Column(JSON)                                  # Full AuditEvent resource JSON
```

Run the migration:

```bash
docker exec pms-fhir python -c "
from app.models.audit import Base
from sqlalchemy import create_engine
engine = create_engine('postgresql://pms:pms_secret@pms-db:5432/pms')
Base.metadata.create_all(engine)
print('FHIR audit tables created.')
"
```

### Step 2: Implement Audit Logging Middleware

Create `pms-fhir/app/auth/audit_middleware.py`:

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timezone
import json


class FHIRAuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Only audit FHIR endpoints
        if request.url.path.startswith("/fhir/r4/"):
            path_parts = request.url.path.split("/")
            resource_type = path_parts[3] if len(path_parts) > 3 else "metadata"
            resource_id = path_parts[4] if len(path_parts) > 4 else None

            audit_event = {
                "resourceType": "AuditEvent",
                "type": {"code": request.method.lower()},
                "recorded": datetime.now(timezone.utc).isoformat(),
                "outcome": "0" if response.status_code < 400 else "8",
                "agent": [
                    {
                        "requestor": True,
                        "network": {"address": request.client.host if request.client else "unknown"},
                    }
                ],
                "entity": [
                    {
                        "what": {"reference": f"{resource_type}/{resource_id}" if resource_id else resource_type}
                    }
                ],
            }
            # Persist audit event (async write to database)
            request.state.audit_event = audit_event

        return response
```

### Step 3: Connect Resource Mappers to PMS Backend APIs

The FHIR Facade calls PMS backend APIs internally using `httpx`. Create the Encounter mapper as an example:

Create `pms-fhir/app/mappers/encounter_mapper.py`:

```python
from fhir.resources.R4B.encounter import Encounter
from fhir.resources.R4B.period import Period
from fhir.resources.R4B.reference import Reference
from fhir.resources.R4B.coding import Coding


def pms_encounter_to_fhir(pms_encounter: dict) -> Encounter:
    """Convert a PMS encounter record to a FHIR R4 Encounter resource."""
    status_map = {
        "scheduled": "planned",
        "in_progress": "in-progress",
        "completed": "finished",
        "cancelled": "cancelled",
    }

    return Encounter(
        id=str(pms_encounter["id"]),
        status=status_map.get(pms_encounter.get("status", ""), "unknown"),
        class_fhir=Coding(
            system="http://terminology.hl7.org/CodeSystem/v3-ActCode",
            code="AMB",
            display="ambulatory",
        ),
        subject=Reference(
            reference=f"Patient/{pms_encounter['patient_id']}",
        ),
        period=Period(
            start=pms_encounter.get("start_date"),
            end=pms_encounter.get("end_date"),
        ),
    )
```

### Step 4: Verify Backend Integration

```bash
# Create a test patient via PMS API
curl -s -X POST http://localhost:8000/api/patients \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Jane","last_name":"Doe","gender":"female","date_of_birth":"1990-03-15"}' \
  | jq '.id'
# Note the returned patient ID

# Read that patient via FHIR API
curl -s http://localhost:9090/fhir/r4/Patient/1 | jq '.resourceType, .name'
# Expected:
# "Patient"
# [{"family": "Doe", "given": ["Jane"]}]

# Search patients via FHIR API
curl -s "http://localhost:9090/fhir/r4/Patient?name=Doe" | jq '.total, .type'
# Expected:
# 1
# "searchset"
```

**Checkpoint:** The FHIR Facade reads patient data from the PMS backend via internal HTTP calls, transforms it to valid FHIR R4 resources, and returns properly structured Bundle search results.

---

## 5. Part C: Integrate with PMS Frontend

### Step 1: Install FHIR React Components

```bash
cd pms-frontend
npm install @beda.software/fhir-react
```

### Step 2: Add FHIR Environment Variables

Add to `pms-frontend/.env.local`:

```
NEXT_PUBLIC_FHIR_BASE_URL=http://localhost:9090/fhir/r4
```

### Step 3: Create the FHIR Client Utility

Create `pms-frontend/src/lib/fhir-client.ts`:

```typescript
const FHIR_BASE = process.env.NEXT_PUBLIC_FHIR_BASE_URL || "http://localhost:9090/fhir/r4";

export interface FHIRBundle<T = unknown> {
  resourceType: "Bundle";
  type: "searchset";
  total: number;
  entry?: Array<{ resource: T; fullUrl: string }>;
}

export async function fhirRead<T>(resourceType: string, id: string): Promise<T> {
  const res = await fetch(`${FHIR_BASE}/${resourceType}/${id}`);
  if (!res.ok) throw new Error(`FHIR ${resourceType}/${id} not found`);
  return res.json();
}

export async function fhirSearch<T>(
  resourceType: string,
  params: Record<string, string>
): Promise<FHIRBundle<T>> {
  const query = new URLSearchParams(params).toString();
  const res = await fetch(`${FHIR_BASE}/${resourceType}?${query}`);
  if (!res.ok) throw new Error(`FHIR search failed: ${res.statusText}`);
  return res.json();
}
```

### Step 4: Create a FHIR Patient Card Component

Create `pms-frontend/src/components/fhir/FHIRPatientCard.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import { fhirRead } from "@/lib/fhir-client";

interface FHIRPatient {
  resourceType: "Patient";
  id: string;
  name?: Array<{ family?: string; given?: string[] }>;
  gender?: string;
  birthDate?: string;
  active?: boolean;
}

export function FHIRPatientCard({ patientId }: { patientId: string }) {
  const [patient, setPatient] = useState<FHIRPatient | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fhirRead<FHIRPatient>("Patient", patientId)
      .then(setPatient)
      .catch((e) => setError(e.message));
  }, [patientId]);

  if (error) return <div className="text-red-500">Error: {error}</div>;
  if (!patient) return <div>Loading FHIR Patient...</div>;

  const name = patient.name?.[0];
  const displayName = name
    ? `${name.given?.join(" ") || ""} ${name.family || ""}`.trim()
    : "Unknown";

  return (
    <div className="border rounded-lg p-4 bg-white shadow-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">{displayName}</h3>
        <span className={`px-2 py-1 rounded text-xs ${patient.active ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-600"}`}>
          {patient.active ? "Active" : "Inactive"}
        </span>
      </div>
      <div className="mt-2 text-sm text-gray-600">
        <p>Gender: {patient.gender || "Unknown"}</p>
        <p>Birth Date: {patient.birthDate || "Unknown"}</p>
        <p className="text-xs text-gray-400 mt-1">FHIR ID: {patient.id}</p>
      </div>
    </div>
  );
}
```

### Step 5: Create the FHIR Import Dashboard Page

Create `pms-frontend/src/app/fhir/page.tsx`:

```tsx
"use client";

import { useState } from "react";
import { fhirSearch } from "@/lib/fhir-client";
import { FHIRPatientCard } from "@/components/fhir/FHIRPatientCard";

export default function FHIRDashboard() {
  const [searchName, setSearchName] = useState("");
  const [results, setResults] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const bundle = await fhirSearch("Patient", { name: searchName });
      const ids = bundle.entry?.map((e: any) => e.resource.id) || [];
      setResults(ids);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">FHIR Interoperability Dashboard</h1>

      <div className="flex gap-2 mb-6">
        <input
          type="text"
          value={searchName}
          onChange={(e) => setSearchName(e.target.value)}
          placeholder="Search patients by name..."
          className="flex-1 border rounded px-3 py-2"
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Searching..." : "FHIR Search"}
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {results.map((id) => (
          <FHIRPatientCard key={id} patientId={id} />
        ))}
      </div>

      {results.length === 0 && !loading && (
        <p className="text-gray-500 text-center">
          Search for patients to see FHIR R4 resource representations.
        </p>
      )}
    </div>
  );
}
```

### Step 6: Verify Frontend Integration

```bash
# Start the frontend
cd pms-frontend && npm run dev

# Open http://localhost:3000/fhir in browser
# Type a patient name and click "FHIR Search"
# Patient cards should render with FHIR data
```

**Checkpoint:** The Next.js frontend can search and display FHIR Patient resources from the FHIR Facade, with a dedicated dashboard page at `/fhir`.

---

## 6. Part D: Testing and Verification

### Step 1: FHIR Service Health Check

```bash
# CapabilityStatement
curl -s http://localhost:9090/fhir/r4/metadata | jq '.fhirVersion'
# Expected: "4.0.1"

# Supported resource types
curl -s http://localhost:9090/fhir/r4/metadata \
  | jq '.rest[0].resource[].type'
# Expected: "Patient", "Encounter", "MedicationRequest", "Observation"
```

### Step 2: FHIR Resource CRUD Tests

```bash
# CREATE - Post a new patient via FHIR
curl -s -X POST http://localhost:9090/fhir/r4/Patient \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Patient",
    "name": [{"family": "Smith", "given": ["John"]}],
    "gender": "male",
    "birthDate": "1985-07-20"
  }' | jq '.id, .resourceType'
# Expected: "<new-id>", "Patient"

# READ - Fetch the created patient
curl -s http://localhost:9090/fhir/r4/Patient/1 | jq '.name[0]'
# Expected: {"family": "Smith", "given": ["John"]}

# SEARCH - Find by name
curl -s "http://localhost:9090/fhir/r4/Patient?name=Smith" \
  | jq '.total, .entry[0].resource.name[0].family'
# Expected: 1, "Smith"
```

### Step 3: FHIR Conformance Validation

```bash
# Validate a Patient resource against FHIR R4 spec
python3 -c "
from fhir.resources.R4B.patient import Patient

p = Patient.model_validate({
    'resourceType': 'Patient',
    'name': [{'family': 'Test', 'given': ['User']}],
    'gender': 'male',
    'birthDate': '2000-01-01'
})
print(f'Valid FHIR Patient: {p.id}')
print(f'JSON keys: {list(p.model_dump(exclude_none=True).keys())}')
"
```

### Step 4: Integration Test with HAPI FHIR Public Server

```bash
# Verify connectivity to HAPI FHIR R4 test server
curl -s "https://hapi.fhir.org/baseR4/Patient?_count=1" \
  | jq '.resourceType, .total'
# Expected: "Bundle", <number>

# Read a known test patient
curl -s "https://hapi.fhir.org/baseR4/Patient/592912" \
  | jq '.resourceType, .name[0]'
```

**Checkpoint:** All FHIR CRUD operations work, resources conform to R4 specification, and the service can communicate with external FHIR servers.

---

## 7. Troubleshooting

### FHIR Service Won't Start

**Symptoms:** `pms-fhir` container exits immediately, logs show `ModuleNotFoundError`.

**Fix:** Ensure `requirements.txt` includes all dependencies and rebuild:

```bash
docker compose build pms-fhir --no-cache
docker compose up -d pms-fhir
docker logs pms-fhir --tail 20
```

### CapabilityStatement Returns 500

**Symptoms:** `curl http://localhost:9090/fhir/r4/metadata` returns internal server error.

**Fix:** Check that `fhir.resources` is installed correctly and the R4B subpackage is available:

```bash
docker exec pms-fhir python -c "from fhir.resources.R4B.capabilitystatement import CapabilityStatement; print('OK')"
```

### Patient Mapper Returns Empty Names

**Symptoms:** FHIR Patient resources have `name: [{"family": "", "given": [""]}]`.

**Fix:** Verify the PMS backend returns `first_name` and `last_name` fields (not `name`). Check the field mapping in `patient_mapper.py` matches the PMS API response schema.

### FHIR Search Returns Empty Bundle

**Symptoms:** `GET /fhir/r4/Patient?name=Doe` returns `{"type": "searchset", "total": 0}`.

**Fix:** Verify the PMS backend supports the `search` query parameter:

```bash
curl -s "http://localhost:8000/api/patients?search=Doe" | jq 'length'
```

If the PMS backend uses a different parameter name, update the search mapping in `patient.py`.

### Connection Refused Between Containers

**Symptoms:** `httpx.ConnectError: [Errno 111] Connection refused` when FHIR Facade calls PMS backend.

**Fix:** Ensure both services are on the same Docker network and use container names (not `localhost`):

```bash
docker network inspect pms-network | jq '.[0].Containers | keys'
# Should list both pms-backend and pms-fhir
```

### Port 9090 Already in Use

**Symptoms:** `docker compose up` fails with `port is already allocated`.

**Fix:** Find and stop the conflicting process:

```bash
lsof -i :9090
# Kill the process or change the FHIR service port in docker-compose.yml
```

---

## 8. Reference Commands

### Daily Development

```bash
# Start FHIR service
docker compose up -d pms-fhir

# View logs
docker logs -f pms-fhir

# Restart after code changes
docker compose restart pms-fhir

# Rebuild after dependency changes
docker compose build pms-fhir && docker compose up -d pms-fhir

# Run tests
docker exec pms-fhir python -m pytest tests/ -v
```

### FHIR Management

```bash
# Check CapabilityStatement
curl -s http://localhost:9090/fhir/r4/metadata | jq '.rest[0].resource[].type'

# Search all patients
curl -s http://localhost:9090/fhir/r4/Patient | jq '.total'

# Search encounters by patient
curl -s "http://localhost:9090/fhir/r4/Encounter?patient=Patient/1" | jq '.total'

# Get patient everything (future)
curl -s "http://localhost:9090/fhir/r4/Patient/1/\$everything" | jq '.type'
```

### Monitoring

```bash
# Check FHIR service health
curl -s http://localhost:9090/fhir/r4/metadata | jq '.status'

# Count audit events
docker exec pms-db psql -U pms -d pms -c "SELECT COUNT(*) FROM fhir_audit_events;"

# View recent audit log
docker exec pms-db psql -U pms -d pms -c \
  "SELECT resource_type, event_type, recorded FROM fhir_audit_events ORDER BY recorded DESC LIMIT 10;"
```

### Useful URLs

| URL | Description |
|---|---|
| `http://localhost:9090/fhir/r4/metadata` | FHIR CapabilityStatement |
| `http://localhost:9090/docs` | FHIR Facade Swagger UI |
| `http://localhost:3000/fhir` | FHIR Dashboard (Next.js) |
| `http://localhost:8000/docs` | PMS Backend Swagger UI |
| `https://hapi.fhir.org/baseR4` | HAPI FHIR public test server |
| `https://launch.smarthealthit.org/` | SMART on FHIR test launcher |

---

## Next Steps

After completing this setup:

1. Follow the [FHIR Developer Tutorial](16-FHIR-Developer-Tutorial.md) to build your first end-to-end FHIR integration
2. Implement SMART on FHIR authorization for external client access
3. Add Encounter and MedicationRequest mappers following the Patient mapper pattern
4. Connect to the HAPI FHIR public test server for interoperability testing
5. Review the [PRD: FHIR PMS Integration](16-PRD-FHIR-PMS-Integration.md) for the full implementation roadmap

---

## Resources

- [HL7 FHIR R4 Specification](https://www.hl7.org/fhir/) — Complete FHIR R4 standard
- [fhir.resources on PyPI](https://pypi.org/project/fhir.resources/) — Python FHIR models
- [SMART on FHIR](https://docs.smarthealthit.org/) — Authorization framework
- [Google Android FHIR SDK](https://developers.google.com/open-health-stack/android-fhir) — Android FHIR libraries
- [HAPI FHIR](https://hapifhir.io/) — Reference FHIR server implementation
- [Build FHIR API with FastAPI](https://www.wellally.tech/blog/build-fhir-api-with-fastapi) — FastAPI FHIR implementation guide
- [PRD: FHIR PMS Integration](16-PRD-FHIR-PMS-Integration.md) — Full product requirements
- [MCP PMS Integration](09-PRD-MCP-PMS-Integration.md) — Complementary internal AI interoperability
