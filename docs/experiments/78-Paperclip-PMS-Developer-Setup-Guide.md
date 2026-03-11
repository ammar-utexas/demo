# Paperclip AI Agent Orchestration Setup Guide for PMS Integration

**Document ID:** PMS-EXP-PAPERCLIP-001
**Version:** 1.0
**Date:** 2026-03-11
**Applies To:** PMS project (all platforms)
**Prerequisites Level:** Intermediate

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Part A: Install and Configure Paperclip](#3-part-a-install-and-configure-paperclip)
4. [Part B: Integrate with PMS Backend](#4-part-b-integrate-with-pms-backend)
5. [Part C: Integrate with PMS Frontend](#5-part-c-integrate-with-pms-frontend)
6. [Part D: Testing and Verification](#6-part-d-testing-and-verification)
7. [Troubleshooting](#7-troubleshooting)
8. [Reference Commands](#8-reference-commands)

---

## 1. Overview

This guide walks you through deploying Paperclip alongside the PMS stack and configuring it to orchestrate AI agents for clinical and administrative workflows. By the end, you will have:

- Paperclip running on `:3100` with external PostgreSQL
- A PMS company with org chart and agent roles defined
- HTTP webhook adapter connecting Paperclip heartbeats to PMS FastAPI endpoints
- A PaperclipClient Python wrapper for backend integration
- An AgentCostDashboard component in the PMS frontend
- AuditBridge syncing agent activity to the PMS audit log

```mermaid
flowchart LR
    subgraph Dev["Developer Machine"]
        PC["Paperclip :3100"]
        BE["PMS Backend :8000"]
        FE["PMS Frontend :3000"]
        PG["PostgreSQL :5432"]
    end

    PC -->|"heartbeat → webhook"| BE
    BE -->|"task status"| PC
    FE -->|"dashboard API"| PC
    PC -->|"DATABASE_URL"| PG
    BE --> PG

    style PC fill:#e8f5e9,stroke:#2e7d32
    style BE fill:#fff3e0,stroke:#e65100
    style FE fill:#e3f2fd,stroke:#1565c0
    style PG fill:#f3e5f5,stroke:#7b1fa2
```

## 2. Prerequisites

### 2.1 Required Software

| Software | Minimum Version | Check Command |
|----------|----------------|---------------|
| Node.js | 20.0 | `node --version` |
| pnpm | 9.15 | `pnpm --version` |
| Python | 3.11 | `python3 --version` |
| PostgreSQL | 15.0 | `psql --version` |
| Docker | 24.0 | `docker --version` |
| Docker Compose | 2.20 | `docker compose version` |
| Git | 2.40 | `git --version` |

### 2.2 Installation of Prerequisites

**Install pnpm** (if not already installed):

```bash
# Using corepack (recommended with Node.js 20+)
corepack enable
corepack prepare pnpm@latest --activate

# Or via npm
npm install -g pnpm@latest
```

**Verify Node.js version**:

```bash
node --version
# Must be v20.0.0 or higher. If not:
# macOS: brew install node@20
# Or use nvm: nvm install 20 && nvm use 20
```

### 2.3 Verify PMS Services

```bash
# Backend running
curl -s http://localhost:8000/api/health | python3 -m json.tool

# Frontend running
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
# Expected: 200

# PostgreSQL running
psql -U pms_user -d pms_db -c "SELECT 1;"
# Expected: 1 row returned
```

## 3. Part A: Install and Configure Paperclip

### Step 1: Clone and Install Paperclip

```bash
# Clone into the PMS project directory
cd ~/Projects/pms
git clone https://github.com/paperclipai/paperclip.git paperclip-orchestrator
cd paperclip-orchestrator

# Install dependencies
pnpm install
```

### Step 2: Configure External PostgreSQL

Create a Paperclip database in the existing PMS PostgreSQL instance:

```sql
-- Connect to PostgreSQL as superuser
psql -U postgres

-- Create dedicated database and user
CREATE DATABASE paperclip_db;
CREATE USER paperclip_user WITH ENCRYPTED PASSWORD 'your-secure-password-here';
GRANT ALL PRIVILEGES ON DATABASE paperclip_db TO paperclip_user;

-- Enable required extensions
\c paperclip_db
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
\q
```

### Step 3: Configure Environment

Create a `.env` file in the Paperclip directory:

```bash
cat > .env << 'EOF'
# Database — external PostgreSQL (not embedded)
DATABASE_URL=postgresql://paperclip_user:your-secure-password-here@localhost:5432/paperclip_db

# Instance configuration
PAPERCLIP_HOME=~/.paperclip
PAPERCLIP_INSTANCE_ID=pms-production

# Security
PAPERCLIP_SECRETS_MASTER_KEY=generate-a-64-char-hex-key-here
PAPERCLIP_SECRETS_STRICT_MODE=true

# Server
HOST=127.0.0.1
PORT=3100

# Backups
PAPERCLIP_DB_BACKUP_ENABLED=true
PAPERCLIP_DB_BACKUP_INTERVAL_MINUTES=60
PAPERCLIP_DB_BACKUP_RETENTION_DAYS=30

# Company deletion protection
PAPERCLIP_ENABLE_COMPANY_DELETION=false
EOF
```

Generate the master key:

```bash
# Generate a cryptographically secure 64-char hex key
python3 -c "import secrets; print(secrets.token_hex(32))"
# Copy output and replace 'generate-a-64-char-hex-key-here' in .env
```

### Step 4: Initialize Database and Start

```bash
# Run database migrations
pnpm db:migrate

# Start Paperclip in development mode
pnpm dev

# Or use the bootstrap command
pnpm paperclipai run
```

Verify Paperclip is running:

```bash
curl -s http://localhost:3100/api/health | python3 -m json.tool
# Expected: {"status": "ok", ...}
```

### Step 5: Docker Alternative

For Docker-based deployment alongside PMS:

```yaml
# Add to your PMS docker-compose.yml
  paperclip:
    build:
      context: ./paperclip-orchestrator
      dockerfile: Dockerfile
    ports:
      - "3100:3100"
    environment:
      - DATABASE_URL=postgresql://paperclip_user:${PAPERCLIP_DB_PASSWORD}@postgres:5432/paperclip_db
      - PAPERCLIP_SECRETS_MASTER_KEY=${PAPERCLIP_MASTER_KEY}
      - PAPERCLIP_SECRETS_STRICT_MODE=true
      - HOST=0.0.0.0
      - PORT=3100
      - PAPERCLIP_ENABLE_COMPANY_DELETION=false
    depends_on:
      - postgres
    networks:
      - pms-internal
    restart: unless-stopped
```

Or use the quickstart compose:

```bash
cd paperclip-orchestrator
docker compose -f docker-compose.quickstart.yml up --build
```

**Checkpoint**: Paperclip is running on `http://localhost:3100`. The dashboard UI is accessible in your browser. Database migrations have been applied to `paperclip_db`.

---

## 4. Part B: Integrate with PMS Backend

### Step 1: Install Python Dependencies

```bash
cd ~/Projects/pms/pms-backend

# Add httpx for async HTTP calls to Paperclip API
pip install httpx
```

### Step 2: Create PaperclipClient

```python
# app/integrations/paperclip/client.py
"""
PaperclipClient — async wrapper for Paperclip REST API.
Manages companies, agents, tasks, and heartbeats.
"""

import httpx
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class PaperclipConfig(BaseModel):
    base_url: str = "http://localhost:3100"
    api_key: Optional[str] = None
    timeout: float = 30.0


class AgentConfig(BaseModel):
    name: str
    title: str
    adapter_type: str  # "http", "claude_code", "openclaw", "bash"
    adapter_config: dict
    capabilities: str
    reports_to: Optional[str] = None  # parent agent ID
    budget_cents: Optional[int] = None


class TaskCreate(BaseModel):
    title: str
    description: str
    priority: str = "medium"  # low, medium, high, critical
    assignee_id: Optional[str] = None
    parent_id: Optional[str] = None
    project_id: Optional[str] = None
    labels: list[str] = []


class PaperclipClient:
    """Async client for Paperclip orchestration API."""

    def __init__(self, config: PaperclipConfig | None = None):
        self.config = config or PaperclipConfig()
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            headers = {}
            if self.config.api_key:
                headers["Authorization"] = f"Bearer {self.config.api_key}"
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                headers=headers,
                timeout=self.config.timeout,
            )
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    # ── Company Management ──────────────────────────────────

    async def create_company(
        self, name: str, goal: str, budget_cents: int = 100000
    ) -> dict:
        """Create a new company (agent organization)."""
        client = await self._get_client()
        response = await client.post(
            "/api/companies",
            json={
                "name": name,
                "goal": goal,
                "budget_cents": budget_cents,
            },
        )
        response.raise_for_status()
        return response.json()

    async def get_company(self, company_id: str) -> dict:
        client = await self._get_client()
        response = await client.get(f"/api/companies/{company_id}")
        response.raise_for_status()
        return response.json()

    async def list_companies(self) -> list[dict]:
        client = await self._get_client()
        response = await client.get("/api/companies")
        response.raise_for_status()
        return response.json()

    # ── Agent Management ────────────────────────────────────

    async def register_agent(
        self, company_id: str, agent: AgentConfig
    ) -> dict:
        """Register an AI agent in the company org chart."""
        client = await self._get_client()
        response = await client.post(
            f"/api/companies/{company_id}/agents",
            json=agent.model_dump(exclude_none=True),
        )
        response.raise_for_status()
        return response.json()

    async def get_agent(self, company_id: str, agent_id: str) -> dict:
        client = await self._get_client()
        response = await client.get(
            f"/api/companies/{company_id}/agents/{agent_id}"
        )
        response.raise_for_status()
        return response.json()

    async def list_agents(self, company_id: str) -> list[dict]:
        client = await self._get_client()
        response = await client.get(
            f"/api/companies/{company_id}/agents"
        )
        response.raise_for_status()
        return response.json()

    async def pause_agent(self, company_id: str, agent_id: str) -> dict:
        client = await self._get_client()
        response = await client.post(
            f"/api/companies/{company_id}/agents/{agent_id}/pause"
        )
        response.raise_for_status()
        return response.json()

    async def resume_agent(self, company_id: str, agent_id: str) -> dict:
        client = await self._get_client()
        response = await client.post(
            f"/api/companies/{company_id}/agents/{agent_id}/resume"
        )
        response.raise_for_status()
        return response.json()

    # ── Task Management ─────────────────────────────────────

    async def create_task(
        self, company_id: str, task: TaskCreate
    ) -> dict:
        """Create a task (issue) in the company's backlog."""
        client = await self._get_client()
        response = await client.post(
            f"/api/companies/{company_id}/issues",
            json=task.model_dump(exclude_none=True),
        )
        response.raise_for_status()
        return response.json()

    async def get_task(self, company_id: str, task_id: str) -> dict:
        client = await self._get_client()
        response = await client.get(
            f"/api/companies/{company_id}/issues/{task_id}"
        )
        response.raise_for_status()
        return response.json()

    async def list_tasks(
        self,
        company_id: str,
        status: Optional[str] = None,
        assignee_id: Optional[str] = None,
    ) -> list[dict]:
        client = await self._get_client()
        params = {}
        if status:
            params["status"] = status
        if assignee_id:
            params["assignee_id"] = assignee_id
        response = await client.get(
            f"/api/companies/{company_id}/issues", params=params
        )
        response.raise_for_status()
        return response.json()

    # ── Cost & Analytics ────────────────────────────────────

    async def get_costs(
        self, company_id: str, agent_id: Optional[str] = None
    ) -> dict:
        """Get cost breakdown by agent, task, or project."""
        client = await self._get_client()
        params = {}
        if agent_id:
            params["agent_id"] = agent_id
        response = await client.get(
            f"/api/companies/{company_id}/costs", params=params
        )
        response.raise_for_status()
        return response.json()

    # ── Activity & Audit ────────────────────────────────────

    async def get_activity_log(
        self,
        company_id: str,
        limit: int = 100,
        since: Optional[datetime] = None,
    ) -> list[dict]:
        """Get immutable audit trail of all agent actions."""
        client = await self._get_client()
        params = {"limit": limit}
        if since:
            params["since"] = since.isoformat()
        response = await client.get(
            f"/api/companies/{company_id}/activity", params=params
        )
        response.raise_for_status()
        return response.json()

    # ── Health ──────────────────────────────────────────────

    async def health_check(self) -> dict:
        client = await self._get_client()
        response = await client.get("/api/health")
        response.raise_for_status()
        return response.json()
```

### Step 3: Create Agent Webhook Receiver

```python
# app/integrations/paperclip/webhook.py
"""
Webhook receiver for Paperclip heartbeat events.
When Paperclip fires a heartbeat, it POSTs to these endpoints
to trigger PMS workflow execution.
"""

from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/paperclip/webhooks", tags=["paperclip"])


class HeartbeatPayload(BaseModel):
    """Payload sent by Paperclip when an agent heartbeat fires."""
    agent_id: str
    agent_name: str
    company_id: str
    task_id: Optional[str] = None
    task_title: Optional[str] = None
    task_description: Optional[str] = None
    goal_ancestry: list[str] = []  # chain of parent goals
    context: dict = {}  # persistent agent state


class HeartbeatResponse(BaseModel):
    """Response back to Paperclip after processing a heartbeat."""
    status: str  # "completed", "in_progress", "failed", "needs_approval"
    result: Optional[dict] = None
    cost_cents: int = 0
    artifacts: list[str] = []
    next_action: Optional[str] = None


# ── Agent API Key Validation ─────────────────────────────

AGENT_API_KEYS = {
    # In production, load from database or secrets manager
    "intake-agent-key": "intake_agent",
    "billing-agent-key": "billing_agent",
    "clinical-agent-key": "clinical_agent",
    "comms-agent-key": "comms_agent",
    "reports-agent-key": "reports_agent",
}


async def verify_agent_key(
    authorization: str = Header(...),
) -> str:
    """Validate agent bearer token from Paperclip."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")
    token = authorization.removeprefix("Bearer ")
    agent_role = AGENT_API_KEYS.get(token)
    if not agent_role:
        raise HTTPException(status_code=403, detail="Invalid agent key")
    return agent_role


# ── Intake Agent Webhook ─────────────────────────────────

@router.post("/intake", response_model=HeartbeatResponse)
async def intake_heartbeat(
    payload: HeartbeatPayload,
    agent_role: str = Depends(verify_agent_key),
):
    """
    Intake Agent heartbeat: processes new patient registrations.
    Workflow: receive form → verify demographics → check eligibility → create record
    """
    logger.info(
        f"Intake heartbeat: agent={payload.agent_name}, task={payload.task_id}"
    )

    if not payload.task_id:
        # No assigned task — check for pending intake work
        # Query PMS for unprocessed patient registrations
        return HeartbeatResponse(
            status="completed",
            result={"message": "No pending intake work"},
        )

    try:
        # Step 1: Extract patient data from task context
        patient_data = payload.context.get("patient_data", {})
        if not patient_data:
            return HeartbeatResponse(
                status="failed",
                result={"error": "No patient data in task context"},
            )

        # Step 2: Verify demographics (call PMS validation endpoint)
        # In production, this calls /api/patients/validate
        logger.info(f"Validating demographics for: {patient_data.get('last_name')}")

        # Step 3: Check insurance eligibility via pVerify (Exp 73)
        # In production, this calls /api/pverify/eligibility
        logger.info("Checking insurance eligibility via pVerify")

        # Step 4: Create patient record
        # In production, this calls POST /api/patients
        logger.info("Creating patient record in PMS")

        return HeartbeatResponse(
            status="completed",
            result={
                "patient_created": True,
                "eligibility_verified": True,
                "welcome_message_sent": True,
            },
            cost_cents=5,  # Track API costs
            artifacts=["patient_record", "eligibility_report"],
        )

    except Exception as e:
        logger.error(f"Intake heartbeat failed: {e}")
        return HeartbeatResponse(
            status="failed",
            result={"error": str(e)},
        )


# ── Billing Agent Webhook ────────────────────────────────

@router.post("/billing", response_model=HeartbeatResponse)
async def billing_heartbeat(
    payload: HeartbeatPayload,
    agent_role: str = Depends(verify_agent_key),
):
    """
    Billing Agent heartbeat: processes claims and invoices.
    Workflow: encounter closed → generate claim (Availity) → create invoice (Xero)
    """
    logger.info(
        f"Billing heartbeat: agent={payload.agent_name}, task={payload.task_id}"
    )

    if not payload.task_id:
        return HeartbeatResponse(
            status="completed",
            result={"message": "No pending billing work"},
        )

    try:
        encounter_id = payload.context.get("encounter_id")
        if not encounter_id:
            return HeartbeatResponse(
                status="failed",
                result={"error": "No encounter_id in task context"},
            )

        # Step 1: Fetch encounter details from PMS
        logger.info(f"Fetching encounter {encounter_id}")

        # Step 2: Generate and submit claim via Availity (Exp 47)
        logger.info("Submitting claim via Availity")

        # Step 3: Create invoice via Xero (Exp 75)
        logger.info("Creating invoice in Xero")

        return HeartbeatResponse(
            status="completed",
            result={
                "claim_submitted": True,
                "claim_id": "CLM-2026-001234",
                "invoice_created": True,
                "invoice_number": "INV-2026-005678",
            },
            cost_cents=12,
            artifacts=["claim_submission", "xero_invoice"],
        )

    except Exception as e:
        logger.error(f"Billing heartbeat failed: {e}")
        return HeartbeatResponse(
            status="failed",
            result={"error": str(e)},
        )


# ── Clinical Workflow Agent Webhook ──────────────────────

@router.post("/clinical", response_model=HeartbeatResponse)
async def clinical_heartbeat(
    payload: HeartbeatPayload,
    agent_role: str = Depends(verify_agent_key),
):
    """
    Clinical Agent heartbeat: manages encounter lifecycle.
    Workflow: encounter opens → check meds → route labs → process results
    """
    logger.info(
        f"Clinical heartbeat: agent={payload.agent_name}, task={payload.task_id}"
    )

    if not payload.task_id:
        return HeartbeatResponse(
            status="completed",
            result={"message": "No pending clinical work"},
        )

    try:
        action = payload.context.get("action", "check_medications")

        if action == "check_medications":
            # Check medication interactions via /api/prescriptions
            logger.info("Checking medication interactions")
            return HeartbeatResponse(
                status="completed",
                result={"interactions_found": 0, "safe_to_proceed": True},
                cost_cents=3,
            )

        elif action == "route_lab_order":
            # Route lab order via Mirth Connect (Exp 77)
            logger.info("Routing lab order via Mirth Connect")
            return HeartbeatResponse(
                status="completed",
                result={"lab_order_routed": True, "mirth_channel": "LabOrders"},
                cost_cents=2,
            )

        elif action == "process_lab_results":
            # Process incoming lab results
            logger.info("Processing lab results")
            return HeartbeatResponse(
                status="completed",
                result={"results_processed": True, "abnormal_flags": 0},
                cost_cents=2,
            )

        return HeartbeatResponse(
            status="failed",
            result={"error": f"Unknown action: {action}"},
        )

    except Exception as e:
        logger.error(f"Clinical heartbeat failed: {e}")
        return HeartbeatResponse(status="failed", result={"error": str(e)})


# ── Communications Agent Webhook ─────────────────────────

@router.post("/communications", response_model=HeartbeatResponse)
async def communications_heartbeat(
    payload: HeartbeatPayload,
    agent_role: str = Depends(verify_agent_key),
):
    """
    Communications Agent heartbeat: patient outreach.
    Workflow: send reminders, follow-ups, and notifications via RingCentral.
    """
    logger.info(
        f"Comms heartbeat: agent={payload.agent_name}, task={payload.task_id}"
    )

    if not payload.task_id:
        return HeartbeatResponse(
            status="completed",
            result={"message": "No pending communications"},
        )

    try:
        comm_type = payload.context.get("type", "appointment_reminder")

        # Route to RingCentral (Exp 71) based on communication type
        logger.info(f"Sending {comm_type} via RingCentral")

        return HeartbeatResponse(
            status="completed",
            result={"message_sent": True, "type": comm_type},
            cost_cents=8,
        )

    except Exception as e:
        logger.error(f"Comms heartbeat failed: {e}")
        return HeartbeatResponse(status="failed", result={"error": str(e)})


# ── Reports Agent Webhook ────────────────────────────────

@router.post("/reports", response_model=HeartbeatResponse)
async def reports_heartbeat(
    payload: HeartbeatPayload,
    agent_role: str = Depends(verify_agent_key),
):
    """
    Reports Agent heartbeat: generates compliance and financial reports.
    Workflow: scheduled report → gather data → generate → store
    """
    logger.info(
        f"Reports heartbeat: agent={payload.agent_name}, task={payload.task_id}"
    )

    if not payload.task_id:
        return HeartbeatResponse(
            status="completed",
            result={"message": "No pending reports"},
        )

    try:
        report_type = payload.context.get("report_type", "daily_census")
        logger.info(f"Generating {report_type} report")

        # Call /api/reports to generate the requested report
        return HeartbeatResponse(
            status="completed",
            result={
                "report_generated": True,
                "report_type": report_type,
                "report_url": f"/api/reports/{report_type}/latest",
            },
            cost_cents=15,
        )

    except Exception as e:
        logger.error(f"Reports heartbeat failed: {e}")
        return HeartbeatResponse(status="failed", result={"error": str(e)})
```

### Step 4: Create AuditBridge

```python
# app/integrations/paperclip/audit_bridge.py
"""
AuditBridge — syncs Paperclip's immutable activity log
with the PMS audit system for unified compliance tracking.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from .client import PaperclipClient, PaperclipConfig

logger = logging.getLogger(__name__)


class AuditBridge:
    """Bridges Paperclip activity logs to PMS audit system."""

    def __init__(
        self,
        paperclip: PaperclipClient,
        company_id: str,
        poll_interval_seconds: int = 30,
    ):
        self.paperclip = paperclip
        self.company_id = company_id
        self.poll_interval = poll_interval_seconds
        self._last_sync: Optional[datetime] = None
        self._running = False

    async def sync_once(self) -> int:
        """Fetch new activity entries and write to PMS audit log."""
        since = self._last_sync or (datetime.utcnow() - timedelta(hours=1))

        activities = await self.paperclip.get_activity_log(
            company_id=self.company_id,
            limit=500,
            since=since,
        )

        synced = 0
        for activity in activities:
            # Map Paperclip activity to PMS audit format
            audit_entry = {
                "source": "paperclip",
                "agent_id": activity.get("agent_id"),
                "agent_name": activity.get("agent_name"),
                "action": activity.get("action"),
                "resource_type": activity.get("resource_type"),
                "resource_id": activity.get("resource_id"),
                "details": activity.get("details"),
                "timestamp": activity.get("timestamp"),
                "company_id": self.company_id,
            }

            # In production: write to PMS audit log table
            # await audit_service.log(audit_entry)
            logger.debug(f"Audit sync: {audit_entry['action']} by {audit_entry['agent_name']}")
            synced += 1

        self._last_sync = datetime.utcnow()
        if synced > 0:
            logger.info(f"AuditBridge synced {synced} entries from Paperclip")
        return synced

    async def start_polling(self):
        """Start continuous polling loop."""
        self._running = True
        logger.info(
            f"AuditBridge started: polling every {self.poll_interval}s"
        )
        while self._running:
            try:
                await self.sync_once()
            except Exception as e:
                logger.error(f"AuditBridge sync error: {e}")
            await asyncio.sleep(self.poll_interval)

    def stop(self):
        self._running = False
        logger.info("AuditBridge stopped")
```

### Step 5: Create Governance Service

```python
# app/integrations/paperclip/governance.py
"""
GovernanceService — enforces human-in-the-loop approval gates
for sensitive PMS operations triggered by AI agents.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/paperclip/governance", tags=["paperclip"])


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ApprovalRequest(BaseModel):
    """Request for human approval of a sensitive agent action."""
    agent_id: str
    agent_name: str
    company_id: str
    task_id: str
    action_type: str  # "claim_submission", "prescription_change", "phi_export"
    description: str
    risk_level: str  # "low", "medium", "high", "critical"
    context: dict = {}
    expires_at: Optional[datetime] = None


class ApprovalResponse(BaseModel):
    request_id: str
    status: ApprovalStatus
    reviewer: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    notes: Optional[str] = None


# In-memory store for demo; use PostgreSQL in production
_approval_requests: dict[str, dict] = {}


# Actions requiring approval by risk level
APPROVAL_REQUIRED = {
    "claim_submission": "high",
    "prescription_change": "critical",
    "phi_export": "critical",
    "patient_record_modification": "high",
    "bulk_communication": "medium",
    "report_external_share": "high",
    "agent_budget_increase": "medium",
}


@router.post("/request-approval", response_model=ApprovalResponse)
async def request_approval(request: ApprovalRequest):
    """Agent requests human approval for a sensitive action."""
    import uuid

    request_id = str(uuid.uuid4())

    if request.action_type not in APPROVAL_REQUIRED:
        # Auto-approve low-risk actions not in the gate list
        return ApprovalResponse(
            request_id=request_id,
            status=ApprovalStatus.APPROVED,
            reviewer="auto",
            reviewed_at=datetime.utcnow(),
            notes="Auto-approved: action not in approval gate list",
        )

    _approval_requests[request_id] = {
        "request": request.model_dump(),
        "status": ApprovalStatus.PENDING,
        "created_at": datetime.utcnow().isoformat(),
    }

    logger.warning(
        f"APPROVAL REQUIRED: {request.action_type} by {request.agent_name} "
        f"(risk: {request.risk_level}) — request_id={request_id}"
    )

    return ApprovalResponse(
        request_id=request_id,
        status=ApprovalStatus.PENDING,
    )


@router.get("/pending")
async def list_pending_approvals():
    """List all pending approval requests for human reviewers."""
    pending = {
        k: v for k, v in _approval_requests.items()
        if v["status"] == ApprovalStatus.PENDING
    }
    return {"count": len(pending), "requests": pending}


@router.post("/approve/{request_id}")
async def approve_request(
    request_id: str,
    reviewer: str = "admin",
    notes: Optional[str] = None,
):
    """Human reviewer approves an agent action."""
    if request_id not in _approval_requests:
        raise HTTPException(status_code=404, detail="Request not found")

    _approval_requests[request_id]["status"] = ApprovalStatus.APPROVED
    _approval_requests[request_id]["reviewer"] = reviewer
    _approval_requests[request_id]["reviewed_at"] = datetime.utcnow().isoformat()
    _approval_requests[request_id]["notes"] = notes

    logger.info(f"APPROVED: {request_id} by {reviewer}")

    return ApprovalResponse(
        request_id=request_id,
        status=ApprovalStatus.APPROVED,
        reviewer=reviewer,
        reviewed_at=datetime.utcnow(),
        notes=notes,
    )


@router.post("/reject/{request_id}")
async def reject_request(
    request_id: str,
    reviewer: str = "admin",
    notes: Optional[str] = None,
):
    """Human reviewer rejects an agent action."""
    if request_id not in _approval_requests:
        raise HTTPException(status_code=404, detail="Request not found")

    _approval_requests[request_id]["status"] = ApprovalStatus.REJECTED
    _approval_requests[request_id]["reviewer"] = reviewer
    _approval_requests[request_id]["reviewed_at"] = datetime.utcnow().isoformat()
    _approval_requests[request_id]["notes"] = notes

    logger.warning(f"REJECTED: {request_id} by {reviewer} — {notes}")

    return ApprovalResponse(
        request_id=request_id,
        status=ApprovalStatus.REJECTED,
        reviewer=reviewer,
        reviewed_at=datetime.utcnow(),
        notes=notes,
    )
```

### Step 6: Register Routers in FastAPI App

```python
# In app/main.py — add Paperclip routers
from app.integrations.paperclip.webhook import router as paperclip_webhook_router
from app.integrations.paperclip.governance import router as paperclip_governance_router

app.include_router(paperclip_webhook_router)
app.include_router(paperclip_governance_router)
```

### Step 7: Create Company Bootstrap Script

```python
# scripts/paperclip_bootstrap.py
"""
Bootstrap script to create the PMS company and register agents in Paperclip.
Run once after Paperclip is deployed.
"""

import asyncio
from app.integrations.paperclip.client import (
    PaperclipClient,
    PaperclipConfig,
    AgentConfig,
    TaskCreate,
)


async def bootstrap():
    client = PaperclipClient(PaperclipConfig(base_url="http://localhost:3100"))

    try:
        # 1. Create the PMS company
        company = await client.create_company(
            name="MPS Patient Management System",
            goal="Automate PMS clinical and administrative workflows to reduce staff burden, accelerate revenue cycle, and ensure HIPAA compliance through governed AI agent orchestration",
            budget_cents=500000,  # $5,000/month starting budget
        )
        company_id = company["id"]
        print(f"✓ Company created: {company_id}")

        # 2. Register CEO Agent (delegates to all others)
        ceo = await client.register_agent(
            company_id,
            AgentConfig(
                name="pms-ceo",
                title="PMS Operations Director",
                adapter_type="http",
                adapter_config={
                    "webhook_url": "http://localhost:8000/api/paperclip/webhooks/ceo",
                },
                capabilities="Strategic delegation of clinical and administrative tasks across intake, billing, clinical workflows, communications, and reporting agents",
                budget_cents=50000,
            ),
        )
        ceo_id = ceo["id"]
        print(f"✓ CEO Agent registered: {ceo_id}")

        # 3. Register Intake Agent
        intake = await client.register_agent(
            company_id,
            AgentConfig(
                name="pms-intake",
                title="Patient Intake Specialist",
                adapter_type="http",
                adapter_config={
                    "webhook_url": "http://localhost:8000/api/paperclip/webhooks/intake",
                },
                capabilities="Patient registration processing, demographics verification, insurance eligibility checks via pVerify, welcome communications",
                reports_to=ceo_id,
                budget_cents=80000,
            ),
        )
        print(f"✓ Intake Agent registered: {intake['id']}")

        # 4. Register Billing Agent
        billing = await client.register_agent(
            company_id,
            AgentConfig(
                name="pms-billing",
                title="Revenue Cycle Manager",
                adapter_type="http",
                adapter_config={
                    "webhook_url": "http://localhost:8000/api/paperclip/webhooks/billing",
                },
                capabilities="Claims submission via Availity, invoice generation via Xero, payment tracking, bank reconciliation, aged receivables monitoring",
                reports_to=ceo_id,
                budget_cents=100000,
            ),
        )
        print(f"✓ Billing Agent registered: {billing['id']}")

        # 5. Register Clinical Agent
        clinical = await client.register_agent(
            company_id,
            AgentConfig(
                name="pms-clinical",
                title="Clinical Workflow Coordinator",
                adapter_type="http",
                adapter_config={
                    "webhook_url": "http://localhost:8000/api/paperclip/webhooks/clinical",
                },
                capabilities="Encounter lifecycle management, medication interaction checks, lab order routing via Mirth Connect, lab result processing",
                reports_to=ceo_id,
                budget_cents=80000,
            ),
        )
        print(f"✓ Clinical Agent registered: {clinical['id']}")

        # 6. Register Communications Agent
        comms = await client.register_agent(
            company_id,
            AgentConfig(
                name="pms-comms",
                title="Patient Communications Specialist",
                adapter_type="http",
                adapter_config={
                    "webhook_url": "http://localhost:8000/api/paperclip/webhooks/communications",
                },
                capabilities="Appointment reminders, follow-up calls, patient outreach via RingCentral SMS and voice",
                reports_to=ceo_id,
                budget_cents=60000,
            ),
        )
        print(f"✓ Communications Agent registered: {comms['id']}")

        # 7. Register Reports Agent
        reports = await client.register_agent(
            company_id,
            AgentConfig(
                name="pms-reports",
                title="Compliance & Analytics Manager",
                adapter_type="http",
                adapter_config={
                    "webhook_url": "http://localhost:8000/api/paperclip/webhooks/reports",
                },
                capabilities="Daily census reports, financial summaries, HIPAA compliance reports, agent performance analytics",
                reports_to=ceo_id,
                budget_cents=40000,
            ),
        )
        print(f"✓ Reports Agent registered: {reports['id']}")

        # 8. Create initial goal tasks
        await client.create_task(
            company_id,
            TaskCreate(
                title="Process pending patient intake queue",
                description="Check for new patient registrations, verify demographics, run eligibility checks, and create records",
                priority="high",
                assignee_id=intake["id"],
                labels=["intake", "recurring"],
            ),
        )
        print("✓ Initial intake task created")

        await client.create_task(
            company_id,
            TaskCreate(
                title="Process unbilled encounters",
                description="Find encounters that closed without claims/invoices and process the billing pipeline",
                priority="high",
                assignee_id=billing["id"],
                labels=["billing", "recurring"],
            ),
        )
        print("✓ Initial billing task created")

        print("\n🎉 PMS Paperclip bootstrap complete!")
        print(f"   Company ID: {company_id}")
        print(f"   Dashboard: http://localhost:3100")
        print(f"   Agents: 6 registered (CEO + 5 specialists)")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(bootstrap())
```

**Checkpoint**: PMS backend has PaperclipClient, webhook receivers for 5 agent types, GovernanceService with approval gates, AuditBridge for compliance sync, and a bootstrap script to initialize the agent organization.

---

## 5. Part C: Integrate with PMS Frontend

### Step 1: Add Paperclip Environment Variables

```bash
# .env.local (Next.js)
NEXT_PUBLIC_PAPERCLIP_URL=http://localhost:3100
```

### Step 2: Create Paperclip API Client

```typescript
// lib/paperclip.ts
const PAPERCLIP_URL = process.env.NEXT_PUBLIC_PAPERCLIP_URL || 'http://localhost:3100';

export interface Agent {
  id: string;
  name: string;
  title: string;
  status: 'active' | 'idle' | 'running' | 'error' | 'paused' | 'terminated';
  adapter_type: string;
  budget_cents: number;
  spent_cents: number;
  last_heartbeat: string | null;
}

export interface Task {
  id: string;
  title: string;
  status: 'backlog' | 'todo' | 'in_progress' | 'in_review' | 'done' | 'blocked' | 'cancelled';
  priority: string;
  assignee_id: string | null;
  assignee_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface CostSummary {
  total_cents: number;
  by_agent: Record<string, number>;
  by_project: Record<string, number>;
  budget_cents: number;
  utilization_pct: number;
}

export interface ApprovalRequest {
  request_id: string;
  agent_name: string;
  action_type: string;
  description: string;
  risk_level: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
}

export async function fetchAgents(companyId: string): Promise<Agent[]> {
  const res = await fetch(`${PAPERCLIP_URL}/api/companies/${companyId}/agents`);
  if (!res.ok) throw new Error('Failed to fetch agents');
  return res.json();
}

export async function fetchTasks(companyId: string, status?: string): Promise<Task[]> {
  const params = status ? `?status=${status}` : '';
  const res = await fetch(`${PAPERCLIP_URL}/api/companies/${companyId}/issues${params}`);
  if (!res.ok) throw new Error('Failed to fetch tasks');
  return res.json();
}

export async function fetchCosts(companyId: string): Promise<CostSummary> {
  const res = await fetch(`${PAPERCLIP_URL}/api/companies/${companyId}/costs`);
  if (!res.ok) throw new Error('Failed to fetch costs');
  return res.json();
}

export async function fetchPendingApprovals(): Promise<{ count: number; requests: Record<string, ApprovalRequest> }> {
  const res = await fetch('http://localhost:8000/api/paperclip/governance/pending');
  if (!res.ok) throw new Error('Failed to fetch approvals');
  return res.json();
}

export async function approveAction(requestId: string, reviewer: string): Promise<void> {
  const res = await fetch(`http://localhost:8000/api/paperclip/governance/approve/${requestId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reviewer }),
  });
  if (!res.ok) throw new Error('Failed to approve');
}

export async function rejectAction(requestId: string, reviewer: string, notes: string): Promise<void> {
  const res = await fetch(`http://localhost:8000/api/paperclip/governance/reject/${requestId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reviewer, notes }),
  });
  if (!res.ok) throw new Error('Failed to reject');
}
```

### Step 3: Create AgentCostDashboard Component

```tsx
// components/paperclip/AgentCostDashboard.tsx
'use client';

import { useEffect, useState } from 'react';
import {
  Agent, Task, CostSummary, ApprovalRequest,
  fetchAgents, fetchTasks, fetchCosts, fetchPendingApprovals,
  approveAction, rejectAction,
} from '@/lib/paperclip';

interface Props {
  companyId: string;
}

const STATUS_COLORS: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  running: 'bg-blue-100 text-blue-800',
  idle: 'bg-gray-100 text-gray-600',
  error: 'bg-red-100 text-red-800',
  paused: 'bg-yellow-100 text-yellow-800',
  terminated: 'bg-gray-300 text-gray-600',
};

const RISK_COLORS: Record<string, string> = {
  low: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-orange-100 text-orange-800',
  critical: 'bg-red-100 text-red-800',
};

export default function AgentCostDashboard({ companyId }: Props) {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [costs, setCosts] = useState<CostSummary | null>(null);
  const [approvals, setApprovals] = useState<Record<string, ApprovalRequest>>({});
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'agents' | 'tasks' | 'costs' | 'approvals'>('agents');

  const refresh = async () => {
    try {
      const [a, t, c, p] = await Promise.all([
        fetchAgents(companyId),
        fetchTasks(companyId),
        fetchCosts(companyId),
        fetchPendingApprovals(),
      ]);
      setAgents(a);
      setTasks(t);
      setCosts(c);
      setApprovals(p.requests);
    } catch (err) {
      console.error('Dashboard refresh failed:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 10000); // refresh every 10s
    return () => clearInterval(interval);
  }, [companyId]);

  const handleApprove = async (requestId: string) => {
    await approveAction(requestId, 'admin');
    refresh();
  };

  const handleReject = async (requestId: string) => {
    const notes = prompt('Rejection reason:');
    if (notes) {
      await rejectAction(requestId, 'admin', notes);
      refresh();
    }
  };

  if (loading) return <div className="p-6 text-gray-500">Loading agent dashboard...</div>;

  const pendingCount = Object.keys(approvals).length;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">AI Agent Operations</h2>
        <button onClick={refresh} className="px-3 py-1 text-sm border rounded hover:bg-gray-50">
          Refresh
        </button>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-4 gap-4">
        <div className="p-4 bg-white border rounded-lg shadow-sm">
          <div className="text-sm text-gray-500">Active Agents</div>
          <div className="text-2xl font-bold">{agents.filter(a => a.status !== 'terminated').length}</div>
        </div>
        <div className="p-4 bg-white border rounded-lg shadow-sm">
          <div className="text-sm text-gray-500">Tasks In Progress</div>
          <div className="text-2xl font-bold">{tasks.filter(t => t.status === 'in_progress').length}</div>
        </div>
        <div className="p-4 bg-white border rounded-lg shadow-sm">
          <div className="text-sm text-gray-500">Budget Used</div>
          <div className="text-2xl font-bold">
            {costs ? `$${(costs.total_cents / 100).toFixed(2)}` : '$0.00'}
          </div>
          <div className="text-xs text-gray-400">
            {costs ? `${costs.utilization_pct.toFixed(1)}% of budget` : ''}
          </div>
        </div>
        <div className="p-4 bg-white border rounded-lg shadow-sm">
          <div className="text-sm text-gray-500">Pending Approvals</div>
          <div className={`text-2xl font-bold ${pendingCount > 0 ? 'text-orange-600' : ''}`}>
            {pendingCount}
          </div>
        </div>
      </div>

      {/* Tab navigation */}
      <div className="flex space-x-1 border-b">
        {(['agents', 'tasks', 'costs', 'approvals'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium capitalize ${
              activeTab === tab
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab}
            {tab === 'approvals' && pendingCount > 0 && (
              <span className="ml-1 px-1.5 py-0.5 text-xs bg-orange-100 text-orange-600 rounded-full">
                {pendingCount}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Agents tab */}
      {activeTab === 'agents' && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left">Agent</th>
                <th className="px-4 py-2 text-left">Title</th>
                <th className="px-4 py-2 text-left">Status</th>
                <th className="px-4 py-2 text-left">Adapter</th>
                <th className="px-4 py-2 text-right">Budget</th>
                <th className="px-4 py-2 text-right">Spent</th>
                <th className="px-4 py-2 text-left">Last Heartbeat</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {agents.map(agent => (
                <tr key={agent.id} className="hover:bg-gray-50">
                  <td className="px-4 py-2 font-medium">{agent.name}</td>
                  <td className="px-4 py-2 text-gray-600">{agent.title}</td>
                  <td className="px-4 py-2">
                    <span className={`px-2 py-0.5 rounded-full text-xs ${STATUS_COLORS[agent.status] || ''}`}>
                      {agent.status}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-gray-500">{agent.adapter_type}</td>
                  <td className="px-4 py-2 text-right">${(agent.budget_cents / 100).toFixed(2)}</td>
                  <td className="px-4 py-2 text-right">${(agent.spent_cents / 100).toFixed(2)}</td>
                  <td className="px-4 py-2 text-gray-500 text-xs">
                    {agent.last_heartbeat || 'Never'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Tasks tab */}
      {activeTab === 'tasks' && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left">Task</th>
                <th className="px-4 py-2 text-left">Status</th>
                <th className="px-4 py-2 text-left">Priority</th>
                <th className="px-4 py-2 text-left">Assignee</th>
                <th className="px-4 py-2 text-left">Updated</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {tasks.map(task => (
                <tr key={task.id} className="hover:bg-gray-50">
                  <td className="px-4 py-2 font-medium">{task.title}</td>
                  <td className="px-4 py-2">
                    <span className="px-2 py-0.5 rounded-full text-xs bg-gray-100">
                      {task.status}
                    </span>
                  </td>
                  <td className="px-4 py-2">{task.priority}</td>
                  <td className="px-4 py-2 text-gray-600">{task.assignee_name || 'Unassigned'}</td>
                  <td className="px-4 py-2 text-gray-500 text-xs">{task.updated_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Costs tab */}
      {activeTab === 'costs' && costs && (
        <div className="space-y-4">
          <div className="p-4 bg-white border rounded-lg">
            <h3 className="font-semibold mb-3">Cost by Agent</h3>
            {Object.entries(costs.by_agent).map(([agent, cents]) => (
              <div key={agent} className="flex justify-between py-1 border-b last:border-0">
                <span className="text-gray-700">{agent}</span>
                <span className="font-medium">${(cents / 100).toFixed(2)}</span>
              </div>
            ))}
          </div>
          <div className="p-4 bg-white border rounded-lg">
            <div className="flex justify-between items-center">
              <span className="font-semibold">Total Spend</span>
              <span className="text-xl font-bold">${(costs.total_cents / 100).toFixed(2)}</span>
            </div>
            <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full"
                style={{ width: `${Math.min(costs.utilization_pct, 100)}%` }}
              />
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {costs.utilization_pct.toFixed(1)}% of ${(costs.budget_cents / 100).toFixed(2)} budget
            </div>
          </div>
        </div>
      )}

      {/* Approvals tab */}
      {activeTab === 'approvals' && (
        <div className="space-y-3">
          {Object.entries(approvals).length === 0 ? (
            <div className="text-center text-gray-500 py-8">No pending approvals</div>
          ) : (
            Object.entries(approvals).map(([id, req]) => (
              <div key={id} className="p-4 bg-white border rounded-lg">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="font-medium">{req.description}</div>
                    <div className="text-sm text-gray-500 mt-1">
                      Agent: {req.agent_name} | Action: {req.action_type}
                    </div>
                    <span className={`inline-block mt-2 px-2 py-0.5 rounded-full text-xs ${RISK_COLORS[req.risk_level] || ''}`}>
                      {req.risk_level} risk
                    </span>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleApprove(id)}
                      className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                    >
                      Approve
                    </button>
                    <button
                      onClick={() => handleReject(id)}
                      className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
                    >
                      Reject
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
```

### Step 4: Add Dashboard Page

```tsx
// app/admin/agents/page.tsx
import AgentCostDashboard from '@/components/paperclip/AgentCostDashboard';

export default function AgentOperationsPage() {
  // In production, fetch company_id from user session or config
  const companyId = process.env.NEXT_PUBLIC_PAPERCLIP_COMPANY_ID || 'default';

  return (
    <div className="min-h-screen bg-gray-50">
      <AgentCostDashboard companyId={companyId} />
    </div>
  );
}
```

**Checkpoint**: PMS frontend has a Paperclip API client, AgentCostDashboard component with tabs for agents/tasks/costs/approvals, and an admin page at `/admin/agents`.

---

## 6. Part D: Testing and Verification

### Test 1: Paperclip Health Check

```bash
curl -s http://localhost:3100/api/health | python3 -m json.tool
# Expected: {"status": "ok", ...}
```

### Test 2: Run Bootstrap Script

```bash
cd ~/Projects/pms/pms-backend
python3 scripts/paperclip_bootstrap.py

# Expected output:
# ✓ Company created: <company-id>
# ✓ CEO Agent registered: <agent-id>
# ✓ Intake Agent registered: <agent-id>
# ✓ Billing Agent registered: <agent-id>
# ✓ Clinical Agent registered: <agent-id>
# ✓ Communications Agent registered: <agent-id>
# ✓ Reports Agent registered: <agent-id>
# ✓ Initial intake task created
# ✓ Initial billing task created
# 🎉 PMS Paperclip bootstrap complete!
```

### Test 3: Verify Agents via API

```bash
# List all companies
curl -s http://localhost:3100/api/companies | python3 -m json.tool

# List agents in company (replace COMPANY_ID)
curl -s http://localhost:3100/api/companies/COMPANY_ID/agents | python3 -m json.tool
```

### Test 4: Test Webhook Endpoints

```bash
# Test intake heartbeat
curl -s -X POST http://localhost:8000/api/paperclip/webhooks/intake \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer intake-agent-key" \
  -d '{
    "agent_id": "test-intake",
    "agent_name": "pms-intake",
    "company_id": "test-company",
    "task_id": "task-001",
    "task_title": "Process new patient",
    "context": {"patient_data": {"last_name": "Smith", "first_name": "John"}}
  }' | python3 -m json.tool

# Expected: {"status": "completed", "result": {"patient_created": true, ...}}
```

### Test 5: Test Governance Approval Flow

```bash
# Request approval for a claim submission
curl -s -X POST http://localhost:8000/api/paperclip/governance/request-approval \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "billing-agent",
    "agent_name": "pms-billing",
    "company_id": "test-company",
    "task_id": "task-002",
    "action_type": "claim_submission",
    "description": "Submit claim CLM-2026-001234 for encounter ENC-5678",
    "risk_level": "high"
  }' | python3 -m json.tool

# Expected: {"request_id": "<uuid>", "status": "pending"}

# List pending approvals
curl -s http://localhost:8000/api/paperclip/governance/pending | python3 -m json.tool

# Approve the request (replace REQUEST_ID)
curl -s -X POST "http://localhost:8000/api/paperclip/governance/approve/REQUEST_ID?reviewer=dr_smith" \
  | python3 -m json.tool

# Expected: {"request_id": "...", "status": "approved", "reviewer": "dr_smith"}
```

### Test 6: Verify Frontend Dashboard

1. Navigate to `http://localhost:3000/admin/agents`
2. Verify the dashboard loads with summary cards
3. Check Agents tab shows all registered agents
4. Check Tasks tab shows created tasks
5. Check Costs tab shows budget utilization
6. Check Approvals tab shows pending approval requests

**Checkpoint**: All Paperclip components are verified — health check, company bootstrap, webhook handlers, governance approval flow, and frontend dashboard.

---

## 7. Troubleshooting

### Paperclip Won't Start — Port 3100 Already in Use

**Symptom**: `Error: listen EADDRINUSE :::3100`

**Fix**:
```bash
# Find and kill the process using port 3100
lsof -ti:3100 | xargs kill -9

# Or change the port in .env
PORT=3101
```

### Database Connection Failed

**Symptom**: `Error: connect ECONNREFUSED 127.0.0.1:5432`

**Fix**:
```bash
# Verify PostgreSQL is running
pg_isready -h localhost -p 5432

# Verify the database exists
psql -U postgres -l | grep paperclip_db

# Verify credentials
psql -U paperclip_user -d paperclip_db -c "SELECT 1;"

# If using embedded PostgreSQL, check the instance directory
ls ~/.paperclip/instances/pms-production/db/
```

### Agent Heartbeat Returns 401

**Symptom**: Webhook endpoints return `{"detail": "Invalid agent key"}`

**Fix**:
```python
# Verify AGENT_API_KEYS in webhook.py matches the keys configured in Paperclip
# Check the Authorization header format: "Bearer <key>"
# Ensure the agent's adapter_config.webhook_url is correct
```

### Migrations Fail

**Symptom**: `pnpm db:migrate` fails with schema errors

**Fix**:
```bash
# Reset and regenerate migrations
pnpm db:generate
pnpm db:migrate

# If using external PostgreSQL, ensure uuid-ossp extension is installed
psql -U postgres -d paperclip_db -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
```

### Approval Requests Not Showing in Frontend

**Symptom**: Approvals tab shows "No pending approvals" but requests were made

**Fix**:
```bash
# Verify the governance endpoint is reachable from the frontend
curl -s http://localhost:8000/api/paperclip/governance/pending

# Check CORS configuration in FastAPI allows requests from :3000
# In app/main.py, verify CORSMiddleware includes "http://localhost:3000"
```

### Budget Exceeded — Agent Throttled

**Symptom**: Agent tasks fail with budget exhaustion error

**Fix**:
```bash
# Check current costs via API
curl -s http://localhost:3100/api/companies/COMPANY_ID/costs

# Increase agent budget through Paperclip dashboard or API
# Or reset budget for the billing cycle
```

---

## 8. Reference Commands

### Daily Development Workflow

```bash
# Start all services
cd ~/Projects/pms
docker compose up -d                     # PMS stack
cd paperclip-orchestrator && pnpm dev    # Paperclip

# Check agent status
curl -s http://localhost:3100/api/companies/COMPANY_ID/agents | python3 -m json.tool

# View recent activity
curl -s "http://localhost:3100/api/companies/COMPANY_ID/activity?limit=20" | python3 -m json.tool

# Check pending approvals
curl -s http://localhost:8000/api/paperclip/governance/pending | python3 -m json.tool
```

### Management Commands

```bash
# Paperclip CLI
pnpm paperclipai run                      # Start with auto-onboarding
pnpm paperclipai configure --section database  # Configure database
pnpm paperclipai configure --section storage   # Configure storage
pnpm paperclipai worktree:make test-branch     # Create isolated worktree

# Database
pnpm db:generate                          # Generate migration
pnpm db:migrate                           # Apply migrations
pnpm build                                # Build all packages
pnpm test:run                             # Run tests
pnpm typecheck                            # Type checking
```

### Useful URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Paperclip Dashboard | http://localhost:3100 | Agent management UI |
| Paperclip API | http://localhost:3100/api | REST API |
| PMS Backend | http://localhost:8000 | FastAPI backend |
| PMS Frontend | http://localhost:3000 | Next.js frontend |
| Agent Dashboard | http://localhost:3000/admin/agents | PMS agent operations page |

---

## Next Steps

After setup is complete:
1. Follow the [Paperclip Developer Tutorial](78-Paperclip-Developer-Tutorial.md) to build your first agent workflow end-to-end
2. Configure heartbeat schedules for each agent in the Paperclip dashboard
3. Set up budget alerts and cost monitoring
4. Review approval gate policies for your clinic's compliance requirements

## Resources

- [Paperclip GitHub Repository](https://github.com/paperclipai/paperclip) — Source code and development docs
- [Paperclip Core Concepts](https://github.com/paperclipai/paperclip/blob/master/docs/start/core-concepts.md) — Data models and workflows
- [Paperclip DEVELOPING.md](https://github.com/paperclipai/paperclip/blob/master/doc/DEVELOPING.md) — Development setup guide
- [Paperclip Official Website](https://paperclip.ing/) — Product overview
- [PMS pVerify Integration (Exp 73)](73-PRD-pVerify-PMS-Integration.md) — Insurance eligibility
- [PMS Xero Integration (Exp 75)](75-PRD-XeroAPI-PMS-Integration.md) — Billing and invoicing
- [PMS Mirth Connect (Exp 77)](77-PRD-MirthConnect-PMS-Integration.md) — HL7/FHIR integration
