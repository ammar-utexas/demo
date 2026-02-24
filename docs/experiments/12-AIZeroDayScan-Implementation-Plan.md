# AI Zero-Day Scan — Claude Code Security Implementation Plan

**Document ID:** PMS-EXP-AIZERODAYSCAN-003
**Version:** 1.0
**Date:** February 23, 2026
**Applies To:** PMS project (all platforms)
**Source:** [Anthropic Claude Code Security Announcement](https://www.anthropic.com/news/claude-code-security)
**Status:** Actionable — Claude Code Security now available in limited research preview

---

## Context

Claude Code Security (limited research preview) provides AI-powered vulnerability scanning that reads and reasons about code like a human security researcher — catching business logic flaws, broken access control, and inter-procedural bugs that Snyk/SonarCloud miss. PMS already has Experiment 12 (AI Zero-Day Scan) as the PRD blueprint. These steps turn that blueprint into reality using the new official product.

---

## Phase 1: Get Access (This Week)

1. **Apply for the research preview** at [claude.com/contact-sales/security](https://claude.com/contact-sales/security) — mention PMS is a HIPAA-regulated healthcare application with Enterprise tier + BAA
2. **Request open-source maintainer access** if any PMS repos are public (expedited free access)
3. **Confirm BAA coverage** — verify with Anthropic that Claude Code Security scanning falls under the existing Enterprise BAA (source code only, no PHI)

## Phase 2: CI/CD Integration (Sprint 1 — 2 weeks)

4. **Add the GitHub Action** to all 3 PMS repos. Create `.github/workflows/claude-security.yml`:
   ```yaml
   name: Claude Code Security Review
   on:
     pull_request:
       types: [opened, synchronize]
   jobs:
     security-review:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: anthropics/claude-code-security-review@v1
           with:
             anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
             severity_threshold: medium
             model: claude-sonnet-4-6
   ```

5. **Create `.scanignore`** in each repo root to exclude PHI-adjacent files:
   ```
   # Database migrations with test data
   **/migrations/versions/*.py
   # Environment and secrets
   .env*
   docker-compose*.yml
   # Test fixtures with synthetic PHI
   **/fixtures/*.json
   **/test_data/
   ```

6. **Add `ANTHROPIC_API_KEY`** to GitHub org-level secrets (same key used for other PMS Claude integrations)

7. **Configure severity gating** in the workflow — block PRs on Critical/High findings, warn on Medium (matching Experiment 12 PRD spec)

## Phase 3: Update Security Scanning Docs

8. **Update `docs/config/security-scanning.md`** — add a new "Claude Code Security" section alongside SonarCloud, CodeRabbit, and Snyk:
   - Scan type: AI-powered reasoning (logic flaws, broken access control, zero-days)
   - Scope: PR diffs (CI/CD) + full codebase (scheduled deep scan)
   - Complements: Snyk (known CVEs), SonarCloud (code quality rules), CodeRabbit (AI review)
   - HIPAA: Source code only — no PHI sent to API

## Phase 4: Developer Workflow (Sprint 2)

9. **Enable ad-hoc scanning** — developers run `/security-review` in Claude Code CLI against local changes before pushing. No infrastructure needed.

10. **Add PMS-specific security rules to `CLAUDE.md`** in each repo:
    ```markdown
    ## Security Review Rules
    - Flag any endpoint accessing /api/patients without RBAC middleware
    - Flag PHI fields (patient_name, dob, ssn, mrn) without AES-256 encryption
    - Flag audit log gaps on clinical data mutations
    - Flag raw SQL or unparameterized queries in any router
    - Flag JWT validation bypass patterns
    ```

11. **Validate with intentional vulnerabilities** — create 10 test PRs with known issues (SQL injection, BOLA, broken auth, unencrypted PHI) and confirm Claude Code Security catches them

## Phase 5: Deep Scan Service (Sprint 3-4)

12. **Deploy the Deep Dependency Auditor** as outlined in Experiment 12 PRD (Section 5.2):
    - FastAPI microservice on `:8001` in Docker
    - Weekly cron scanning full dependency tree (pip, npm, Gradle)
    - Opus 4.6 for deep analysis (Sonnet 4.6 for CI/CD)
    - SARIF output → GitHub Security tab

13. **Build findings storage** — new `security_findings` schema in PostgreSQL with:
    - Finding severity, CWE classification, confidence rating
    - Affected file/line, remediation suggestion
    - Status workflow: `open` → `triaged` → `in_progress` → `resolved`
    - Encrypted at rest (AES-256), RBAC-restricted to `security_admin` role

## Phase 6: Dashboard & Unified View (Sprint 5)

14. **Build the Security Dashboard** in PMS Frontend (Next.js):
    - Findings table with severity filters
    - Dependency risk heatmap
    - Trend charts (findings over time)
    - Unified view merging Claude Code Security + Snyk + SonarCloud findings

15. **Set up weekly digest** — automated email/Slack summary of new findings, open critical issues, and remediation progress

## Phase 7: Ongoing Operations

16. **Establish triage SLA** — Critical findings: 48hr remediation, High: 1 week, Medium: 1 sprint
17. **Track false positive rate** — target <20%; feed false positives back to improve `.scanignore` and CLAUDE.md rules
18. **Quarterly review** — audit Anthropic data retention policy, validate BAA, review API costs (~$50-150/month estimated)

---

## Integration with Existing Security Stack

| Layer | Tool | What It Catches | Status |
|-------|------|-----------------|--------|
| Known CVEs | **Snyk** | Published vulnerabilities in dependencies | Active |
| Code quality | **SonarCloud** | Bug patterns, code smells, coverage | Active |
| AI code review | **CodeRabbit** | Style, HIPAA patterns, design issues | Active |
| AI security reasoning | **Claude Code Security** | Logic flaws, zero-days, broken access control | **New** |

The key value: Claude Code Security fills the gap between what rule-based tools detect (known patterns) and what requires human-level reasoning (business logic flaws, inter-procedural vulnerabilities, partially-fixed bugs). Experiment 12's PRD already has the full architecture — these steps execute it using the now-available official product.

---

## Related Documents

- [PRD: AI Zero-Day Scan PMS Integration](12-PRD-AIZeroDayScan-PMS-Integration.md)
- [AI Zero-Day Scan Setup Guide](12-AIZeroDayScan-PMS-Developer-Setup-Guide.md)
- [AI Zero-Day Scan Developer Tutorial](12-AIZeroDayScan-Developer-Tutorial.md)
- [Security Scanning Configuration](../config/security-scanning.md)
- [Anthropic Claude Code Security Announcement](https://www.anthropic.com/news/claude-code-security)
