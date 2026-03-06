# GPT-5.4 Clinical Benchmark Setup Guide for PMS Integration

**Document ID:** PMS-EXP-GPT54BENCH-001
**Version:** 1.0
**Date:** 2026-03-06
**Applies To:** PMS project (all platforms)
**Prerequisites Level:** Intermediate

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Part A: Configure API Access for Both Providers](#3-part-a-configure-api-access-for-both-providers)
4. [Part B: Build the Benchmark Runner Service](#4-part-b-build-the-benchmark-runner-service)
5. [Part C: Build the Quality Evaluator](#5-part-c-build-the-quality-evaluator)
6. [Part D: Build the Benchmark Dashboard](#6-part-d-build-the-benchmark-dashboard)
7. [Part E: Testing and Verification](#7-part-e-testing-and-verification)
8. [Troubleshooting](#8-troubleshooting)
9. [Reference Commands](#9-reference-commands)

## 1. Overview

This guide sets up a head-to-head benchmarking framework that evaluates GPT-5.4 and Claude Opus 4.6 on clinical PMS tasks. By the end, you will have:

- Both OpenAI and Anthropic SDKs configured with API keys
- A Benchmark Runner that sends identical de-identified prompts to both models
- A Quality Evaluator that scores responses on clinical dimensions
- A Cost Analysis Engine that projects savings at scale
- A Next.js dashboard displaying comparison results

```mermaid
flowchart LR
    subgraph Setup["What You're Building"]
        A["API Access<br/>(OpenAI + Anthropic)"] --> B["Benchmark Runner<br/>(FastAPI service)"]
        B --> C["Quality Evaluator<br/>(LLM-as-Judge)"]
        B --> D["Cost Analyzer"]
        C --> E["Dashboard<br/>(Next.js)"]
        D --> E
    end

    style A fill:#10a37f,color:#fff
    style B fill:#7c3aed,color:#fff
    style C fill:#e74c3c,color:#fff
    style D fill:#2ecc71,color:#fff
    style E fill:#0070f3,color:#fff
```

## 2. Prerequisites

### 2.1 Required Software

| Software | Minimum Version | Check Command |
|----------|----------------|---------------|
| Python | 3.11+ | `python --version` |
| Node.js | 18+ | `node --version` |
| PostgreSQL | 15+ | `psql --version` |
| pip | 23+ | `pip --version` |
| OpenAI API key | — | Set in `OPENAI_API_KEY` |
| Anthropic API key | — | Set in `ANTHROPIC_API_KEY` |

### 2.2 Installation of Prerequisites

**1. Install the OpenAI Python SDK:**

```bash
pip install openai>=1.70
```

**2. Install the Anthropic Python SDK (if not already installed):**

```bash
pip install anthropic>=0.50
```

**3. Install benchmark utilities:**

```bash
pip install pandas numpy tabulate
```

### 2.3 Verify PMS Services

```bash
# Backend should respond on port 8000
curl -s http://localhost:8000/api/health | python -m json.tool

# Frontend should respond on port 3000
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000

# PostgreSQL should accept connections
psql -h localhost -p 5432 -U pms_user -d pms_db -c "SELECT 1;"
```

## 3. Part A: Configure API Access for Both Providers

### Step 1: Set up environment variables

Add to your `.env` file in the PMS backend:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-openai-key-here
OPENAI_MODEL=gpt-5.4
OPENAI_ORG_ID=org-your-org-id  # Optional

# Anthropic Configuration (likely already set)
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
ANTHROPIC_MODEL=claude-opus-4-6-20260204

# Benchmark Configuration
BENCHMARK_JUDGE_MODEL=claude-sonnet-4-6-20260514
BENCHMARK_MAX_CONCURRENT=5
BENCHMARK_TIMEOUT_SECONDS=60
```

### Step 2: Verify OpenAI API connectivity

```bash
python -c "
from openai import OpenAI
client = OpenAI()
response = client.responses.create(
    model='gpt-5.4',
    input='Respond with exactly: CONNECTED'
)
print(response.output_text)
"
```

Expected output: `CONNECTED`

### Step 3: Verify Anthropic API connectivity

```bash
python -c "
import anthropic
client = anthropic.Anthropic()
msg = client.messages.create(
    model='claude-opus-4-6-20260204',
    max_tokens=10,
    messages=[{'role': 'user', 'content': 'Respond with exactly: CONNECTED'}]
)
print(msg.content[0].text)
"
```

Expected output: `CONNECTED`

### Step 4: Create benchmark database tables

```sql
-- Run in PostgreSQL
CREATE TABLE IF NOT EXISTS benchmark_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_type VARCHAR(50) NOT NULL,  -- 'summarization', 'medication_analysis', 'prior_auth'
    task_id VARCHAR(100) NOT NULL,
    prompt_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS benchmark_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES benchmark_runs(id),
    model_provider VARCHAR(20) NOT NULL,  -- 'openai' or 'anthropic'
    model_id VARCHAR(100) NOT NULL,
    response_text TEXT NOT NULL,
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    latency_ms INTEGER NOT NULL,
    cost_input_usd NUMERIC(10, 6) NOT NULL,
    cost_output_usd NUMERIC(10, 6) NOT NULL,
    cost_total_usd NUMERIC(10, 6) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS benchmark_evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES benchmark_runs(id),
    result_id UUID REFERENCES benchmark_results(id),
    judge_model VARCHAR(100) NOT NULL,
    accuracy_score SMALLINT CHECK (accuracy_score BETWEEN 1 AND 5),
    completeness_score SMALLINT CHECK (completeness_score BETWEEN 1 AND 5),
    clinical_relevance_score SMALLINT CHECK (clinical_relevance_score BETWEEN 1 AND 5),
    safety_score SMALLINT CHECK (safety_score BETWEEN 1 AND 5),
    structure_score SMALLINT CHECK (structure_score BETWEEN 1 AND 5),
    aggregate_score NUMERIC(3, 2),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_benchmark_results_run_id ON benchmark_results(run_id);
CREATE INDEX idx_benchmark_evaluations_run_id ON benchmark_evaluations(run_id);
CREATE INDEX idx_benchmark_runs_task_type ON benchmark_runs(task_type);
```

**Checkpoint:** You have both SDKs installed, API keys configured, connectivity verified, and database tables created.

## 4. Part B: Build the Benchmark Runner Service

### Step 1: Create the provider abstraction

Create `app/services/benchmark/providers.py`:

```python
"""Dual-provider abstraction for GPT-5.4 and Claude Opus 4.6."""

import time
from dataclasses import dataclass
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from app.core.config import settings


@dataclass
class ModelResponse:
    provider: str
    model_id: str
    text: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    cost_input: float
    cost_output: float
    cost_total: float


# Pricing per million tokens
PRICING = {
    "openai": {"input": 2.50, "output": 15.00},
    "anthropic": {"input": 5.00, "output": 25.00},
}


def _calculate_cost(provider: str, input_tokens: int, output_tokens: int) -> tuple[float, float, float]:
    rates = PRICING[provider]
    cost_in = (input_tokens / 1_000_000) * rates["input"]
    cost_out = (output_tokens / 1_000_000) * rates["output"]
    return cost_in, cost_out, cost_in + cost_out


async def call_openai(prompt: str, system: str = "") -> ModelResponse:
    client = AsyncOpenAI()
    instructions = system or "You are a clinical AI assistant."

    start = time.perf_counter_ns()
    response = await client.responses.create(
        model=settings.OPENAI_MODEL,
        instructions=instructions,
        input=prompt,
    )
    latency_ms = (time.perf_counter_ns() - start) // 1_000_000

    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    cost_in, cost_out, cost_total = _calculate_cost("openai", input_tokens, output_tokens)

    return ModelResponse(
        provider="openai",
        model_id=settings.OPENAI_MODEL,
        text=response.output_text,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        cost_input=cost_in,
        cost_output=cost_out,
        cost_total=cost_total,
    )


async def call_anthropic(prompt: str, system: str = "") -> ModelResponse:
    client = AsyncAnthropic()
    sys_msg = system or "You are a clinical AI assistant."

    start = time.perf_counter_ns()
    message = await client.messages.create(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=4096,
        system=sys_msg,
        messages=[{"role": "user", "content": prompt}],
    )
    latency_ms = (time.perf_counter_ns() - start) // 1_000_000

    input_tokens = message.usage.input_tokens
    output_tokens = message.usage.output_tokens
    cost_in, cost_out, cost_total = _calculate_cost("anthropic", input_tokens, output_tokens)

    return ModelResponse(
        provider="anthropic",
        model_id=settings.ANTHROPIC_MODEL,
        text=message.content[0].text,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        cost_input=cost_in,
        cost_output=cost_out,
        cost_total=cost_total,
    )
```

### Step 2: Create clinical task templates

Create `app/services/benchmark/tasks.py`:

```python
"""Clinical benchmark task definitions for the three target use cases."""

from dataclasses import dataclass


@dataclass
class BenchmarkTask:
    task_type: str
    task_id: str
    system_prompt: str
    user_prompt_template: str


ENCOUNTER_SUMMARIZATION = BenchmarkTask(
    task_type="summarization",
    task_id="encounter_summary",
    system_prompt=(
        "You are a clinical documentation specialist. Summarize the encounter note "
        "into a structured format with: Chief Complaint, History of Present Illness "
        "(2-3 sentences), Assessment (numbered problem list), and Plan (numbered, "
        "with specific actions). Use medical terminology. Do not invent information "
        "not present in the note."
    ),
    user_prompt_template="Summarize the following encounter note:\n\n{encounter_text}",
)

MEDICATION_INTERACTION = BenchmarkTask(
    task_type="medication_analysis",
    task_id="drug_interaction",
    system_prompt=(
        "You are a clinical pharmacology AI. Analyze the medication list for potential "
        "drug-drug interactions, contraindications given the patient context, and "
        "dosing concerns. For each finding, provide: Severity (Critical/Major/Moderate/"
        "Minor), Mechanism, Clinical Significance, and Recommended Action. "
        "If no interactions are found, state that explicitly."
    ),
    user_prompt_template=(
        "Patient context: {patient_context}\n\n"
        "Current medications:\n{medication_list}\n\n"
        "Analyze for drug interactions and safety concerns."
    ),
)

PRIOR_AUTH_DECISION = BenchmarkTask(
    task_type="prior_auth",
    task_id="prior_auth_decision",
    system_prompt=(
        "You are a prior authorization clinical reviewer. Given the clinical notes "
        "and payer criteria, produce a structured decision with: Decision (Approve/"
        "Deny/Request Additional Info), Clinical Justification (citing specific "
        "criteria met/unmet), Key Supporting Evidence from the notes, and if denied, "
        "a draft Appeal Letter. Be specific and cite exact criteria."
    ),
    user_prompt_template=(
        "Clinical notes:\n{clinical_notes}\n\n"
        "Payer authorization criteria:\n{payer_criteria}\n\n"
        "Requested service: {requested_service}\n\n"
        "Provide prior authorization determination."
    ),
)

ALL_TASKS = [ENCOUNTER_SUMMARIZATION, MEDICATION_INTERACTION, PRIOR_AUTH_DECISION]
```

### Step 3: Create the benchmark runner

Create `app/services/benchmark/runner.py`:

```python
"""Benchmark runner: sends identical prompts to both models and records results."""

import asyncio
import hashlib
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.benchmark.providers import call_openai, call_anthropic, ModelResponse
from app.services.benchmark.tasks import BenchmarkTask
from app.services.phi_deid import deidentify_text  # Existing PHI De-ID Gateway


async def run_benchmark(
    task: BenchmarkTask,
    template_vars: dict,
    db: AsyncSession,
) -> dict:
    """Run a single benchmark: same prompt to both models, record results."""

    # Build prompt from template
    raw_prompt = task.user_prompt_template.format(**template_vars)

    # De-identify before sending to either provider
    deid_prompt = await deidentify_text(raw_prompt)
    prompt_hash = hashlib.sha256(deid_prompt.encode()).hexdigest()

    # Create benchmark run record
    run_id = str(uuid.uuid4())
    await db.execute(
        """INSERT INTO benchmark_runs (id, task_type, task_id, prompt_hash)
           VALUES (:id, :task_type, :task_id, :prompt_hash)""",
        {"id": run_id, "task_type": task.task_type, "task_id": task.task_id, "prompt_hash": prompt_hash},
    )

    # Call both models in parallel
    openai_result, anthropic_result = await asyncio.gather(
        call_openai(deid_prompt, task.system_prompt),
        call_anthropic(deid_prompt, task.system_prompt),
    )

    # Persist results
    for result in [openai_result, anthropic_result]:
        await db.execute(
            """INSERT INTO benchmark_results
               (id, run_id, model_provider, model_id, response_text,
                input_tokens, output_tokens, latency_ms,
                cost_input_usd, cost_output_usd, cost_total_usd)
               VALUES (:id, :run_id, :provider, :model_id, :text,
                       :input_tokens, :output_tokens, :latency_ms,
                       :cost_input, :cost_output, :cost_total)""",
            {
                "id": str(uuid.uuid4()),
                "run_id": run_id,
                "provider": result.provider,
                "model_id": result.model_id,
                "text": result.text,
                "input_tokens": result.input_tokens,
                "output_tokens": result.output_tokens,
                "latency_ms": result.latency_ms,
                "cost_input": result.cost_input,
                "cost_output": result.cost_output,
                "cost_total": result.cost_total,
            },
        )

    await db.commit()

    return {
        "run_id": run_id,
        "openai": _response_summary(openai_result),
        "anthropic": _response_summary(anthropic_result),
        "cost_savings": anthropic_result.cost_total - openai_result.cost_total,
        "cost_savings_pct": (
            (anthropic_result.cost_total - openai_result.cost_total)
            / anthropic_result.cost_total
            * 100
            if anthropic_result.cost_total > 0
            else 0
        ),
    }


def _response_summary(r: ModelResponse) -> dict:
    return {
        "provider": r.provider,
        "model": r.model_id,
        "tokens": {"input": r.input_tokens, "output": r.output_tokens},
        "latency_ms": r.latency_ms,
        "cost_usd": round(r.cost_total, 6),
    }
```

### Step 4: Create the FastAPI router

Create `app/routers/benchmark.py`:

```python
"""Benchmark API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.benchmark.runner import run_benchmark
from app.services.benchmark.tasks import ALL_TASKS, ENCOUNTER_SUMMARIZATION
from pydantic import BaseModel

router = APIRouter(prefix="/api/benchmark", tags=["benchmark"])


class BenchmarkRequest(BaseModel):
    task_type: str  # "summarization", "medication_analysis", "prior_auth"
    template_vars: dict


class BenchmarkSuiteResponse(BaseModel):
    total_runs: int
    total_cost_openai: float
    total_cost_anthropic: float
    total_savings: float


@router.post("/run")
async def run_single_benchmark(req: BenchmarkRequest, db: AsyncSession = Depends(get_db)):
    task = next((t for t in ALL_TASKS if t.task_type == req.task_type), None)
    if not task:
        return {"error": f"Unknown task type: {req.task_type}"}
    result = await run_benchmark(task, req.template_vars, db)
    return result


@router.get("/results")
async def get_benchmark_results(
    task_type: str | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    query = """
        SELECT r.id as run_id, r.task_type, r.created_at,
               br.model_provider, br.model_id,
               br.input_tokens, br.output_tokens, br.latency_ms,
               br.cost_total_usd
        FROM benchmark_runs r
        JOIN benchmark_results br ON br.run_id = r.id
    """
    params = {"limit": limit}
    if task_type:
        query += " WHERE r.task_type = :task_type"
        params["task_type"] = task_type
    query += " ORDER BY r.created_at DESC LIMIT :limit"

    rows = await db.execute(query, params)
    return {"results": [dict(row) for row in rows]}


@router.get("/cost-analysis")
async def get_cost_analysis(
    daily_volume: int = 1000,
    db: AsyncSession = Depends(get_db),
):
    """Project monthly costs based on benchmark averages and specified daily volume."""
    rows = await db.execute("""
        SELECT model_provider,
               AVG(cost_total_usd) as avg_cost_per_task,
               AVG(input_tokens) as avg_input_tokens,
               AVG(output_tokens) as avg_output_tokens,
               AVG(latency_ms) as avg_latency_ms,
               COUNT(*) as sample_size
        FROM benchmark_results
        GROUP BY model_provider
    """)
    results = {row["model_provider"]: dict(row) for row in rows}

    if "openai" in results and "anthropic" in results:
        openai_monthly = results["openai"]["avg_cost_per_task"] * daily_volume * 30
        anthropic_monthly = results["anthropic"]["avg_cost_per_task"] * daily_volume * 30
        return {
            "daily_volume": daily_volume,
            "openai": {
                **results["openai"],
                "projected_daily_usd": results["openai"]["avg_cost_per_task"] * daily_volume,
                "projected_monthly_usd": openai_monthly,
            },
            "anthropic": {
                **results["anthropic"],
                "projected_daily_usd": results["anthropic"]["avg_cost_per_task"] * daily_volume,
                "projected_monthly_usd": anthropic_monthly,
            },
            "monthly_savings_usd": anthropic_monthly - openai_monthly,
            "monthly_savings_pct": (
                (anthropic_monthly - openai_monthly) / anthropic_monthly * 100
                if anthropic_monthly > 0 else 0
            ),
        }
    return {"error": "Insufficient benchmark data. Run benchmarks first."}
```

**Checkpoint:** You have a working Benchmark Runner that calls both models in parallel, records results to PostgreSQL, and exposes API endpoints for running benchmarks and viewing results.

## 5. Part C: Build the Quality Evaluator

### Step 1: Create the LLM-as-Judge evaluator

Create `app/services/benchmark/evaluator.py`:

```python
"""LLM-as-Judge quality evaluator for clinical benchmark responses."""

import json
from anthropic import AsyncAnthropic
from app.core.config import settings

JUDGE_RUBRIC = """You are evaluating a clinical AI response for quality.
Score each dimension from 1 (poor) to 5 (excellent):

1. **Accuracy**: Are all clinical facts correct? No hallucinated medications, dosages, or diagnoses?
2. **Completeness**: Does the response address all aspects of the clinical query?
3. **Clinical Relevance**: Is the information clinically actionable and appropriate?
4. **Safety**: Does the response avoid potentially harmful recommendations? Does it flag uncertainties?
5. **Structure**: Is the output well-organized and follows the requested format?

Respond in JSON:
{"accuracy": N, "completeness": N, "clinical_relevance": N, "safety": N, "structure": N, "notes": "brief justification"}
"""


async def evaluate_response(
    task_description: str,
    prompt: str,
    response_text: str,
    model_provider: str,
) -> dict:
    """Score a single model response using LLM-as-Judge."""
    client = AsyncAnthropic()

    judge_prompt = f"""Task: {task_description}

Original prompt (de-identified):
{prompt[:2000]}

Model response ({model_provider}):
{response_text[:4000]}

{JUDGE_RUBRIC}"""

    message = await client.messages.create(
        model=settings.BENCHMARK_JUDGE_MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": judge_prompt}],
    )

    try:
        scores = json.loads(message.content[0].text)
        scores["aggregate"] = round(
            sum(scores[k] for k in ["accuracy", "completeness", "clinical_relevance", "safety", "structure"]) / 5, 2
        )
        return scores
    except (json.JSONDecodeError, KeyError):
        return {"error": "Failed to parse judge response", "raw": message.content[0].text}
```

**Checkpoint:** You have an automated quality evaluator that scores clinical responses on 5 dimensions using an LLM judge.

## 6. Part D: Build the Benchmark Dashboard

### Step 1: Create the comparison component

Create `components/benchmark/BenchmarkComparison.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";

interface BenchmarkResult {
  run_id: string;
  task_type: string;
  openai: { cost_usd: number; latency_ms: number; tokens: { input: number; output: number } };
  anthropic: { cost_usd: number; latency_ms: number; tokens: { input: number; output: number } };
  cost_savings_pct: number;
}

interface CostAnalysis {
  daily_volume: number;
  openai: { projected_monthly_usd: number; avg_latency_ms: number };
  anthropic: { projected_monthly_usd: number; avg_latency_ms: number };
  monthly_savings_usd: number;
  monthly_savings_pct: number;
}

export default function BenchmarkComparison() {
  const [costAnalysis, setCostAnalysis] = useState<CostAnalysis | null>(null);
  const [volume, setVolume] = useState(1000);

  useEffect(() => {
    fetch(`/api/benchmark/cost-analysis?daily_volume=${volume}`)
      .then((r) => r.json())
      .then(setCostAnalysis);
  }, [volume]);

  if (!costAnalysis) return <div className="p-4">Loading benchmark data...</div>;

  return (
    <div className="space-y-6 p-6">
      <h2 className="text-2xl font-bold">GPT-5.4 vs Claude Opus 4.6 — Cost-Benefit Analysis</h2>

      {/* Volume slider */}
      <div className="flex items-center gap-4">
        <label className="text-sm font-medium">Daily task volume:</label>
        <input
          type="range"
          min={100}
          max={5000}
          step={100}
          value={volume}
          onChange={(e) => setVolume(Number(e.target.value))}
          className="w-64"
        />
        <span className="text-lg font-mono">{volume.toLocaleString()}</span>
      </div>

      {/* Cost comparison cards */}
      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-lg border bg-emerald-50 p-4">
          <h3 className="text-sm font-medium text-emerald-800">GPT-5.4 Monthly Cost</h3>
          <p className="text-3xl font-bold text-emerald-600">
            ${costAnalysis.openai.projected_monthly_usd.toFixed(2)}
          </p>
        </div>
        <div className="rounded-lg border bg-amber-50 p-4">
          <h3 className="text-sm font-medium text-amber-800">Claude Opus 4.6 Monthly Cost</h3>
          <p className="text-3xl font-bold text-amber-600">
            ${costAnalysis.anthropic.projected_monthly_usd.toFixed(2)}
          </p>
        </div>
        <div className="rounded-lg border bg-blue-50 p-4">
          <h3 className="text-sm font-medium text-blue-800">Monthly Savings (GPT-5.4)</h3>
          <p className="text-3xl font-bold text-blue-600">
            ${costAnalysis.monthly_savings_usd.toFixed(2)}
            <span className="text-lg ml-2">({costAnalysis.monthly_savings_pct.toFixed(1)}%)</span>
          </p>
        </div>
      </div>

      {/* Pricing reference */}
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="border-b">
            <th className="text-left p-2">Dimension</th>
            <th className="text-right p-2">GPT-5.4</th>
            <th className="text-right p-2">Claude Opus 4.6</th>
            <th className="text-right p-2">Difference</th>
          </tr>
        </thead>
        <tbody>
          <tr className="border-b">
            <td className="p-2">Input ($/MTok)</td>
            <td className="text-right p-2 font-mono">$2.50</td>
            <td className="text-right p-2 font-mono">$5.00</td>
            <td className="text-right p-2 text-emerald-600 font-mono">2x cheaper</td>
          </tr>
          <tr className="border-b">
            <td className="p-2">Output ($/MTok)</td>
            <td className="text-right p-2 font-mono">$15.00</td>
            <td className="text-right p-2 font-mono">$25.00</td>
            <td className="text-right p-2 text-emerald-600 font-mono">1.67x cheaper</td>
          </tr>
          <tr className="border-b">
            <td className="p-2">Avg Latency</td>
            <td className="text-right p-2 font-mono">{costAnalysis.openai.avg_latency_ms}ms</td>
            <td className="text-right p-2 font-mono">{costAnalysis.anthropic.avg_latency_ms}ms</td>
            <td className="text-right p-2 font-mono">—</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}
```

**Checkpoint:** You have a Next.js dashboard component showing cost projections with an adjustable volume slider.

## 7. Part E: Testing and Verification

### Step 1: Run a single benchmark with synthetic data

```bash
curl -X POST http://localhost:8000/api/benchmark/run \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "summarization",
    "template_vars": {
      "encounter_text": "Patient is a 65-year-old male presenting with chest pain radiating to the left arm for the past 2 hours. History of hypertension and type 2 diabetes. Current medications include metformin 1000mg BID, lisinopril 20mg daily, and aspirin 81mg daily. Vitals: BP 158/92, HR 88, SpO2 97%. ECG shows ST depression in leads V4-V6. Troponin pending. Assessment: Acute coronary syndrome, rule out NSTEMI. Plan: Admit to telemetry, start heparin drip, serial troponins q6h, cardiology consult."
    }
  }'
```

Expected response:

```json
{
  "run_id": "uuid-here",
  "openai": {
    "provider": "openai",
    "model": "gpt-5.4",
    "tokens": {"input": 285, "output": 180},
    "latency_ms": 2500,
    "cost_usd": 0.003413
  },
  "anthropic": {
    "provider": "anthropic",
    "model": "claude-opus-4-6-20260204",
    "tokens": {"input": 290, "output": 195},
    "latency_ms": 3200,
    "cost_usd": 0.006325
  },
  "cost_savings": 0.002912,
  "cost_savings_pct": 46.1
}
```

### Step 2: Run a medication interaction benchmark

```bash
curl -X POST http://localhost:8000/api/benchmark/run \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "medication_analysis",
    "template_vars": {
      "patient_context": "72-year-old female, CKD stage 3 (eGFR 42), atrial fibrillation, osteoarthritis, depression",
      "medication_list": "1. Warfarin 5mg daily\n2. Amiodarone 200mg daily\n3. Ibuprofen 400mg TID\n4. Sertraline 100mg daily\n5. Metformin 500mg BID\n6. Lisinopril 10mg daily"
    }
  }'
```

### Step 3: Check cost analysis

```bash
curl "http://localhost:8000/api/benchmark/cost-analysis?daily_volume=1500"
```

### Step 4: Verify database records

```bash
psql -h localhost -p 5432 -U pms_user -d pms_db -c "
  SELECT r.task_type, br.model_provider, br.input_tokens, br.output_tokens,
         br.latency_ms, br.cost_total_usd
  FROM benchmark_runs r
  JOIN benchmark_results br ON br.run_id = r.id
  ORDER BY r.created_at DESC
  LIMIT 10;
"
```

**Checkpoint:** You have run benchmarks for at least two clinical task types, verified results are stored in PostgreSQL, and confirmed the cost analysis endpoint returns projections.

## 8. Troubleshooting

### OpenAI API returns 429 (Rate Limited)

**Symptom**: `RateLimitError` when running multiple benchmarks.

**Fix**: Reduce `BENCHMARK_MAX_CONCURRENT` in `.env`, or upgrade your OpenAI API tier. For batch benchmarks, use the Batch API at half the rate.

### Anthropic API returns model not found

**Symptom**: `NotFoundError: model claude-opus-4-6-20260204 not found`.

**Fix**: Verify exact model ID. Run `python -c "import anthropic; print(anthropic.Anthropic().models.list())"` to list available models. Update `ANTHROPIC_MODEL` in `.env`.

### Token count mismatch between providers

**Symptom**: GPT-5.4 and Claude report different input token counts for the same prompt.

**Cause**: Different tokenizers (tiktoken vs Claude's tokenizer). This is expected — token counts will differ by 5-15%. The cost calculation uses each provider's own token count, which is correct for cost projections.

### Quality Evaluator returns parse errors

**Symptom**: `Failed to parse judge response` in evaluation results.

**Fix**: The judge model may not always produce valid JSON. Add retry logic or use structured output (Anthropic's `tool_use` with JSON schema, or OpenAI's `response_format`).

### Latency results inconsistent

**Symptom**: Same benchmark shows 2x latency variation between runs.

**Cause**: Network variability, provider load, and cold starts. Run each benchmark 3-5 times and use median latency for comparisons.

## 9. Reference Commands

### Daily workflow

```bash
# Run the full benchmark suite (all 3 task types)
python -m app.services.benchmark.run_suite

# View latest results
curl http://localhost:8000/api/benchmark/results?limit=20

# Get cost projection for 2000 tasks/day
curl "http://localhost:8000/api/benchmark/cost-analysis?daily_volume=2000"

# Export results to CSV
psql -h localhost -p 5432 -U pms_user -d pms_db -c "
  COPY (SELECT * FROM benchmark_results ORDER BY created_at DESC)
  TO STDOUT WITH CSV HEADER
" > benchmark_export.csv
```

### Useful URLs

| Resource | URL |
|----------|-----|
| OpenAI API Playground | https://platform.openai.com/playground |
| OpenAI Usage Dashboard | https://platform.openai.com/usage |
| Anthropic Console | https://console.anthropic.com |
| Anthropic Usage | https://console.anthropic.com/settings/usage |
| PMS Benchmark Dashboard | http://localhost:3000/admin/benchmark |
| PMS Benchmark API | http://localhost:8000/api/benchmark/results |

## Next Steps

After completing setup:

1. Follow the [GPT-5.4 Clinical Benchmark Developer Tutorial](42-GPT54ClinicalBenchmark-Developer-Tutorial.md) to run your first full benchmark suite
2. Review [Claude Model Selection (Exp 15)](15-PRD-ClaudeModelSelection-PMS-Integration.md) to understand how benchmark results feed into the Model Router
3. Run the 150-task benchmark suite across all three clinical use cases
4. Present cost-benefit analysis to the clinical team for routing approval

## Resources

- [OpenAI API Documentation](https://developers.openai.com/api/docs/)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [Anthropic API Documentation](https://platform.claude.com/docs/)
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)
- [GPT-5.4 Model Card](https://developers.openai.com/api/docs/models/gpt-5.4)
- [Claude Opus 4.6](https://www.anthropic.com/claude/opus)
- [OpenAI Pricing](https://developers.openai.com/api/docs/pricing)
- [Claude Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
