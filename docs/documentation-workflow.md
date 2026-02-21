# PMS Documentation Workflow

**Date:** 2026-02-21
**Purpose:** Visualizes how a feature flows through the documentation system, from initial research through requirements, implementation, testing, and release.

---

## Documentation Flow Diagram

```mermaid
flowchart TB
    %% ── ENTRY POINTS ──
    Feature["New Feature / Change Request"]
    Experiment["Technology Research"]

    %% ── EXPERIMENTS ──
    subgraph EXP["experiments/"]
        PRD["PRD<br/>(00–19 PRDs)"]
        Setup["Setup Guide<br/>(00–19 Guides)"]
        Tutorial["Developer Tutorial<br/>(00–19 Tutorials)"]
        POC["POC Gap Analysis<br/>(04-POC-Gap-Analysis)"]
        PRD --> Setup --> Tutorial
    end

    %% ── FEATURES ──
    subgraph FEAT["features/"]
        FeatureDoc["Feature Docs<br/>initial-project-scaffolds<br/>vision-capabilities"]
        PromptMgmt["aria-prompt-management<br/>(.docx)"]
    end

    %% ── ARCHITECTURE DECISIONS ──
    subgraph ADR["architecture/"]
        ADR1["0001 Repo-Based Knowledge Mgmt"]
        ADR2["0002 Multi-Repo Structure"]
        ADR3["0003 Backend Tech Stack"]
        ADR4["0004 Frontend Tech Stack"]
        ADR5["0005 Android Tech Stack"]
        ADR6["0006 Release Management"]
        ADR7["0007 Jetson Thor Edge"]
    end

    %% ── SYSTEM SPECIFICATION ──
    subgraph SPEC["specs/"]
        SysSpec["system-spec.md<br/>System Specification"]
        SubVer["subsystem-versions.md"]
        RelCompat["release-compatibility-matrix.md"]

        subgraph REQ["specs/requirements/"]
            SysReq["SYS-REQ.md<br/>12 System Requirements"]
            SubPR["SUB-PR.md<br/>Patient Records<br/>16 domain / 36 platform"]
            SubCW["SUB-CW.md<br/>Clinical Workflow<br/>8 domain / 14 platform"]
            SubMM["SUB-MM.md<br/>Medication Mgmt<br/>9 domain / 13 platform"]
            SubRA["SUB-RA.md<br/>Reporting & Analytics<br/>8 domain / 19 platform"]
            SubPM["SUB-PM.md<br/>Prompt Mgmt<br/>7 domain / 13 platform"]
        end

        SysSpec --> SysReq
        SysReq --> SubPR
        SysReq --> SubCW
        SysReq --> SubMM
        SysReq --> SubRA
        SysReq --> SubPM
    end

    %% ── TESTING ──
    subgraph TEST["testing/"]
        Strategy["testing-strategy.md<br/>Test Levels & Conventions"]
        RTM["traceability-matrix.md<br/>Forward & Backward Traceability<br/>60 domain / 95 platform reqs"]
        Evidence["evidence/<br/>Test Run Records"]
    end

    %% ── QUALITY ──
    subgraph QMS["quality/"]
        Governance["processes/<br/>requirements-governance.md"]
        DevInstr["processes/<br/>PMS_Developer_Working_Instructions"]
        Pipeline["processes/<br/>Development_Pipeline_Tutorial"]
        ISO["standards/<br/>iso-13485-2016.pdf"]
        Audits["audits/"]
        CAPA["capa/"]
        Risk["risk-management/"]
    end

    %% ── API ──
    subgraph API["api/"]
        Endpoints["backend-endpoints.md<br/>REST API Reference"]
    end

    %% ── CONFIG ──
    subgraph CFG["config/"]
        ProjectSetup["project-setup.md"]
        Deps["dependencies.md"]
        SecScan["security-scanning.md"]
        Envs["environments.md"]
        RelProcess["release-process.md"]
        Flags["feature-flags.md"]
        Jetson["jetson-deployment.md"]
    end

    %% ── VIEWS ──
    subgraph VIEWS["Documentation Views"]
        subgraph DOM["domain/"]
            DomIdx["index.md"]
            DomPM["property-management"]
            DomSec["security-compliance"]
            DomVis["vision-ai"]
            DomAgent["agentic-ai"]
            DomUI["frontend-ui"]
            DomRel["release-management"]
            DomTest["testing-qa"]
            DomCfg["configuration-devops"]
            DomProj["project-management"]
        end
        subgraph PLAT["platform/"]
            PlatIdx["index.md"]
            PlatBE["backend-server"]
            PlatWEB["web-frontend"]
            PlatAND["android"]
            PlatEdge["jetson-edge"]
            PlatCI["infrastructure-cicd"]
            PlatX["cross-platform"]
        end
    end

    %% ── TOP-LEVEL ──
    Index["index.md<br/>Knowledge Base TOC"]
    Overview["PMS_Project_Overview.md<br/>Bird's Eye View"]
    ReqMatrix["PMS_Requirements_Matrix.xlsx"]

    %% ── FLOW CONNECTIONS ──

    %% Entry → Research
    Experiment --> PRD
    Feature --> FeatureDoc

    %% Research → Architecture
    PRD -->|"informs"| ADR1
    PRD -->|"informs"| ADR7

    %% Feature/PRD → System Spec
    FeatureDoc -->|"drives"| SysSpec
    PRD -->|"drives"| SysSpec

    %% Architecture → System Spec
    ADR3 -->|"constrains"| SysSpec
    ADR4 -->|"constrains"| SysSpec
    ADR5 -->|"constrains"| SysSpec

    %% System Req → Subsystem Reqs (already in SPEC subgraph)

    %% Subsystem Reqs → API Contracts
    SubPR -->|"defines endpoints"| Endpoints
    SubCW -->|"defines endpoints"| Endpoints
    SubMM -->|"defines endpoints"| Endpoints
    SubRA -->|"defines endpoints"| Endpoints
    SubPM -->|"defines endpoints"| Endpoints

    %% Subsystem Reqs → Traceability
    SubPR -->|"traces to"| RTM
    SubCW -->|"traces to"| RTM
    SubMM -->|"traces to"| RTM
    SubRA -->|"traces to"| RTM
    SubPM -->|"traces to"| RTM
    SysReq -->|"traces to"| RTM
    Strategy -->|"governs"| RTM
    RTM --> Evidence

    %% Subsystem Reqs → Versions & Compatibility
    SubPR --> SubVer
    SubCW --> SubVer
    SubMM --> SubVer
    SubRA --> SubVer
    SubPM --> SubVer
    SubVer --> RelCompat

    %% Quality governs the process
    ISO -->|"standard"| Governance
    Governance -->|"governs"| SysReq
    Governance -->|"governs"| RTM
    DevInstr -->|"process"| Pipeline

    %% Config supports implementation
    ADR6 --> RelProcess
    ADR6 --> Flags
    ADR6 --> Envs
    ADR7 --> Jetson
    RelProcess --> RelCompat

    %% Views aggregate documentation
    SysSpec --> Overview
    RTM --> Overview
    SysReq --> ReqMatrix

    %% Index links everything
    Index -.->|"links to"| SPEC
    Index -.->|"links to"| TEST
    Index -.->|"links to"| QMS
    Index -.->|"links to"| API
    Index -.->|"links to"| CFG
    Index -.->|"links to"| EXP
    Index -.->|"links to"| FEAT
    Index -.->|"links to"| ADR
    Index -.->|"links to"| VIEWS

    %% ── STYLES ──
    style Feature fill:#ff6b6b,stroke:#c92a2a,color:#fff
    style Experiment fill:#ff6b6b,stroke:#c92a2a,color:#fff
    style EXP fill:#fff9db,stroke:#f59f00
    style FEAT fill:#fff9db,stroke:#f59f00
    style ADR fill:#d3f9d8,stroke:#37b24d
    style SPEC fill:#d0ebff,stroke:#1c7ed6
    style REQ fill:#a5d8ff,stroke:#1971c2
    style TEST fill:#e5dbff,stroke:#7048e8
    style QMS fill:#ffe3e3,stroke:#e03131
    style API fill:#c3fae8,stroke:#0ca678
    style CFG fill:#f3f0ff,stroke:#845ef7
    style DOM fill:#fff4e6,stroke:#fd7e14
    style PLAT fill:#fff4e6,stroke:#fd7e14
    style VIEWS fill:#fff4e6,stroke:#fd7e14
    style Index fill:#343a40,stroke:#212529,color:#fff
    style Overview fill:#343a40,stroke:#212529,color:#fff
    style SysReq fill:#1971c2,stroke:#1864ab,color:#fff
    style SysSpec fill:#1c7ed6,stroke:#1864ab,color:#fff
```

---

## Workflow Steps with AI Agent Checklists

Each step includes a checklist and a ready-to-use AI agent prompt. Replace `{FEATURE}` with the feature name and `{TECH}` with the technology name.

---

### Step 1: Research & Discovery

**When:** A new technology or feature is being evaluated for PMS integration.

**Checklist:**
- [ ] Scan `docs/experiments/` for the highest numeric prefix (currently `19`)
- [ ] Set new prefix to highest + 1 (zero-padded: `20`, `21`, etc.)
- [ ] Research the technology: architecture, features, security, HIPAA implications
- [ ] Create PRD: `docs/experiments/NN-PRD-{TECH}-PMS-Integration.md`
- [ ] Create Setup Guide: `docs/experiments/NN-{TECH}-PMS-Developer-Setup-Guide.md`
- [ ] Create Developer Tutorial: `docs/experiments/NN-{TECH}-Developer-Tutorial.md`
- [ ] Add experiment section to `docs/index.md` under "Experiments & Tool Evaluations"
- [ ] Commit and push

**AI Agent Prompt:**
```
/tech-research {URL_OR_TOPIC}
```

**Manual prompt alternative:**
```
Research {TECH} for integration into the PMS (Patient Management System).
Read docs/index.md and docs/experiments/ to understand existing conventions.
Create three files in docs/experiments/ following the exact format of
existing experiment docs (e.g., 18-ISICArchive-*):
1. PRD with architecture diagrams, HIPAA analysis, and PMS data sources
2. Developer Setup Guide with step-by-step installation and PMS integration
3. Developer Tutorial with hands-on exercises building a PMS integration
Update docs/index.md with the new experiment section.
```

---

### Step 2: Architecture Decision

**When:** A technology choice, structural change, or design approach needs to be recorded.

**Checklist:**
- [ ] Scan `docs/architecture/` for the highest ADR number (currently `0007`)
- [ ] Create new ADR: `docs/architecture/NNNN-{short-title}.md`
- [ ] Include: Context, Options Considered, Decision, Rationale, Trade-offs, Consequences
- [ ] Cross-reference related PRDs from `docs/experiments/`
- [ ] Update `docs/index.md` under "Architecture Decisions"
- [ ] Commit and push

**AI Agent Prompt:**
```
Read docs/architecture/ to understand the ADR format and numbering.
Create a new Architecture Decision Record for {DECISION_TOPIC}.
The ADR must include:
- Context: why this decision is needed
- Options considered (at least 2-3 alternatives)
- Decision: what was chosen
- Rationale: why this option was selected
- Trade-offs and consequences
- References to related PRDs in docs/experiments/
Follow the naming convention: NNNN-short-title.md
Update docs/index.md with the new ADR link.
```

---

### Step 3: System Requirements

**When:** A new capability is being added to the PMS that requires a formal system-level requirement.

**Checklist:**
- [ ] Read `docs/specs/requirements/SYS-REQ.md` — note current version, date, highest req ID
- [ ] Add new row to the requirements table: `SYS-REQ-XXXX`
- [ ] Add detailed section with: Rationale, Acceptance Criteria, Current Implementation, Decomposes To
- [ ] Increment version number and update date in SYS-REQ.md header
- [ ] Read `docs/specs/system-spec.md` — update subsystem decomposition table, system context diagram, platform codes if needed
- [ ] Increment version number and update date in system-spec.md header
- [ ] Read `docs/PMS_Project_Overview.md` — update system requirements table, subsystem progress, gap analysis
- [ ] Update date in PMS_Project_Overview.md header
- [ ] Commit and push

**AI Agent Prompt:**
```
Read these files to understand the current state:
- docs/specs/requirements/SYS-REQ.md
- docs/specs/system-spec.md
- docs/PMS_Project_Overview.md

Add a new system requirement SYS-REQ-{NEXT_ID} for {FEATURE}.
Follow the exact format of existing requirements (e.g., SYS-REQ-0012).

For the SYS-REQ detailed section include:
- Rationale citing relevant regulations (HIPAA if applicable)
- Numbered acceptance criteria (5-7 items)
- Current Implementation status
- "Decomposes To" listing which SUB-* requirements it creates

Update system-spec.md:
- Subsystem decomposition table scope descriptions
- System context Mermaid diagram if new components are added
- Platform codes table if new platforms are needed

Update PMS_Project_Overview.md:
- System requirements status table
- Subsystem progress counts
- Gap analysis priorities

Increment version numbers and dates in all modified file headers.
```

---

### Step 4: Subsystem Decomposition

**When:** A system requirement needs to be broken down into domain and platform requirements.

**Checklist:**
- [ ] Identify which subsystem(s) the feature belongs to (PR, CW, MM, RA, PM)
- [ ] Read the target `docs/specs/requirements/SUB-{code}.md` — note version, highest req ID, platform counts
- [ ] Add domain requirement rows to the Requirements table: `SUB-{code}-XXXX`
- [ ] Add platform requirement rows to each applicable platform section (BE, WEB, AND, AI):
  - [ ] `SUB-{code}-XXXX-BE` — Backend API endpoint, service, model
  - [ ] `SUB-{code}-XXXX-WEB` — Web UI component, page, form
  - [ ] `SUB-{code}-XXXX-AND` — Android screen, ViewModel, repository
  - [ ] `SUB-{code}-XXXX-AI` — ML model, inference service, embedding pipeline
- [ ] Update platform section counts (e.g., "Backend (BE) — N requirements")
- [ ] Update status rollup note at bottom of Requirements table
- [ ] Increment version number and update date in SUB-*.md header
- [ ] Read `docs/api/backend-endpoints.md` — add new API endpoint definitions
- [ ] Read `docs/specs/subsystem-versions.md` — update if version changes
- [ ] Update `docs/index.md` requirement counts in "Specifications & Requirements" section
- [ ] Commit and push

**AI Agent Prompt:**
```
Read these files to understand current state and conventions:
- docs/specs/requirements/SUB-{CODE}.md (the target subsystem)
- docs/specs/requirements/SYS-REQ.md (to see the parent requirement)
- docs/api/backend-endpoints.md
- docs/index.md (Specifications & Requirements section)

Decompose SYS-REQ-{ID} into subsystem requirements for SUB-{CODE}.
Follow the exact table format of existing requirements in the file.

For each domain requirement (SUB-{CODE}-XXXX), create platform requirements:
- BE: API endpoint with router, service, model modules and test case ID
- WEB: UI component/page with module path and test case ID
- AND: Screen/ViewModel with module path and test case ID (if applicable)
- AI: ML model/inference service with module path and test case ID (if applicable)

Use the naming convention: SUB-{CODE}-XXXX-{PLATFORM}
Test case IDs follow: TST-{CODE}-XXXX-{PLATFORM}

Update:
- Platform section counts in the subsystem doc
- Status rollup note
- Version and date in the file header
- docs/api/backend-endpoints.md with new endpoint definitions
- docs/index.md requirement counts
```

---

### Step 5: Governance & Quality

**When:** New requirements introduce conflicts, risks, or process changes.

**Checklist:**
- [ ] Read `docs/quality/processes/requirements-governance.md` — check for conflicts with existing requirements
- [ ] Analyze new requirements for:
  - [ ] Domain conflicts (DC-*): contradictions between subsystem requirements
  - [ ] Platform conflicts (PC-*): implementation tensions across BE/WEB/AND/AI
  - [ ] Race conditions (RC-*): concurrency issues in multi-platform scenarios
- [ ] Add new conflict entries with IDs, descriptions, and resolution strategies
- [ ] Read `docs/quality/risk-management/` — assess new risks if applicable
- [ ] Verify new requirements comply with `docs/quality/processes/PMS_Developer_Working_Instructions.md`
- [ ] Verify alignment with `docs/quality/standards/iso-13485-2016.pdf` if medical device relevant
- [ ] Commit and push

**AI Agent Prompt:**
```
Read these files:
- docs/quality/processes/requirements-governance.md
- docs/specs/requirements/SUB-{CODE}.md (the newly updated subsystem)
- docs/quality/processes/PMS_Developer_Working_Instructions.md

Analyze the new requirements (SUB-{CODE}-{IDs}) for:

1. Domain Conflicts (DC-*): Do any new requirements contradict existing
   requirements in the same or different subsystems? Check all SUB-*.md files.

2. Platform Conflicts (PC-*): Are there implementation tensions between
   platforms? E.g., encryption approach differs between BE and AND,
   auth token handling differs between WEB and AND.

3. Race Conditions (RC-*): Can concurrent operations across platforms
   cause data inconsistency? E.g., optimistic locking, token refresh
   thundering herd, camera resource contention.

For each conflict found, add an entry to requirements-governance.md with:
- Conflict ID (DC-{CODE}-NN, PC-{PLATFORM}-NN, or RC-{PLATFORM}-NN)
- Description of the conflict
- Affected requirements
- Resolution strategy
- Status (Open/Resolved)

Follow the exact format of existing conflict entries in the file.
```

---

### Step 6: Testing & Traceability

**When:** New requirements have been added and need test coverage tracking.

**Checklist:**
- [ ] Read `docs/testing/traceability-matrix.md` — note version, current counts
- [ ] **Forward traceability:** Add SYS-REQ row mapping to subsystem reqs, modules, and test cases
- [ ] **Backward traceability (subsystem tests):** Add one row per platform requirement:
  - [ ] Test Case ID: `TST-{CODE}-XXXX-{PLATFORM}`
  - [ ] Description, Repository, Test Function (or "not implemented"), Traces To, Last Result, Run ID
- [ ] **Backward traceability (system tests):** Add `TST-SYS-XXXX` row
- [ ] **Platform Traceability Summary:** Add rows to the relevant SUB-* section, update platform req count in header
- [ ] **Coverage Summary by Platform:** Update BE/WEB/AND/AI totals (Total Reqs, Not Started columns)
- [ ] **Coverage Summary:** Update domain req counts, platform req counts, No Tests counts, Domain Coverage percentages
- [ ] Add version update note (e.g., "Note on v1.X updates")
- [ ] Increment version number and update date in header
- [ ] Read `docs/testing/testing-strategy.md` — verify naming conventions are followed
- [ ] Commit and push

**AI Agent Prompt:**
```
Read these files:
- docs/testing/traceability-matrix.md
- docs/testing/testing-strategy.md
- docs/specs/requirements/SUB-{CODE}.md (to get the new requirement IDs)
- docs/specs/requirements/SYS-REQ.md (to get the parent SYS-REQ ID)

Update the traceability matrix for the new requirements:

1. FORWARD TRACEABILITY: Add a row for SYS-REQ-{ID} mapping to all
   subsystem reqs, backend modules, test case IDs, and status.

2. BACKWARD TRACEABILITY (Subsystem Tests): Add one row per NEW platform
   requirement using format:
   | TST-{CODE}-XXXX-{PLATFORM} | Description | Repository | — (not implemented) | SUB-{CODE}-XXXX, SYS-REQ-{ID} | — | — |

   Repositories: pms-backend for BE, pms-frontend for WEB, pms-android for AND

3. BACKWARD TRACEABILITY (System Tests): Add TST-SYS-{ID} row.

4. PLATFORM TRACEABILITY SUMMARY: Add rows to SUB-{CODE} section.
   Update the header count (e.g., "SUB-PR — Patient Records (N platform reqs)").

5. COVERAGE SUMMARY BY PLATFORM: Recalculate BE/WEB/AND/AI totals.

6. COVERAGE SUMMARY: Recalculate domain reqs, platform reqs, No Tests,
   and Domain Coverage percentages for affected subsystems and totals.

7. Add a version update note documenting all changes made.

8. Increment version and update date in file header.

Verify all test case IDs follow the TST-{CODE}-XXXX-{PLATFORM} convention
from testing-strategy.md.
```

---

### Step 7: Configuration & Deployment

**When:** New requirements introduce dependencies, feature flags, environment variables, or deployment changes.

**Checklist:**
- [ ] Read `docs/config/dependencies.md` — add new libraries/services with rationale
- [ ] Read `docs/config/feature-flags.md` — add feature flags for new capabilities
  - [ ] Flag name following convention: `FF_{SUBSYSTEM}_{FEATURE}`
  - [ ] Default state per environment (dev/qa/staging/prod)
  - [ ] Linked requirement IDs
- [ ] Read `docs/config/environments.md` — add new environment variables or services
- [ ] Read `docs/config/project-setup.md` — update setup steps if new services are needed
- [ ] Read `docs/config/security-scanning.md` — verify new dependencies are covered by Snyk/SonarCloud
- [ ] If edge/AI deployment: Read `docs/config/jetson-deployment.md` — update Docker services
- [ ] Commit and push

**AI Agent Prompt:**
```
Read these files:
- docs/config/dependencies.md
- docs/config/feature-flags.md
- docs/config/environments.md
- docs/config/project-setup.md
- docs/config/security-scanning.md

For the new feature {FEATURE} (requirements: {REQ_IDS}), update:

1. dependencies.md: Add any new libraries, Docker services, or external
   dependencies. Include: name, version, purpose, and why it was chosen
   over alternatives.

2. feature-flags.md: Add feature flag(s) for the new capability.
   Follow the naming convention FF_{SUBSYSTEM}_{FEATURE}.
   Set default state: dev=ON, qa=ON, staging=OFF, prod=OFF.
   Link to the requirement IDs.

3. environments.md: Add any new environment variables needed
   (API keys, service URLs, ports, secrets).

4. project-setup.md: Update the setup steps if developers need to
   install new tools or start new services.

5. security-scanning.md: Verify new dependencies are covered.
   Note any exclusions or false-positive suppressions needed.
```

---

### Step 8: Release

**When:** All implementation is complete and the feature is ready to ship.

**Checklist:**
- [ ] Read `docs/specs/subsystem-versions.md` — bump version for affected subsystem(s)
- [ ] Read `docs/specs/release-compatibility-matrix.md` — add new version combination row
- [ ] Read `docs/config/release-process.md` — follow the release checklist:
  - [ ] All tests passing
  - [ ] Security scans clean
  - [ ] Feature flags configured for target environment
  - [ ] Documentation complete (all steps 1-7 done)
- [ ] Read `docs/config/feature-flags.md` — update flag states for release environment
- [ ] Update `docs/PMS_Project_Overview.md` — refresh all counts, coverage, gap analysis
- [ ] Update `docs/index.md` — verify all links, update requirement counts
- [ ] Update `docs/documentation-workflow.md` — update file inventory if new files were added
- [ ] Commit and push
- [ ] Create PR targeting main branch

**AI Agent Prompt:**
```
Read these files:
- docs/specs/subsystem-versions.md
- docs/specs/release-compatibility-matrix.md
- docs/config/release-process.md
- docs/config/feature-flags.md
- docs/PMS_Project_Overview.md
- docs/index.md
- docs/documentation-workflow.md

Prepare the release for {FEATURE} (branch: feature/{BRANCH_NAME}):

1. subsystem-versions.md: Bump version for {SUBSYSTEM} based on the
   scope of changes (patch for fixes, minor for features, major for breaking).

2. release-compatibility-matrix.md: Add a row with the new version
   combination across all repos (backend, frontend, android, docs).

3. feature-flags.md: Update flag states — enable for the target
   release environment.

4. PMS_Project_Overview.md: Refresh ALL counts:
   - System requirements status table
   - Subsystem progress table (domain reqs, platform reqs, coverage)
   - Platform coverage table
   - Requirements test coverage table
   - Gap analysis priorities

5. index.md: Verify all links work, update requirement counts in
   "Specifications & Requirements" section.

6. documentation-workflow.md: Update file inventory if new files
   were added during this feature.

7. Create a summary of all documentation changes made across all steps
   for the PR description.
```

---

### Quick Reference: Which Files to Touch Per Step

| Step | Files Modified |
|---|---|
| 1. Research | `experiments/NN-*` (3 new files), `index.md` |
| 2. Architecture | `architecture/NNNN-*.md` (1 new file), `index.md` |
| 3. System Reqs | `SYS-REQ.md`, `system-spec.md`, `PMS_Project_Overview.md` |
| 4. Subsystem | `SUB-*.md` (1-2 files), `backend-endpoints.md`, `subsystem-versions.md`, `index.md` |
| 5. Governance | `requirements-governance.md` |
| 6. Testing | `traceability-matrix.md` |
| 7. Config | `dependencies.md`, `feature-flags.md`, `environments.md`, `project-setup.md` |
| 8. Release | `subsystem-versions.md`, `release-compatibility-matrix.md`, `feature-flags.md`, `PMS_Project_Overview.md`, `index.md` |

---

## File Inventory

### Total: 97 files (89 markdown + 8 non-markdown)

| Directory | Files | Purpose |
|---|---|---|
| `experiments/` | 58 (55 .md + 3 .docx) | Technology research: PRDs, setup guides, tutorials |
| `architecture/` | 7 | Architecture Decision Records |
| `specs/requirements/` | 6 | System and subsystem requirement documents |
| `specs/` | 3 (+ requirements/) | System spec, versions, compatibility matrix |
| `config/` | 7 | Setup, dependencies, environments, deployment |
| `testing/` | 2 (+ evidence/) | Test strategy, traceability matrix, run records |
| `quality/` | 3 .md + 1 .pdf + 4 assets | QMS processes, governance, ISO standard |
| `features/` | 2 .md + 1 .docx | Feature implementation docs |
| `api/` | 1 | Backend API reference |
| `domain/` | 10 | Documentation views by business domain |
| `platform/` | 6 | Documentation views by deployment platform |
| Root | 3 | index.md, PMS_Project_Overview.md, Requirements Matrix |
