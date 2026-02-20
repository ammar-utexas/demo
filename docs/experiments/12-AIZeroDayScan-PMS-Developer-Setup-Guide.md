# AI Zero-Day Vulnerability Scan Setup Guide for PMS Integration

**Document ID:** PMS-EXP-AIZERODAYSCAN-001
**Version:** 1.0
**Date:** February 20, 2026
**Applies To:** PMS project (all platforms)
**Prerequisites Level:** Intermediate

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Part A: CI/CD Security Gate Setup](#3-part-a-cicd-security-gate-setup)
4. [Part B: Developer CLI Integration](#4-part-b-developer-cli-integration)
5. [Part C: Deep Dependency Auditor Service](#5-part-c-deep-dependency-auditor-service)
6. [Part D: Security Dashboard Integration](#6-part-d-security-dashboard-integration)
7. [Part E: Testing and Verification](#7-part-e-testing-and-verification)
8. [Troubleshooting](#8-troubleshooting)
9. [Reference Commands](#9-reference-commands)
10. [Next Steps](#10-next-steps)
11. [Resources](#11-resources)

---

## 1. Overview

This guide walks you through setting up AI-powered zero-day vulnerability scanning for the PMS using Claude Opus 4.6. By the end, you will have:

- **CI/CD gate:** Every pull request automatically scanned for security vulnerabilities via GitHub Actions
- **Developer CLI:** Ad-hoc security scanning from your terminal via Claude Code's `/security-review`
- **Deep auditor:** A scheduled service that scans the full dependency tree weekly
- **Dashboard:** A frontend view of all security findings with severity, trends, and remediation tracking

```mermaid
flowchart LR
    subgraph Scan_Levels["Three Scanning Levels"]
        L1["Level 1: CI/CD<br/>Every PR"]
        L2["Level 2: CLI<br/>Ad-hoc"]
        L3["Level 3: Deep Scan<br/>Weekly"]
    end

    subgraph Tools["Tools Used"]
        GHA["GitHub Action<br/>claude-code-security-review"]
        CLI["Claude Code<br/>/security-review"]
        SVC["Deep Scan Service<br/>FastAPI :8001"]
    end

    L1 --> GHA
    L2 --> CLI
    L3 --> SVC

    GHA --> CLAUDE["Claude API<br/>(Sonnet 4.6)"]
    CLI --> CLAUDE
    SVC --> CLAUDE2["Claude API<br/>(Opus 4.6)"]

    style CLAUDE fill:#7C3AED,color:#fff
    style CLAUDE2 fill:#7C3AED,color:#fff
    style GHA fill:#2563EB,color:#fff
    style CLI fill:#2563EB,color:#fff
    style SVC fill:#2563EB,color:#fff
```

---

## 2. Prerequisites

### 2.1 Required Software

| Software | Minimum Version | Check Command |
|----------|----------------|---------------|
| Node.js | 20.x | `node --version` |
| Python | 3.11+ | `python --version` |
| Docker | 24.x | `docker --version` |
| Git | 2.40+ | `git --version` |
| Claude Code CLI | 2.1.0+ | `claude --version` |
| GitHub CLI | 2.x | `gh --version` |

### 2.2 Required Accounts & Keys

| Account | Purpose | How to Get |
|---------|---------|-----------|
| Anthropic API key | Claude API access | [console.anthropic.com](https://console.anthropic.com) — Enterprise tier recommended for BAA |
| GitHub repo admin | Configure Actions secrets | Must have admin access to PMS repos |
| Claude Code subscription | CLI `/security-review` | Anthropic Pro ($20/mo), Max, or Enterprise |

### 2.3 Verify PMS Services

Confirm the PMS backend, frontend, and database are running:

```bash
# Check backend
curl -s http://localhost:8000/docs | head -5
# Expected: HTML for FastAPI Swagger docs

# Check frontend
curl -s http://localhost:3000 | head -5
# Expected: HTML for Next.js app

# Check database
psql -h localhost -p 5432 -U pms_user -d pms -c "SELECT 1;"
# Expected: 1 row returned
```

**Checkpoint:** All three services respond. You have an Anthropic API key and Claude Code CLI installed.

---

## 3. Part A: CI/CD Security Gate Setup

### Step 1: Store the Anthropic API key in GitHub Secrets

```bash
# For each PMS repository (backend, frontend, android)
gh secret set ANTHROPIC_API_KEY --repo your-org/pms-backend
gh secret set ANTHROPIC_API_KEY --repo your-org/pms-frontend
gh secret set ANTHROPIC_API_KEY --repo your-org/pms-android
```

### Step 2: Create the GitHub Actions workflow

Create `.github/workflows/security-review.yml` in each repo:

```yaml
name: AI Security Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write

jobs:
  security-review:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Claude Security Review
        uses: anthropics/claude-code-security-review@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          model: claude-sonnet-4-6-20260217
          severity_threshold: high
          max_tokens: 8192
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Step 3: Create `.scanignore` in repo root

```text
# Exclude files that may contain test PHI or secrets
**/migrations/**
**/.env*
**/fixtures/**
**/test_data/**
**/secrets/**
*.key
*.pem
*.p12
```

### Step 4: Add CLAUDE.md security rules

Add to the project's `CLAUDE.md` or `.claude/rules/security.md`:

```markdown
# Security Review Rules

## FastAPI Backend
- Flag any use of `eval()`, `exec()`, or `pickle.loads()` with untrusted input
- Flag SQL queries constructed with string concatenation instead of parameterized queries
- Flag missing authentication decorators on endpoints handling PHI
- Flag `CORS(allow_origins=["*"])` in production configurations
- Flag missing rate limiting on authentication endpoints
- Flag hardcoded secrets, API keys, or credentials

## Next.js Frontend
- Flag `dangerouslySetInnerHTML` without sanitization
- Flag client-side storage of PHI (localStorage, sessionStorage, cookies without httpOnly)
- Flag missing CSRF protection on form submissions
- Flag API keys exposed in client-side bundles

## Kotlin/Android
- Flag cleartext HTTP traffic in network security config
- Flag missing certificate pinning for API communication
- Flag PHI stored in SharedPreferences without encryption
- Flag WebView with JavaScript enabled loading external URLs
```

### Step 5: Test with a deliberate vulnerability

Create a test branch with an intentional vulnerability:

```bash
git checkout -b test/security-review-validation
```

Add a file `test_vuln.py`:

```python
import subprocess

def unsafe_command(user_input: str):
    # Intentional command injection for testing
    result = subprocess.run(f"echo {user_input}", shell=True, capture_output=True)
    return result.stdout
```

Push and open a PR. Verify the security review action:
- Flags the command injection
- Posts an inline comment on the PR
- Reports severity as High or Critical

Then delete the test branch.

**Checkpoint:** The GitHub Action runs on PRs, detects intentional vulnerabilities, and posts inline comments with severity classifications.

---

## 4. Part B: Developer CLI Integration

### Step 1: Verify Claude Code is installed and authenticated

```bash
claude --version
# Expected: claude-code/2.1.0 or higher

claude auth status
# Expected: Authenticated as your-email@company.com
```

### Step 2: Run your first security review

```bash
# Review unstaged changes
claude /security-review

# Review specific files
claude /security-review --files src/api/patients.py src/api/auth.py

# Review the last commit
claude /security-review --diff HEAD~1
```

### Step 3: Understand the output

Claude Code's `/security-review` output includes:

- **Severity:** Critical / High / Medium / Low
- **CWE:** Common Weakness Enumeration identifier
- **Location:** File path and line number
- **Description:** What the vulnerability is
- **Exploitability:** Confidence percentage (only findings >80% are shown)
- **Remediation:** Specific fix recommendation

### Step 4: Add a pre-commit hook (optional)

Create `.claude/hooks/pre-commit-security.sh`:

```bash
#!/bin/bash
# Run Claude security review on staged files before commit
echo "Running AI security review on staged changes..."
claude /security-review --staged --severity-threshold high

if [ $? -ne 0 ]; then
    echo "Security issues detected. Review findings above before committing."
    echo "Use --no-verify to bypass (not recommended for PHI-related code)."
    exit 1
fi
```

```bash
chmod +x .claude/hooks/pre-commit-security.sh
```

**Checkpoint:** You can run `/security-review` from your terminal and receive formatted vulnerability findings on your code changes.

---

## 5. Part C: Deep Dependency Auditor Service

### Step 1: Create the service directory

```bash
mkdir -p services/security-scanner
```

### Step 2: Create `services/security-scanner/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Step 3: Create `services/security-scanner/requirements.txt`

```text
fastapi==0.115.0
uvicorn==0.34.0
anthropic==0.49.0
httpx==0.28.0
apscheduler==3.10.4
sqlalchemy==2.0.36
psycopg2-binary==2.9.10
pydantic==2.10.0
```

### Step 4: Create `services/security-scanner/main.py`

```python
"""AI Zero-Day Vulnerability Scanner — Deep Dependency Auditor."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import anthropic
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# --- Configuration ---
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://pms_user:pms_pass@localhost:5432/pms"
)
REPO_PATH = os.environ.get("REPO_PATH", "/repos/pms-backend")
SCAN_MODEL = os.environ.get("SCAN_MODEL", "claude-opus-4-6-20260205")

# --- Database ---
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Finding(Base):
    __tablename__ = "security_findings"
    __table_args__ = {"schema": "security"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(String(64), nullable=False, index=True)
    severity = Column(String(16), nullable=False, index=True)
    cwe = Column(String(16))
    title = Column(String(512), nullable=False)
    description = Column(Text, nullable=False)
    file_path = Column(String(512))
    line_number = Column(Integer)
    component = Column(String(256))
    remediation = Column(Text)
    status = Column(String(32), default="open", index=True)
    discovered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)


# --- App ---
app = FastAPI(title="AI Zero-Day Scanner", version="1.0.0")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
scheduler = AsyncIOScheduler()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ScanRequest(BaseModel):
    target: str = "dependencies"
    component: Optional[str] = None


class FindingResponse(BaseModel):
    id: int
    scan_id: str
    severity: str
    cwe: Optional[str]
    title: str
    description: str
    file_path: Optional[str]
    component: Optional[str]
    status: str
    discovered_at: datetime


def extract_dependency_tree(repo_path: str) -> dict:
    """Extract dependency manifests from the repo."""
    deps = {}
    req_file = Path(repo_path) / "requirements.txt"
    if req_file.exists():
        deps["python"] = req_file.read_text()

    lock_file = Path(repo_path) / "package-lock.json"
    if lock_file.exists():
        deps["javascript"] = json.loads(lock_file.read_text())

    gradle_file = Path(repo_path) / "app" / "build.gradle.kts"
    if gradle_file.exists():
        deps["kotlin"] = gradle_file.read_text()

    return deps


def build_scan_prompt(deps: dict, component: Optional[str] = None) -> str:
    """Build the scanning prompt for Claude."""
    target = f"Focus on the {component} component." if component else ""

    return f"""You are a senior security researcher performing a zero-day vulnerability
audit on a healthcare Patient Management System (PMS) that handles PHI under HIPAA.

Analyze the following dependency manifests for:
1. Known-vulnerable library versions (cross-reference with NVD)
2. Libraries with a history of security issues (e.g., unsafe C parsing, memory
   corruption, deserialization flaws)
3. Transitive dependencies that increase attack surface
4. Libraries handling PDF/image processing, cryptography, authentication,
   or serialization — categories where Opus 4.6 found zero-days in GhostScript,
   OpenSC, and CGIF
5. Supply chain risks: typosquatting, dependency confusion, abandoned packages

{target}

For each finding, provide:
- Severity: Critical / High / Medium / Low
- CWE number (if applicable)
- Title: one-line description
- Description: what the vulnerability is and why it matters for a healthcare PMS
- Affected component: package name and version
- Remediation: specific action to take

Return findings as a JSON array.

DEPENDENCY MANIFESTS:
{json.dumps(deps, indent=2, default=str)[:50000]}
"""


async def run_deep_scan(component: Optional[str] = None):
    """Execute a deep dependency scan."""
    scan_id = f"deep-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

    deps = extract_dependency_tree(REPO_PATH)
    if not deps:
        return {"scan_id": scan_id, "status": "no_dependencies_found"}

    prompt = build_scan_prompt(deps, component)

    message = client.messages.create(
        model=SCAN_MODEL,
        max_tokens=16384,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text

    # Parse findings and store in database
    db = SessionLocal()
    try:
        findings = json.loads(
            response_text[
                response_text.find("[") : response_text.rfind("]") + 1
            ]
        )
        for f in findings:
            db.add(
                Finding(
                    scan_id=scan_id,
                    severity=f.get("severity", "Medium"),
                    cwe=f.get("cwe"),
                    title=f.get("title", "Untitled finding"),
                    description=f.get("description", ""),
                    file_path=f.get("file_path"),
                    component=f.get("affected_component"),
                    remediation=f.get("remediation"),
                )
            )
        db.commit()
        return {"scan_id": scan_id, "findings_count": len(findings)}
    except (json.JSONDecodeError, ValueError):
        return {"scan_id": scan_id, "status": "parse_error", "raw": response_text[:500]}
    finally:
        db.close()


@app.post("/api/security/scan")
async def trigger_scan(request: ScanRequest):
    """Trigger an on-demand security scan."""
    result = await run_deep_scan(request.component)
    return result


@app.get("/api/security/findings", response_model=list[FindingResponse])
def list_findings(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List security findings with optional filters."""
    query = db.query(Finding)
    if severity:
        query = query.filter(Finding.severity == severity)
    if status:
        query = query.filter(Finding.status == status)
    return query.order_by(Finding.discovered_at.desc()).limit(100).all()


@app.patch("/api/security/findings/{finding_id}")
def update_finding(finding_id: int, status: str, db: Session = Depends(get_db)):
    """Update finding status (open → investigating → resolved → false_positive)."""
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    finding.status = status
    if status == "resolved":
        finding.resolved_at = datetime.now(timezone.utc)
    db.commit()
    return {"id": finding_id, "status": status}


@app.on_event("startup")
async def startup():
    """Create tables and start scheduler."""
    Base.metadata.create_all(engine)
    scheduler.add_job(run_deep_scan, "cron", day_of_week="mon", hour=2, minute=0)
    scheduler.start()


@app.on_event("shutdown")
async def shutdown():
    scheduler.shutdown()
```

### Step 5: Create the database schema

```bash
psql -h localhost -p 5432 -U pms_user -d pms -c "CREATE SCHEMA IF NOT EXISTS security;"
```

### Step 6: Add to `docker-compose.yml`

```yaml
  security-scanner:
    build: ./services/security-scanner
    ports:
      - "8001:8001"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DATABASE_URL=postgresql://pms_user:pms_pass@db:5432/pms
      - REPO_PATH=/repos/pms-backend
      - SCAN_MODEL=claude-opus-4-6-20260205
    volumes:
      - ./:/repos/pms-backend:ro
    depends_on:
      - db
    restart: unless-stopped
```

### Step 7: Start the service

```bash
docker compose up -d security-scanner
```

### Step 8: Verify the service

```bash
curl -s http://localhost:8001/docs | head -5
# Expected: FastAPI Swagger docs HTML

# Trigger a test scan
curl -X POST http://localhost:8001/api/security/scan \
  -H "Content-Type: application/json" \
  -d '{"target": "dependencies"}'
# Expected: {"scan_id": "deep-...", "findings_count": N}
```

**Checkpoint:** The deep scan service is running on port 8001, responds to health checks, and can execute dependency scans against the Claude API.

---

## 6. Part D: Security Dashboard Integration

### Step 1: Create the findings API proxy in PMS backend

Add to `pms-backend/src/api/security.py`:

```python
"""Security findings API — proxies to the deep scan service."""

from fastapi import APIRouter, Query
from typing import Optional
import httpx

router = APIRouter(prefix="/api/security", tags=["security"])
SCANNER_URL = "http://localhost:8001"


@router.get("/findings")
async def get_findings(
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    async with httpx.AsyncClient() as client:
        params = {}
        if severity:
            params["severity"] = severity
        if status:
            params["status"] = status
        resp = await client.get(f"{SCANNER_URL}/api/security/findings", params=params)
        return resp.json()


@router.post("/scan")
async def trigger_scan(target: str = "dependencies", component: Optional[str] = None):
    async with httpx.AsyncClient(timeout=300) as client:
        resp = await client.post(
            f"{SCANNER_URL}/api/security/scan",
            json={"target": target, "component": component},
        )
        return resp.json()
```

### Step 2: Create the frontend security dashboard page

Create `pms-frontend/src/app/security/page.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";

interface Finding {
  id: number;
  scan_id: string;
  severity: string;
  cwe: string | null;
  title: string;
  description: string;
  file_path: string | null;
  component: string | null;
  status: string;
  discovered_at: string;
}

const SEVERITY_COLORS: Record<string, string> = {
  Critical: "bg-red-600 text-white",
  High: "bg-orange-500 text-white",
  Medium: "bg-yellow-400 text-black",
  Low: "bg-blue-300 text-black",
};

export default function SecurityDashboard() {
  const [findings, setFindings] = useState<Finding[]>([]);
  const [filter, setFilter] = useState<string>("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const params = filter !== "all" ? `?severity=${filter}` : "";
    fetch(`/api/security/findings${params}`)
      .then((res) => res.json())
      .then((data) => {
        setFindings(data);
        setLoading(false);
      });
  }, [filter]);

  const counts = {
    Critical: findings.filter((f) => f.severity === "Critical").length,
    High: findings.filter((f) => f.severity === "High").length,
    Medium: findings.filter((f) => f.severity === "Medium").length,
    Low: findings.filter((f) => f.severity === "Low").length,
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Security Findings Dashboard</h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {Object.entries(counts).map(([severity, count]) => (
          <button
            key={severity}
            onClick={() => setFilter(severity)}
            className={`p-4 rounded-lg text-center cursor-pointer ${SEVERITY_COLORS[severity]}`}
          >
            <div className="text-3xl font-bold">{count}</div>
            <div className="text-sm">{severity}</div>
          </button>
        ))}
      </div>

      {/* Findings Table */}
      <table className="w-full border-collapse border border-gray-300">
        <thead>
          <tr className="bg-gray-100">
            <th className="border p-2 text-left">Severity</th>
            <th className="border p-2 text-left">Title</th>
            <th className="border p-2 text-left">CWE</th>
            <th className="border p-2 text-left">Component</th>
            <th className="border p-2 text-left">Status</th>
            <th className="border p-2 text-left">Discovered</th>
          </tr>
        </thead>
        <tbody>
          {findings.map((f) => (
            <tr key={f.id} className="hover:bg-gray-50">
              <td className="border p-2">
                <span className={`px-2 py-1 rounded text-xs ${SEVERITY_COLORS[f.severity]}`}>
                  {f.severity}
                </span>
              </td>
              <td className="border p-2">{f.title}</td>
              <td className="border p-2 font-mono text-sm">{f.cwe || "—"}</td>
              <td className="border p-2 text-sm">{f.component || "—"}</td>
              <td className="border p-2 text-sm">{f.status}</td>
              <td className="border p-2 text-sm">
                {new Date(f.discovered_at).toLocaleDateString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {loading && <p className="text-center mt-4 text-gray-500">Loading...</p>}
    </div>
  );
}
```

**Checkpoint:** The PMS backend proxies security findings from the scanner service, and the Next.js frontend renders a dashboard with severity cards and a findings table.

---

## 7. Part E: Testing and Verification

### Test 1: CI/CD Pipeline

```bash
# Create a test branch with an intentional vulnerability
git checkout -b test/security-gate
echo 'import os; os.system(input())' > test_vuln.py
git add test_vuln.py && git commit -m "test: intentional vulnerability"
git push -u origin test/security-gate

# Open a PR and check GitHub Actions
gh pr create --title "test: security gate validation" --body "Testing AI security review"

# Verify the action posts a comment flagging the command injection
gh pr checks
```

### Test 2: Developer CLI

```bash
# Create an intentionally vulnerable file
cat > /tmp/test_vuln.py << 'EOF'
from flask import request
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect("app.db")
    cursor = conn.execute(f"SELECT * FROM users WHERE id = '{user_id}'")
    return cursor.fetchone()
EOF

# Run security review on it
claude /security-review --files /tmp/test_vuln.py
# Expected: SQL injection flagged as Critical
```

### Test 3: Deep Scan Service

```bash
# Health check
curl -s http://localhost:8001/docs | grep -o "AI Zero-Day Scanner"

# Trigger scan
curl -X POST http://localhost:8001/api/security/scan \
  -H "Content-Type: application/json" \
  -d '{"target": "dependencies"}'

# Wait for completion, then check findings
sleep 60
curl -s http://localhost:8001/api/security/findings | python -m json.tool | head -30
```

### Test 4: End-to-End Dashboard

1. Open `http://localhost:3000/security` in your browser
2. Verify severity cards show counts
3. Click a severity to filter findings
4. Verify finding details include CWE, component, and remediation

**Checkpoint:** All four test levels pass -- CI/CD, CLI, deep scan, and dashboard.

---

## 8. Troubleshooting

### GitHub Action fails with "API key invalid"

**Symptom:** Security review action exits with authentication error.

**Fix:** Verify the secret is set correctly:
```bash
gh secret list --repo your-org/pms-backend
# Should show ANTHROPIC_API_KEY
```

Re-set if needed:
```bash
gh secret set ANTHROPIC_API_KEY --repo your-org/pms-backend
```

### Claude Code `/security-review` returns no findings

**Symptom:** Command runs but reports zero issues.

**Fix:** Check that you have staged or unstaged changes. `/security-review` only scans diffs by default:
```bash
# Review specific files instead
claude /security-review --files src/api/patients.py

# Or review the last commit
claude /security-review --diff HEAD~1
```

### Deep scan service can't connect to database

**Symptom:** Service starts but scans fail with `OperationalError`.

**Fix:** Verify the `DATABASE_URL` environment variable and that the `security` schema exists:
```bash
docker compose exec security-scanner env | grep DATABASE_URL
psql -h localhost -p 5432 -U pms_user -d pms -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'security';"
```

### Scan results contain hallucinated package names

**Symptom:** Findings reference packages not in your dependency tree.

**Fix:** This is a known LLM limitation ("slopsquatting"). Always cross-reference findings:
```bash
# Python
pip show <package-name>

# JavaScript
npm ls <package-name>

# If the package doesn't exist, mark as false_positive
curl -X PATCH http://localhost:8001/api/security/findings/<id> \
  -H "Content-Type: application/json" \
  -d '"false_positive"'
```

### API rate limiting errors

**Symptom:** Scans fail with HTTP 429 from Claude API.

**Fix:** The deep scan service uses Opus 4.6 which has lower rate limits. Reduce scan frequency or switch to Sonnet 4.6 for non-critical scans:
```bash
# In docker-compose.yml, change:
SCAN_MODEL=claude-sonnet-4-6-20260217
```

### CI/CD scan takes too long (>5 minutes)

**Symptom:** GitHub Action times out.

**Fix:** The action analyzes the full PR diff. For large PRs, reduce scope:
```yaml
# In security-review.yml, add:
with:
  max_files: 20
  max_diff_size: 50000
```

---

## 9. Reference Commands

### Daily Development

```bash
# Quick security check on current changes
claude /security-review

# Check specific high-risk files
claude /security-review --files src/api/auth.py src/api/patients.py

# Review before committing
claude /security-review --staged
```

### Management

```bash
# Trigger a deep scan manually
curl -X POST http://localhost:8001/api/security/scan \
  -H "Content-Type: application/json" \
  -d '{"target": "dependencies"}'

# List all Critical findings
curl -s "http://localhost:8001/api/security/findings?severity=Critical" | python -m json.tool

# Resolve a finding
curl -X PATCH "http://localhost:8001/api/security/findings/42" \
  -H "Content-Type: application/json" \
  -d '"resolved"'

# Check scanner service logs
docker compose logs -f security-scanner --tail=50
```

### Useful URLs

| URL | Description |
|-----|-------------|
| `http://localhost:8001/docs` | Scanner service API docs |
| `http://localhost:3000/security` | Security findings dashboard |
| `https://github.com/your-org/pms-backend/actions` | CI/CD security review runs |
| `https://console.anthropic.com/usage` | Claude API usage monitoring |

---

## 10. Next Steps

After setup is complete:

1. Run the first full deep scan and triage all Critical/High findings
2. Complete the [AI Zero-Day Scan Developer Tutorial](12-AIZeroDayScan-Developer-Tutorial.md) for hands-on practice
3. Review the [PRD](12-PRD-AIZeroDayScan-PMS-Integration.md) for Phase 2 and Phase 3 features
4. Schedule a security review meeting to discuss initial scan results
5. Add security scanning to the team's PR review checklist

---

## 11. Resources

- [Anthropic Zero-Day Research](https://red.anthropic.com/2026/zero-days/) -- How Opus 4.6 finds vulnerabilities
- [Claude Code Security Review GitHub Action](https://github.com/anthropics/claude-code-security-review) -- CI/CD integration
- [Automate Security Reviews with Claude Code](https://www.anthropic.com/news/automate-security-reviews-with-claude-code) -- Official guide
- [PMS Security Scanning Configuration](../config/security-scanning.md) -- Existing Snyk/SonarCloud setup
- [OWASP Top 10](https://owasp.org/www-project-top-ten/) -- Web application security risks
- [CWE Database](https://cwe.mitre.org/) -- Common Weakness Enumeration reference
