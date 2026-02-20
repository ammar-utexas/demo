# AI Zero-Day Vulnerability Scan Developer Onboarding Tutorial

**Welcome to the MPS PMS AI Security Scanning Team**

This tutorial takes you from zero to running your first AI-powered vulnerability scan on the PMS codebase. By the end, you will understand how Claude Opus 4.6 discovers zero-day vulnerabilities, have scanned your own code, triaged findings, and built a custom scanning workflow for healthcare-specific risks.

**Document ID:** PMS-EXP-AIZERODAYSCAN-002
**Version:** 1.0
**Date:** February 20, 2026
**Applies To:** PMS project (all platforms)
**Prerequisite:** [AI Zero-Day Scan Setup Guide](12-AIZeroDayScan-PMS-Developer-Setup-Guide.md)
**Estimated time:** 2-3 hours
**Difficulty:** Beginner-friendly

---

## What You Will Learn

1. How Claude Opus 4.6 discovers zero-day vulnerabilities that traditional tools miss
2. The difference between pattern-matching (SAST) and reasoning-based (LLM) vulnerability discovery
3. How to run ad-hoc security scans from your terminal using Claude Code
4. How to interpret findings: severity, CWE, exploitability, and remediation
5. How to triage findings: true positive vs false positive vs hallucination
6. How to write custom scanning prompts targeting healthcare-specific risks
7. How the CI/CD security gate protects every pull request
8. How the deep dependency auditor scans your supply chain
9. HIPAA security considerations for AI-assisted scanning
10. How to build a complete security review workflow into your daily development

---

## Part 1: Understanding AI Vulnerability Scanning (15 min read)

### 1.1 What Problem Does AI Scanning Solve?

The PMS handles Protected Health Information (PHI) — patient records, prescriptions, encounter notes, clinical documents. A single exploitable vulnerability in the codebase or its dependencies could result in:

- **Data breach:** PHI exposure triggering HIPAA breach notification to patients and HHS
- **Supply chain attack:** A compromised transitive dependency injecting malware into the PMS
- **Logic flaw:** A broken authorization check allowing one patient's data to be accessed by another

The PMS already uses **Snyk** (known CVE database), **SonarCloud** (code quality rules), and **CodeRabbit** (AI code review). But these tools have blind spots:

| Capability | Snyk | SonarCloud | Claude Opus 4.6 |
|-----------|------|------------|-----------------|
| Known CVE detection | Yes | Partial | Yes (cross-references NVD) |
| Pattern-based code rules | No | Yes | Yes |
| Business logic flaws | No | No | **Yes** |
| Inter-procedural taint flow | No | Partial | **Yes** |
| Commit history analysis | No | No | **Yes** |
| Zero-day discovery | No | No | **Yes** |
| F-1 score (benchmark) | — | 0.260 | **0.797** |

Claude Opus 4.6 fills the gap by reasoning about code the way a human security researcher does.

### 1.2 How Claude Finds Zero-Days — The Key Concepts

```mermaid
flowchart TB
    subgraph Traditional["Traditional SAST (Snyk/SonarCloud)"]
        RULES["Pattern Rules<br/>e.g. 'dangerous function calls'"]
        MATCH["String Matching<br/>Against Known Patterns"]
        CVE["Known CVE<br/>Database"]
    end

    subgraph Claude["Claude Opus 4.6"]
        READ["Read Code<br/>Like a Human"]
        HISTORY["Examine<br/>Commit History"]
        REASON["Reason About<br/>Algorithm Semantics"]
        PARTIAL["Find Partially<br/>Fixed Patterns"]
        CRAFT["Craft Trigger<br/>Inputs"]
    end

    RULES --> MATCH --> CVE
    CVE -->|"Only finds<br/>KNOWN vulns"| KNOWN["Known<br/>Vulnerabilities"]

    READ --> HISTORY
    READ --> REASON
    HISTORY --> PARTIAL
    REASON --> CRAFT
    PARTIAL -->|"Finds bugs in<br/>code similar to<br/>past fixes"| UNKNOWN["Zero-Day<br/>Vulnerabilities"]
    CRAFT -->|"Understands<br/>algorithm to<br/>trigger bug"| UNKNOWN

    style KNOWN fill:#FCA5A5
    style UNKNOWN fill:#86EFAC
    style Claude fill:#F3E8FF,stroke:#7C3AED
    style Traditional fill:#E0E7FF,stroke:#4338CA
```

**Three techniques Anthropic documented:**

1. **Commit history analysis:** Claude reads the git log, finds a past security fix, then searches for similar unfixed patterns elsewhere in the codebase. This is how it found vulnerabilities in GhostScript — a fix for one buffer overflow revealed a class of similar bugs.

2. **Algorithmic reasoning:** For the CGIF vulnerability, Claude understood the LZW compression algorithm well enough to know that maxing out the symbol table forces a "clear" token, causing the compressed output to exceed the uncompressed size — triggering a buffer overflow. No fuzzer could reason about this.

3. **Unsafe API pattern detection:** For OpenSC, Claude identified successive `strcat` operations on fixed-size buffers — a classic C vulnerability pattern that humans miss when the concatenation spans multiple functions.

### 1.3 How AI Scanning Fits with Other PMS Technologies

| Experiment | Relationship to AI Scanning |
|-----------|---------------------------|
| **MCP Integration (09)** | AI scanning secures the MCP server code that exposes PMS APIs to AI clients |
| **Adaptive Thinking (08)** | Adaptive effort routing can optimize scan cost — use Sonnet for CI/CD, Opus for deep scans |
| **OpenClaw (05)** | AI scanning validates the security of autonomous workflow skills before they execute clinical actions |
| **Speechmatics Medical (10)** | Scanning checks the voice AI integration code for audio processing library vulnerabilities |
| **Sanford Guide (11)** | Scanning validates the CDS integration code for injection flaws in API client |

AI scanning is **foundational** — it secures the code that every other experiment runs on.

### 1.4 Key Vocabulary

| Term | Meaning |
|------|---------|
| **Zero-day** | A vulnerability unknown to the software vendor and security community — no patch exists |
| **CVE** | Common Vulnerabilities and Exposures — a public identifier for a known vulnerability |
| **CWE** | Common Weakness Enumeration — a classification of vulnerability types (e.g., CWE-78: OS Command Injection) |
| **SAST** | Static Application Security Testing — analyzes source code without executing it |
| **DAST** | Dynamic Application Security Testing — tests the running application |
| **SCA** | Software Composition Analysis — identifies known vulnerabilities in dependencies |
| **SARIF** | Static Analysis Results Interchange Format — standard JSON format for security findings |
| **Taint flow** | Tracking untrusted input through code to a sensitive operation (source → sink) |
| **BOLA** | Broken Object Level Authorization — accessing another user's data by manipulating IDs |
| **Supply chain attack** | Compromising a dependency to inject malicious code into downstream projects |
| **Slopsquatting** | LLM hallucinating package names that don't exist — a false positive pattern unique to AI scanning |
| **Exploitability** | The confidence level that a vulnerability can actually be exploited in practice |

### 1.5 Our Architecture

```mermaid
flowchart TB
    subgraph DevLoop["Developer Workflow"]
        DEV["Developer"]
        CLI["Claude Code CLI<br/>/security-review"]
        COMMIT["git commit / push"]
    end

    subgraph CICD["CI/CD Pipeline"]
        PR["Pull Request"]
        ACTION["claude-code-security-review<br/>GitHub Action"]
        SNYK["Snyk SCA"]
        SONAR["SonarCloud SAST"]
        GATE["Security Gate<br/>Pass / Fail"]
    end

    subgraph DeepScan["Deep Scan Service :8001"]
        CRON["Weekly Cron<br/>(Monday 2 AM)"]
        ENGINE["Scan Engine"]
        CLAUDE_API["Claude API<br/>(Opus 4.6)"]
    end

    subgraph PMS["PMS Stack"]
        BACKEND["PMS Backend<br/>FastAPI :8000"]
        FRONTEND["PMS Frontend<br/>Next.js :3000"]
        DASHBOARD["Security<br/>Dashboard"]
        DB[("PostgreSQL<br/>:5432")]
    end

    DEV -->|"Ad-hoc scan"| CLI
    DEV --> COMMIT --> PR
    PR --> ACTION
    PR --> SNYK
    PR --> SONAR
    ACTION --> GATE
    SNYK --> GATE
    SONAR --> GATE

    CRON --> ENGINE --> CLAUDE_API
    ENGINE -->|"Findings"| DB
    BACKEND -->|"Read findings"| DB
    DASHBOARD --> BACKEND
    FRONTEND --> DASHBOARD

    style CLAUDE_API fill:#7C3AED,color:#fff
    style ACTION fill:#7C3AED,color:#fff
    style CLI fill:#7C3AED,color:#fff
    style ENGINE fill:#7C3AED,color:#fff
    style GATE fill:#DC2626,color:#fff
```

---

## Part 2: Environment Verification (15 min)

### 2.1 Checklist

Run each command and verify the expected output:

```bash
# 1. Claude Code CLI
claude --version
# Expected: claude-code/2.1.0 or higher

# 2. Claude Code authentication
claude auth status
# Expected: Authenticated

# 3. PMS backend running
curl -s http://localhost:8000/docs | grep -o "FastAPI"
# Expected: FastAPI

# 4. Deep scan service running
curl -s http://localhost:8001/docs | grep -o "AI Zero-Day Scanner"
# Expected: AI Zero-Day Scanner

# 5. Database accessible
psql -h localhost -p 5432 -U pms_user -d pms -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'security';"
# Expected: security (1 row)

# 6. GitHub CLI authenticated
gh auth status
# Expected: Logged in to github.com
```

### 2.2 Quick Test

Run a quick scan on a single file to confirm end-to-end:

```bash
claude /security-review --files src/api/auth.py
```

You should see output with findings (or "No security issues found" if the file is clean). Either result confirms the tool is working.

---

## Part 3: Build Your First Security Scan (45 min)

### 3.1 What We Are Building

We'll create a **vulnerable test file**, scan it with three different methods (CLI, API, CI/CD), compare results, and learn to triage findings.

### 3.2 Create the Vulnerable Test File

Create `test_security_scan.py` in the repo root:

```python
"""
Intentionally vulnerable file for security scanning tutorial.
DO NOT deploy to production. Delete after tutorial.
"""
import os
import sqlite3
import subprocess
import pickle
import hashlib
from typing import Optional


# Vulnerability 1: SQL Injection (CWE-89)
def get_patient_by_name(name: str):
    conn = sqlite3.connect("patients.db")
    query = f"SELECT * FROM patients WHERE name = '{name}'"
    return conn.execute(query).fetchall()


# Vulnerability 2: Command Injection (CWE-78)
def generate_report(report_type: str):
    result = subprocess.run(
        f"generate-report --type {report_type}",
        shell=True,
        capture_output=True,
    )
    return result.stdout


# Vulnerability 3: Insecure Deserialization (CWE-502)
def load_session(session_data: bytes):
    return pickle.loads(session_data)


# Vulnerability 4: Weak Cryptography (CWE-328)
def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()


# Vulnerability 5: Path Traversal (CWE-22)
def read_clinical_document(filename: str) -> str:
    filepath = os.path.join("/var/pms/documents", filename)
    with open(filepath) as f:
        return f.read()


# Vulnerability 6: Hardcoded Secret (CWE-798)
API_KEY = "sk-ant-api03-FAKE-KEY-FOR-TESTING-ONLY"


# Vulnerability 7: Missing Auth Check (business logic flaw)
def get_any_patient_record(patient_id: int):
    """Returns patient record without verifying the caller has access."""
    conn = sqlite3.connect("patients.db")
    return conn.execute(
        "SELECT * FROM patients WHERE id = ?", (patient_id,)
    ).fetchone()
```

### 3.3 Scan with Claude Code CLI

```bash
claude /security-review --files test_security_scan.py
```

**What to observe:**
- How many of the 7 vulnerabilities does Claude find?
- What severity does it assign to each?
- Does it suggest specific remediation for each?
- Does it flag the business logic flaw (Vulnerability 7) — which traditional SAST tools miss?

### 3.4 Scan with the Deep Scan Service API

```bash
curl -X POST http://localhost:8001/api/security/scan \
  -H "Content-Type: application/json" \
  -d '{"target": "source", "component": "test_security_scan"}'
```

Wait for completion, then retrieve findings:

```bash
curl -s http://localhost:8001/api/security/findings | python -m json.tool
```

### 3.5 Compare with Traditional Tools

If Snyk and SonarCloud are configured, compare:

```bash
# Snyk (known CVEs — will likely find nothing since this is custom code)
snyk test --file=requirements.txt

# SonarCloud (will find some patterns but miss logic flaws)
# Check your SonarCloud dashboard after pushing
```

### 3.6 Triage the Findings

For each finding, classify it:

| Classification | Meaning | Action |
|---------------|---------|--------|
| **True Positive** | Real vulnerability, exploitable | Fix immediately (Critical/High) or schedule (Medium/Low) |
| **True Positive, Low Risk** | Real weakness, but not exploitable in this context | Document risk acceptance |
| **False Positive** | Not actually a vulnerability | Mark as `false_positive` in the dashboard |
| **Hallucination** | Claude referenced a package or pattern that doesn't exist | Mark as `false_positive`, note in team knowledge base |

Practice triaging: update the status of each finding via the API:

```bash
# Mark a finding as resolved (after fixing it)
curl -X PATCH http://localhost:8001/api/security/findings/1 \
  -H "Content-Type: application/json" \
  -d '"resolved"'

# Mark a finding as false positive
curl -X PATCH http://localhost:8001/api/security/findings/2 \
  -H "Content-Type: application/json" \
  -d '"false_positive"'
```

### 3.7 Clean Up

```bash
rm test_security_scan.py
```

**Checkpoint:** You've scanned a vulnerable file with three methods, compared AI vs traditional results, and practiced triaging findings.

---

## Part 4: Evaluating Strengths and Weaknesses (15 min)

### 4.1 Strengths

- **Reasoning over pattern-matching:** Claude understands *why* code is vulnerable, not just that it matches a pattern. This catches business logic flaws, partially-fixed bugs, and algorithmic vulnerabilities that SAST tools miss.
- **Commit history awareness:** Analyzing git history to find "sibling bugs" — vulnerabilities similar to past fixes — is a technique unique to LLM scanning.
- **Low barrier to entry:** `/security-review` works out of the box with no configuration, custom rules, or specialized knowledge.
- **Healthcare context understanding:** Claude understands HIPAA, PHI, BAA, and clinical workflow concepts when evaluating code — it doesn't just find generic web vulnerabilities but understands the healthcare-specific implications.
- **Benchmark superiority:** F-1 score of 0.797 vs traditional SAST at 0.260 — nearly 3x better at finding real vulnerabilities with fewer false positives.

### 4.2 Weaknesses

- **Hallucinations:** Claude may reference packages, CVEs, or patterns that don't exist ("slopsquatting"). Always cross-reference Critical/High findings.
- **No runtime testing:** Claude analyzes source code only — it cannot detect vulnerabilities that only manifest at runtime (e.g., race conditions, timing attacks). DAST tools are still needed.
- **Token limits:** Large codebases require chunking. A single file over 10K lines may need to be split for analysis.
- **Cost:** Opus 4.6 at $15/$75 per 1M tokens is expensive for scanning large repos frequently. Sonnet 4.6 at $3/$15 is more practical for CI/CD.
- **Non-deterministic:** The same code may produce slightly different findings on different scan runs. Critical findings are consistent; edge cases may vary.
- **No formal verification:** Claude provides reasoning-based analysis, not mathematical proof of vulnerability. Findings are expert opinions, not proofs.

### 4.3 When to Use AI Scanning vs Alternatives

| Scenario | Best Tool |
|----------|-----------|
| Check for known CVEs in dependencies | **Snyk** (definitive CVE database) |
| Enforce code quality standards | **SonarCloud** (deterministic rules) |
| Find zero-day vulnerabilities in custom code | **Claude Opus 4.6** |
| Find business logic flaws (broken auth, BOLA) | **Claude Opus 4.6** |
| Test running application for vulnerabilities | **DAST tool** (StackHawk, OWASP ZAP) |
| Review PR diffs for security issues | **Claude Sonnet 4.6** (fast, cost-effective) |
| Deep audit of high-risk library source code | **Claude Opus 4.6** (maximum reasoning) |
| Scan for secrets in code | **git-secrets / TruffleHog** (specialized) |

### 4.4 HIPAA / Healthcare Considerations

- **No PHI is sent to the Claude API.** Only source code and dependency metadata are analyzed. This is critical for HIPAA compliance.
- **Findings may reference PHI-adjacent concepts** (patient records, prescriptions, encounter data) but never contain actual patient data.
- **Audit logging:** Every scan invocation is logged with timestamp and user for HIPAA audit trail.
- **BAA required:** Use Anthropic Enterprise tier with BAA for production scanning, even though no PHI is transmitted — defense-in-depth.
- **Access control:** Security findings dashboard should be restricted to `security_admin` role — findings may describe attack paths against PHI systems.
- **Data retention:** HIPAA requires 7-year retention of security-related records. Configure finding retention accordingly.

---

## Part 5: Debugging Common Issues (15 min read)

### Issue 1: Claude reports a vulnerability in a package you don't use

**Symptom:** Finding references a package not in your `requirements.txt` or `package-lock.json`.

**Cause:** LLM hallucination ("slopsquatting") — Claude inferred a likely dependency that doesn't actually exist.

**Fix:** Cross-reference with your actual dependency tree:
```bash
pip show <package-name> || echo "Not installed"
npm ls <package-name> 2>/dev/null || echo "Not in tree"
```
Mark as `false_positive` if the package doesn't exist.

### Issue 2: Different scan results each time

**Symptom:** Running the same scan twice produces different findings.

**Cause:** LLM responses are non-deterministic. Claude may explore different reasoning paths.

**Fix:** For critical audits, run 3 scans and take the union of findings. Use `temperature: 0` in API calls for more consistent results.

### Issue 3: Scan is too slow for CI/CD

**Symptom:** Security review action takes >5 minutes, delaying PRs.

**Cause:** Large PR diffs or using Opus 4.6 instead of Sonnet 4.6 for CI/CD.

**Fix:** Use Sonnet 4.6 for CI/CD (3x faster, 5x cheaper). Reserve Opus for deep scans:
```yaml
# In GitHub Action
model: claude-sonnet-4-6-20260217  # Not opus
```

### Issue 4: Too many false positives

**Symptom:** Most findings are not exploitable in your context.

**Cause:** Claude applies general security knowledge without full understanding of your authentication/authorization layers.

**Fix:** Add context to your CLAUDE.md security rules:
```markdown
# Security Context
- All API endpoints require JWT authentication via FastAPI Depends()
- RBAC is enforced at the middleware level — assume all endpoints are authenticated
- Database queries use SQLAlchemy ORM — raw SQL is never used in production
- File uploads are sanitized by the upload middleware before storage
```

### Issue 5: Claude doesn't understand your framework

**Symptom:** Findings about FastAPI are generic web vulnerability patterns, not framework-specific.

**Cause:** Claude needs framework-specific context to understand security patterns.

**Fix:** Add framework rules to `.claude/rules/security.md`:
```markdown
# FastAPI Security Patterns
- `Depends(get_current_user)` provides authentication — don't flag endpoints using it as "missing auth"
- SQLAlchemy ORM queries are parameterized — don't flag them as SQL injection
- Pydantic models validate input — don't flag validated fields as unsanitized input
```

---

## Part 6: Practice Exercises (45 min)

### Exercise A: Scan Your Most Critical Module

Identify the PMS module that handles the most sensitive PHI operations (likely the patients or prescriptions API) and run a deep scan:

```bash
claude /security-review --files src/api/patients.py src/models/patient.py src/services/patient_service.py
```

**Goal:** Find at least one actionable security improvement. Document it in the findings dashboard.

**Hints:**
- Look for authorization checks — does the API verify that the requesting user has access to this specific patient?
- Check input validation — are all fields validated before database writes?
- Review error handling — do error messages leak internal state (stack traces, query details)?

### Exercise B: Audit a High-Risk Dependency

Pick one dependency that handles security-critical operations:

```bash
# Find your cryptography library
pip show cryptography

# Or your PDF library
pip show reportlab
```

Download its source and scan it:

```bash
pip download <package-name> --no-binary :all: --no-deps -d /tmp/audit
cd /tmp/audit && tar xzf *.tar.gz
claude /security-review --files /tmp/audit/<package-name>/src/**/*.py
```

**Goal:** Understand what a dependency audit looks like. Even if no zero-days are found, you'll learn to evaluate the security posture of upstream libraries.

### Exercise C: Build a Custom Healthcare Scanning Prompt

Write a custom scanning prompt that targets PMS-specific risks. Use the Claude API directly:

```python
import anthropic

client = anthropic.Anthropic()

with open("src/api/prescriptions.py") as f:
    source_code = f.read()

message = client.messages.create(
    model="claude-sonnet-4-6-20260217",
    max_tokens=4096,
    messages=[{
        "role": "user",
        "content": f"""You are a healthcare security auditor. Analyze this PMS
prescription API for vulnerabilities specific to medication safety:

1. Can a user prescribe medications for a patient they don't have access to?
2. Are dose values validated against safe ranges?
3. Can the prescription be modified after it's been dispensed?
4. Are drug interaction checks enforced before prescribing?
5. Is the prescriber's license/credentials verified?

SOURCE CODE:
{source_code}
"""
    }]
)

print(message.content[0].text)
```

**Goal:** Learn to write domain-specific scanning prompts that go beyond generic vulnerability patterns.

---

## Part 7: Development Workflow and Conventions

### 7.1 File Organization

```
pms-backend/
├── .github/
│   └── workflows/
│       └── security-review.yml      # CI/CD security gate
├── .claude/
│   └── rules/
│       └── security.md              # Framework-specific security rules
├── .scanignore                      # Files excluded from scanning
├── services/
│   └── security-scanner/
│       ├── Dockerfile
│       ├── main.py                  # Deep scan service
│       └── requirements.txt
└── src/
    └── api/
        └── security.py              # Security findings API proxy
```

### 7.2 Naming Conventions

| Item | Convention | Example |
|------|-----------|---------|
| Scan IDs | `{type}-{YYYYMMDD-HHMMSS}` | `deep-20260220-020000` |
| Finding status | `open` → `investigating` → `resolved` / `false_positive` | — |
| Security rules files | `.claude/rules/{scope}.md` | `.claude/rules/security.md` |
| Scanning prompts | `prompts/security/{focus}.txt` | `prompts/security/hipaa-audit.txt` |

### 7.3 PR Checklist

Before submitting a PR that modifies security-sensitive code:

- [ ] Ran `claude /security-review` locally and addressed all Critical/High findings
- [ ] CI/CD security gate passed (check GitHub Actions)
- [ ] No new dependencies added without security evaluation
- [ ] No secrets, API keys, or credentials in committed files
- [ ] Authorization checks present on all new endpoints handling PHI
- [ ] Input validation via Pydantic models on all new request parameters
- [ ] Error responses don't leak internal state (stack traces, SQL queries)
- [ ] Audit logging added for new operations on PHI

### 7.4 Security Reminders

- **Never send PHI to the Claude API.** Only source code and dependency metadata.
- **Always validate Critical findings manually** before reporting them upstream or patching.
- **Cross-reference package names** mentioned in findings against your actual dependency tree.
- **Use Sonnet 4.6 for CI/CD** (fast, cheap) and **Opus 4.6 for deep scans** (thorough, expensive).
- **Log all scan invocations** for HIPAA audit trail.
- **Restrict dashboard access** to `security_admin` role — findings describe attack paths.

---

## Part 8: Quick Reference Card

### Key Commands

```bash
# Ad-hoc scan (current changes)
claude /security-review

# Scan specific files
claude /security-review --files src/api/patients.py

# Scan staged changes
claude /security-review --staged

# Scan last commit
claude /security-review --diff HEAD~1

# Trigger deep dependency scan
curl -X POST http://localhost:8001/api/security/scan \
  -H "Content-Type: application/json" \
  -d '{"target": "dependencies"}'

# List Critical findings
curl -s "http://localhost:8001/api/security/findings?severity=Critical"
```

### Key Files

| File | Purpose |
|------|---------|
| `.github/workflows/security-review.yml` | CI/CD security gate |
| `.claude/rules/security.md` | Framework-specific security rules |
| `.scanignore` | Excluded files/paths |
| `services/security-scanner/main.py` | Deep scan service |
| `src/api/security.py` | Findings API proxy |

### Key URLs

| URL | Purpose |
|-----|---------|
| `http://localhost:3000/security` | Security dashboard |
| `http://localhost:8001/docs` | Scanner API docs |
| `https://red.anthropic.com/2026/zero-days/` | Anthropic's zero-day research |
| `https://cwe.mitre.org/` | CWE vulnerability classification |

### Starter Template: Custom Security Prompt

```python
HEALTHCARE_SECURITY_PROMPT = """
Analyze this healthcare PMS code for:
1. PHI exposure (logging, error messages, API responses)
2. Broken authorization (BOLA — can user A access user B's data?)
3. Input validation gaps (injection, path traversal, deserialization)
4. Cryptographic weaknesses (weak hashing, missing encryption)
5. Supply chain risks (unsafe dependencies, outdated libraries)

Context: This is a HIPAA-regulated Patient Management System.
Severity: Only report findings with >80% exploitability confidence.
Format: JSON array with severity, cwe, title, description, remediation.

CODE:
{source_code}
"""
```

---

## Next Steps

1. **Run a full dependency audit** of the PMS backend using the deep scan service
2. **Review the first week of CI/CD findings** and triage all Critical/High items
3. **Build a custom scanning prompt** for your most sensitive PMS module (Exercise C above)
4. **Read Anthropic's zero-day research** at [red.anthropic.com/2026/zero-days/](https://red.anthropic.com/2026/zero-days/)
5. **Schedule a team security review** to discuss findings and establish triage conventions
