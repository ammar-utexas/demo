# RingCentral API Setup Guide for PMS Integration

**Document ID:** PMS-EXP-RINGCENTRALAPI-001
**Version:** 1.0
**Date:** 2026-03-10
**Applies To:** PMS project (all platforms)
**Prerequisites Level:** Intermediate

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Part A: RingCentral Account Setup and OAuth Configuration](#3-part-a-ringcentral-account-setup-and-oauth-configuration)
4. [Part B: Integrate with PMS Backend](#4-part-b-integrate-with-pms-backend)
5. [Part C: Integrate with PMS Frontend](#5-part-c-integrate-with-pms-frontend)
6. [Part D: Testing and Verification](#6-part-d-testing-and-verification)
7. [Troubleshooting](#7-troubleshooting)
8. [Reference Commands](#8-reference-commands)

---

## 1. Overview

This guide walks you through connecting RingCentral's REST API to the PMS backend (FastAPI), frontend (Next.js), and Android app. By the end, you will have:

- A RingCentral sandbox account with OAuth 2.0 credentials
- A `RingCentralClient` Python SDK wrapper integrated into FastAPI
- A `CommsService` FastAPI router with SMS, voice, fax, and video endpoints
- Webhook subscriptions receiving inbound call and SMS events
- A `CallerIDResolver` matching phone numbers to patient records
- A `ReminderScheduler` sending automated appointment SMS reminders
- A Next.js Communications Dashboard with call log, SMS compose, and fax inbox
- HIPAA audit logging for all communication operations

```mermaid
flowchart LR
    subgraph DEV["Developer Machine"]
        CODE["PMS Backend\nFastAPI :8000"]
        FRONT["PMS Frontend\nNext.js :3000"]
        PG[(PostgreSQL\n:5432)]
        RD["Redis\n:6379"]
        NGROK["ngrok\nWebhook Tunnel"]
    end

    subgraph RC["RingCentral Cloud"]
        API["REST API v1.0\nplatform.ringcentral.com"]
        SANDBOX["Sandbox\nplatform.devtest.ringcentral.com"]
        CONSOLE["Developer Console\ndevelopers.ringcentral.com"]
    end

    CODE -->|"HTTPS REST"| SANDBOX
    SANDBOX -->|"Webhook POST"| NGROK
    NGROK -->|"Forward"| CODE
    CODE --> PG
    CODE --> RD
    FRONT -->|"REST"| CODE

    style CODE fill:#4A90D9,color:#fff
    style FRONT fill:#4A90D9,color:#fff
    style PG fill:#2E7D32,color:#fff
    style RD fill:#D32F2F,color:#fff
    style NGROK fill:#7B1FA2,color:#fff
    style API fill:#FF6F00,color:#fff
    style SANDBOX fill:#FF6F00,color:#fff
    style CONSOLE fill:#FF6F00,color:#fff
```

## 2. Prerequisites

### 2.1 Required Software

| Software | Minimum Version | Check Command |
|---|---|---|
| Python | 3.11+ | `python --version` |
| Node.js | 18+ | `node --version` |
| PostgreSQL | 15+ | `psql --version` |
| Redis | 7+ | `redis-cli --version` |
| Docker | 24+ | `docker --version` |
| ngrok | 3+ | `ngrok --version` |
| Git | 2.40+ | `git --version` |

### 2.2 Installation of Prerequisites

```bash
# Install RingCentral Python SDK
pip install ringcentral pydantic apscheduler

# Install ngrok (macOS)
brew install ngrok

# Verify installations
python -c "from ringcentral import SDK; print('RingCentral SDK loaded')"
ngrok --version
```

### 2.3 Verify PMS Services

```bash
# Check FastAPI backend
curl -s http://localhost:8000/docs | head -5
# Expected: HTML for Swagger UI

# Check PostgreSQL
psql -U pms_user -d pms_db -c "SELECT 1;"
# Expected: 1

# Check Redis
redis-cli ping
# Expected: PONG

# Check Next.js frontend
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
# Expected: 200
```

## 3. Part A: RingCentral Account Setup and OAuth Configuration

### Step 1: Create RingCentral Developer Account

1. Navigate to [https://developers.ringcentral.com/](https://developers.ringcentral.com/)
2. Click **Create Free Account** or sign in with existing RingCentral credentials
3. This creates both a Developer Console account and a sandbox environment

### Step 2: Create an Application in Developer Console

1. In the [Developer Console](https://developers.ringcentral.com/my-account.html), click **Create App**
2. Configure the application:

| Setting | Value |
|---|---|
| App Name | `PMS Communications` |
| App Type | `REST API App` |
| Platform Type | `Server/Bot` (for backend JWT auth) |
| Permissions | Read Accounts, Read Call Log, Read Messages, Send Messages, Read Presence, RingOut, Fax, Video, Webhook Subscriptions |

3. Note the generated **Client ID** and **Client Secret**

### Step 3: Generate JWT Credentials

For server-to-server authentication (no user interaction):

1. In Developer Console → Your App → **Credentials** tab
2. Under **JWT Credentials**, click **Generate JWT**
3. Copy the JWT token — this is used for backend authentication

### Step 4: Configure Environment Variables

```bash
# .env (DO NOT commit this file)
RC_CLIENT_ID=your-client-id
RC_CLIENT_SECRET=your-client-secret
RC_JWT_TOKEN=your-jwt-token
RC_SERVER_URL=https://platform.devtest.ringcentral.com  # Sandbox
# RC_SERVER_URL=https://platform.ringcentral.com  # Production
RC_WEBHOOK_URL=https://your-ngrok-url.ngrok-free.app/api/comms/webhooks/ringcentral
```

For Docker deployments:

```bash
echo "your-client-id" | docker secret create rc_client_id -
echo "your-client-secret" | docker secret create rc_client_secret -
echo "your-jwt-token" | docker secret create rc_jwt_token -
```

### Step 5: Start ngrok Webhook Tunnel

```bash
# Start ngrok tunnel for webhook development
ngrok http 8000

# Note the HTTPS URL, e.g.: https://abc123.ngrok-free.app
# Update RC_WEBHOOK_URL in .env with this URL + /api/comms/webhooks/ringcentral
```

### Step 6: Verify Sandbox Access

```python
# test_rc_connection.py
from ringcentral import SDK

sdk = SDK(
    client_id="your-client-id",
    client_secret="your-client-secret",
    server="https://platform.devtest.ringcentral.com"
)
platform = sdk.platform()
platform.login(jwt="your-jwt-token")

# Get account info
response = platform.get("/restapi/v1.0/account/~/extension/~")
print(response.json()["name"])
# Expected: Your sandbox extension name
```

**Checkpoint**: You have a RingCentral developer account, a REST API app with JWT credentials, environment variables configured, ngrok tunnel running, and successful sandbox API connectivity verified.

## 4. Part B: Integrate with PMS Backend

### Step 1: Create PostgreSQL Schema

```sql
-- migrations/comms_tables.sql

-- Call log linked to patient records
CREATE TABLE comms_call_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ringcentral_call_id VARCHAR(100) UNIQUE,
    patient_id UUID REFERENCES patients(id),
    encounter_id UUID REFERENCES encounters(id),
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('inbound', 'outbound')),
    from_number VARCHAR(20) NOT NULL,
    to_number VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    duration_seconds INT DEFAULT 0,
    recording_url TEXT,
    recording_data BYTEA, -- AES-256-GCM encrypted local copy
    call_notes TEXT,
    consent_recorded BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    created_by UUID REFERENCES users(id)
);

-- SMS message log
CREATE TABLE comms_sms_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ringcentral_message_id VARCHAR(100),
    patient_id UUID REFERENCES patients(id),
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('inbound', 'outbound')),
    from_number VARCHAR(20) NOT NULL,
    to_number VARCHAR(20) NOT NULL,
    message_text TEXT NOT NULL,
    message_type VARCHAR(10) DEFAULT 'sms' CHECK (message_type IN ('sms', 'mms')),
    delivery_status VARCHAR(20),
    template_id VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Inbound fax queue
CREATE TABLE comms_fax_inbox (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ringcentral_message_id VARCHAR(100) UNIQUE,
    from_number VARCHAR(20),
    to_number VARCHAR(20),
    page_count INT,
    fax_document BYTEA, -- AES-256-GCM encrypted PDF
    patient_id UUID REFERENCES patients(id), -- NULL until matched
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'matched', 'filed', 'rejected')),
    matched_by UUID REFERENCES users(id),
    received_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- Patient communication preferences
CREATE TABLE patient_comms_preferences (
    patient_id UUID PRIMARY KEY REFERENCES patients(id),
    sms_opt_in BOOLEAN DEFAULT TRUE,
    sms_reminder_opt_in BOOLEAN DEFAULT TRUE,
    preferred_phone VARCHAR(20),
    preferred_contact_time VARCHAR(20) DEFAULT 'any',
    language VARCHAR(10) DEFAULT 'en',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- HIPAA audit log for communications
CREATE TABLE comms_audit_log (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    user_id UUID,
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(30) NOT NULL,
    resource_id VARCHAR(100),
    patient_id UUID,
    request_summary JSONB,
    response_status INT,
    ip_address INET
);

-- Indexes
CREATE INDEX idx_comms_call_patient ON comms_call_log(patient_id);
CREATE INDEX idx_comms_call_number ON comms_call_log(from_number);
CREATE INDEX idx_comms_sms_patient ON comms_sms_log(patient_id);
CREATE INDEX idx_comms_fax_status ON comms_fax_inbox(status);
CREATE INDEX idx_comms_audit_timestamp ON comms_audit_log(timestamp);
CREATE INDEX idx_comms_audit_patient ON comms_audit_log(patient_id);
```

### Step 2: RingCentral Client Wrapper

```python
# app/services/ringcentral_client.py

from ringcentral import SDK
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.core.config import settings
import json


class SMSMessage(BaseModel):
    message_id: str
    from_number: str
    to_number: str
    text: str
    delivery_status: str
    created_at: datetime


class CallSession(BaseModel):
    session_id: str
    from_number: str
    to_number: str
    status: str
    direction: str


class FaxMessage(BaseModel):
    message_id: str
    from_number: str
    to_number: str
    page_count: int
    status: str


class RingCentralClient:
    """Wrapper around RingCentral Python SDK with PMS-specific methods."""

    def __init__(self):
        self.sdk = SDK(
            client_id=settings.RC_CLIENT_ID,
            client_secret=settings.RC_CLIENT_SECRET,
            server=settings.RC_SERVER_URL,
        )
        self.platform = self.sdk.platform()
        self._authenticated = False

    def _ensure_auth(self):
        """Authenticate if not already authenticated or token expired."""
        if not self._authenticated or not self.platform.logged_in():
            self.platform.login(jwt=settings.RC_JWT_TOKEN)
            self._authenticated = True

    def send_sms(self, from_number: str, to_number: str, text: str) -> SMSMessage:
        """Send an SMS message to a patient."""
        self._ensure_auth()
        response = self.platform.post(
            "/restapi/v1.0/account/~/extension/~/sms",
            {
                "from": {"phoneNumber": from_number},
                "to": [{"phoneNumber": to_number}],
                "text": text,
            },
        )
        data = response.json()
        return SMSMessage(
            message_id=str(data["id"]),
            from_number=from_number,
            to_number=to_number,
            text=text,
            delivery_status=data.get("messageStatus", "Queued"),
            created_at=datetime.utcnow(),
        )

    def initiate_call(self, from_number: str, to_number: str) -> CallSession:
        """Initiate an outbound call via RingOut."""
        self._ensure_auth()
        response = self.platform.post(
            "/restapi/v1.0/account/~/extension/~/ring-out",
            {
                "from": {"phoneNumber": from_number},
                "to": {"phoneNumber": to_number},
                "playPrompt": True,  # Play "Please hold" prompt
            },
        )
        data = response.json()
        return CallSession(
            session_id=str(data["id"]),
            from_number=from_number,
            to_number=to_number,
            status=data["status"]["callStatus"],
            direction="outbound",
        )

    def send_fax(
        self, to_number: str, pdf_bytes: bytes, cover_text: str = ""
    ) -> FaxMessage:
        """Send a fax document (PDF) to a referral source."""
        self._ensure_auth()
        # Multipart request: JSON metadata + PDF attachment
        body = {
            "to": [{"phoneNumber": to_number}],
            "faxResolution": "High",
            "coverPageText": cover_text,
        }
        attachment = ("document.pdf", pdf_bytes, "application/pdf")
        response = self.platform.post(
            "/restapi/v1.0/account/~/extension/~/fax",
            body,
            files=[attachment],
        )
        data = response.json()
        return FaxMessage(
            message_id=str(data["id"]),
            from_number=data.get("from", {}).get("phoneNumber", ""),
            to_number=to_number,
            page_count=data.get("pgCnt", 0),
            status=data.get("messageStatus", "Queued"),
        )

    def create_video_meeting(self, topic: str) -> dict:
        """Create a RingCentral Video meeting for a telehealth visit."""
        self._ensure_auth()
        response = self.platform.post(
            "/restapi/v1.0/account/~/extension/~/video/conference",
            {"name": topic, "type": "Scheduled"},
        )
        data = response.json()
        return {
            "meeting_id": data.get("id"),
            "join_url": data.get("joinUri") or data.get("session", {}).get("joinUri"),
            "host_url": data.get("hostUri"),
            "topic": topic,
        }

    def get_call_log(
        self, date_from: str = None, date_to: str = None, per_page: int = 100
    ) -> list[dict]:
        """Retrieve call log records."""
        self._ensure_auth()
        params = {"perPage": per_page, "view": "Detailed"}
        if date_from:
            params["dateFrom"] = date_from
        if date_to:
            params["dateTo"] = date_to
        response = self.platform.get(
            "/restapi/v1.0/account/~/extension/~/call-log", params
        )
        return response.json().get("records", [])

    def get_recording(self, recording_id: str) -> bytes:
        """Download a call recording as audio data."""
        self._ensure_auth()
        response = self.platform.get(
            f"/restapi/v1.0/account/~/recording/{recording_id}/content"
        )
        return response.response().content

    def subscribe_webhook(self, webhook_url: str, event_filters: list[str]) -> dict:
        """Create a webhook subscription for real-time events."""
        self._ensure_auth()
        response = self.platform.post(
            "/restapi/v1.0/subscription",
            {
                "eventFilters": event_filters,
                "deliveryMode": {
                    "transportType": "WebHook",
                    "address": webhook_url,
                },
                "expiresIn": 604800,  # 7 days
            },
        )
        return response.json()

    def get_sms_history(self, phone_number: str = None, per_page: int = 50) -> list[dict]:
        """Retrieve SMS message history."""
        self._ensure_auth()
        params = {"messageType": "SMS", "perPage": per_page}
        if phone_number:
            params["phoneNumber"] = phone_number
        response = self.platform.get(
            "/restapi/v1.0/account/~/extension/~/message-store", params
        )
        return response.json().get("records", [])
```

### Step 3: CallerID Resolver

```python
# app/services/caller_id_resolver.py

from app.db.session import get_db
import redis.asyncio as redis
from app.core.config import settings
import json


class CallerIDResolver:
    """Match incoming phone numbers to PMS patient records."""

    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)
        self.cache_ttl = 300  # 5 minutes

    async def resolve(self, phone_number: str, db) -> dict | None:
        """
        Look up a phone number and return patient info.
        Checks Redis cache first, then PostgreSQL.
        """
        # Normalize phone number (strip country code formatting)
        normalized = phone_number.replace("+1", "").replace("-", "").replace(" ", "")
        if len(normalized) == 10:
            normalized = f"+1{normalized}"

        # Check Redis cache
        cache_key = f"caller_id:{normalized}"
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)

        # Query PostgreSQL for patient with matching phone
        result = await db.execute(
            """SELECT id, first_name, last_name, phone, mrn,
                      date_of_birth
               FROM patients
               WHERE phone = $1 OR mobile_phone = $1
               LIMIT 1""",
            [normalized],
        )
        row = result.first()

        if not row:
            return None

        patient_info = {
            "patient_id": str(row.id),
            "name": f"{row.first_name} {row.last_name}",
            "mrn": row.mrn,
            "phone": normalized,
            "dob": str(row.date_of_birth) if row.date_of_birth else None,
        }

        # Cache result
        await self.redis.set(cache_key, json.dumps(patient_info), ex=self.cache_ttl)

        return patient_info

    async def close(self):
        await self.redis.close()
```

### Step 4: CommsService FastAPI Router

```python
# app/api/routes/comms.py

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.services.ringcentral_client import RingCentralClient
from app.services.caller_id_resolver import CallerIDResolver
from app.services.comms_audit import log_comms_action
from app.db.session import get_db
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/comms", tags=["communications"])


class SendSMSRequest(BaseModel):
    patient_id: str
    to_number: str
    message_text: str
    template_id: Optional[str] = None


class InitiateCallRequest(BaseModel):
    patient_id: Optional[str] = None
    to_number: str
    from_number: str


class SendFaxRequest(BaseModel):
    to_number: str
    document_base64: str  # Base64-encoded PDF
    cover_text: Optional[str] = ""
    patient_id: Optional[str] = None


class CreateVideoMeetingRequest(BaseModel):
    patient_id: str
    encounter_id: Optional[str] = None
    topic: str = "Telehealth Visit"


# --- SMS Endpoints ---

@router.post("/sms")
async def send_sms(
    request: SendSMSRequest,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Send an SMS message to a patient."""
    # Check patient opt-in
    prefs = await db.execute(
        "SELECT sms_opt_in FROM patient_comms_preferences WHERE patient_id = $1",
        [request.patient_id],
    )
    pref_row = prefs.first()
    if pref_row and not pref_row.sms_opt_in:
        raise HTTPException(status_code=403, detail="Patient has opted out of SMS")

    client = RingCentralClient()
    result = client.send_sms(
        from_number="+1YOUR_RC_NUMBER",  # Configured in env
        to_number=request.to_number,
        text=request.message_text,
    )

    # Log to database
    await db.execute(
        """INSERT INTO comms_sms_log
           (ringcentral_message_id, patient_id, direction, from_number,
            to_number, message_text, delivery_status, template_id)
           VALUES ($1,$2,$3,$4,$5,$6,$7,$8)""",
        [
            result.message_id, request.patient_id, "outbound",
            result.from_number, result.to_number, request.message_text,
            result.delivery_status, request.template_id,
        ],
    )

    await log_comms_action(
        db=db, user_id=current_user.id, action="send_sms",
        resource_type="sms", resource_id=result.message_id,
        patient_id=request.patient_id,
    )
    await db.commit()

    return {"message_id": result.message_id, "status": result.delivery_status}


@router.get("/sms/history/{patient_id}")
async def get_sms_history(
    patient_id: str,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get SMS conversation history for a patient."""
    result = await db.execute(
        """SELECT direction, from_number, to_number, message_text,
                  delivery_status, created_at
           FROM comms_sms_log
           WHERE patient_id = $1
           ORDER BY created_at DESC
           LIMIT 50""",
        [patient_id],
    )
    rows = result.fetchall()
    return {
        "patient_id": patient_id,
        "messages": [
            {
                "direction": r.direction,
                "from": r.from_number,
                "to": r.to_number,
                "text": r.message_text,
                "status": r.delivery_status,
                "timestamp": r.created_at.isoformat(),
            }
            for r in rows
        ],
    }


# --- Voice Endpoints ---

@router.post("/call")
async def initiate_call(
    request: InitiateCallRequest,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Initiate an outbound call via RingOut."""
    client = RingCentralClient()
    result = client.initiate_call(
        from_number=request.from_number,
        to_number=request.to_number,
    )

    await db.execute(
        """INSERT INTO comms_call_log
           (ringcentral_call_id, patient_id, direction, from_number,
            to_number, status, created_by)
           VALUES ($1,$2,$3,$4,$5,$6,$7)""",
        [
            result.session_id, request.patient_id, "outbound",
            request.from_number, request.to_number, result.status,
            current_user.id,
        ],
    )

    await log_comms_action(
        db=db, user_id=current_user.id, action="initiate_call",
        resource_type="call", resource_id=result.session_id,
        patient_id=request.patient_id,
    )
    await db.commit()

    return {"session_id": result.session_id, "status": result.status}


@router.get("/calls/log")
async def get_call_log(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user=Depends(get_current_user),
):
    """Get call history from RingCentral."""
    client = RingCentralClient()
    records = client.get_call_log(date_from=date_from, date_to=date_to)
    return {"records": records}


@router.get("/calls/{call_id}/recording")
async def get_call_recording(
    call_id: str,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Download a call recording."""
    # Look up recording URL from local log
    result = await db.execute(
        "SELECT recording_url FROM comms_call_log WHERE ringcentral_call_id = $1",
        [call_id],
    )
    row = result.first()
    if not row or not row.recording_url:
        raise HTTPException(status_code=404, detail="Recording not found")

    client = RingCentralClient()
    recording_data = client.get_recording(call_id)

    await log_comms_action(
        db=db, user_id=current_user.id, action="access_recording",
        resource_type="recording", resource_id=call_id,
    )
    await db.commit()

    from fastapi.responses import Response
    return Response(content=recording_data, media_type="audio/mpeg")


# --- Fax Endpoints ---

@router.post("/fax")
async def send_fax(
    request: SendFaxRequest,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Send a fax document to a referral source."""
    import base64
    pdf_bytes = base64.b64decode(request.document_base64)

    client = RingCentralClient()
    result = client.send_fax(
        to_number=request.to_number,
        pdf_bytes=pdf_bytes,
        cover_text=request.cover_text or "",
    )

    await log_comms_action(
        db=db, user_id=current_user.id, action="send_fax",
        resource_type="fax", resource_id=result.message_id,
        patient_id=request.patient_id,
    )
    await db.commit()

    return {
        "message_id": result.message_id,
        "page_count": result.page_count,
        "status": result.status,
    }


@router.get("/fax/inbox")
async def get_fax_inbox(
    status: Optional[str] = "pending",
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List inbound faxes in the queue."""
    result = await db.execute(
        """SELECT id, from_number, page_count, patient_id, status, received_at
           FROM comms_fax_inbox
           WHERE status = $1
           ORDER BY received_at DESC
           LIMIT 50""",
        [status],
    )
    rows = result.fetchall()
    return {
        "faxes": [
            {
                "id": str(r.id),
                "from_number": r.from_number,
                "page_count": r.page_count,
                "patient_id": str(r.patient_id) if r.patient_id else None,
                "status": r.status,
                "received_at": r.received_at.isoformat(),
            }
            for r in rows
        ]
    }


# --- Video Endpoints ---

@router.post("/video/meeting")
async def create_video_meeting(
    request: CreateVideoMeetingRequest,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a telehealth video meeting."""
    client = RingCentralClient()
    meeting = client.create_video_meeting(topic=request.topic)

    await log_comms_action(
        db=db, user_id=current_user.id, action="create_video_meeting",
        resource_type="video", resource_id=meeting.get("meeting_id"),
        patient_id=request.patient_id,
    )
    await db.commit()

    return meeting


# --- Webhook Endpoint ---

@router.post("/webhooks/ringcentral")
async def ringcentral_webhook(request: Request, db=Depends(get_db)):
    """Receive webhook events from RingCentral."""
    body = await request.json()

    # Handle validation token (subscription creation verification)
    validation_token = request.headers.get("Validation-Token")
    if validation_token:
        from fastapi.responses import Response
        return Response(
            content="",
            headers={"Validation-Token": validation_token},
            status_code=200,
        )

    # Process event
    event = body.get("event", "")
    event_body = body.get("body", {})

    if "/telephony/sessions" in event:
        # Inbound/outbound call event
        caller_number = event_body.get("parties", [{}])[0].get("from", {}).get("phoneNumber", "")
        resolver = CallerIDResolver()
        patient = await resolver.resolve(caller_number, db)

        if patient:
            await db.execute(
                """INSERT INTO comms_call_log
                   (ringcentral_call_id, patient_id, direction, from_number,
                    to_number, status)
                   VALUES ($1,$2,$3,$4,$5,$6)
                   ON CONFLICT (ringcentral_call_id) DO UPDATE SET status = $6""",
                [
                    event_body.get("sessionId", ""),
                    patient["patient_id"],
                    "inbound",
                    caller_number,
                    event_body.get("parties", [{}])[0].get("to", {}).get("phoneNumber", ""),
                    event_body.get("parties", [{}])[0].get("status", {}).get("code", ""),
                ],
            )
            await db.commit()

        await resolver.close()

    elif "/message-store" in event:
        # Inbound SMS event
        for msg in event_body.get("changes", []):
            if msg.get("type") == "SMS":
                # Process inbound SMS — match to patient, log
                pass

    return {"status": "ok"}
```

### Step 5: Reminder Scheduler

```python
# app/services/reminder_scheduler.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.ringcentral_client import RingCentralClient
from app.db.session import async_session
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

SMS_TEMPLATES = {
    "reminder_48h": (
        "Reminder: You have an appointment at Texas Retina Associates "
        "on {date} at {time}. Reply YES to confirm or call us to reschedule."
    ),
    "reminder_24h": (
        "Your appointment is tomorrow, {date} at {time}. "
        "Please arrive 15 minutes early. Reply YES to confirm."
    ),
    "reminder_2h": (
        "Your appointment today at {time} is in 2 hours. "
        "We look forward to seeing you."
    ),
}


async def send_appointment_reminders(hours_before: int = 48):
    """Send SMS reminders for appointments N hours from now."""
    async with async_session() as db:
        target_time = datetime.utcnow() + timedelta(hours=hours_before)
        window_start = target_time - timedelta(minutes=30)
        window_end = target_time + timedelta(minutes=30)

        # Query upcoming appointments with opted-in patients
        result = await db.execute(
            """SELECT a.id, a.appointment_date, a.appointment_time,
                      p.id as patient_id, p.phone, p.first_name
               FROM appointments a
               JOIN patients p ON a.patient_id = p.id
               LEFT JOIN patient_comms_preferences pcp ON p.id = pcp.patient_id
               WHERE a.appointment_date BETWEEN $1 AND $2
                 AND (pcp.sms_reminder_opt_in IS NULL OR pcp.sms_reminder_opt_in = TRUE)
                 AND a.status = 'scheduled'""",
            [window_start, window_end],
        )
        appointments = result.fetchall()

        if not appointments:
            return

        client = RingCentralClient()
        template_key = f"reminder_{hours_before}h"
        template = SMS_TEMPLATES.get(template_key, SMS_TEMPLATES["reminder_48h"])

        for appt in appointments:
            try:
                message = template.format(
                    date=appt.appointment_date.strftime("%B %d"),
                    time=appt.appointment_time.strftime("%I:%M %p"),
                )

                client.send_sms(
                    from_number="+1YOUR_RC_NUMBER",
                    to_number=appt.phone,
                    text=message,
                )

                # Log the reminder
                await db.execute(
                    """INSERT INTO comms_sms_log
                       (patient_id, direction, from_number, to_number,
                        message_text, delivery_status, template_id)
                       VALUES ($1,$2,$3,$4,$5,$6,$7)""",
                    [
                        str(appt.patient_id), "outbound",
                        "+1YOUR_RC_NUMBER", appt.phone,
                        message, "Queued", template_key,
                    ],
                )

                logger.info(f"Sent {template_key} reminder to patient {appt.patient_id}")

            except Exception as e:
                logger.error(f"Failed to send reminder to {appt.patient_id}: {e}")

        await db.commit()


def start_reminder_scheduler():
    """Start the appointment reminder scheduler."""
    # 48-hour reminders at 7:00 AM daily
    scheduler.add_job(
        send_appointment_reminders,
        "cron", hour=7, minute=0,
        kwargs={"hours_before": 48},
        id="reminder_48h",
    )
    # 24-hour reminders at 7:00 AM daily
    scheduler.add_job(
        send_appointment_reminders,
        "cron", hour=7, minute=0,
        kwargs={"hours_before": 24},
        id="reminder_24h",
    )
    # 2-hour reminders every 30 minutes
    scheduler.add_job(
        send_appointment_reminders,
        "interval", minutes=30,
        kwargs={"hours_before": 2},
        id="reminder_2h",
    )
    scheduler.start()
    logger.info("Appointment reminder scheduler started")
```

### Step 6: HIPAA Audit Logger

```python
# app/services/comms_audit.py

from datetime import datetime


async def log_comms_action(
    db,
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    patient_id: str = None,
    request_summary: dict = None,
    response_status: int = 200,
    ip_address: str = None,
):
    """Log a communication operation to the HIPAA audit trail."""
    await db.execute(
        """INSERT INTO comms_audit_log
           (user_id, action, resource_type, resource_id, patient_id,
            request_summary, response_status, ip_address, timestamp)
           VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)""",
        [
            user_id, action, resource_type, resource_id, patient_id,
            request_summary, response_status, ip_address,
            datetime.utcnow(),
        ],
    )
```

**Checkpoint**: The PMS backend has a `RingCentralClient` SDK wrapper, `CallerIDResolver`, `CommsService` router with 10 endpoints (SMS, voice, fax, video, webhook), `ReminderScheduler`, and HIPAA audit logging — all connected to the RingCentral REST API via OAuth 2.0.

## 5. Part C: Integrate with PMS Frontend

### Step 1: Environment Variables

```bash
# .env.local (Next.js)
NEXT_PUBLIC_COMMS_API_URL=http://localhost:8000/api/comms
```

### Step 2: Communications API Client

```typescript
// src/lib/comms-api.ts

export interface SMSHistoryEntry {
  direction: "inbound" | "outbound";
  from: string;
  to: string;
  text: string;
  status: string;
  timestamp: string;
}

export interface CallLogEntry {
  id: string;
  direction: "inbound" | "outbound";
  from: { phoneNumber: string; name?: string };
  to: { phoneNumber: string; name?: string };
  duration: number;
  result: string;
  startTime: string;
  recording?: { id: string; contentUri: string };
}

export interface FaxInboxEntry {
  id: string;
  from_number: string;
  page_count: number;
  patient_id: string | null;
  status: string;
  received_at: string;
}

const BASE = process.env.NEXT_PUBLIC_COMMS_API_URL;

async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const token = localStorage.getItem("auth_token");
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });
  if (!res.ok) throw new Error(`Comms API error: ${res.status}`);
  return res.json();
}

export const commsApi = {
  // SMS
  sendSMS: (patientId: string, toNumber: string, text: string) =>
    fetchWithAuth(`${BASE}/sms`, {
      method: "POST",
      body: JSON.stringify({
        patient_id: patientId,
        to_number: toNumber,
        message_text: text,
      }),
    }),

  getSMSHistory: (patientId: string): Promise<{ messages: SMSHistoryEntry[] }> =>
    fetchWithAuth(`${BASE}/sms/history/${patientId}`),

  // Voice
  initiateCall: (fromNumber: string, toNumber: string, patientId?: string) =>
    fetchWithAuth(`${BASE}/call`, {
      method: "POST",
      body: JSON.stringify({
        from_number: fromNumber,
        to_number: toNumber,
        patient_id: patientId,
      }),
    }),

  getCallLog: (dateFrom?: string, dateTo?: string): Promise<{ records: CallLogEntry[] }> =>
    fetchWithAuth(`${BASE}/calls/log?${new URLSearchParams({ ...(dateFrom && { date_from: dateFrom }), ...(dateTo && { date_to: dateTo }) })}`),

  // Fax
  sendFax: (toNumber: string, documentBase64: string, coverText?: string) =>
    fetchWithAuth(`${BASE}/fax`, {
      method: "POST",
      body: JSON.stringify({
        to_number: toNumber,
        document_base64: documentBase64,
        cover_text: coverText,
      }),
    }),

  getFaxInbox: (status?: string): Promise<{ faxes: FaxInboxEntry[] }> =>
    fetchWithAuth(`${BASE}/fax/inbox?status=${status || "pending"}`),

  // Video
  createVideoMeeting: (patientId: string, topic?: string) =>
    fetchWithAuth(`${BASE}/video/meeting`, {
      method: "POST",
      body: JSON.stringify({
        patient_id: patientId,
        topic: topic || "Telehealth Visit",
      }),
    }),
};
```

### Step 3: Communications Dashboard Component

```tsx
// src/components/comms/CommsDashboard.tsx

"use client";

import { useEffect, useState } from "react";
import { commsApi, CallLogEntry, FaxInboxEntry } from "@/lib/comms-api";

export function CommsDashboard() {
  const [callLog, setCallLog] = useState<CallLogEntry[]>([]);
  const [faxInbox, setFaxInbox] = useState<FaxInboxEntry[]>([]);
  const [activeTab, setActiveTab] = useState<"calls" | "fax" | "sms">("calls");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [callRes, faxRes] = await Promise.all([
          commsApi.getCallLog(),
          commsApi.getFaxInbox(),
        ]);
        setCallLog(callRes.records || []);
        setFaxInbox(faxRes.faxes || []);
      } catch (err) {
        console.error("Failed to load comms data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) return <div className="p-4">Loading communications...</div>;

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Tab Navigation */}
      <div className="border-b flex">
        {(["calls", "fax", "sms"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-6 py-3 text-sm font-medium capitalize ${
              activeTab === tab
                ? "border-b-2 border-blue-600 text-blue-600"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {tab === "calls" ? "Call Log" : tab === "fax" ? "Fax Inbox" : "SMS"}
            {tab === "fax" && faxInbox.length > 0 && (
              <span className="ml-2 bg-red-100 text-red-800 text-xs px-2 py-0.5 rounded-full">
                {faxInbox.length}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Call Log Tab */}
      {activeTab === "calls" && (
        <div className="p-4">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2">Direction</th>
                <th className="pb-2">Number</th>
                <th className="pb-2">Duration</th>
                <th className="pb-2">Result</th>
                <th className="pb-2">Time</th>
                <th className="pb-2">Recording</th>
              </tr>
            </thead>
            <tbody>
              {callLog.map((call, i) => (
                <tr key={i} className="border-b hover:bg-gray-50">
                  <td className="py-2">
                    <span className={`text-xs px-2 py-1 rounded ${
                      call.direction === "inbound"
                        ? "bg-green-100 text-green-800"
                        : "bg-blue-100 text-blue-800"
                    }`}>
                      {call.direction}
                    </span>
                  </td>
                  <td className="py-2">
                    {call.direction === "inbound"
                      ? call.from?.phoneNumber
                      : call.to?.phoneNumber}
                  </td>
                  <td className="py-2">{Math.floor(call.duration / 60)}:{(call.duration % 60).toString().padStart(2, "0")}</td>
                  <td className="py-2">{call.result}</td>
                  <td className="py-2">{new Date(call.startTime).toLocaleString()}</td>
                  <td className="py-2">
                    {call.recording && (
                      <button className="text-blue-600 hover:underline text-xs">
                        Play
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Fax Inbox Tab */}
      {activeTab === "fax" && (
        <div className="p-4 space-y-3">
          {faxInbox.map((fax) => (
            <div key={fax.id} className="border rounded p-3 flex justify-between items-center">
              <div>
                <span className="font-medium">From: {fax.from_number}</span>
                <span className="ml-3 text-sm text-gray-500">{fax.page_count} pages</span>
                <div className="text-xs text-gray-400 mt-1">
                  {new Date(fax.received_at).toLocaleString()}
                </div>
              </div>
              <div className="flex gap-2">
                <span className={`text-xs px-2 py-1 rounded ${
                  fax.status === "pending"
                    ? "bg-yellow-100 text-yellow-800"
                    : "bg-green-100 text-green-800"
                }`}>
                  {fax.status}
                </span>
                <button className="text-sm text-blue-600 hover:underline">
                  {fax.patient_id ? "View" : "Match Patient"}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* SMS Tab placeholder */}
      {activeTab === "sms" && (
        <div className="p-4 text-gray-500">
          Select a patient to view SMS conversation history.
        </div>
      )}
    </div>
  );
}
```

### Step 4: Add Route

```tsx
// src/app/communications/page.tsx

import { CommsDashboard } from "@/components/comms/CommsDashboard";

export default function CommunicationsPage() {
  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6">
        <h1 className="text-2xl font-bold mb-6 px-4">
          Patient Communications
        </h1>
        <CommsDashboard />
      </div>
    </main>
  );
}
```

**Checkpoint**: The PMS frontend has a `commsApi` TypeScript client, `CommsDashboard` with call log/fax inbox/SMS tabs, and a `/communications` route — all connected to the backend `CommsService`.

## 6. Part D: Testing and Verification

### Step 1: Verify OAuth Authentication

```bash
python -c "
from ringcentral import SDK
sdk = SDK('$RC_CLIENT_ID', '$RC_CLIENT_SECRET', '$RC_SERVER_URL')
p = sdk.platform()
p.login(jwt='$RC_JWT_TOKEN')
print('Auth OK:', p.logged_in())
info = p.get('/restapi/v1.0/account/~/extension/~').json()
print('Extension:', info['name'], '|', info['extensionNumber'])
"
# Expected: Auth OK: True, Extension: <your name> | <ext number>
```

### Step 2: Test SMS Sending (Sandbox)

```bash
curl -s -X POST http://localhost:8000/api/comms/sms \
  -H "Authorization: Bearer $PMS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "test-patient-uuid",
    "to_number": "+1YOUR_SANDBOX_NUMBER",
    "message_text": "Reminder: Your appointment is tomorrow at 10:00 AM."
  }' | python -m json.tool

# Expected: {"message_id": "...", "status": "Queued"}
# Note: Sandbox SMS are watermarked and may not deliver to real phones
```

### Step 3: Test Call Initiation (Sandbox)

```bash
curl -s -X POST http://localhost:8000/api/comms/call \
  -H "Authorization: Bearer $PMS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "from_number": "+1YOUR_RC_NUMBER",
    "to_number": "+1YOUR_SANDBOX_NUMBER"
  }' | python -m json.tool

# Expected: {"session_id": "...", "status": "InProgress"}
```

### Step 4: Test Webhook Delivery

```bash
# Verify ngrok is forwarding
curl -s http://localhost:4040/api/tunnels | python -m json.tool
# Expected: Shows active tunnel to localhost:8000

# Send a test SMS to your sandbox number to trigger inbound webhook
# Check PMS logs for webhook receipt
```

### Step 5: Verify Audit Logging

```bash
psql -U pms_user -d pms_db -c \
  "SELECT action, resource_type, resource_id, timestamp
   FROM comms_audit_log ORDER BY timestamp DESC LIMIT 5;"

# Expected: Rows showing send_sms, initiate_call actions
```

### Step 6: Test Frontend

1. Navigate to `http://localhost:3000/communications`
2. Verify the Communications Dashboard renders with Call Log, Fax Inbox, and SMS tabs
3. Check call log populates with recent calls from RingCentral

**Checkpoint**: OAuth authentication works, SMS and call endpoints respond correctly, webhooks are forwarded via ngrok, audit logging captures all actions, and the frontend dashboard renders.

## 7. Troubleshooting

### OAuth Authentication Failure

**Symptoms**: `401 Unauthorized` or "JWT token is invalid" error.

**Solution**:
1. Verify JWT token hasn't expired — regenerate in Developer Console if needed
2. Confirm Client ID and Client Secret match the app in Developer Console
3. Check `RC_SERVER_URL` matches environment (sandbox vs. production)
4. Ensure the app has the required permissions (Read Messages, Send Messages, etc.)

### SMS Not Delivering

**Symptoms**: SMS shows "Queued" but never delivers.

**Solution**:
1. In sandbox, SMS are watermarked and may not reach real phones — use sandbox phone numbers
2. Check 10DLC registration status (required for A2P SMS in production)
3. Verify SMS quota: 50/extension/month in sandbox, 200/extension/month in production
4. Check the "from" number is a valid RingCentral number assigned to your extension

### Webhook Not Receiving Events

**Symptoms**: No webhook POSTs arriving at the PMS backend.

**Solution**:
1. Verify ngrok is running: `curl http://localhost:4040/api/tunnels`
2. Check the webhook subscription was created successfully (check RingCentral Developer Console → Webhooks)
3. Ensure the webhook URL in the subscription matches your current ngrok URL (ngrok URLs change on restart)
4. Check firewall isn't blocking inbound HTTPS on the ngrok tunnel
5. Verify the webhook endpoint returns 200 and the `Validation-Token` header during subscription creation

### Call Recording Not Available

**Symptoms**: `recording_url` is null in call log entries.

**Solution**:
1. Call recording must be enabled in RingCentral account settings (not just API)
2. Recordings may take 1-5 minutes to process after the call ends
3. In sandbox, recording quality is watermarked but should still be accessible
4. Check account-level permissions: Admin → Phone System → Call Recording

### Rate Limiting (429 Errors)

**Symptoms**: `429 Too Many Requests` on API calls.

**Solution**:
1. RingCentral rate limits vary by endpoint (10-60 req/min typical)
2. Add exponential backoff with jitter to the `RingCentralClient`
3. Cache frequently accessed data (call log, account info) in Redis
4. For bulk SMS, use the High Volume SMS API instead of individual sends
5. Check `X-Rate-Limit-*` response headers for current limits

### Port Conflicts with ngrok

**Symptoms**: ngrok tunnel shows errors or webhook URL is inaccessible.

**Solution**:
1. Kill existing ngrok processes: `pkill ngrok`
2. Restart: `ngrok http 8000`
3. Update `RC_WEBHOOK_URL` in `.env` with the new URL
4. Re-create webhook subscription (old URL is now invalid)

## 8. Reference Commands

### Daily Development Workflow

```bash
# Start services
docker compose up -d postgres redis
uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev

# Start ngrok for webhooks
ngrok http 8000

# Test API auth
python -c "
from ringcentral import SDK
sdk = SDK('$RC_CLIENT_ID','$RC_CLIENT_SECRET','$RC_SERVER_URL')
sdk.platform().login(jwt='$RC_JWT_TOKEN')
print('OK')
"

# Send test SMS
curl -s -X POST http://localhost:8000/api/comms/sms \
  -H "Authorization: Bearer $PMS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"test","to_number":"+1555XXXXXXX","message_text":"Test"}'

# Check audit log
psql -U pms_user -d pms_db -c "SELECT * FROM comms_audit_log ORDER BY timestamp DESC LIMIT 10;"
```

### RingCentral Management

| Action | Location |
|---|---|
| Create/manage apps | [Developer Console](https://developers.ringcentral.com/my-account.html) |
| Generate JWT tokens | Developer Console → App → Credentials |
| View webhook subscriptions | Developer Console → App → Webhooks |
| Check API usage | Developer Console → App → Analytics |
| Account settings | [RingCentral Admin Portal](https://service.ringcentral.com/) |
| Enable call recording | Admin Portal → Phone System → Call Recording |

### Useful URLs

| Resource | URL |
|---|---|
| RingCentral Developer Portal | `https://developers.ringcentral.com/` |
| API Reference | `https://developers.ringcentral.com/api-reference` |
| API Explorer | `https://developers.ringcentral.com/api-reference/explorer` |
| Developer Console | `https://developers.ringcentral.com/my-account.html` |
| Sandbox Base URL | `https://platform.devtest.ringcentral.com/restapi/v1.0/` |
| Production Base URL | `https://platform.ringcentral.com/restapi/v1.0/` |
| Python SDK (GitHub) | `https://github.com/ringcentral/ringcentral-python` |
| PMS Comms Dashboard | `http://localhost:3000/communications` |
| PMS Comms API | `http://localhost:8000/api/comms/` |
| ngrok Dashboard | `http://localhost:4040/` |

## Next Steps

1. Complete the [RingCentral API Developer Tutorial](71-RingCentralAPI-Developer-Tutorial.md) for a hands-on integration walkthrough
2. Set up High Volume SMS for bulk appointment reminders
3. Configure after-hours IVR with clinical triage routing
4. Integrate with [Microsoft Teams (Experiment 68)](68-PRD-MSTeams-PMS-Integration.md) for internal clinical escalation
5. Build the Android app communication module with push notifications

## Resources

- [RingCentral Developer Portal](https://developers.ringcentral.com/) — Main developer hub
- [RingCentral API Products](https://developers.ringcentral.com/api-products) — All API capabilities
- [RingCentral API Reference](https://developers.ringcentral.com/api-reference) — Full endpoint documentation
- [RingCentral Python SDK](https://github.com/ringcentral/ringcentral-python) — Official Python SDK
- [RingCentral for Healthcare](https://developers.ringcentral.com/solutions/healthcare) — Healthcare-specific features
- [RingCentral HIPAA Guide](https://support.ringcentral.com/article-v2/RingCentral-HIPAA-Compliance.html?brand=RC_US&product=RingEX&language=en_US) — HIPAA compliance details
- [PRD: RingCentral API PMS Integration](71-PRD-RingCentralAPI-PMS-Integration.md) — Product requirements document
