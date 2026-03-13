# NullClaw Developer Onboarding Tutorial

**Welcome to the MPS PMS NullClaw Integration Team**

This tutorial will take you from zero to building your first NullClaw integration with the PMS. By the end, you will understand how NullClaw works, have a running local environment, and have built and tested a custom patient lookup assistant end-to-end.

**Document ID:** PMS-EXP-NULLCLAW-002
**Version:** 1.0
**Date:** March 12, 2026
**Applies To:** PMS project (all platforms)
**Prerequisite:** [NullClaw Setup Guide](83-NullClaw-PMS-Developer-Setup-Guide.md)
**Estimated time:** 2-3 hours
**Difficulty:** Beginner-friendly

---

## What You Will Learn

1. What NullClaw is and why it matters for the PMS
2. How NullClaw's vtable-driven architecture works (providers, channels, tools, memory)
3. How NullClaw's gateway API enables external system integration
4. How to configure NullClaw with a custom system prompt for clinical use
5. How to build a custom PMS tool that NullClaw can invoke
6. How to test tool invocations through the gateway webhook
7. How NullClaw's sandbox and autonomy controls protect PHI
8. How to embed a NullClaw chat interface in the Next.js frontend
9. How to monitor NullClaw activity through audit logs
10. How NullClaw compares to alternative AI assistant runtimes

---

## Part 1: Understanding NullClaw (15 min read)

### 1.1 What Problem Does NullClaw Solve?

Picture a typical morning at the clinic. Nurse Maria needs to check if patient John Doe has any drug allergies before administering a new medication. She walks to the workstation, logs into the PMS web portal, navigates to the patient search screen, types the patient name, clicks through to the allergy tab, and reads the results. This takes 2-3 minutes and interrupts her clinical flow.

With NullClaw integrated into the PMS, Nurse Maria opens Telegram on her phone and types: "Any allergies for patient John Doe, MRN 12345?" Within seconds, NullClaw queries the PMS patient API, formats the allergy list, and sends it back to her Telegram chat. She never left the patient's bedside.

NullClaw solves three core problems for PMS staff:
- **Access friction**: Staff need PMS data but don't always have a workstation nearby. NullClaw brings PMS data to any messaging channel.
- **Context switching**: Navigating the web portal for a simple lookup breaks clinical flow. Natural language queries are faster.
- **Proactive assistance**: NullClaw can run scheduled tasks (daily census, overdue medication alerts) and push results to staff channels automatically.

### 1.2 How NullClaw Works — The Key Pieces

```mermaid
flowchart LR
    subgraph Input["1. Message In"]
        CH["Channel<br/>(Telegram, Slack,<br/>Web, CLI)"]
    end

    subgraph Brain["2. Think"]
        LLM["LLM Provider<br/>(OpenRouter, Anthropic,<br/>Ollama, etc.)"]
        MEM["Memory Engine<br/>(PostgreSQL, SQLite,<br/>Redis, etc.)"]
    end

    subgraph Act["3. Act"]
        TOOL["Tools<br/>(PMS patient_lookup,<br/>rx_check, shell, etc.)"]
        SAND["Sandbox<br/>(Landlock, Docker)"]
    end

    subgraph Output["4. Message Out"]
        RESP["Response<br/>(Same channel<br/>as input)"]
    end

    CH -->|"Staff message"| LLM
    LLM -->|"Retrieve context"| MEM
    LLM -->|"Decide action"| TOOL
    TOOL -->|"Isolated execution"| SAND
    SAND -->|"Tool result"| LLM
    LLM -->|"Format response"| RESP

    style CH fill:#0088CC,color:#fff
    style LLM fill:#E74C3C,color:#fff
    style MEM fill:#27AE60,color:#fff
    style TOOL fill:#E67E22,color:#fff
    style SAND fill:#8E44AD,color:#fff
    style RESP fill:#0088CC,color:#fff
```

NullClaw has three conceptual layers:

1. **Channels** (message in/out): How staff communicate with NullClaw. Each channel is a separate implementation behind the `Channel` vtable — Telegram, Slack, CLI, web webhook, etc. A staff message arrives through a channel and the response goes back through the same channel.

2. **Brain** (LLM + memory): The AI reasoning layer. NullClaw sends the staff message plus conversation history (from the memory engine) to an LLM provider. The LLM decides whether to answer directly or invoke a tool.

3. **Tools** (actions): External capabilities NullClaw can use. Built-in tools include shell execution, file operations, and web requests. Custom tools (like our PMS `patient_lookup`) are registered and callable by the LLM. All tool executions run inside a sandbox.

### 1.3 How NullClaw Fits with Other PMS Technologies

| Technology | Experiment | Relationship to NullClaw |
|---|---|---|
| OpenClaw (TypeScript AI runtime) | Exp 05 | Alternative AI runtime — heavier (1 GB RAM, 28 MB binary) but richer JS ecosystem. NullClaw replaces it for edge/lightweight deployments. |
| Redis (Caching) | Exp 76 | Complementary — NullClaw can use Redis as a memory backend for high-throughput caching of conversation state. |
| Mirth Connect (HL7 Integration) | Exp 77 | Complementary — NullClaw could surface HL7 integration status and errors through chat channels. |
| Amazon Textract (Document OCR) | Exp 81 | Complementary — NullClaw could trigger document extraction jobs and notify staff when OCR results are ready for review. |
| OpenRouter (LLM Gateway) | Exp 82 | Complementary — NullClaw natively supports OpenRouter as a provider, giving access to 200+ models through a single API key. |

### 1.4 Key Vocabulary

| Term | Meaning |
|---|---|
| **Provider** | An LLM backend (OpenRouter, Anthropic, Ollama, etc.) that NullClaw sends inference requests to |
| **Channel** | A communication interface (Telegram, Slack, CLI, webhook) through which staff interact with NullClaw |
| **Tool** | A registered function that NullClaw's LLM can invoke to take actions (query APIs, execute commands, read files) |
| **Memory engine** | A persistent storage backend (PostgreSQL, SQLite, Redis) that stores conversation history for context retrieval |
| **Gateway** | NullClaw's HTTP API server (default :3000, our config :3001) that accepts webhook messages and serves health endpoints |
| **Pairing** | One-time authentication where a 6-digit code is exchanged for a bearer token |
| **Sandbox** | An isolation layer (Landlock, Firejail, Bubblewrap, Docker) that restricts what tools can access |
| **Autonomy level** | Configuration (`supervised` or `full`) that controls whether NullClaw can take actions without staff confirmation |
| **vtable** | NullClaw's plugin architecture — each subsystem (provider, channel, tool, memory) is an interface with swappable implementations |
| **Observer** | A logging/monitoring backend that records NullClaw events (we use it for HIPAA audit logging) |
| **Tunnel** | A secure ingress mechanism (Cloudflare, Tailscale, ngrok) that lets external channels reach the local NullClaw gateway |
| **Peripheral** | Hardware interfaces (serial, GPIO) that NullClaw can interact with — relevant for Jetson Thor edge deployment |

### 1.5 Our Architecture

```mermaid
flowchart TB
    subgraph External["External Channels"]
        TG["Telegram"]
        SL["Slack"]
    end

    subgraph PMS_Network["PMS Docker Network"]
        subgraph NullClaw_Container["NullClaw Container"]
            NC["NullClaw Binary<br/>678 KB | ~1 MB RAM<br/>:3001"]
            GW["Gateway API"]
            PMS_TOOLS["PMS Tools<br/>patient_lookup<br/>encounter_summary<br/>rx_check<br/>report_gen<br/>schedule_query"]
        end

        subgraph Backend_Container["PMS Backend Container"]
            API["FastAPI :8000"]
            ADAPTER["/integrations/nullclaw/execute"]
        end

        subgraph Frontend_Container["PMS Frontend Container"]
            FE["Next.js :3000"]
            CHAT["Chat Widget"]
        end

        PG["PostgreSQL :5432"]
    end

    subgraph LLM_Cloud["LLM Cloud"]
        OR["OpenRouter API"]
    end

    TG -->|"Webhook"| NC
    SL -->|"Webhook"| NC
    CHAT -->|"HTTP POST"| GW
    NC -->|"Inference"| OR
    PMS_TOOLS -->|"HTTP POST"| ADAPTER
    ADAPTER -->|"SQL"| PG
    NC -->|"Memory + Audit"| PG
    FE --> CHAT

    style NC fill:#E74C3C,color:#fff
    style GW fill:#E74C3C,color:#fff
    style PMS_TOOLS fill:#E74C3C,color:#fff
    style API fill:#E67E22,color:#fff
    style ADAPTER fill:#E67E22,color:#fff
    style FE fill:#4A90D9,color:#fff
    style CHAT fill:#4A90D9,color:#fff
    style PG fill:#27AE60,color:#fff
    style OR fill:#9B59B6,color:#fff
    style TG fill:#0088CC,color:#fff
    style SL fill:#4A154B,color:#fff
```

---

## Part 2: Environment Verification (15 min)

### 2.1 Checklist

Complete these checks before proceeding. Every command should succeed.

```bash
# 1. NullClaw is installed
nullclaw --version
# Expected: v2026.3.12 or later

# 2. NullClaw gateway is running
curl -s http://127.0.0.1:3001/health
# Expected: {"status":"ok"}

# 3. PMS backend is running
curl -s http://127.0.0.1:8000/integrations/nullclaw/health
# Expected: {"status":"ok","tools_available":[...],"tool_count":5}

# 4. PMS frontend is running
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000
# Expected: 200

# 5. PostgreSQL is accessible
psql -h localhost -U pms_user -d pms_db -c "SELECT COUNT(*) FROM nullclaw_audit;"
# Expected: count (0 if fresh install)

# 6. Bearer token is set
echo $NULLCLAW_TOKEN
# Expected: a non-empty token string

# 7. Service token is set
echo $NULLCLAW_SERVICE_TOKEN
# Expected: a non-empty token string
```

### 2.2 Quick Test

Send a message through NullClaw and verify the full pipeline:

```bash
curl -X POST http://127.0.0.1:3001/webhook \
  -H "Authorization: Bearer $NULLCLAW_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What tools do you have available?"}'
```

Expected: NullClaw responds listing its available PMS tools (patient_lookup, encounter_summary, rx_check, report_gen, schedule_query).

---

## Part 3: Build Your First Integration (45 min)

### 3.1 What We Are Building

We will build a **Medication Interaction Checker** — a new NullClaw tool that accepts two or more medication names, queries the PMS prescriptions API, and returns a formatted interaction report. Staff can ask NullClaw: "Check interactions between aspirin, warfarin, and ibuprofen" and get an immediate response.

This exercise covers:
- Creating a new Python tool function
- Registering it in the PMS backend adapter
- Configuring it in NullClaw
- Testing it end-to-end

### 3.2 Create the Tool Function

Add to `pms-backend/app/integrations/nullclaw/tools.py`:

```python
async def medication_interaction_check(params: dict) -> dict:
    """Check for drug-drug interactions between specified medications.

    Params:
        medications: list of medication names (minimum 2)
    Returns:
        Interaction report with severity levels
    """
    medications = params.get("medications", [])
    if len(medications) < 2:
        return {"error": "Provide at least 2 medication names"}

    async with httpx.AsyncClient() as client:
        # Query PMS prescriptions API for interaction data
        resp = await client.post(
            f"{PMS_BASE_URL}/api/prescriptions/interactions",
            json={"medications": medications},
        )
        resp.raise_for_status()
        interactions = resp.json()

        return {
            "medications_checked": medications,
            "interaction_count": len(interactions.get("interactions", [])),
            "interactions": [
                {
                    "drug_pair": f"{ix['drug_a']} + {ix['drug_b']}",
                    "severity": ix["severity"],
                    "description": ix["description"],
                    "recommendation": ix.get("recommendation", "Consult pharmacist"),
                }
                for ix in interactions.get("interactions", [])
            ],
            "safe": len(interactions.get("interactions", [])) == 0,
        }
```

### 3.3 Register the Tool

Update the `TOOL_REGISTRY` dict in the same file:

```python
TOOL_REGISTRY = {
    "patient_lookup": patient_lookup,
    "encounter_summary": encounter_summary,
    "rx_check": rx_check,
    "report_gen": report_gen,
    "schedule_query": schedule_query,
    "medication_interaction_check": medication_interaction_check,  # NEW
}
```

### 3.4 Restart the PMS Backend

```bash
# If running directly:
cd pms-backend && uvicorn app.main:app --reload

# If running in Docker:
docker compose restart pms-backend
```

Verify the new tool appears:

```bash
curl -s http://127.0.0.1:8000/integrations/nullclaw/health | python3 -m json.tool
# Expected: "tool_count": 6, "tools_available" includes "medication_interaction_check"
```

### 3.5 Configure the Tool in NullClaw

Add the new tool to NullClaw's configuration (in the `tools.custom` array):

```json
{
  "name": "medication_interaction_check",
  "description": "Check for drug-drug interactions between two or more medications. Returns severity levels and clinical recommendations. Use when staff ask about drug interactions or medication safety.",
  "endpoint": "http://127.0.0.1:8000/integrations/nullclaw/execute",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer YOUR_SERVICE_TOKEN",
    "Content-Type": "application/json"
  },
  "body_template": "{\"tool\": \"medication_interaction_check\", \"params\": {{params}}, \"staff_id\": \"{{staff_id}}\"}"
}
```

Restart NullClaw to pick up the new tool:

```bash
# If running as service:
nullclaw service restart

# If running manually, stop and restart:
nullclaw gateway --port 3001
```

### 3.6 Test End-to-End

```bash
# Step 1: Test tool directly via PMS adapter
curl -X POST http://127.0.0.1:8000/integrations/nullclaw/execute \
  -H "Authorization: Bearer $NULLCLAW_SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "medication_interaction_check",
    "params": {"medications": ["aspirin", "warfarin", "ibuprofen"]},
    "staff_id": "tutorial-dev"
  }'
# Expected: interaction report JSON

# Step 2: Test via NullClaw natural language
curl -X POST http://127.0.0.1:3001/webhook \
  -H "Authorization: Bearer $NULLCLAW_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Check for drug interactions between aspirin, warfarin, and ibuprofen"}'
# Expected: NullClaw invokes medication_interaction_check and returns a formatted interaction report

# Step 3: Verify audit log
psql -h localhost -U pms_user -d pms_db -c \
  "SELECT timestamp, tool_name, approval_status FROM nullclaw_audit ORDER BY timestamp DESC LIMIT 3;"
# Expected: medication_interaction_check entry in recent logs
```

**Checkpoint**: You have built a new PMS tool, registered it in both the backend and NullClaw, and tested it end-to-end through natural language.

---

## Part 4: Evaluating Strengths and Weaknesses (15 min)

### 4.1 Strengths

- **Minimal resource footprint**: 678 KB binary, ~1 MB RAM, < 2 ms startup. No other AI assistant runtime comes close. This makes edge deployment (Jetson Thor) trivially easy.
- **True portability**: Single static binary runs on ARM, x86, and RISC-V. No Node.js, no Python runtime, no JVM — just libc.
- **Channel richness**: 19 built-in channels means staff can use whatever messaging platform they prefer without custom integration work.
- **Provider agnostic**: 50+ LLM providers with a single config change. Switch from OpenRouter to Ollama (local) to Anthropic without code changes.
- **Security by default**: Pairing auth, sandbox isolation, workspace scoping, encrypted secrets, and audit logging are all enabled out of the box.
- **Pluggable everything**: vtable architecture means adding a new tool, channel, or memory backend doesn't require modifying core code.

### 4.2 Weaknesses

- **Zig ecosystem immaturity**: Zig is pre-1.0. The community is smaller than Rust, Go, or TypeScript. Finding Zig developers for customization may be challenging.
- **Limited web UI**: NullClaw focuses on CLI and messaging channels. The web chat widget must be built externally (as we did with the React component).
- **No built-in HIPAA certification**: NullClaw provides the security primitives (encryption, sandboxing, audit logging) but is not HIPAA-certified as a product. The PMS team must ensure the overall deployment meets compliance requirements.
- **Custom tool integration overhead**: While the vtable system is elegant, registering custom HTTP-based tools requires JSON configuration that can become verbose for many tools.
- **Documentation gaps**: As a fast-moving open-source project, some advanced features may have incomplete or outdated documentation.

### 4.3 When to Use NullClaw vs Alternatives

| Scenario | Best Choice | Why |
|---|---|---|
| Edge device (Jetson, Raspberry Pi) | **NullClaw** | Only option that fits in < 1 MB RAM |
| Cloud deployment with rich JS integrations | OpenClaw | Larger ecosystem, easier to extend in TypeScript |
| Local-only AI with no cloud LLM | **NullClaw** + Ollama | NullClaw's minimal footprint pairs well with local inference |
| Enterprise deployment with compliance team | Either | Both support audit logging; NullClaw has stronger sandbox isolation |
| Multi-channel staff communication | **NullClaw** | 19 channels vs fewer in alternatives |
| Custom UI-heavy AI assistant | OpenClaw or custom | NullClaw is channel-focused, not UI-focused |

### 4.4 HIPAA / Healthcare Considerations

| Concern | NullClaw's Approach | PMS Integration Requirement |
|---|---|---|
| PHI in transit | TLS for gateway communication; tunnel encryption for external channels | Ensure all tunnel connections use HTTPS/TLS |
| PHI at rest | ChaCha20-Poly1305 for secrets; memory engine stores conversation history | Store only patient IDs in memory, not raw PHI; resolve IDs via API on each request |
| Access control | Pairing auth + channel allowlists | Implement role-based tool access in the PMS adapter layer |
| Audit trail | Observer vtable with file/log backends | Use PostgreSQL audit table with 6-year retention |
| Minimum necessary | Tools return only requested fields | PMS adapter functions should filter response data to minimum necessary |
| Breach notification | Audit logs enable forensic analysis | Monitor audit logs for anomalous access patterns |

---

## Part 5: Debugging Common Issues (15 min read)

### Issue 1: NullClaw Doesn't Call PMS Tools

**Symptom**: NullClaw responds conversationally but never invokes tools.

**Cause**: The system prompt or tool descriptions may not be clear enough for the LLM to recognize when to use tools.

**Fix**:
```bash
# Check that tools are registered
nullclaw status
# Look for "tools" section in output

# Improve the system prompt to explicitly mention tools:
# "When a user asks about patients, ALWAYS use the patient_lookup tool."

# Test with an explicit tool-triggering message:
curl -X POST http://127.0.0.1:3001/webhook \
  -H "Authorization: Bearer $NULLCLAW_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Use the patient_lookup tool to search for Smith"}'
```

### Issue 2: Tool Execution Returns Empty Results

**Symptom**: Tool is called but returns `{"count": 0, "patients": []}`.

**Cause**: PMS database may not have matching records, or the query parameters don't match the API's expected format.

**Fix**:
```bash
# Test the PMS API directly
curl http://127.0.0.1:8000/api/patients?search=Smith

# Check if data exists
psql -h localhost -U pms_user -d pms_db -c "SELECT id, first_name, last_name FROM patients LIMIT 5;"

# Verify tool parameter mapping in the adapter
```

### Issue 3: Gateway Returns 403 Forbidden

**Symptom**: Webhook requests return 403.

**Cause**: Bearer token is expired or invalid, or pairing was not completed.

**Fix**:
```bash
# Check if token works for health endpoint (no auth required)
curl http://127.0.0.1:3001/health

# Re-pair if needed
# Restart NullClaw gateway to get a new pairing code
nullclaw gateway --port 3001
# Use the new 6-digit code to pair again
```

### Issue 4: PostgreSQL Memory Backend Connection Errors

**Symptom**: NullClaw logs show "memory backend unavailable" errors.

**Cause**: PostgreSQL connection string is incorrect, or the `nullclaw_memory` table doesn't exist.

**Fix**:
```bash
# Test the connection string directly
psql "postgresql://pms_user:pms_pass@127.0.0.1:5432/pms_db" -c "SELECT 1;"

# Verify tables exist
psql -h localhost -U pms_user -d pms_db -c "\dt nullclaw_*"

# If tables are missing, recreate them (see Setup Guide Step 4)
```

### Issue 5: Slow Response Times (> 10 seconds)

**Symptom**: End-to-end queries take much longer than expected.

**Cause**: Almost always the LLM inference step, not NullClaw itself.

**Fix**:
```bash
# Time the health check (should be < 5 ms)
time curl -s http://127.0.0.1:3001/health

# Time a direct PMS API call (should be < 100 ms)
time curl -s http://127.0.0.1:8000/api/patients?search=test

# If health check and API are fast, the bottleneck is LLM inference
# Try a faster model in NullClaw config:
# "model": "anthropic/claude-haiku-4-5-20251001"  (fastest)
# Or switch to local Ollama for no-network-latency inference
```

### Reading NullClaw Logs

```bash
# NullClaw logs to stderr by default
# Redirect to a file for analysis:
nullclaw gateway --port 3001 2> nullclaw.log &

# Tail the log
tail -f nullclaw.log

# Filter for errors
grep -i "error\|fail\|panic" nullclaw.log

# Filter for tool invocations
grep "tool" nullclaw.log
```

---

## Part 6: Practice Exercise (45 min)

### Option A: Build a "Shift Handoff Report" Tool

Build a tool that generates a shift handoff report by combining data from multiple PMS endpoints.

**What it does**: When a nurse types "Generate shift handoff for Dr. Smith", NullClaw calls the tool, which:
1. Queries today's encounters for the provider (`/api/encounters`)
2. Checks for any pending prescriptions (`/api/prescriptions`)
3. Lists upcoming appointments (`/api/appointments`)
4. Combines into a formatted handoff report

**Hints**:
- Create `shift_handoff_report` function in `tools.py`
- Make multiple `httpx` calls within the same tool function
- Format the output as structured sections (Active Patients, Pending Orders, Upcoming Appointments)
- Register in `TOOL_REGISTRY` and NullClaw config

### Option B: Add a Telegram Channel

Configure NullClaw to accept messages from a Telegram bot.

**Steps outline**:
1. Create a Telegram bot via @BotFather and get the API token
2. Add Telegram channel configuration to NullClaw config
3. Set up a tunnel (ngrok or Cloudflare) for webhook delivery
4. Configure `allow_from` allowlist for authorized Telegram users
5. Test by sending a patient lookup query from Telegram

**Hints**:
```json
{
  "channels": {
    "telegram": [{
      "token": "enc2:...",
      "allow_from": ["YOUR_TELEGRAM_USER_ID"],
      "webhook_mode": true
    }]
  }
}
```

### Option C: Build an Audit Dashboard

Create a Next.js page that visualizes NullClaw audit data.

**What it shows**:
- Total queries per day (bar chart)
- Most-used tools (pie chart)
- Queries per staff member (table)
- Recent activity feed (scrolling list)

**Hints**:
- Create a new API endpoint in FastAPI that queries `nullclaw_audit`
- Build a Next.js page at `/admin/nullclaw` using the chart library of your choice
- Group audit records by `tool_name`, `staff_id`, and `DATE(timestamp)`

---

## Part 7: Development Workflow and Conventions

### 7.1 File Organization

```
pms-backend/
└── app/
    └── integrations/
        └── nullclaw/
            ├── __init__.py
            ├── adapter.py          # FastAPI routes for NullClaw tool execution
            ├── auth.py             # Token verification
            └── tools.py            # PMS tool implementations

pms-frontend/
└── src/
    └── components/
        └── nullclaw/
            └── ChatWidget.tsx      # Floating chat widget

config/
└── nullclaw/
    └── config.json                 # NullClaw configuration (DO NOT commit API keys)
```

### 7.2 Naming Conventions

| Item | Convention | Example |
|---|---|---|
| Tool function names | `snake_case` verb-noun | `patient_lookup`, `rx_check` |
| NullClaw tool name (config) | Must match Python function name | `"name": "patient_lookup"` |
| API route prefix | `/integrations/nullclaw/` | `/integrations/nullclaw/execute` |
| PostgreSQL tables | `nullclaw_` prefix | `nullclaw_memory`, `nullclaw_audit` |
| Environment variables | `NULLCLAW_` prefix, uppercase | `NULLCLAW_SERVICE_TOKEN` |
| Frontend components | PascalCase in `nullclaw/` directory | `ChatWidget.tsx` |
| Docker service name | `nullclaw` | `services.nullclaw` in docker-compose |

### 7.3 PR Checklist

When submitting a PR that involves NullClaw:

- [ ] New tool function has docstring explaining params and return value
- [ ] Tool is registered in `TOOL_REGISTRY`
- [ ] Tool is added to NullClaw config JSON (in docs, not committed secrets)
- [ ] Tool returns only minimum necessary data (HIPAA minimum necessary rule)
- [ ] Audit logging captures tool invocation (automatic via adapter)
- [ ] Error cases return structured `{"error": "..."}` responses, not exceptions
- [ ] No PHI (names, DOBs, MRNs) hardcoded in test fixtures
- [ ] PMS adapter health endpoint reflects new tool count
- [ ] Setup guide updated if new prerequisites are introduced
- [ ] Tested via both direct API call and NullClaw webhook

### 7.4 Security Reminders

1. **Never commit API keys or bearer tokens.** Use environment variables or NullClaw's encrypted secret storage (`enc2:` prefix).
2. **Never store raw PHI in NullClaw memory.** Store patient IDs and resolve them via API calls. If a conversation mentions "John Doe, DOB 01/15/1980", the memory should store "patient_id: 12345", not the name and DOB.
3. **Always use supervised autonomy** for tools that modify PMS data. Read-only tools can use auto-approval.
4. **Channel allowlists are mandatory.** Never deploy with `allow_from: ["*"]` in production.
5. **Audit log retention**: Minimum 6 years (2,190 days) per HIPAA requirements. Do not reduce `retention_days` below this.
6. **Review sandbox configuration** before adding tools that execute shell commands or access the filesystem.

---

## Part 8: Quick Reference Card

### Key Commands

```bash
# Start / Stop
nullclaw gateway --port 3001          # Start gateway
nullclaw service install              # Install as system service
nullclaw service status               # Check service status

# Interact
nullclaw agent                        # Interactive CLI chat
nullclaw agent -m "message"          # One-shot message

# Diagnose
nullclaw doctor                       # System diagnostics
nullclaw status                       # Configuration summary
nullclaw channel status               # Channel health

# Memory
nullclaw memory list --limit 10       # Recent conversations
nullclaw memory archive --older-than 90d  # Archive old data
```

### Key Files

| File | Purpose |
|---|---|
| `~/.config/nullclaw/config.json` | NullClaw configuration |
| `pms-backend/app/integrations/nullclaw/tools.py` | PMS tool implementations |
| `pms-backend/app/integrations/nullclaw/adapter.py` | Gateway adapter routes |
| `pms-frontend/src/components/nullclaw/ChatWidget.tsx` | Frontend chat widget |

### Key URLs

| URL | Purpose |
|---|---|
| `http://127.0.0.1:3001/health` | NullClaw gateway health |
| `http://127.0.0.1:3001/webhook` | NullClaw message endpoint |
| `http://127.0.0.1:3001/pair` | Pairing endpoint |
| `http://127.0.0.1:8000/integrations/nullclaw/health` | PMS adapter health |
| `http://127.0.0.1:8000/integrations/nullclaw/execute` | PMS tool execution |

### Starter Template: New PMS Tool

```python
# In pms-backend/app/integrations/nullclaw/tools.py

async def my_new_tool(params: dict) -> dict:
    """Brief description of what this tool does.

    Params:
        param_name: description
    Returns:
        description of return structure
    """
    # Validate input
    required_param = params.get("param_name")
    if not required_param:
        return {"error": "Provide 'param_name'"}

    # Call PMS API
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{PMS_BASE_URL}/api/your-endpoint",
            params={"key": required_param},
        )
        resp.raise_for_status()
        data = resp.json()

    # Return minimum necessary data
    return {
        "result_field": data["relevant_field"],
        "count": len(data.get("items", [])),
    }

# Don't forget to add to TOOL_REGISTRY:
# "my_new_tool": my_new_tool,
```

---

## Next Steps

1. **Configure additional channels**: Follow the [NullClaw Configuration Guide](https://github.com/nullclaw/nullclaw/blob/main/docs/en/configuration.md) to add Telegram, Slack, or Signal channels for your clinical staff.
2. **Explore edge deployment**: Review [ADR-0007: Jetson Thor Edge Deployment](../architecture/0007-jetson-thor-edge-deployment.md) and deploy a NullClaw instance on the Jetson for point-of-care AI assistance.
3. **Build more tools**: The PMS has additional APIs (billing, insurance verification, lab results) that could benefit from NullClaw tool integrations.
4. **Review the PRD**: Read the [NullClaw PMS Integration PRD](83-PRD-NullClaw-PMS-Integration.md) for the full roadmap including scheduled tasks, multi-provider failover, and analytics dashboards.
5. **Contribute upstream**: If you build a tool or fix that could benefit the NullClaw community, consider contributing back to the [NullClaw repository](https://github.com/nullclaw/nullclaw).
