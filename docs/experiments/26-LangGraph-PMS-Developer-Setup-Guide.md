# LangGraph Setup Guide for PMS Integration

**Document ID:** PMS-EXP-LANGGRAPH-001
**Version:** 1.0
**Date:** March 2, 2026
**Applies To:** PMS project (all platforms)
**Prerequisites Level:** Intermediate

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Part A: Install and Configure LangGraph](#3-part-a-install-and-configure-langgraph)
4. [Part B: Integrate with PMS Backend](#4-part-b-integrate-with-pms-backend)
5. [Part C: Integrate with PMS Frontend](#5-part-c-integrate-with-pms-frontend)
6. [Part D: Testing and Verification](#6-part-d-testing-and-verification)
7. [Troubleshooting](#7-troubleshooting)
8. [Reference Commands](#8-reference-commands)

---

## 1. Overview

This guide walks you through setting up **LangGraph** as the stateful agent orchestration layer for the PMS. By the end, you will have:

- LangGraph and the PostgreSQL checkpointer installed in the PMS backend
- Checkpoint tables created in the PMS PostgreSQL database
- A sample Encounter Summary agent graph running with durable state
- HITL (Human-in-the-Loop) approval endpoints functional
- SSE streaming of graph progress to the frontend
- Audit logging for all agent operations

### Architecture at a Glance

```mermaid
flowchart LR
    subgraph Clients["Clients"]
        NEXT["Next.js :3000<br/>(SSE + REST)"]
        AND["Android App<br/>(REST + Polling)"]
    end

    subgraph Docker["Docker Network"]
        direction TB
        FAST["PMS Backend :8000<br/>(FastAPI + LangGraph)"]
        MCP["PMS MCP Server<br/>:9000"]
        DB[("PostgreSQL :5432<br/>+ Checkpoint Tables")]
    end

    subgraph Models["AI Models"]
        CLAUDE["Claude API"]
        LOCAL["Gemma 3 / Qwen 3.5"]
    end

    NEXT -->|"SSE + REST"| FAST
    AND -->|"REST"| FAST
    FAST -->|"MCP tools/call"| MCP
    FAST -->|"Checkpoints"| DB
    MCP -->|"HTTP"| FAST
    FAST -->|"LLM"| Models

    style FAST fill:#d4edda,stroke:#28a745
    style MCP fill:#f8d7da,stroke:#dc3545
    style DB fill:#fff3cd,stroke:#ffc107
```

---

## 2. Prerequisites

### 2.1 Required Software

| Software | Minimum Version | Check Command |
|---|---|---|
| Python | 3.12+ | `python3 --version` |
| Node.js | 20+ | `node --version` |
| Docker | 24+ | `docker --version` |
| Docker Compose | 2.20+ | `docker compose version` |
| Git | 2.40+ | `git --version` |
| pip | 23+ | `pip --version` |
| uv (recommended) | 0.4+ | `uv --version` |
| PostgreSQL client | 14+ | `psql --version` |

### 2.2 Installation of Prerequisites

If you don't have `uv` (recommended Python package manager):

```bash
# macOS
brew install uv

# Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2.3 Verify PMS Services

Before proceeding, confirm the PMS stack is running:

```bash
# Check PMS backend
curl -s http://localhost:8000/api/health | jq .
# Expected: {"status": "healthy", ...}

# Check PostgreSQL
psql -h localhost -p 5432 -U pms -d pms_db -c "SELECT 1;"
# Expected: ?column? = 1

# Check MCP server (if Experiment 09 is set up)
curl -s http://localhost:9000/health | jq .
# Expected: {"status": "ok", ...}
```

> **Note:** The MCP server (Experiment 09) is recommended but not required for initial setup. LangGraph can call PMS APIs directly via HTTP as a fallback.

---

## 3. Part A: Install and Configure LangGraph

### Step 1: Install Python packages

From the PMS backend project root:

```bash
cd pms-backend

# Using uv (recommended)
uv pip install langgraph \
  langgraph-checkpoint-postgres \
  "psycopg[binary,pool]" \
  langchain-anthropic \
  langchain-core

# Or using pip
pip install langgraph \
  langgraph-checkpoint-postgres \
  "psycopg[binary,pool]" \
  langchain-anthropic \
  langchain-core
```

### Step 2: Verify installation

```bash
python3 -c "
import langgraph
print(f'LangGraph version: {langgraph.__version__}')

from langgraph.graph import StateGraph
print('StateGraph imported successfully')

from langgraph.checkpoint.postgres import PostgresSaver
print('PostgresSaver imported successfully')
"
```

Expected output:

```
LangGraph version: 1.0.x
StateGraph imported successfully
PostgresSaver imported successfully
```

### Step 3: Add environment variables

Add the following to your `.env` file (or Docker Compose environment):

```bash
# LangGraph Configuration
LANGGRAPH_CHECKPOINT_DB_URI=postgresql://pms:pms_password@localhost:5432/pms_db
LANGGRAPH_MAX_CONCURRENT_THREADS=50
LANGGRAPH_CHECKPOINT_PRUNE_DAYS=30

# Anthropic API (if not already set)
ANTHROPIC_API_KEY=sk-ant-...
```

### Step 4: Create checkpoint database tables

Create a migration script at `pms-backend/alembic/versions/xxxx_add_langgraph_checkpoints.py`:

```python
"""Add LangGraph checkpoint and agent audit tables

Revision ID: xxxx_langgraph
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
import uuid


def upgrade():
    # Agent audit log table
    op.create_table(
        'agent_audit_log',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('thread_id', sa.String(255), nullable=False, index=True),
        sa.Column('graph_name', sa.String(100), nullable=False),
        sa.Column('node_name', sa.String(100), nullable=True),
        sa.Column('event_type', sa.String(50), nullable=False),  # node_start, node_end, tool_call, hitl_request, hitl_response, error
        sa.Column('event_data', JSONB, nullable=True),
        sa.Column('clinician_id', UUID(as_uuid=True), nullable=True),
        sa.Column('patient_id', UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_agent_audit_thread_created', 'agent_audit_log', ['thread_id', 'created_at'])


def downgrade():
    op.drop_table('agent_audit_log')
```

Run the migration:

```bash
alembic upgrade head
```

Then initialize the LangGraph checkpoint tables:

```python
# Run once to create checkpoint tables
python3 -c "
from langgraph.checkpoint.postgres import PostgresSaver

DB_URI = 'postgresql://pms:pms_password@localhost:5432/pms_db'
with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup()
    print('Checkpoint tables created successfully')
"
```

### Step 5: Verify checkpoint tables

```bash
psql -h localhost -p 5432 -U pms -d pms_db -c "\dt *checkpoint*"
```

Expected output:

```
              List of relations
 Schema |        Name         | Type  | Owner
--------+---------------------+-------+-------
 public | checkpoint_blobs    | table | pms
 public | checkpoint_metadata | table | pms
 public | checkpoint_writes   | table | pms
 public | checkpoints         | table | pms
```

**Checkpoint: LangGraph installed, environment configured, database tables created.**

---

## 4. Part B: Integrate with PMS Backend

### Step 1: Create the agent module structure

```bash
mkdir -p pms-backend/app/agents/graphs
touch pms-backend/app/agents/__init__.py
touch pms-backend/app/agents/registry.py
touch pms-backend/app/agents/state.py
touch pms-backend/app/agents/hitl.py
touch pms-backend/app/agents/streaming.py
touch pms-backend/app/agents/graphs/__init__.py
touch pms-backend/app/agents/graphs/encounter_summary.py
```

### Step 2: Define the base agent state

Create `pms-backend/app/agents/state.py`:

```python
"""Base state schemas for PMS LangGraph agents."""
from __future__ import annotations

import operator
from dataclasses import dataclass, field
from typing import Annotated, Any

from langgraph.graph import MessagesState


class PmsAgentState(MessagesState):
    """Base state for all PMS agent graphs.

    Extends MessagesState with PMS-specific fields.
    """
    # PMS context
    patient_id: str | None = None
    encounter_id: str | None = None
    clinician_id: str | None = None

    # Workflow tracking
    current_step: str = ""
    steps_completed: Annotated[list[str], operator.add] = field(default_factory=list)

    # HITL
    pending_approval: dict[str, Any] | None = None
    approval_decision: str | None = None  # "approved" | "rejected" | "modified"

    # Output
    result: dict[str, Any] | None = None
    error: str | None = None
```

### Step 3: Create the graph registry

Create `pms-backend/app/agents/registry.py`:

```python
"""Graph registry for PMS LangGraph agents."""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import StateGraph

from app.agents.graphs.encounter_summary import build_encounter_summary_graph


class GraphRegistry:
    """Central registry of all PMS agent graphs."""

    def __init__(self):
        self._graphs: dict[str, StateGraph] = {}
        self._checkpointer: AsyncPostgresSaver | None = None

    async def initialize(self):
        """Initialize checkpointer and register graphs."""
        db_uri = os.environ["LANGGRAPH_CHECKPOINT_DB_URI"]
        self._checkpointer = AsyncPostgresSaver.from_conn_string(db_uri)
        await self._checkpointer.setup()

        # Register all graphs
        self._graphs["encounter_summary"] = build_encounter_summary_graph()

    async def shutdown(self):
        """Clean up resources."""
        if self._checkpointer:
            await self._checkpointer.conn.close()

    def get_compiled_graph(self, graph_name: str):
        """Get a compiled graph by name."""
        if graph_name not in self._graphs:
            raise ValueError(f"Unknown graph: {graph_name}. Available: {list(self._graphs.keys())}")

        graph = self._graphs[graph_name]
        return graph.compile(checkpointer=self._checkpointer)

    def list_graphs(self) -> list[dict[str, str]]:
        """List all registered graphs."""
        return [{"name": name} for name in self._graphs]


# Singleton
registry = GraphRegistry()
```

### Step 4: Build the Encounter Summary graph

Create `pms-backend/app/agents/graphs/encounter_summary.py`:

```python
"""Encounter Summary agent graph.

Generates structured encounter notes from clinical data.
"""
from __future__ import annotations

from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph
from langgraph.types import interrupt

from app.agents.state import PmsAgentState


def build_encounter_summary_graph() -> StateGraph:
    """Build the encounter summary StateGraph."""

    model = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)

    async def gather_data(state: PmsAgentState) -> dict[str, Any]:
        """Node: Gather patient and encounter data from PMS."""
        # In production, this calls PMS APIs via MCP
        return {
            "current_step": "gather_data",
            "steps_completed": ["gather_data"],
        }

    async def generate_summary(state: PmsAgentState) -> dict[str, Any]:
        """Node: Generate SOAP note using LLM."""
        messages = [
            SystemMessage(content="You are a clinical documentation assistant. Generate a SOAP note."),
            HumanMessage(content=f"Generate encounter summary for patient {state.patient_id}, encounter {state.encounter_id}."),
        ]
        response = await model.ainvoke(messages)
        return {
            "messages": [response],
            "current_step": "generate_summary",
            "steps_completed": ["generate_summary"],
            "pending_approval": {
                "type": "encounter_summary_review",
                "summary": response.content,
            },
        }

    async def clinician_review(state: PmsAgentState) -> dict[str, Any]:
        """Node: HITL — pause for clinician review."""
        # interrupt() pauses the graph and waits for external input
        decision = interrupt({
            "type": "clinician_review",
            "message": "Please review the encounter summary.",
            "data": state.pending_approval,
        })
        return {
            "approval_decision": decision.get("action", "approved"),
            "current_step": "clinician_review",
            "steps_completed": ["clinician_review"],
        }

    async def finalize(state: PmsAgentState) -> dict[str, Any]:
        """Node: Finalize and save the encounter summary."""
        return {
            "result": {
                "status": "completed",
                "decision": state.approval_decision,
            },
            "current_step": "finalize",
            "steps_completed": ["finalize"],
        }

    def route_after_review(state: PmsAgentState) -> str:
        """Conditional edge: route based on clinician decision."""
        if state.approval_decision == "rejected":
            return "generate_summary"  # regenerate
        return "finalize"

    # Build the graph
    graph = StateGraph(PmsAgentState)

    graph.add_node("gather_data", gather_data)
    graph.add_node("generate_summary", generate_summary)
    graph.add_node("clinician_review", clinician_review)
    graph.add_node("finalize", finalize)

    graph.set_entry_point("gather_data")
    graph.add_edge("gather_data", "generate_summary")
    graph.add_edge("generate_summary", "clinician_review")
    graph.add_conditional_edges("clinician_review", route_after_review)
    graph.add_edge("finalize", END)

    return graph


```

### Step 5: Add agent API endpoints to FastAPI

Create `pms-backend/app/agents/router.py`:

```python
"""FastAPI router for LangGraph agent endpoints."""
from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agents.registry import registry

router = APIRouter(prefix="/api/agents", tags=["agents"])


class RunAgentRequest(BaseModel):
    graph_name: str
    patient_id: str | None = None
    encounter_id: str | None = None
    clinician_id: str | None = None
    initial_input: dict[str, Any] = {}


class ApproveRequest(BaseModel):
    action: str  # "approved" | "rejected" | "modified"
    modifications: dict[str, Any] | None = None


@router.get("/graphs")
async def list_graphs():
    """List all available agent graphs."""
    return registry.list_graphs()


@router.post("/run")
async def run_agent(req: RunAgentRequest):
    """Start a new agent graph execution."""
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    graph = registry.get_compiled_graph(req.graph_name)

    initial_state = {
        "patient_id": req.patient_id,
        "encounter_id": req.encounter_id,
        "clinician_id": req.clinician_id,
        "messages": [],
        **req.initial_input,
    }

    # Run until first interrupt (HITL) or completion
    result = await graph.ainvoke(initial_state, config)

    return {
        "thread_id": thread_id,
        "status": "completed" if result.get("result") else "waiting_for_approval",
        "state": result,
    }


@router.post("/approve/{thread_id}")
async def approve_agent(thread_id: str, req: ApproveRequest):
    """Resume an agent graph after HITL approval."""
    config = {"configurable": {"thread_id": thread_id}}

    # Find which graph this thread belongs to
    # In production, look up from agent_audit_log
    graph = registry.get_compiled_graph("encounter_summary")

    result = await graph.ainvoke(
        None,  # resume from checkpoint
        config,
    )

    return {
        "thread_id": thread_id,
        "status": "completed" if result.get("result") else "waiting_for_approval",
        "state": result,
    }


@router.get("/status/{thread_id}")
async def get_agent_status(thread_id: str):
    """Get current state of an agent thread."""
    config = {"configurable": {"thread_id": thread_id}}
    graph = registry.get_compiled_graph("encounter_summary")
    state = await graph.aget_state(config)

    return {
        "thread_id": thread_id,
        "current_step": state.values.get("current_step", "unknown"),
        "steps_completed": state.values.get("steps_completed", []),
        "pending_approval": state.values.get("pending_approval"),
        "result": state.values.get("result"),
        "next": state.next,
    }
```

### Step 6: Register the router in the FastAPI app

Add to your main `app/main.py`:

```python
from app.agents.router import router as agents_router
from app.agents.registry import registry

# In your lifespan or startup event:
@asynccontextmanager
async def lifespan(app: FastAPI):
    await registry.initialize()
    yield
    await registry.shutdown()

app = FastAPI(lifespan=lifespan)
app.include_router(agents_router)
```

**Checkpoint: LangGraph integrated into PMS backend with agent endpoints, checkpointing, and HITL.**

---

## 5. Part C: Integrate with PMS Frontend

### Step 1: Create the agent API client

Create `pms-frontend/src/lib/agents.ts`:

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface AgentRunRequest {
  graph_name: string;
  patient_id?: string;
  encounter_id?: string;
  clinician_id?: string;
  initial_input?: Record<string, unknown>;
}

export interface AgentStatus {
  thread_id: string;
  status: "running" | "waiting_for_approval" | "completed" | "error";
  current_step: string;
  steps_completed: string[];
  pending_approval?: {
    type: string;
    message: string;
    data: Record<string, unknown>;
  };
  result?: Record<string, unknown>;
}

export async function runAgent(req: AgentRunRequest): Promise<AgentStatus> {
  const res = await fetch(`${API_BASE}/api/agents/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(`Agent run failed: ${res.statusText}`);
  return res.json();
}

export async function getAgentStatus(threadId: string): Promise<AgentStatus> {
  const res = await fetch(`${API_BASE}/api/agents/status/${threadId}`);
  if (!res.ok) throw new Error(`Status fetch failed: ${res.statusText}`);
  return res.json();
}

export async function approveAgent(
  threadId: string,
  action: "approved" | "rejected" | "modified",
  modifications?: Record<string, unknown>
): Promise<AgentStatus> {
  const res = await fetch(`${API_BASE}/api/agents/approve/${threadId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, modifications }),
  });
  if (!res.ok) throw new Error(`Approval failed: ${res.statusText}`);
  return res.json();
}

export function streamAgentProgress(
  threadId: string,
  onEvent: (event: Record<string, unknown>) => void
): EventSource {
  const source = new EventSource(
    `${API_BASE}/api/agents/stream/${threadId}`
  );
  source.onmessage = (e) => onEvent(JSON.parse(e.data));
  return source;
}
```

### Step 2: Create the Agent Progress component

Create `pms-frontend/src/components/agents/AgentProgress.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import { AgentStatus, getAgentStatus, approveAgent } from "@/lib/agents";

interface AgentProgressProps {
  threadId: string;
  onComplete?: (result: Record<string, unknown>) => void;
}

export function AgentProgress({ threadId, onComplete }: AgentProgressProps) {
  const [status, setStatus] = useState<AgentStatus | null>(null);

  useEffect(() => {
    const poll = setInterval(async () => {
      const s = await getAgentStatus(threadId);
      setStatus(s);
      if (s.status === "completed" && onComplete) {
        onComplete(s.result || {});
        clearInterval(poll);
      }
    }, 2000);
    return () => clearInterval(poll);
  }, [threadId, onComplete]);

  if (!status) return <div className="animate-pulse">Loading agent status...</div>;

  return (
    <div className="rounded-lg border p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Agent Workflow</h3>
        <span className={`text-xs px-2 py-1 rounded ${
          status.status === "completed" ? "bg-green-100 text-green-800" :
          status.status === "waiting_for_approval" ? "bg-yellow-100 text-yellow-800" :
          "bg-blue-100 text-blue-800"
        }`}>
          {status.status}
        </span>
      </div>

      {/* Step progress */}
      <div className="space-y-1">
        {status.steps_completed.map((step) => (
          <div key={step} className="flex items-center gap-2 text-sm text-green-700">
            <span>✓</span> {step}
          </div>
        ))}
        {status.current_step && !status.steps_completed.includes(status.current_step) && (
          <div className="flex items-center gap-2 text-sm text-blue-700">
            <span className="animate-spin">⟳</span> {status.current_step}
          </div>
        )}
      </div>

      {/* HITL Approval */}
      {status.status === "waiting_for_approval" && status.pending_approval && (
        <div className="border-t pt-3 space-y-2">
          <p className="text-sm font-medium">{status.pending_approval.message}</p>
          <div className="flex gap-2">
            <button
              onClick={() => approveAgent(threadId, "approved")}
              className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
            >
              Approve
            </button>
            <button
              onClick={() => approveAgent(threadId, "rejected")}
              className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
            >
              Reject & Regenerate
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
```

### Step 3: Add environment variables

Add to `pms-frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Checkpoint: Frontend agent client, progress component, and HITL approval UI created.**

---

## 6. Part D: Testing and Verification

### Step 1: Verify the backend agent endpoints

```bash
# List available graphs
curl -s http://localhost:8000/api/agents/graphs | jq .
# Expected: [{"name": "encounter_summary"}]
```

### Step 2: Run an agent

```bash
# Start an encounter summary workflow
curl -s -X POST http://localhost:8000/api/agents/run \
  -H "Content-Type: application/json" \
  -d '{
    "graph_name": "encounter_summary",
    "patient_id": "patient-001",
    "encounter_id": "enc-001",
    "clinician_id": "dr-smith-001"
  }' | jq .

# Expected: {"thread_id": "...", "status": "waiting_for_approval", "state": {...}}
```

### Step 3: Check agent status

```bash
# Replace with your thread_id from Step 2
THREAD_ID="<your-thread-id>"
curl -s "http://localhost:8000/api/agents/status/$THREAD_ID" | jq .

# Expected: {"thread_id": "...", "current_step": "clinician_review", "pending_approval": {...}}
```

### Step 4: Approve and complete

```bash
curl -s -X POST "http://localhost:8000/api/agents/approve/$THREAD_ID" \
  -H "Content-Type: application/json" \
  -d '{"action": "approved"}' | jq .

# Expected: {"thread_id": "...", "status": "completed", "state": {"result": {...}}}
```

### Step 5: Verify checkpoint persistence

```bash
# Check checkpoint tables have data
psql -h localhost -p 5432 -U pms -d pms_db -c "SELECT COUNT(*) FROM checkpoints;"
# Expected: count > 0

# Check audit log
psql -h localhost -p 5432 -U pms -d pms_db -c "SELECT thread_id, event_type, created_at FROM agent_audit_log ORDER BY created_at DESC LIMIT 5;"
```

### Step 6: Test fault tolerance

```bash
# Start an agent, then restart the backend before approving
curl -s -X POST http://localhost:8000/api/agents/run \
  -H "Content-Type: application/json" \
  -d '{"graph_name": "encounter_summary", "patient_id": "patient-002"}' | jq .thread_id

# Restart the backend
docker compose restart pms-backend

# Check the status — it should still be waiting_for_approval
curl -s "http://localhost:8000/api/agents/status/$THREAD_ID" | jq .status
# Expected: "waiting_for_approval"
```

**Checkpoint: Agent endpoints verified, graph execution tested, fault tolerance confirmed.**

---

## 7. Troubleshooting

### Checkpoint tables not created

**Symptom:** `relation "checkpoints" does not exist` error when running an agent.

**Fix:** Run the checkpoint setup manually:

```python
from langgraph.checkpoint.postgres import PostgresSaver
with PostgresSaver.from_conn_string("postgresql://pms:pms_password@localhost:5432/pms_db") as cp:
    cp.setup()
```

### Connection pool exhaustion

**Symptom:** `too many clients already` or `connection pool exhausted` errors under load.

**Fix:** Configure connection pooling in the checkpointer:

```python
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
checkpointer = AsyncPostgresSaver.from_conn_string(
    db_uri,
    pool_size=10,      # increase from default
    max_overflow=20,
)
```

### Agent hangs at HITL interrupt

**Symptom:** Agent status shows `waiting_for_approval` but the approve endpoint returns an error.

**Fix:** Ensure you're passing the correct `thread_id` in the config. The thread ID must match exactly. Check:

```bash
psql -h localhost -p 5432 -U pms -d pms_db \
  -c "SELECT thread_id FROM checkpoints ORDER BY created_at DESC LIMIT 5;"
```

### Import errors after installation

**Symptom:** `ModuleNotFoundError: No module named 'langgraph'`

**Fix:** Ensure you installed in the correct virtual environment:

```bash
# Check which Python is active
which python3

# Verify the package is installed
pip list | grep langgraph
```

### PostgreSQL version incompatibility

**Symptom:** SQL errors during checkpoint setup.

**Fix:** The checkpointer requires PostgreSQL 14+. Check your version:

```bash
psql -h localhost -p 5432 -U pms -d pms_db -c "SELECT version();"
```

### SSE connection drops

**Symptom:** Frontend loses SSE connection during long-running workflows.

**Fix:** Configure keep-alive in your nginx/reverse proxy:

```nginx
proxy_read_timeout 3600;
proxy_send_timeout 3600;
proxy_buffering off;
```

---

## 8. Reference Commands

### Daily Development Workflow

```bash
# Start PMS stack
docker compose up -d

# Run an agent (quick test)
curl -s -X POST http://localhost:8000/api/agents/run \
  -H "Content-Type: application/json" \
  -d '{"graph_name": "encounter_summary", "patient_id": "test-001"}' | jq .

# Check agent status
curl -s http://localhost:8000/api/agents/status/<thread_id> | jq .

# Approve HITL
curl -s -X POST http://localhost:8000/api/agents/approve/<thread_id> \
  -H "Content-Type: application/json" \
  -d '{"action": "approved"}' | jq .
```

### Management Commands

```bash
# List checkpoint data
psql -h localhost -p 5432 -U pms -d pms_db \
  -c "SELECT thread_id, created_at FROM checkpoints ORDER BY created_at DESC LIMIT 10;"

# View audit log
psql -h localhost -p 5432 -U pms -d pms_db \
  -c "SELECT thread_id, graph_name, event_type, created_at FROM agent_audit_log ORDER BY created_at DESC LIMIT 20;"

# Prune old checkpoints (> 30 days)
psql -h localhost -p 5432 -U pms -d pms_db \
  -c "DELETE FROM checkpoints WHERE created_at < NOW() - INTERVAL '30 days';"

# Count active threads
psql -h localhost -p 5432 -U pms -d pms_db \
  -c "SELECT COUNT(DISTINCT thread_id) FROM checkpoints WHERE created_at > NOW() - INTERVAL '1 day';"
```

### Useful URLs

| Resource | URL |
|---|---|
| PMS Backend | http://localhost:8000 |
| Agent API docs | http://localhost:8000/docs#/agents |
| PMS Frontend | http://localhost:3000 |
| PMS MCP Server | http://localhost:9000 |
| LangGraph Docs | https://docs.langchain.com/oss/python/langgraph/overview |
| LangGraph GitHub | https://github.com/langchain-ai/langgraph |
| Checkpoint Postgres PyPI | https://pypi.org/project/langgraph-checkpoint-postgres/ |

---

## Next Steps

- Follow the [LangGraph Developer Tutorial](26-LangGraph-Developer-Tutorial.md) to build your first clinical agent end-to-end
- Review the [PRD](26-PRD-LangGraph-PMS-Integration.md) for the full implementation roadmap
- Connect agents to the [PMS MCP Server](09-MCP-PMS-Developer-Setup-Guide.md) for tool discovery

## Resources

- [LangGraph Official Documentation](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangGraph GitHub Repository](https://github.com/langchain-ai/langgraph)
- [LangGraph Persistence Docs](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangGraph Streaming Docs](https://docs.langchain.com/oss/python/langgraph/streaming)
- [langgraph-checkpoint-postgres on PyPI](https://pypi.org/project/langgraph-checkpoint-postgres/)
- [FastAPI + LangGraph Template](https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template)
- [PMS MCP Integration (Experiment 09)](09-PRD-MCP-PMS-Integration.md)
