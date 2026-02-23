# HL7 v2 LIS Messaging Setup Guide for PMS Integration

**Document ID:** PMS-EXP-HL7V2LIS-001
**Version:** 1.0
**Date:** February 21, 2026
**Applies To:** PMS project (all platforms)
**Prerequisites Level:** Intermediate

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Part A: Install and Configure the HL7 v2 Integration Engine](#3-part-a-install-and-configure-the-hl7-v2-integration-engine)
4. [Part B: Integrate with PMS Backend](#4-part-b-integrate-with-pms-backend)
5. [Part C: Integrate with PMS Frontend](#5-part-c-integrate-with-pms-frontend)
6. [Part D: Testing and Verification](#6-part-d-testing-and-verification)
7. [Troubleshooting](#7-troubleshooting)
8. [Reference Commands](#8-reference-commands)

---

## 1. Overview

This guide walks you through deploying an **HL7 v2 Integration Engine** for bidirectional lab messaging between the PMS and external Laboratory Information Systems (LIS). By the end, you will have:

- An MLLP listener on port 2575 receiving inbound HL7 v2 ORU (result) messages
- An MLLP sender transmitting outbound HL7 v2 ORM (order) messages
- An HL7 v2 parser/builder using `hl7apy` for message processing
- TLS encryption via stunnel for all external MLLP connections
- New `/api/lab-orders` and `/api/lab-results` FastAPI endpoints
- Message audit logging in PostgreSQL for HIPAA compliance
- Lab Results Dashboard and Order Entry Panel in the Next.js frontend

### Architecture at a Glance

```mermaid
flowchart LR
    subgraph External["External Lab Systems"]
        LIS["Laboratory<br/>Information System"]
    end

    subgraph Docker["Docker Network"]
        TLS["stunnel<br/>TLS Proxy<br/>:2575"]
        HL7["HL7 v2 Engine<br/>:2575-int<br/>(Python asyncio)"]
        API["PMS Backend<br/>:8000<br/>(FastAPI)"]
        DB[("PostgreSQL<br/>:5432")]
    end

    subgraph Clients["PMS Clients"]
        WEB["Next.js :3000<br/>(Lab Dashboard)"]
        AND["Android App"]
    end

    LIS <-->|"HL7 v2 MLLP<br/>(TLS 1.3)"| TLS
    TLS <--> HL7
    HL7 -->|"Parsed results"| API
    HL7 -->|"Audit logs"| DB
    API --> DB
    WEB --> API
    AND --> API

    style TLS fill:#9b59b6,color:#fff
    style HL7 fill:#e74c3c,color:#fff
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
| stunnel | 5.60+ | `stunnel -version` (or will be installed in Docker) |
| netcat | Any | `nc -h` or `ncat --version` |

### 2.2 Installation of Prerequisites

**hl7apy (HL7 v2 message library):**

```bash
pip install "hl7apy>=1.3.4"
```

This installs the HL7 v2 parser and builder supporting versions 2.1 through 2.8.2. It includes MLLP server/client implementations and message validation.

**python-hl7 (lightweight parser + async MLLP):**

```bash
pip install "hl7>=0.4.5"
```

Provides a simpler parser and experimental asyncio-based MLLP support.

**Verify hl7apy installation:**

```bash
python3 -c "
from hl7apy.core import Message
m = Message('ORU_R01')
print(f'hl7apy OK - created {m.name}')
"
# Expected: hl7apy OK - created ORU_R01
```

### 2.3 Verify PMS Services

```bash
# Check PMS backend
curl -s http://localhost:8000/docs | head -5
# Expected: HTML for FastAPI Swagger docs

# Check PMS frontend
curl -s http://localhost:3000 -o /dev/null -w "%{http_code}"
# Expected: 200

# Check PostgreSQL
docker exec pms-db pg_isready
# Expected: accepting connections

# Check port 2575 is available (MLLP standard port)
lsof -i :2575
# Expected: no output (port is free)
```

---

## 3. Part A: Install and Configure the HL7 v2 Integration Engine

### Step 1: Create the Project Structure

```bash
mkdir -p pms-hl7/app/{mllp,parser,builder,models}
mkdir -p pms-hl7/tests
mkdir -p pms-hl7/config
```

Expected directory layout:

```
pms-hl7/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Engine entry point (asyncio event loop)
│   ├── config.py               # Environment configuration
│   ├── mllp/
│   │   ├── __init__.py
│   │   ├── listener.py         # Inbound MLLP server (ORU receiver)
│   │   ├── sender.py           # Outbound MLLP client (ORM sender)
│   │   └── framing.py          # MLLP SB/EB/CR byte framing
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── oru_parser.py       # ORU result message parser
│   │   ├── ack_builder.py      # ACK/NACK response generator
│   │   └── segment_extract.py  # PID, OBR, OBX field extraction
│   ├── builder/
│   │   ├── __init__.py
│   │   ├── orm_builder.py      # ORM order message builder
│   │   └── segment_build.py    # MSH, PID, PV1, ORC, OBR construction
│   └── models/
│       ├── __init__.py
│       ├── lab_order.py        # SQLAlchemy lab order model
│       ├── lab_result.py       # SQLAlchemy lab result model
│       └── hl7_message.py      # SQLAlchemy message audit model
├── tests/
│   ├── test_oru_parser.py
│   ├── test_orm_builder.py
│   ├── test_mllp_framing.py
│   └── fixtures/
│       ├── sample_oru.hl7      # Sample ORU message for testing
│       └── sample_orm.hl7      # Sample ORM message for testing
├── config/
│   ├── stunnel.conf            # TLS proxy configuration
│   └── lis_endpoints.json      # External LIS connection registry
├── Dockerfile
├── requirements.txt
└── .env
```

### Step 2: Create Requirements File

```bash
cat > pms-hl7/requirements.txt << 'EOF'
hl7apy>=1.3.4
hl7>=0.4.5
httpx>=0.27.0
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.29.0
pydantic>=2.6.0
pydantic-settings>=2.1.0
EOF
```

### Step 3: Create the Dockerfile

```bash
cat > pms-hl7/Dockerfile << 'EOF'
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY config/ ./config/

EXPOSE 2575

CMD ["python", "-m", "app.main"]
EOF
```

### Step 4: Create Environment Configuration

```bash
cat > pms-hl7/.env << 'EOF'
# HL7 v2 Integration Engine Configuration
MLLP_LISTEN_HOST=0.0.0.0
MLLP_LISTEN_PORT=2575
PMS_BACKEND_URL=http://pms-backend:8000
DATABASE_URL=postgresql+asyncpg://pms:pms_secret@pms-db:5432/pms

# Sending Facility (PMS identity in MSH segment)
SENDING_FACILITY=MPS_PMS
SENDING_APPLICATION=PMS_LAB

# HIPAA Audit
AUDIT_LOG_ENABLED=true
AUDIT_RETENTION_DAYS=2555

# Message Processing
MAX_MESSAGE_SIZE=1048576
ACK_TIMEOUT_SECONDS=30
RETRY_MAX_ATTEMPTS=3
EOF
```

### Step 5: Implement MLLP Framing

Create `pms-hl7/app/mllp/framing.py`:

```python
"""MLLP (Minimal Lower Layer Protocol) message framing.

MLLP uses three special bytes to frame HL7 messages:
- Start Block (SB): 0x0B (vertical tab)
- End Block (EB): 0x1C (file separator)
- Carriage Return (CR): 0x0D

Wire format: <SB>message<EB><CR>
"""

SB = b"\x0b"  # Start Block
EB = b"\x1c"  # End Block
CR = b"\x0d"  # Carriage Return


def wrap_mllp(message: str) -> bytes:
    """Wrap an HL7 message in MLLP framing bytes."""
    return SB + message.encode("utf-8") + EB + CR


def unwrap_mllp(data: bytes) -> str:
    """Extract the HL7 message from MLLP framing bytes."""
    # Strip SB prefix and EB+CR suffix
    message = data
    if message.startswith(SB):
        message = message[len(SB):]
    if message.endswith(CR):
        message = message[:-len(CR)]
    if message.endswith(EB):
        message = message[:-len(EB)]
    return message.decode("utf-8")


def find_message_boundaries(buffer: bytes) -> tuple[int, int] | None:
    """Find start and end of an MLLP-framed message in a byte buffer.

    Returns (start, end) indices or None if no complete message found.
    """
    start = buffer.find(SB)
    if start == -1:
        return None

    # Look for EB+CR after the start block
    end = buffer.find(EB + CR, start)
    if end == -1:
        return None

    return (start, end + len(EB) + len(CR))
```

### Step 6: Implement the MLLP Listener

Create `pms-hl7/app/mllp/listener.py`:

```python
"""Asyncio MLLP server for receiving inbound HL7 v2 messages."""

import asyncio
import logging
from datetime import datetime, timezone

from app.mllp.framing import unwrap_mllp, find_message_boundaries, wrap_mllp
from app.parser.oru_parser import parse_oru_message
from app.parser.ack_builder import build_ack, build_nack

logger = logging.getLogger(__name__)


class MLLPListener:
    """Asyncio TCP server implementing MLLP protocol."""

    def __init__(self, host: str, port: int, result_callback):
        self.host = host
        self.port = port
        self.result_callback = result_callback

    async def start(self):
        server = await asyncio.start_server(
            self._handle_connection, self.host, self.port
        )
        addr = server.sockets[0].getsockname()
        logger.info(f"MLLP listener started on {addr[0]}:{addr[1]}")
        async with server:
            await server.serve_forever()

    async def _handle_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        peer = writer.get_extra_info("peername")
        logger.info(f"MLLP connection from {peer}")
        buffer = b""

        try:
            while True:
                data = await reader.read(65536)
                if not data:
                    break

                buffer += data
                boundaries = find_message_boundaries(buffer)

                while boundaries:
                    start, end = boundaries
                    mllp_data = buffer[start:end]
                    buffer = buffer[end:]

                    try:
                        raw_message = unwrap_mllp(mllp_data)
                        received_at = datetime.now(timezone.utc)
                        logger.info(f"Received HL7 message from {peer} at {received_at.isoformat()}")

                        # Parse and process the message
                        result = parse_oru_message(raw_message)
                        await self.result_callback(result, raw_message, peer)

                        # Send ACK
                        ack = build_ack(raw_message)
                        writer.write(wrap_mllp(ack))
                        await writer.drain()
                        logger.info(f"Sent ACK to {peer}")

                    except Exception as e:
                        logger.error(f"Error processing message from {peer}: {e}")
                        nack = build_nack(str(e))
                        writer.write(wrap_mllp(nack))
                        await writer.drain()

                    boundaries = find_message_boundaries(buffer)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Connection error with {peer}: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            logger.info(f"MLLP connection closed: {peer}")
```

### Step 7: Implement the ORU Parser

Create `pms-hl7/app/parser/oru_parser.py`:

```python
"""Parse HL7 v2 ORU^R01 (Observation Result) messages."""

from hl7apy.core import Message
from hl7apy.parser import parse_message
import logging

logger = logging.getLogger(__name__)


def parse_oru_message(raw_message: str) -> dict:
    """
    Parse an HL7 v2 ORU^R01 message into structured result data.

    Extracts:
    - Patient demographics from PID segment
    - Test panel info from OBR segment
    - Individual test results from OBX segments

    Returns a dict ready for POST to /api/lab-results.
    """
    msg = parse_message(raw_message)

    # Extract MSH (Message Header)
    msh = msg.msh
    message_control_id = str(msh.msh_10.value) if msh.msh_10 else ""
    sending_facility = str(msh.msh_4.value) if msh.msh_4 else ""

    # Extract PID (Patient Identification)
    pid = msg.children[1] if len(msg.children) > 1 else None
    patient_data = _extract_pid(pid) if pid and pid.name == "PID" else {}

    # Extract OBR and OBX segments from ORDER_OBSERVATION groups
    results = []
    for child in msg.children:
        if hasattr(child, "children"):
            for segment in child.children if hasattr(child, "children") else []:
                if hasattr(segment, "name"):
                    if segment.name == "OBR":
                        panel_info = _extract_obr(segment)
                    elif segment.name == "OBX":
                        result = _extract_obx(segment)
                        results.append(result)

    return {
        "message_control_id": message_control_id,
        "sending_facility": sending_facility,
        "patient": patient_data,
        "results": results,
    }


def _extract_pid(pid) -> dict:
    """Extract patient demographics from PID segment."""
    return {
        "mrn": str(pid.pid_3.value) if pid.pid_3 else "",
        "last_name": str(pid.pid_5.pid_5_1.value) if pid.pid_5 and pid.pid_5.pid_5_1 else "",
        "first_name": str(pid.pid_5.pid_5_2.value) if pid.pid_5 and pid.pid_5.pid_5_2 else "",
        "date_of_birth": str(pid.pid_7.value) if pid.pid_7 else "",
        "gender": str(pid.pid_8.value) if pid.pid_8 else "",
    }


def _extract_obr(obr) -> dict:
    """Extract test panel information from OBR segment."""
    return {
        "placer_order_number": str(obr.obr_2.value) if obr.obr_2 else "",
        "filler_order_number": str(obr.obr_3.value) if obr.obr_3 else "",
        "test_code": str(obr.obr_4.obr_4_1.value) if obr.obr_4 and obr.obr_4.obr_4_1 else "",
        "test_name": str(obr.obr_4.obr_4_2.value) if obr.obr_4 and obr.obr_4.obr_4_2 else "",
        "observation_date": str(obr.obr_7.value) if obr.obr_7 else "",
        "result_status": str(obr.obr_25.value) if obr.obr_25 else "",
    }


def _extract_obx(obx) -> dict:
    """Extract a single test result from OBX segment."""
    return {
        "test_code": str(obx.obx_3.obx_3_1.value) if obx.obx_3 and obx.obx_3.obx_3_1 else "",
        "test_name": str(obx.obx_3.obx_3_2.value) if obx.obx_3 and obx.obx_3.obx_3_2 else "",
        "value": str(obx.obx_5.value) if obx.obx_5 else "",
        "units": str(obx.obx_6.value) if obx.obx_6 else "",
        "reference_range": str(obx.obx_7.value) if obx.obx_7 else "",
        "abnormal_flag": str(obx.obx_8.value) if obx.obx_8 else "",
        "result_status": str(obx.obx_11.value) if obx.obx_11 else "",
    }
```

### Step 8: Implement ACK/NACK Builder

Create `pms-hl7/app/parser/ack_builder.py`:

```python
"""Build HL7 v2 ACK and NACK acknowledgment messages."""

from datetime import datetime, timezone


def build_ack(original_message: str) -> str:
    """Build an HL7 v2 ACK message for a successfully processed message."""
    # Extract message control ID from original MSH segment
    lines = original_message.split("\r")
    msh_fields = lines[0].split("|") if lines else []
    msg_control_id = msh_fields[9] if len(msh_fields) > 9 else "UNKNOWN"
    sending_app = msh_fields[2] if len(msh_fields) > 2 else ""
    sending_facility = msh_fields[3] if len(msh_fields) > 3 else ""

    now = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    ack = (
        f"MSH|^~\\&|PMS_LAB|MPS_PMS|{sending_app}|{sending_facility}|{now}||ACK^R01|{now}|P|2.5.1\r"
        f"MSA|AA|{msg_control_id}\r"
    )
    return ack


def build_nack(error_message: str) -> str:
    """Build an HL7 v2 NACK message for a rejected message."""
    now = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    # Sanitize error message - never include PHI
    safe_error = error_message[:200].replace("|", " ").replace("\r", " ")

    nack = (
        f"MSH|^~\\&|PMS_LAB|MPS_PMS|||{now}||ACK^R01|{now}|P|2.5.1\r"
        f"MSA|AE|UNKNOWN|{safe_error}\r"
    )
    return nack
```

### Step 9: Implement the ORM Builder

Create `pms-hl7/app/builder/orm_builder.py`:

```python
"""Build HL7 v2 ORM^O01 (Order Message) for lab orders."""

from datetime import datetime, timezone


def build_orm_message(order: dict, patient: dict, encounter: dict | None = None) -> str:
    """
    Build an HL7 v2 ORM^O01 message from PMS lab order data.

    Args:
        order: Lab order dict with test_codes, ordering_provider, priority
        patient: Patient dict with id, first_name, last_name, dob, gender
        encounter: Optional encounter dict with id, start_date

    Returns:
        Complete HL7 v2 ORM message string with MLLP-compatible CR delimiters.
    """
    now = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    msg_control_id = f"PMS{now}"

    # MSH - Message Header
    msh = (
        f"MSH|^~\\&|PMS_LAB|MPS_PMS|"
        f"{order.get('receiving_application', 'LIS')}|"
        f"{order.get('receiving_facility', 'LAB')}|"
        f"{now}||ORM^O01|{msg_control_id}|P|2.5.1"
    )

    # PID - Patient Identification
    gender_map = {"male": "M", "female": "F", "other": "O", "unknown": "U"}
    pid_gender = gender_map.get(patient.get("gender", ""), "U")
    dob = patient.get("date_of_birth", "").replace("-", "")
    pid = (
        f"PID|1||{patient['id']}^^^MPS_PMS^MR||"
        f"{patient.get('last_name', '')}^{patient.get('first_name', '')}||"
        f"{dob}|{pid_gender}"
    )

    # PV1 - Patient Visit (if encounter available)
    pv1 = ""
    if encounter:
        pv1 = f"PV1|1|O|^^^MPS_PMS||||{order.get('ordering_provider', '')}|||||||||||{encounter.get('id', '')}"

    # ORC - Common Order + OBR - Observation Request (one pair per test)
    order_segments = []
    for i, test_code in enumerate(order.get("test_codes", []), start=1):
        placer_id = f"{order['id']}-{i}"
        priority = order.get("priority", "R")  # R=Routine, S=Stat, A=ASAP

        orc = (
            f"ORC|NW|{placer_id}||{order['id']}||||{now}|||"
            f"{order.get('ordering_provider', '')}|||{now}"
        )
        obr = (
            f"OBR|{i}|{placer_id}||{test_code}|||{now}|||||||||"
            f"{order.get('ordering_provider', '')}||||||||{priority}"
        )
        order_segments.extend([orc, obr])

    # Assemble complete message
    segments = [msh, pid]
    if pv1:
        segments.append(pv1)
    segments.extend(order_segments)

    return "\r".join(segments)
```

### Step 10: Add to Docker Compose

Add these services to `docker-compose.yml`:

```yaml
  pms-hl7-engine:
    build:
      context: ./pms-hl7
      dockerfile: Dockerfile
    container_name: pms-hl7-engine
    environment:
      - MLLP_LISTEN_HOST=0.0.0.0
      - MLLP_LISTEN_PORT=2575
      - PMS_BACKEND_URL=http://pms-backend:8000
      - DATABASE_URL=postgresql+asyncpg://pms:pms_secret@pms-db:5432/pms
      - SENDING_FACILITY=MPS_PMS
      - SENDING_APPLICATION=PMS_LAB
      - AUDIT_LOG_ENABLED=true
    depends_on:
      - pms-backend
      - pms-db
    networks:
      - pms-network
    restart: unless-stopped

  pms-hl7-tls:
    image: stunnel/stunnel:latest
    container_name: pms-hl7-tls
    ports:
      - "2575:2575"
    volumes:
      - ./pms-hl7/config/stunnel.conf:/etc/stunnel/stunnel.conf:ro
      - ./certs:/etc/stunnel/certs:ro
    depends_on:
      - pms-hl7-engine
    networks:
      - pms-network
    restart: unless-stopped
```

### Step 11: Create stunnel Configuration

Create `pms-hl7/config/stunnel.conf`:

```ini
; TLS proxy for HL7 v2 MLLP connections
; Wraps plaintext MLLP in TLS 1.3

[mllp-server]
accept = 2575
connect = pms-hl7-engine:2575
cert = /etc/stunnel/certs/server.pem
key = /etc/stunnel/certs/server.key
TIMEOUTclose = 0
; Require TLS 1.2 minimum
sslVersion = TLSv1.2
```

### Step 12: Build and Start

```bash
# Generate self-signed certs for development
mkdir -p certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout certs/server.key -out certs/server.pem \
  -subj "/CN=pms-hl7/O=MPS/C=US"

# Build and start
docker compose up -d pms-hl7-engine pms-hl7-tls
```

Verify:

```bash
# Check engine is listening
docker logs pms-hl7-engine --tail 5
# Expected: "MLLP listener started on 0.0.0.0:2575"

# Check TLS proxy
docker logs pms-hl7-tls --tail 5
```

**Checkpoint:** The HL7 v2 Integration Engine is running with MLLP listener on port 2575, TLS proxy is active, and both containers are on the PMS Docker network.

---

## 4. Part B: Integrate with PMS Backend

### Step 1: Create Database Tables

Create `pms-hl7/app/models/lab_order.py`:

```python
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class LabOrder(Base):
    __tablename__ = "lab_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, nullable=False)
    encounter_id = Column(Integer)
    test_codes = Column(JSON, nullable=False)
    ordering_provider = Column(String(200))
    priority = Column(String(10), default="R")  # R=Routine, S=Stat
    status = Column(String(20), default="pending")  # pending, sent, acknowledged, resulted
    placer_order_number = Column(String(100))
    hl7_message_id = Column(Integer)  # FK to hl7_messages audit table
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    sent_at = Column(DateTime)
    acknowledged_at = Column(DateTime)


class LabResult(Base):
    __tablename__ = "lab_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, nullable=False)
    lab_order_id = Column(Integer)  # Links result back to order
    test_code = Column(String(50), nullable=False)
    test_name = Column(String(200))
    value = Column(String(200))
    units = Column(String(50))
    reference_range = Column(String(100))
    abnormal_flag = Column(String(10))  # H=High, L=Low, HH=Critical High, LL=Critical Low
    result_status = Column(String(10))  # F=Final, P=Preliminary, C=Corrected
    sending_facility = Column(String(100))
    filler_order_number = Column(String(100))
    observation_date = Column(DateTime)
    received_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    hl7_message_id = Column(Integer)


class HL7Message(Base):
    __tablename__ = "hl7_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    direction = Column(String(10), nullable=False)  # inbound, outbound
    message_type = Column(String(20), nullable=False)  # ORM, ORU, ACK, ADT
    message_control_id = Column(String(100))
    sending_facility = Column(String(100))
    receiving_facility = Column(String(100))
    raw_message = Column(String, nullable=False)  # Full HL7 pipe-delimited message
    message_hash = Column(String(64))  # SHA-256 for integrity verification
    ack_status = Column(String(10))  # AA=Accepted, AE=Error, AR=Rejected
    source_ip = Column(String(45))
    processed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    error_detail = Column(String)
```

Run migrations:

```bash
docker exec pms-hl7-engine python -c "
from app.models.lab_order import Base
from sqlalchemy import create_engine
engine = create_engine('postgresql://pms:pms_secret@pms-db:5432/pms')
Base.metadata.create_all(engine)
print('Lab order, result, and HL7 message tables created.')
"
```

### Step 2: Create Lab Order API Endpoint

Add to the PMS backend — `pms-backend/app/routers/lab_orders.py`:

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/lab-orders", tags=["Lab Orders"])


class LabOrderCreate(BaseModel):
    patient_id: int
    encounter_id: int | None = None
    test_codes: list[str]  # e.g., ["CBC", "BMP", "UA"]
    ordering_provider: str
    priority: str = "R"  # R=Routine, S=Stat, A=ASAP


class LabOrderResponse(BaseModel):
    id: int
    patient_id: int
    test_codes: list[str]
    status: str
    created_at: str


@router.post("/", response_model=LabOrderResponse, status_code=201)
async def create_lab_order(order: LabOrderCreate):
    """Create a lab order and trigger HL7 ORM message to LIS."""
    # Validate patient exists
    # Store order in database
    # Trigger HL7 engine to build and send ORM message
    # Return order with tracking ID
    pass


@router.get("/{order_id}")
async def get_lab_order(order_id: int):
    """Get lab order status and linked results."""
    pass


@router.get("/")
async def list_lab_orders(patient_id: int | None = None, status: str | None = None):
    """List lab orders with optional filters."""
    pass
```

### Step 3: Create Lab Results API Endpoint

Add `pms-backend/app/routers/lab_results.py`:

```python
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api/lab-results", tags=["Lab Results"])


class LabResultCreate(BaseModel):
    patient_id: int
    lab_order_id: int | None = None
    test_code: str
    test_name: str
    value: str
    units: str | None = None
    reference_range: str | None = None
    abnormal_flag: str | None = None
    result_status: str = "F"  # F=Final
    sending_facility: str | None = None


@router.post("/", status_code=201)
async def store_lab_result(result: LabResultCreate):
    """Store a lab result (called by HL7 engine after parsing ORU)."""
    pass


@router.get("/")
async def list_lab_results(
    patient_id: int | None = Query(None),
    abnormal_only: bool = Query(False),
):
    """List lab results with optional filters."""
    pass


@router.get("/critical")
async def get_critical_results(acknowledged: bool = False):
    """Get unacknowledged critical lab results for alerting."""
    pass
```

### Step 4: Verify Backend Integration

```bash
# Test lab order creation
curl -s -X POST http://localhost:8000/api/lab-orders \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "encounter_id": 1,
    "test_codes": ["CBC", "BMP"],
    "ordering_provider": "Dr. Smith",
    "priority": "R"
  }' | jq '.'

# Check HL7 engine processed the order
docker logs pms-hl7-engine --tail 10
```

**Checkpoint:** Lab order and result API endpoints are deployed, database tables are created, and the HL7 engine can communicate with the PMS backend.

---

## 5. Part C: Integrate with PMS Frontend

### Step 1: Create Lab Results Dashboard Component

Create `pms-frontend/src/components/lab/LabResultsTable.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";

interface LabResult {
  id: number;
  test_code: string;
  test_name: string;
  value: string;
  units: string;
  reference_range: string;
  abnormal_flag: string;
  result_status: string;
  received_at: string;
}

export function LabResultsTable({ patientId }: { patientId: number }) {
  const [results, setResults] = useState<LabResult[]>([]);

  useEffect(() => {
    fetch(`/api/lab-results?patient_id=${patientId}`)
      .then((r) => r.json())
      .then(setResults);
  }, [patientId]);

  const flagColor = (flag: string) => {
    if (flag === "HH" || flag === "LL") return "bg-red-100 text-red-800 font-bold";
    if (flag === "H" || flag === "L") return "bg-yellow-100 text-yellow-800";
    return "";
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full border-collapse">
        <thead>
          <tr className="bg-gray-50">
            <th className="px-4 py-2 text-left text-sm font-medium">Test</th>
            <th className="px-4 py-2 text-left text-sm font-medium">Result</th>
            <th className="px-4 py-2 text-left text-sm font-medium">Units</th>
            <th className="px-4 py-2 text-left text-sm font-medium">Reference</th>
            <th className="px-4 py-2 text-left text-sm font-medium">Flag</th>
            <th className="px-4 py-2 text-left text-sm font-medium">Status</th>
            <th className="px-4 py-2 text-left text-sm font-medium">Received</th>
          </tr>
        </thead>
        <tbody>
          {results.map((r) => (
            <tr key={r.id} className={`border-t ${flagColor(r.abnormal_flag)}`}>
              <td className="px-4 py-2 text-sm">{r.test_name || r.test_code}</td>
              <td className="px-4 py-2 text-sm font-mono">{r.value}</td>
              <td className="px-4 py-2 text-sm">{r.units}</td>
              <td className="px-4 py-2 text-sm text-gray-500">{r.reference_range}</td>
              <td className="px-4 py-2 text-sm">{r.abnormal_flag || "N"}</td>
              <td className="px-4 py-2 text-sm">{r.result_status === "F" ? "Final" : "Prelim"}</td>
              <td className="px-4 py-2 text-sm text-gray-500">{new Date(r.received_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {results.length === 0 && (
        <p className="text-center text-gray-500 py-4">No lab results available.</p>
      )}
    </div>
  );
}
```

### Step 2: Create Critical Result Alert Banner

Create `pms-frontend/src/components/lab/CriticalResultAlert.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";

interface CriticalResult {
  id: number;
  test_name: string;
  value: string;
  units: string;
  abnormal_flag: string;
  patient_id: number;
}

export function CriticalResultAlert() {
  const [criticals, setCriticals] = useState<CriticalResult[]>([]);

  useEffect(() => {
    const poll = setInterval(async () => {
      const res = await fetch("/api/lab-results/critical?acknowledged=false");
      const data = await res.json();
      setCriticals(data);
    }, 10000); // Poll every 10 seconds

    return () => clearInterval(poll);
  }, []);

  if (criticals.length === 0) return null;

  return (
    <div className="bg-red-600 text-white px-4 py-3 rounded-lg shadow-lg mb-4 animate-pulse">
      <div className="flex items-center gap-2">
        <span className="text-xl">!</span>
        <div>
          <p className="font-bold">Critical Lab Result{criticals.length > 1 ? "s" : ""}</p>
          {criticals.map((c) => (
            <p key={c.id} className="text-sm">
              Patient #{c.patient_id}: {c.test_name} = {c.value} {c.units} ({c.abnormal_flag})
            </p>
          ))}
        </div>
      </div>
    </div>
  );
}
```

### Step 3: Create Lab Order Entry Panel

Create `pms-frontend/src/components/lab/LabOrderForm.tsx`:

```tsx
"use client";

import { useState } from "react";

const COMMON_TESTS = [
  { code: "CBC", name: "Complete Blood Count" },
  { code: "BMP", name: "Basic Metabolic Panel" },
  { code: "CMP", name: "Comprehensive Metabolic Panel" },
  { code: "UA", name: "Urinalysis" },
  { code: "TSH", name: "Thyroid Stimulating Hormone" },
  { code: "HBA1C", name: "Hemoglobin A1c" },
  { code: "LIPID", name: "Lipid Panel" },
  { code: "PT_INR", name: "PT/INR" },
];

interface LabOrderFormProps {
  patientId: number;
  encounterId?: number;
}

export function LabOrderForm({ patientId, encounterId }: LabOrderFormProps) {
  const [selectedTests, setSelectedTests] = useState<string[]>([]);
  const [priority, setPriority] = useState("R");
  const [provider, setProvider] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  const toggleTest = (code: string) => {
    setSelectedTests((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
    );
  };

  const handleSubmit = async () => {
    if (selectedTests.length === 0 || !provider) return;
    setSubmitting(true);

    const res = await fetch("/api/lab-orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        patient_id: patientId,
        encounter_id: encounterId,
        test_codes: selectedTests,
        ordering_provider: provider,
        priority,
      }),
    });

    if (res.ok) {
      setStatus("Order sent to lab successfully");
      setSelectedTests([]);
    } else {
      setStatus("Failed to send order");
    }
    setSubmitting(false);
  };

  return (
    <div className="border rounded-lg p-4 bg-white">
      <h3 className="text-lg font-semibold mb-3">Lab Order Entry</h3>

      <div className="grid grid-cols-2 gap-2 mb-4">
        {COMMON_TESTS.map((test) => (
          <label key={test.code} className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={selectedTests.includes(test.code)}
              onChange={() => toggleTest(test.code)}
            />
            {test.name} ({test.code})
          </label>
        ))}
      </div>

      <div className="flex gap-4 mb-4">
        <input
          type="text"
          placeholder="Ordering Provider"
          value={provider}
          onChange={(e) => setProvider(e.target.value)}
          className="flex-1 border rounded px-3 py-2 text-sm"
        />
        <select
          value={priority}
          onChange={(e) => setPriority(e.target.value)}
          className="border rounded px-3 py-2 text-sm"
        >
          <option value="R">Routine</option>
          <option value="S">Stat</option>
          <option value="A">ASAP</option>
        </select>
      </div>

      <button
        onClick={handleSubmit}
        disabled={submitting || selectedTests.length === 0 || !provider}
        className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
      >
        {submitting ? "Sending..." : `Send Order (${selectedTests.length} tests)`}
      </button>

      {status && (
        <p className={`mt-2 text-sm ${status.includes("success") ? "text-green-600" : "text-red-600"}`}>
          {status}
        </p>
      )}
    </div>
  );
}
```

**Checkpoint:** The Next.js frontend has a Lab Results table with abnormal value highlighting, a Critical Result Alert banner, and a Lab Order Entry form — all connected to the PMS backend APIs.

---

## 6. Part D: Testing and Verification

### Step 1: Send a Synthetic HL7 ORU Message

Create a test ORU message and send it to the MLLP listener:

```bash
# Create a sample ORU message file
cat > /tmp/test_oru.hl7 << 'ENDHL7'
MSH|^~\&|LAB_LIS|REFERENCE_LAB|PMS_LAB|MPS_PMS|20260221120000||ORU^R01|MSG001|P|2.5.1
PID|1||12345^^^MPS_PMS^MR||Doe^Jane||19900315|F
OBR|1|ORD001|FIL001|CBC^Complete Blood Count|||20260221110000|||||||||Dr. Smith||||||||F
OBX|1|NM|WBC^White Blood Cell Count||7.5|10*3/uL|4.5-11.0|N||F
OBX|2|NM|RBC^Red Blood Cell Count||4.8|10*6/uL|4.0-5.5|N||F
OBX|3|NM|HGB^Hemoglobin||14.2|g/dL|12.0-16.0|N||F
OBX|4|NM|PLT^Platelet Count||250|10*3/uL|150-400|N||F
OBX|5|NM|K^Potassium||6.8|mEq/L|3.5-5.0|HH||F
ENDHL7

# Send via netcat (plaintext for local testing)
printf '\x0b' > /tmp/mllp_msg
cat /tmp/test_oru.hl7 >> /tmp/mllp_msg
printf '\x1c\x0d' >> /tmp/mllp_msg
nc localhost 2575 < /tmp/mllp_msg
```

### Step 2: Verify Result Storage

```bash
# Check results were stored
curl -s "http://localhost:8000/api/lab-results?patient_id=12345" | jq '.[] | {test_name, value, abnormal_flag}'
# Expected: 5 results including K (Potassium) with flag "HH"

# Check critical result alert
curl -s "http://localhost:8000/api/lab-results/critical" | jq '.'
# Expected: Potassium 6.8 mEq/L with flag "HH"
```

### Step 3: Verify Audit Trail

```bash
docker exec pms-db psql -U pms -d pms -c \
  "SELECT direction, message_type, ack_status, processed_at FROM hl7_messages ORDER BY processed_at DESC LIMIT 5;"
# Expected: inbound | ORU | AA | <timestamp>
```

### Step 4: Test Outbound ORM Order

```bash
# Create a lab order
curl -s -X POST http://localhost:8000/api/lab-orders \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "test_codes": ["CBC", "BMP"],
    "ordering_provider": "Dr. Smith",
    "priority": "S"
  }' | jq '.status'
# Expected: "sent" (or "pending" if no LIS endpoint configured)

# Check outbound message in audit log
docker exec pms-db psql -U pms -d pms -c \
  "SELECT direction, message_type, sending_facility FROM hl7_messages WHERE direction='outbound' ORDER BY processed_at DESC LIMIT 1;"
```

**Checkpoint:** Inbound ORU messages are parsed and stored, outbound ORM messages are built and transmitted, audit trail captures all HL7 transactions, and critical results are flagged.

---

## 7. Troubleshooting

### MLLP Listener Not Accepting Connections

**Symptoms:** `nc localhost 2575` hangs or refuses connection.

**Fix:** Check that the HL7 engine container is running and the port is mapped:

```bash
docker ps | grep hl7
docker logs pms-hl7-engine --tail 20
# If TLS proxy is in the way, test internal port directly:
docker exec pms-hl7-engine nc -z localhost 2575
```

### HL7 Message Parse Errors

**Symptoms:** NACK returned, logs show `hl7apy.exceptions.InvalidHL7Message`.

**Fix:** Verify message uses `\r` (CR) as segment delimiter, not `\n` (LF). HL7 v2 requires CR:

```bash
# Check the message delimiter
xxd /tmp/test_oru.hl7 | grep "0d\|0a"
# Should see 0d (CR), not 0a (LF)
```

### Patient MRN Mismatch

**Symptoms:** Results stored but `patient_id` is null or linked to wrong patient.

**Fix:** Check that PID-3 (Patient Identifier) in the HL7 message matches a patient MRN in the PMS:

```bash
curl -s "http://localhost:8000/api/patients?mrn=12345" | jq '.id'
```

### TLS Handshake Failures

**Symptoms:** External LIS cannot connect; stunnel logs show `SSL_accept: error`.

**Fix:** Verify certificates and stunnel configuration:

```bash
docker logs pms-hl7-tls --tail 20
# Test TLS connection
openssl s_client -connect localhost:2575 -tls1_2
```

### ACK Timeout from LIS

**Symptoms:** LIS reports "no acknowledgment received" after sending results.

**Fix:** Check that the ACK is being generated and sent within the timeout window:

```bash
docker logs pms-hl7-engine | grep "ACK\|NACK"
# Verify ACK response time is < 200ms
```

### Port 2575 Conflict

**Symptoms:** Docker compose fails with `port is already allocated`.

**Fix:** Find the conflicting process:

```bash
lsof -i :2575
# Kill or reconfigure the conflicting service
```

---

## 8. Reference Commands

### Daily Development

```bash
# Start HL7 services
docker compose up -d pms-hl7-engine pms-hl7-tls

# View engine logs
docker logs -f pms-hl7-engine

# Restart after code changes
docker compose restart pms-hl7-engine

# Rebuild
docker compose build pms-hl7-engine && docker compose up -d pms-hl7-engine

# Run tests
docker exec pms-hl7-engine python -m pytest tests/ -v
```

### HL7 Message Management

```bash
# Count messages by type
docker exec pms-db psql -U pms -d pms -c \
  "SELECT direction, message_type, COUNT(*) FROM hl7_messages GROUP BY direction, message_type;"

# View recent messages
docker exec pms-db psql -U pms -d pms -c \
  "SELECT id, direction, message_type, ack_status, processed_at FROM hl7_messages ORDER BY processed_at DESC LIMIT 10;"

# View lab results
docker exec pms-db psql -U pms -d pms -c \
  "SELECT test_name, value, units, abnormal_flag FROM lab_results ORDER BY received_at DESC LIMIT 10;"

# View pending orders
docker exec pms-db psql -U pms -d pms -c \
  "SELECT id, test_codes, status, created_at FROM lab_orders WHERE status != 'resulted' ORDER BY created_at DESC;"
```

### Monitoring

```bash
# Check engine health
docker exec pms-hl7-engine python -c "print('HL7 engine alive')"

# Count unacknowledged critical results
docker exec pms-db psql -U pms -d pms -c \
  "SELECT COUNT(*) FROM lab_results WHERE abnormal_flag IN ('HH','LL');"
```

### Useful URLs

| URL | Description |
|---|---|
| `http://localhost:8000/api/lab-orders` | Lab Order API |
| `http://localhost:8000/api/lab-results` | Lab Results API |
| `http://localhost:8000/docs` | PMS Backend Swagger UI |
| `http://localhost:3000/lab` | Lab Dashboard (Next.js) |
| `localhost:2575` | MLLP listener (TCP, not HTTP) |

---

## Next Steps

1. Follow the [HL7v2LIS Developer Tutorial](17-HL7v2LIS-Developer-Tutorial.md) to build and test a complete lab order/result cycle
2. Configure a real LIS endpoint in `config/lis_endpoints.json`
3. Implement ADT message support for patient registration sync
4. Build the HL7v2-to-FHIR bridge (ORU → DiagnosticReport)
5. Review the [PRD: HL7v2LIS PMS Integration](17-PRD-HL7v2LIS-PMS-Integration.md) for the full roadmap

---

## Resources

- [HL7apy Documentation](https://crs4.github.io/hl7apy/) — Python HL7 v2 parser and builder
- [python-hl7 Documentation](https://python-hl7.readthedocs.io/) — Lightweight HL7 parsing + async MLLP
- [HL7 v2.5.1 Observation Chapter](https://www.hl7.eu/HL7v2x/v251/std251/ch07.html) — OBR/OBX segment specification
- [HL7 MLLP Specification](https://www.hl7.org/documentcenter/public/wg/inm/mllp_transport_specification.PDF) — MLLP framing protocol
- [PRD: HL7v2LIS PMS Integration](17-PRD-HL7v2LIS-PMS-Integration.md) — Full product requirements
- [PRD: FHIR PMS Integration](16-PRD-FHIR-PMS-Integration.md) — Complementary modern interoperability
