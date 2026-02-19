---
name: tech-research
description: Research a technology topic and generate a PRD, developer setup guide, and developer tutorial for integrating it into the PMS. Creates three files in docs/experiments/ following existing naming conventions. Use when evaluating a new technology, framework, or tool for possible adoption.
argument-hint: [technology topic]
---

# Tech Research Skill

You are researching **$ARGUMENTS** for potential integration into the MPS Patient Management System (PMS).

Your task is to produce **three comprehensive markdown files** in `docs/experiments/` and update `docs/index.md`.

---

## Step 0: Determine the File Prefix

Scan the `docs/experiments/` directory for existing files. Find the highest two-digit numeric prefix (e.g., if `06-*` files exist, the highest is `06`). The new prefix is that number **plus one**, zero-padded to two digits.

Store this as `NN` (e.g., `07`).

## Step 1: Research the Topic

Use **WebSearch** to gather authoritative information about **$ARGUMENTS**:

- What it is and how it works (core concepts, architecture)
- Official documentation URL and GitHub repository
- Key features, capabilities, and limitations
- Ecosystem maturity, community size, licensing
- How it compares to alternatives
- Security considerations (especially relevant to HIPAA / healthcare)
- How it could apply to a system with: FastAPI backend, Next.js frontend, Android (Kotlin/Jetpack Compose) app, and PostgreSQL database

## Step 2: Generate the Three Files

### File 1: PRD — `docs/experiments/NN-PRD-{Topic}-PMS-Integration.md`

Use the naming pattern where `{Topic}` is the technology name in PascalCase or its canonical short name (e.g., `Redis`, `GraphQL`, `WebAssembly`).

Follow this structure (modeled on existing PRDs in the repo):

```
# Product Requirements Document: {Topic} Integration into Patient Management System (PMS)

**Document ID:** PRD-PMS-{TOPIC}-001
**Version:** 1.0
**Date:** {today's date}
**Author:** Ammar (CEO, MPS Inc.)
**Status:** Draft

---

## 1. Executive Summary
{2-3 paragraphs: what is {Topic}, why integrate it into PMS, what value does it deliver}

## 2. Problem Statement
{What PMS operational bottleneck or gap does this technology address? Be specific to healthcare/clinical workflows}

## 3. Proposed Solution

### 3.1 Architecture Overview
{Mermaid diagram (using ```mermaid code blocks) showing how {Topic} fits into the existing PMS stack:
- PMS Backend (FastAPI) on port 8000
- PMS Frontend (Next.js) on port 3000
- PostgreSQL database
- Android app
Show where the new technology sits and what it connects to.
Use flowchart TB/LR with subgraphs, color-coded styles, and clear connection arrows.}

### 3.2 Deployment Model
{Self-hosted vs cloud, Docker-based, security envelope, HIPAA considerations}

## 4. PMS Data Sources
{Which existing PMS APIs and data would this technology interact with:
- Patient Records API (/api/patients)
- Encounter Records API (/api/encounters)
- Medication & Prescription API (/api/prescriptions)
- Reporting API (/api/reports)
Describe which ones are relevant and how}

## 5. Component/Module Definitions
{Define the key components, modules, or integrations that would be built. For each:
- Name and description
- Input/output
- Which PMS APIs it uses}

## 6. Non-Functional Requirements

### 6.1 Security and HIPAA Compliance
{Specific security measures needed for HIPAA compliance with this technology}

### 6.2 Performance
{Performance targets and expectations}

### 6.3 Infrastructure
{Deployment requirements, Docker, resource needs}

## 7. Implementation Phases
{3 phases with sprint estimates:
- Phase 1: Foundation
- Phase 2: Core integration
- Phase 3: Advanced features}

## 8. Success Metrics
{Table with: Metric | Target | Measurement method}

## 9. Risks and Mitigations
{Table with: Risk | Impact | Mitigation}

## 10. Dependencies
{List of all dependencies: the technology itself, APIs, infrastructure, licenses}

## 11. Comparison with Existing Experiments
{Compare with at least one other experiment already in docs/experiments/ — how is this complementary or different?}

## 12. Research Sources
{List the top 5-10 URLs that were most useful during research. For each, include:
- The clickable markdown link: [Page Title](URL)
- A brief note (5-10 words) on what information it provided

Group by category (e.g., Official Documentation, Architecture & Specification, Security & Compliance, Ecosystem & Adoption). Only include links that materially informed the PRD — not every search result.}

## 13. Appendix: Related Documents
{Links to the other two files being generated, plus official docs}
```

### File 2: Setup Guide — `docs/experiments/NN-{Topic}-PMS-Developer-Setup-Guide.md`

Follow this structure (modeled on existing setup guides):

```
# {Topic} Setup Guide for PMS Integration

**Document ID:** PMS-EXP-{TOPIC}-001
**Version:** 1.0
**Date:** {today's date}
**Applies To:** PMS project (all platforms)
**Prerequisites Level:** {Beginner/Intermediate/Advanced}

---

## Table of Contents
{Numbered list of all sections}

## 1. Overview
{What this guide covers, what you'll have by the end, architecture-at-a-glance Mermaid diagram}

## 2. Prerequisites

### 2.1 Required Software
{Table: Software | Minimum Version | Check Command}

### 2.2 Installation of Prerequisites
{Step-by-step for any prerequisites not commonly installed}

### 2.3 Verify PMS Services
{How to confirm the PMS backend, frontend, and database are running}

## 3. Part A: Install and Configure {Topic}
{Step-by-step with numbered steps, code blocks, and verification checks.
Every section ends with a **Checkpoint** confirming what was accomplished.}

## 4. Part B: Integrate with PMS Backend
{How to connect {Topic} to the FastAPI backend — configuration, API calls, data flow}

## 5. Part C: Integrate with PMS Frontend
{How to add {Topic} to the Next.js frontend — components, environment variables, layout changes}

## 6. Part D: Testing and Verification
{Service health checks, functional tests, integration tests — with specific curl commands and expected outputs}

## 7. Troubleshooting
{Common issues with symptoms and fixes. Include:
- Connection issues
- Authentication issues
- Port conflicts
- Performance issues
Format as ### headings with problem description and solution}

## 8. Reference Commands
{Daily development workflow, management commands, monitoring commands, useful URLs table}

## Next Steps
{What to do after setup is complete, link to the developer tutorial}

## Resources
{Official documentation, GitHub repo, community resources, PMS-specific references}
```

### File 3: Developer Tutorial — `docs/experiments/NN-{Topic}-Developer-Tutorial.md`

Follow this structure (modeled on existing tutorials):

```
# {Topic} Developer Onboarding Tutorial

**Welcome to the MPS PMS {Topic} Integration Team**

This tutorial will take you from zero to building your first {Topic} integration with the PMS. By the end, you will understand how {Topic} works, have a running local environment, and have built and tested a custom integration end-to-end.

**Document ID:** PMS-EXP-{TOPIC}-002
**Version:** 1.0
**Date:** {today's date}
**Applies To:** PMS project (all platforms)
**Prerequisite:** [{Topic} Setup Guide](NN-{Topic}-PMS-Developer-Setup-Guide.md)
**Estimated time:** 2-3 hours
**Difficulty:** Beginner-friendly

---

## What You Will Learn
{Numbered list of 8-10 learning objectives}

## Part 1: Understanding {Topic} (15 min read)

### 1.1 What Problem Does {Topic} Solve?
{Explain the problem in PMS context — what staff pain point does this address}

### 1.2 How {Topic} Works — The Key Pieces
{Mermaid diagram showing the mental model. Break it into 2-3 main concepts. Use flowchart with clear stages and labeled connections.}

### 1.3 How {Topic} Fits with Other PMS Technologies
{Table comparing with existing experiments — what's complementary vs overlapping}

### 1.4 Key Vocabulary
{Table: Term | Meaning — 8-12 domain-specific terms}

### 1.5 Our Architecture
{Mermaid diagram of the full integration architecture. Use flowchart with subgraphs for network boundaries, color-coded nodes by role, and labeled edges.}

## Part 2: Environment Verification (15 min)

### 2.1 Checklist
{Numbered verification steps with bash commands and expected output}

### 2.2 Quick Test
{One simple test to confirm everything works end-to-end}

## Part 3: Build Your First Integration (45 min)

### 3.1 What We Are Building
{Describe a concrete, small integration}

### 3.2-3.6 Step-by-step implementation
{Detailed numbered steps with full code listings, explanations, and checkpoints}

## Part 4: Evaluating Strengths and Weaknesses (15 min)

### 4.1 Strengths
{What {Topic} does well — performance, DX, ecosystem, etc.}

### 4.2 Weaknesses
{Limitations, gotchas, areas where alternatives might be better}

### 4.3 When to Use {Topic} vs Alternatives
{Decision matrix or guidelines}

### 4.4 HIPAA / Healthcare Considerations
{Security and compliance evaluation specific to healthcare}

## Part 5: Debugging Common Issues (15 min read)
{5+ common issues with symptoms, causes, and fixes. Include log reading tips}

## Part 6: Practice Exercise (45 min)
{2-3 options for hands-on exercises the developer can try independently.
Include hints and step outlines for each option}

## Part 7: Development Workflow and Conventions

### 7.1 File Organization
{Directory tree showing where {Topic} code lives}

### 7.2 Naming Conventions
{Table: Item | Convention | Example}

### 7.3 PR Checklist
{Checkbox list for submitting PRs that involve {Topic}}

### 7.4 Security Reminders
{HIPAA-specific security guidelines for this technology}

## Part 8: Quick Reference Card
{Key commands, key files, key URLs, and a starter template — all in a compact format for printing}

## Next Steps
{5 numbered next steps with links to related docs}
```

## Step 3: Update `docs/index.md`

Add a new subsection under the `## Experiments & Tool Evaluations` section in `docs/index.md`. Place it after the last experiment entry, before the `---` separator. Use this format:

```markdown
### {Topic} ({one-line description of what category the tech falls into})
- [PRD: {Topic} PMS Integration](experiments/NN-PRD-{Topic}-PMS-Integration.md) — {one-sentence summary}
- [{Topic} Setup Guide](experiments/NN-{Topic}-PMS-Developer-Setup-Guide.md) — {one-sentence summary}
- [{Topic} Developer Tutorial](experiments/NN-{Topic}-Developer-Tutorial.md) — {one-sentence summary}
```

## Important Guidelines

- **Be specific to PMS**: Every section should reference real PMS concepts — patient records, encounters, medications, clinical workflows, HIPAA compliance. Don't write generic documentation.
- **Use real PMS API endpoints**: Reference `/api/patients`, `/api/encounters`, `/api/prescriptions`, `/api/reports` as the integration points.
- **Use Mermaid diagrams**: All architecture and flow diagrams must use ```mermaid code blocks (not ASCII art). Use `flowchart TB` or `flowchart LR` with subgraphs, color-coded `style` directives, and clear labeled edges. Show how the technology fits into the existing PMS stack (FastAPI :8000, Next.js :3000, PostgreSQL :5432, Android app).
- **HIPAA compliance**: Every PRD and setup guide must address HIPAA security requirements — encryption, audit logging, access control, PHI isolation.
- **Checkpoints**: End each setup guide section with a **Checkpoint** summary.
- **Code blocks**: Include real, runnable code examples (bash commands, config files, TypeScript/Python snippets).
- **Cross-reference**: Link between the three files and to existing experiment docs where relevant.
- **Today's date**: Use today's date in all document headers.
- **Author**: Use "Ammar (CEO, MPS Inc.)" as the author in PRDs.
