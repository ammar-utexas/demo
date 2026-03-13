# NullClaw Setup Guide for PMS Integration

**Document ID:** PMS-EXP-NULLCLAW-001
**Version:** 1.0
**Date:** March 12, 2026
**Applies To:** PMS project (all platforms)
**Prerequisites Level:** Intermediate

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Part A: Install and Configure NullClaw](#3-part-a-install-and-configure-nullclaw)
4. [Part B: Integrate with PMS Backend](#4-part-b-integrate-with-pms-backend)
5. [Part C: Integrate with PMS Frontend](#5-part-c-integrate-with-pms-frontend)
6. [Part D: Testing and Verification](#6-part-d-testing-and-verification)
7. [Troubleshooting](#7-troubleshooting)
8. [Reference Commands](#8-reference-commands)

---

## 1. Overview

This guide walks you through installing NullClaw, configuring it as an AI assistant for the PMS, connecting it to the FastAPI backend via custom tools, and embedding a chat widget in the Next.js frontend. By the end, you will have:

- A running NullClaw instance on port 3001 with pairing authentication
- PostgreSQL-backed conversation memory and audit logging
- Five custom PMS tools (patient lookup, encounter summary, prescription check, report generation, schedule query)
- A gateway adapter in the FastAPI backend that handles NullClaw tool calls
- A web chat widget in the Next.js frontend connected to NullClaw

```mermaid
flowchart LR
    subgraph Setup["What You're Building"]
        NC["NullClaw :3001"]
        BE["PMS Backend :8000"]
        FE["PMS Frontend :3000"]
        PG["PostgreSQL :5432"]
    end

    NC -->|"PMS Tools via HTTP"| BE
    NC -->|"Memory + Audit"| PG
    FE -->|"Chat Widget"| NC
    BE -->|"Data queries"| PG

    style NC fill:#E74C3C,color:#fff
    style BE fill:#E67E22,color:#fff
    style FE fill:#4A90D9,color:#fff
    style PG fill:#27AE60,color:#fff
```

## 2. Prerequisites

### 2.1 Required Software

| Software | Minimum Version | Check Command |
|---|---|---|
| macOS / Linux | macOS 12+ or Ubuntu 20.04+ | `uname -a` |
| Homebrew (macOS) | 4.0+ | `brew --version` |
| Docker & Docker Compose | 24.0+ / 2.20+ | `docker --version && docker compose version` |
| PostgreSQL | 15+ | `psql --version` |
| Python | 3.11+ | `python3 --version` |
| Node.js | 18+ | `node --version` |
| Git | 2.30+ | `git --version` |
| curl | Any | `curl --version` |

### 2.2 Installation of Prerequisites

**Install NullClaw via Homebrew (recommended):**

```bash
brew install nullclaw
nullclaw --version
```

**Or build from source (requires Zig 0.15.2):**

```bash
# Install Zig 0.15.2
brew install zig@0.15.2
zig version  # Must print 0.15.2

# Clone and build
git clone https://github.com/nullclaw/nullclaw.git ~/nullclaw-src
cd ~/nullclaw-src
zig build -Doptimize=ReleaseSmall
ls -lh zig-out/bin/nullclaw  # Should show ~678 KB

# Add to PATH
cp zig-out/bin/nullclaw ~/.local/bin/
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 2.3 Verify PMS Services

Before proceeding, confirm all PMS services are running:

```bash
# Check PMS backend
curl -s http://localhost:8000/docs | head -5
# Expected: HTML content from FastAPI Swagger docs

# Check PMS frontend
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
# Expected: 200

# Check PostgreSQL
psql -h localhost -U pms_user -d pms_db -c "SELECT 1;"
# Expected: 1 row returned
```

**Checkpoint**: All three PMS services (backend :8000, frontend :3000, PostgreSQL :5432) are accessible.

## 3. Part A: Install and Configure NullClaw

### Step 1: Verify NullClaw Installation

```bash
nullclaw --help
nullclaw status
```

Expected: Help text listing available commands; status showing "no configuration found" (first run).

### Step 2: Run the Onboarding Wizard

```bash
nullclaw onboard --interactive
```

The wizard will prompt for:
1. **Provider**: Select `openrouter` (or your preferred provider)
2. **API Key**: Enter your OpenRouter API key
3. **Model**: Select a model (e.g., `anthropic/claude-sonnet-4-20250514`)

Alternatively, configure non-interactively:

```bash
nullclaw onboard --api-key sk-or-v1-YOUR_KEY --provider openrouter
```

### Step 3: Configure the Gateway

Create or edit the NullClaw configuration file:

```bash
# Find config location
nullclaw doctor
```

Edit the configuration (typically `~/.config/nullclaw/config.json`):

```json
{
  "gateway": {
    "host": "127.0.0.1",
    "port": 3001,
    "require_pairing": true,
    "allow_public_bind": false
  },
  "provider": {
    "name": "openrouter",
    "api_key": "enc2:...",
    "model": "anthropic/claude-sonnet-4-20250514"
  },
  "memory": {
    "backend": "postgres",
    "postgres": {
      "connection_string": "postgresql://pms_user:pms_pass@127.0.0.1:5432/pms_db",
      "table_prefix": "nullclaw_",
      "retention_days": 2190
    }
  },
  "autonomy": {
    "level": "supervised",
    "workspace_only": true,
    "max_actions_per_hour": 50
  },
  "security": {
    "sandbox": { "backend": "auto" },
    "audit": {
      "enabled": true,
      "retention_days": 2190
    }
  },
  "system_prompt": "You are a clinical assistant for the MPS Patient Management System. You help healthcare staff look up patient records, check medications, review encounters, and generate reports. Always verify patient identity before sharing information. Never fabricate clinical data — use only the PMS tools provided. If unsure, ask the staff member to clarify."
}
```

> **Note**: Port 3001 avoids conflict with the Next.js frontend on port 3000. The `retention_days: 2190` (6 years) satisfies HIPAA record retention requirements.

### Step 4: Create PostgreSQL Tables for NullClaw

```bash
psql -h localhost -U pms_user -d pms_db <<'SQL'
-- NullClaw conversation memory
CREATE TABLE IF NOT EXISTS nullclaw_memory (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    role VARCHAR(16) NOT NULL,
    content TEXT NOT NULL,
    channel VARCHAR(32),
    staff_id VARCHAR(64),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    archived_at TIMESTAMPTZ
);

CREATE INDEX idx_nullclaw_memory_session ON nullclaw_memory(session_id);
CREATE INDEX idx_nullclaw_memory_staff ON nullclaw_memory(staff_id);

-- NullClaw audit log
CREATE TABLE IF NOT EXISTS nullclaw_audit (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    staff_id VARCHAR(64),
    channel VARCHAR(32) NOT NULL,
    tool_name VARCHAR(64),
    tool_input JSONB,
    tool_output_summary TEXT,
    approval_status VARCHAR(16) DEFAULT 'auto',
    ip_address INET,
    session_id VARCHAR(64)
);

CREATE INDEX idx_nullclaw_audit_staff ON nullclaw_audit(staff_id);
CREATE INDEX idx_nullclaw_audit_timestamp ON nullclaw_audit(timestamp);
CREATE INDEX idx_nullclaw_audit_tool ON nullclaw_audit(tool_name);

-- Row-level security for HIPAA
ALTER TABLE nullclaw_audit ENABLE ROW LEVEL SECURITY;
SQL
```

### Step 5: Start NullClaw

```bash
# Start the gateway
nullclaw gateway --port 3001

# In another terminal, verify health
curl http://127.0.0.1:3001/health
# Expected: {"status":"ok"} or similar health response
```

### Step 6: Pair with NullClaw

```bash
# NullClaw prints a 6-digit pairing code on first gateway start
# Use it to get a bearer token:
curl -X POST \
  -H "X-Pairing-Code: YOUR_6_DIGIT_CODE" \
  http://127.0.0.1:3001/pair

# Save the returned bearer token — you'll need it for all API calls
export NULLCLAW_TOKEN="YOUR_BEARER_TOKEN"
```

### Step 7: Test Basic Chat

```bash
# Send a test message via webhook
curl -X POST \
  -H "Authorization: Bearer $NULLCLAW_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello, are you connected to the PMS?"}' \
  http://127.0.0.1:3001/webhook
```

Expected: A response from the LLM acknowledging the system prompt context.

**Checkpoint**: NullClaw is installed, configured with PostgreSQL memory, running on port 3001, paired, and responding to webhook messages.

## 4. Part B: Integrate with PMS Backend

### Step 1: Create the NullClaw Gateway Adapter Module

Create a new module in the PMS backend for NullClaw integration:

```bash
mkdir -p pms-backend/app/integrations/nullclaw
touch pms-backend/app/integrations/nullclaw/__init__.py
touch pms-backend/app/integrations/nullclaw/adapter.py
touch pms-backend/app/integrations/nullclaw/tools.py
touch pms-backend/app/integrations/nullclaw/auth.py
```

### Step 2: Implement the Tool Definitions

`pms-backend/app/integrations/nullclaw/tools.py`:

```python
"""PMS tool definitions for NullClaw integration.

Each tool function accepts a dict input from NullClaw and returns
a dict response. NullClaw calls these via the gateway adapter.
"""

import httpx
from datetime import date


PMS_BASE_URL = "http://127.0.0.1:8000"


async def patient_lookup(params: dict) -> dict:
    """Look up patient by name, MRN, or DOB."""
    async with httpx.AsyncClient() as client:
        if "mrn" in params:
            resp = await client.get(
                f"{PMS_BASE_URL}/api/patients",
                params={"mrn": params["mrn"]},
            )
        elif "query" in params:
            resp = await client.get(
                f"{PMS_BASE_URL}/api/patients",
                params={"search": params["query"]},
            )
        else:
            return {"error": "Provide 'query' (name) or 'mrn'"}

        resp.raise_for_status()
        patients = resp.json()
        return {
            "count": len(patients),
            "patients": [
                {
                    "id": p["id"],
                    "name": f"{p['first_name']} {p['last_name']}",
                    "mrn": p["mrn"],
                    "dob": p["date_of_birth"],
                    "allergies": p.get("allergies", []),
                }
                for p in patients[:10]  # Limit results
            ],
        }


async def encounter_summary(params: dict) -> dict:
    """Get encounter details or daily encounter list."""
    async with httpx.AsyncClient() as client:
        query_params = {}
        if "patient_id" in params:
            query_params["patient_id"] = params["patient_id"]
        if "provider" in params:
            query_params["provider"] = params["provider"]
        if "date" in params:
            query_params["date"] = (
                str(date.today()) if params["date"] == "today" else params["date"]
            )

        resp = await client.get(
            f"{PMS_BASE_URL}/api/encounters",
            params=query_params,
        )
        resp.raise_for_status()
        encounters = resp.json()
        return {
            "count": len(encounters),
            "encounters": [
                {
                    "id": e["id"],
                    "patient_name": e.get("patient_name", ""),
                    "date": e["encounter_date"],
                    "type": e.get("encounter_type", ""),
                    "provider": e.get("provider_name", ""),
                    "diagnosis": e.get("primary_diagnosis", ""),
                    "status": e.get("status", ""),
                }
                for e in encounters[:20]
            ],
        }


async def rx_check(params: dict) -> dict:
    """Check active medications and drug interactions."""
    async with httpx.AsyncClient() as client:
        if "patient_id" in params:
            resp = await client.get(
                f"{PMS_BASE_URL}/api/prescriptions",
                params={"patient_id": params["patient_id"], "active": True},
            )
            resp.raise_for_status()
            prescriptions = resp.json()
            return {
                "patient_id": params["patient_id"],
                "active_medications": [
                    {
                        "name": rx["medication_name"],
                        "dosage": rx["dosage"],
                        "frequency": rx["frequency"],
                        "prescriber": rx.get("prescriber", ""),
                        "refills_remaining": rx.get("refills_remaining", 0),
                    }
                    for rx in prescriptions
                ],
            }
        return {"error": "Provide 'patient_id'"}


async def report_gen(params: dict) -> dict:
    """Generate or retrieve clinical reports."""
    async with httpx.AsyncClient() as client:
        report_type = params.get("type", "daily_census")
        resp = await client.get(
            f"{PMS_BASE_URL}/api/reports",
            params={"type": report_type, "date": str(date.today())},
        )
        resp.raise_for_status()
        return resp.json()


async def schedule_query(params: dict) -> dict:
    """Query appointments and availability."""
    async with httpx.AsyncClient() as client:
        query_params = {}
        if "provider" in params:
            query_params["provider"] = params["provider"]
        if "date" in params:
            d = params["date"]
            query_params["date"] = str(date.today()) if d == "today" else d
        if "room" in params:
            query_params["room"] = params["room"]

        resp = await client.get(
            f"{PMS_BASE_URL}/api/appointments",
            params=query_params,
        )
        resp.raise_for_status()
        return resp.json()


# Tool registry for the gateway adapter
TOOL_REGISTRY = {
    "patient_lookup": patient_lookup,
    "encounter_summary": encounter_summary,
    "rx_check": rx_check,
    "report_gen": report_gen,
    "schedule_query": schedule_query,
}
```

### Step 3: Implement the Gateway Adapter

`pms-backend/app/integrations/nullclaw/adapter.py`:

```python
"""FastAPI routes that NullClaw calls to execute PMS tools."""

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Any

from .tools import TOOL_REGISTRY
from .auth import verify_nullclaw_token


router = APIRouter(prefix="/integrations/nullclaw", tags=["nullclaw"])


class ToolRequest(BaseModel):
    tool: str
    params: dict[str, Any]
    staff_id: str | None = None
    session_id: str | None = None


class ToolResponse(BaseModel):
    result: dict[str, Any]
    error: str | None = None


@router.post("/execute", response_model=ToolResponse)
async def execute_tool(
    request: ToolRequest,
    authorization: str = Header(...),
):
    """Execute a PMS tool on behalf of NullClaw."""
    if not verify_nullclaw_token(authorization):
        raise HTTPException(status_code=401, detail="Invalid NullClaw token")

    tool_fn = TOOL_REGISTRY.get(request.tool)
    if not tool_fn:
        raise HTTPException(
            status_code=404, detail=f"Unknown tool: {request.tool}"
        )

    try:
        result = await tool_fn(request.params)
        return ToolResponse(result=result)
    except Exception as e:
        return ToolResponse(result={}, error=str(e))


@router.get("/health")
async def nullclaw_health():
    """Health check for NullClaw integration."""
    return {
        "status": "ok",
        "tools_available": list(TOOL_REGISTRY.keys()),
        "tool_count": len(TOOL_REGISTRY),
    }
```

### Step 4: Implement Token Verification

`pms-backend/app/integrations/nullclaw/auth.py`:

```python
"""Authentication for NullClaw gateway adapter."""

import os
import hmac

# Shared secret configured in both NullClaw and PMS backend
NULLCLAW_SERVICE_TOKEN = os.environ.get("NULLCLAW_SERVICE_TOKEN", "")


def verify_nullclaw_token(authorization_header: str) -> bool:
    """Verify the bearer token from NullClaw matches the shared secret."""
    if not NULLCLAW_SERVICE_TOKEN:
        return False
    token = authorization_header.removeprefix("Bearer ").strip()
    return hmac.compare_digest(token, NULLCLAW_SERVICE_TOKEN)
```

### Step 5: Register the Router

Add to your FastAPI app initialization (e.g., `pms-backend/app/main.py`):

```python
from app.integrations.nullclaw.adapter import router as nullclaw_router

app.include_router(nullclaw_router)
```

### Step 6: Set Environment Variables

Add to your `.env` file:

```bash
# NullClaw Integration
NULLCLAW_SERVICE_TOKEN=your-secure-random-token-here
NULLCLAW_GATEWAY_URL=http://127.0.0.1:3001
NULLCLAW_GATEWAY_PORT=3001
```

### Step 7: Configure NullClaw Custom Tools

Add PMS tools to NullClaw's configuration so it knows how to call them:

```json
{
  "tools": {
    "custom": [
      {
        "name": "patient_lookup",
        "description": "Search for patients by name, MRN, or date of birth. Returns demographics, allergies, and insurance info.",
        "endpoint": "http://127.0.0.1:8000/integrations/nullclaw/execute",
        "method": "POST",
        "headers": {
          "Authorization": "Bearer YOUR_SERVICE_TOKEN",
          "Content-Type": "application/json"
        },
        "body_template": "{\"tool\": \"patient_lookup\", \"params\": {{params}}, \"staff_id\": \"{{staff_id}}\"}"
      },
      {
        "name": "encounter_summary",
        "description": "Get encounter details for a patient or list encounters by provider and date.",
        "endpoint": "http://127.0.0.1:8000/integrations/nullclaw/execute",
        "method": "POST",
        "headers": {
          "Authorization": "Bearer YOUR_SERVICE_TOKEN",
          "Content-Type": "application/json"
        },
        "body_template": "{\"tool\": \"encounter_summary\", \"params\": {{params}}, \"staff_id\": \"{{staff_id}}\"}"
      },
      {
        "name": "rx_check",
        "description": "Check active medications and drug interactions for a patient.",
        "endpoint": "http://127.0.0.1:8000/integrations/nullclaw/execute",
        "method": "POST",
        "headers": {
          "Authorization": "Bearer YOUR_SERVICE_TOKEN",
          "Content-Type": "application/json"
        },
        "body_template": "{\"tool\": \"rx_check\", \"params\": {{params}}, \"staff_id\": \"{{staff_id}}\"}"
      },
      {
        "name": "report_gen",
        "description": "Generate or retrieve clinical reports (daily census, pending labs, overdue follow-ups).",
        "endpoint": "http://127.0.0.1:8000/integrations/nullclaw/execute",
        "method": "POST",
        "headers": {
          "Authorization": "Bearer YOUR_SERVICE_TOKEN",
          "Content-Type": "application/json"
        },
        "body_template": "{\"tool\": \"report_gen\", \"params\": {{params}}, \"staff_id\": \"{{staff_id}}\"}"
      },
      {
        "name": "schedule_query",
        "description": "Query appointments, provider schedules, and room availability.",
        "endpoint": "http://127.0.0.1:8000/integrations/nullclaw/execute",
        "method": "POST",
        "headers": {
          "Authorization": "Bearer YOUR_SERVICE_TOKEN",
          "Content-Type": "application/json"
        },
        "body_template": "{\"tool\": \"schedule_query\", \"params\": {{params}}, \"staff_id\": \"{{staff_id}}\"}"
      }
    ]
  }
}
```

**Checkpoint**: PMS backend has a `/integrations/nullclaw/execute` endpoint that NullClaw can call to execute PMS tools. Five tools are registered and callable.

## 5. Part C: Integrate with PMS Frontend

### Step 1: Install WebSocket Client Dependencies

```bash
cd pms-frontend
npm install --save ws
```

### Step 2: Create the NullClaw Chat Widget Component

`pms-frontend/src/components/nullclaw/ChatWidget.tsx`:

```tsx
"use client";

import { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ChatWidgetProps {
  nullclawUrl?: string;
  bearerToken: string;
  staffId: string;
  staffName: string;
}

export default function ChatWidget({
  nullclawUrl = "http://127.0.0.1:3001",
  bearerToken,
  staffId,
  staffName,
}: ChatWidgetProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(`${nullclawUrl}/webhook`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${bearerToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMessage.content,
          metadata: { staff_id: staffId, staff_name: staffName },
        }),
      });

      const data = await response.json();
      const assistantMessage: Message = {
        role: "assistant",
        content: data.response || data.message || "No response received.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Error: Unable to reach NullClaw. Please try again.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 bg-red-600 text-white rounded-full w-14 h-14 flex items-center justify-center shadow-lg hover:bg-red-700 transition-colors z-50"
        aria-label="Open clinical assistant"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
          />
        </svg>
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-96 h-[32rem] bg-white rounded-lg shadow-2xl flex flex-col z-50 border border-gray-200">
      {/* Header */}
      <div className="bg-red-600 text-white px-4 py-3 rounded-t-lg flex justify-between items-center">
        <div>
          <h3 className="font-semibold text-sm">PMS Clinical Assistant</h3>
          <p className="text-xs opacity-80">Powered by NullClaw</p>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="text-white hover:opacity-80"
          aria-label="Close chat"
        >
          &times;
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <p className="text-gray-400 text-sm text-center mt-8">
            Ask me about patients, encounters, medications, or schedules.
          </p>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] px-3 py-2 rounded-lg text-sm ${
                msg.role === "user"
                  ? "bg-red-600 text-white"
                  : "bg-gray-100 text-gray-800"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 px-3 py-2 rounded-lg text-sm text-gray-500">
              Thinking...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t px-4 py-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Ask about a patient..."
            className="flex-1 border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className="bg-red-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-red-700 disabled:opacity-50 transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
```

### Step 3: Add Environment Variables

Add to `pms-frontend/.env.local`:

```bash
NEXT_PUBLIC_NULLCLAW_URL=http://127.0.0.1:3001
NEXT_PUBLIC_NULLCLAW_TOKEN=your-bearer-token
```

### Step 4: Embed the Widget in the Layout

Add the chat widget to your main layout (e.g., `pms-frontend/src/app/layout.tsx`):

```tsx
import ChatWidget from "@/components/nullclaw/ChatWidget";

// Inside your layout component, after the main content:
<ChatWidget
  nullclawUrl={process.env.NEXT_PUBLIC_NULLCLAW_URL}
  bearerToken={process.env.NEXT_PUBLIC_NULLCLAW_TOKEN!}
  staffId={currentUser.id}
  staffName={currentUser.name}
/>
```

**Checkpoint**: The PMS frontend has a floating chat widget in the bottom-right corner that sends messages to NullClaw's gateway and displays responses.

## 6. Part D: Testing and Verification

### Step 1: Service Health Checks

```bash
# NullClaw health
curl -s http://127.0.0.1:3001/health
# Expected: {"status":"ok"}

# PMS NullClaw adapter health
curl -s http://127.0.0.1:8000/integrations/nullclaw/health
# Expected: {"status":"ok","tools_available":["patient_lookup","encounter_summary","rx_check","report_gen","schedule_query"],"tool_count":5}
```

### Step 2: Test Tool Execution Directly

```bash
# Test patient lookup via PMS adapter
curl -X POST http://127.0.0.1:8000/integrations/nullclaw/execute \
  -H "Authorization: Bearer $NULLCLAW_SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tool": "patient_lookup", "params": {"query": "Smith"}, "staff_id": "test-nurse-001"}'

# Expected: {"result":{"count":N,"patients":[...]},"error":null}
```

### Step 3: Test End-to-End via NullClaw

```bash
# Send a clinical query through NullClaw
curl -X POST http://127.0.0.1:3001/webhook \
  -H "Authorization: Bearer $NULLCLAW_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Look up patient John Smith"}'

# Expected: NullClaw calls patient_lookup tool, returns formatted patient info
```

### Step 4: Verify Audit Logging

```bash
psql -h localhost -U pms_user -d pms_db -c \
  "SELECT timestamp, channel, tool_name, approval_status FROM nullclaw_audit ORDER BY timestamp DESC LIMIT 5;"

# Expected: Recent tool invocations with timestamps and tool names
```

### Step 5: Test NullClaw System Diagnostics

```bash
nullclaw doctor
nullclaw status
nullclaw channel status
```

**Checkpoint**: All health checks pass, tools execute correctly via both direct API calls and NullClaw webhook messages, audit logs are being written to PostgreSQL.

## 7. Troubleshooting

### NullClaw Fails to Start

**Symptom**: `nullclaw gateway` exits immediately or prints error.

**Solution**:
```bash
# Check if port 3001 is in use
lsof -i :3001

# Run diagnostics
nullclaw doctor

# Check config syntax
cat ~/.config/nullclaw/config.json | python3 -m json.tool
```

### Pairing Code Not Displayed

**Symptom**: Gateway starts but no pairing code appears.

**Solution**: Pairing may already be completed. Check if a token file exists:
```bash
ls ~/.config/nullclaw/
# Look for a token or pairing file
# To re-pair, delete the existing token and restart the gateway
```

### Connection Refused Between NullClaw and PMS Backend

**Symptom**: NullClaw tool calls return connection errors.

**Solution**:
```bash
# Verify PMS backend is running
curl -s http://127.0.0.1:8000/integrations/nullclaw/health

# If running in Docker, ensure both containers are on the same network
docker network ls
docker network inspect pms_network

# Use Docker service names instead of localhost in NullClaw config
# e.g., "http://pms-backend:8000" instead of "http://127.0.0.1:8000"
```

### Bearer Token Authentication Failures

**Symptom**: 401 errors when NullClaw calls PMS tools.

**Solution**:
```bash
# Verify the token matches
echo $NULLCLAW_SERVICE_TOKEN

# Test directly
curl -X POST http://127.0.0.1:8000/integrations/nullclaw/execute \
  -H "Authorization: Bearer $NULLCLAW_SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tool": "patient_lookup", "params": {"query": "test"}}'

# Ensure .env has NULLCLAW_SERVICE_TOKEN set and the backend was restarted
```

### Port Conflicts

**Symptom**: `Address already in use` error on port 3001.

**Solution**:
```bash
# Find what's using the port
lsof -i :3001

# Kill the process or use a different port
nullclaw gateway --port 3002

# Update all configs to reference the new port
```

### High Memory Usage

**Symptom**: NullClaw using more than expected ~1 MB.

**Solution**: NullClaw itself uses ~1 MB. Higher usage typically comes from:
```bash
# Check NullClaw process memory
/usr/bin/time -l nullclaw status

# If memory grows over time, check conversation history size
psql -h localhost -U pms_user -d pms_db -c \
  "SELECT COUNT(*), pg_size_pretty(pg_total_relation_size('nullclaw_memory')) FROM nullclaw_memory;"

# Archive old conversations
nullclaw memory archive --older-than 90d
```

## 8. Reference Commands

### Daily Development Workflow

```bash
# Start NullClaw (if not running as service)
nullclaw gateway --port 3001

# Interactive chat for testing
nullclaw agent

# Check status
nullclaw status

# View recent conversations
nullclaw memory list --limit 10
```

### Management Commands

```bash
# Install as background service
nullclaw service install
nullclaw service status
nullclaw service stop

# Channel management
nullclaw channel status
nullclaw channel start telegram
nullclaw channel start slack

# Memory management
nullclaw memory archive --older-than 90d
nullclaw memory export --format json > backup.json

# Run diagnostics
nullclaw doctor
```

### Monitoring Commands

```bash
# Health check
curl -s http://127.0.0.1:3001/health | python3 -m json.tool

# Audit log tail
psql -h localhost -U pms_user -d pms_db -c \
  "SELECT timestamp, staff_id, tool_name, approval_status FROM nullclaw_audit ORDER BY timestamp DESC LIMIT 20;"

# Memory usage
psql -h localhost -U pms_user -d pms_db -c \
  "SELECT channel, COUNT(*) as messages FROM nullclaw_memory GROUP BY channel;"
```

### Useful URLs

| Resource | URL |
|---|---|
| NullClaw Gateway Health | http://127.0.0.1:3001/health |
| PMS NullClaw Adapter Health | http://127.0.0.1:8000/integrations/nullclaw/health |
| PMS Backend API Docs | http://127.0.0.1:8000/docs |
| PMS Frontend | http://127.0.0.1:3000 |

## Next Steps

After completing this setup guide:
1. Follow the [NullClaw Developer Tutorial](83-NullClaw-Developer-Tutorial.md) to build your first patient lookup assistant end-to-end
2. Configure additional channels (Telegram, Slack) for staff communication
3. Review the [PRD](83-PRD-NullClaw-PMS-Integration.md) for the full integration roadmap

## Resources

- [NullClaw GitHub Repository](https://github.com/nullclaw/nullclaw) — Source code and documentation
- [NullClaw Official Website](https://nullclaw.io) — Project overview
- [NullClaw Architecture Docs](https://github.com/nullclaw/nullclaw/blob/main/docs/en/architecture.md) — Subsystem design
- [NullClaw Security Docs](https://github.com/nullclaw/nullclaw/blob/main/docs/en/security.md) — Security hardening guide
- [NullClaw Gateway API](https://github.com/nullclaw/nullclaw/blob/main/docs/en/gateway-api.md) — HTTP endpoint reference
- [NullClaw Configuration Guide](https://github.com/nullclaw/nullclaw/blob/main/docs/en/configuration.md) — Full config reference
- [PMS Backend API Endpoints](../api/backend-endpoints.md) — PMS REST API reference
- [ADR-0007: Jetson Thor Edge Deployment](../architecture/0007-jetson-thor-edge-deployment.md) — Edge deployment context
