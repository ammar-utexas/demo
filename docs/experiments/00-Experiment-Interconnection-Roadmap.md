# PMS Experiment Interconnection Roadmap

**Document ID:** PMS-EXP-ROADMAP-001
**Version:** 1.0
**Date:** March 2, 2026
**Author:** Ammar (CEO, MPS Inc.)
**Status:** Living Document

---

## 1. Executive Summary

The PMS project maintains 28 experiments (numbered 00–27) evaluating technologies across frontend UI tools, clinical AI models, healthcare interoperability standards, edge computing, and developer experience. Each experiment has been documented independently — PRDs, setup guides, and tutorials — but no single document maps how these experiments relate to each other or the recommended order to execute them.

This roadmap serves as the **master navigation guide** for the experiment portfolio. It provides:

- A **complete registry** of all 28 experiments with categories, platforms, and documentation inventory
- A **dependency graph** showing which experiments build on or complement others
- **Execution tiers** recommending a foundation-first build order
- **Parallel tracks** for teams that can work on independent streams simultaneously
- A **critical path analysis** identifying bottleneck experiments that gate the most downstream work
- **Quick-start recommendations** for 1-week, 1-month, and 1-quarter execution plans

### How to Use This Document

1. **New to the project?** Start with [Section 8: Quick Start Recommendations](#8-quick-start-recommendations)
2. **Planning a sprint?** Check [Section 4: Execution Tiers](#4-recommended-execution-tiers) for prioritization
3. **Looking for related experiments?** Use the [Section 6: Interconnection Matrix](#6-interconnection-matrix)
4. **Assessing risk?** Review [Section 7: Critical Path Analysis](#7-critical-path-analysis) for bottlenecks

### Scope

This roadmap covers experiments 00–27 as documented in `docs/experiments/`. It does not cover core PMS implementation (requirements, ADRs, platform development) — for that, see the [PMS Project Overview](../PMS_Project_Overview.md).

---

## 2. Experiment Registry

| # | Name | Category | Platforms | Dependencies | Doc Types |
|---|------|----------|-----------|-------------|-----------|
| 00 | [Tambo](00-PRD-Tambo-PMS-Integration.md) | Frontend / AI UI | Web | 09-MCP | PRD, Setup, Tutorial |
| 01 | [Storybook](01-Storybook-Getting-Started.md) | Frontend / Dev Tooling | Web | None | Setup, Tutorial |
| 02 | [v0](02-v0-Getting-Started.md) | Frontend / AI UI | Web | 01-Storybook | Setup, Tutorial |
| 03 | [Banani](03-Banani-Getting-Started.md) | Frontend / AI UI | Web | 01-Storybook | Setup, Tutorial |
| 04 | [POC Gap Analysis](04-POC-Gap-Analysis.md) | Analysis | Cross | None | Analysis |
| 05 | [OpenClaw](05-PRD-OpenClaw-PMS-Integration.md) | Backend / AI Agents | Backend, Web | 09-MCP | PRD, Setup, Tutorial |
| 06 | Minimax M25 ADG | AI Models | Backend | None | .docx only |
| 07 | [MedASR](07-PRD-MedASR-PMS-Integration.md) | Backend / AI Models | Backend, Web | None | PRD, Setup, Tutorial |
| 08 | [Adaptive Thinking](08-PRD-AdaptiveThinking-PMS-Integration.md) | Backend / AI Infra | Backend | 09-MCP | PRD, Setup, Tutorial |
| 09 | [MCP](09-PRD-MCP-PMS-Integration.md) | Backend / AI Infra | Backend, Web, Android | None | PRD, Setup, Tutorial |
| 10 | [Speechmatics Medical](10-PRD-SpeechmaticsMedical-PMS-Integration.md) | Backend / External API | Backend, Web | None | PRD, Setup, Tutorial |
| 11 | [Sanford Guide](11-PRD-SanfordGuide-PMS-Integration.md) | Backend / External API | Backend, Web | 16-FHIR | PRD, Setup, Tutorial |
| 12 | [AI Zero-Day Scan](12-PRD-AIZeroDayScan-PMS-Integration.md) | Dev Tooling / Security | CI/CD | None | PRD, Setup, Tutorial, Plan |
| 13 | [Gemma 3](13-PRD-Gemma3-PMS-Integration.md) | Backend / AI Models | Backend | None | PRD, Setup, Tutorial |
| 14 | [Agent Teams](14-agent-teams-claude-whitepaper.md) | Dev Tooling | Dev | 19-Superpowers | Reference, Tutorial |
| 15 | [Claude Model Selection](15-PRD-ClaudeModelSelection-PMS-Integration.md) | Backend / AI Infra | Backend | 09-MCP, 08-Adaptive | PRD, Setup, Tutorial |
| 16 | [FHIR](16-PRD-FHIR-PMS-Integration.md) | Backend / Interop | Backend, Web | None | PRD, Setup, Tutorial |
| 17 | [HL7v2 LIS](17-PRD-HL7v2LIS-PMS-Integration.md) | Backend / Interop | Backend, Web | 16-FHIR | PRD, Setup, Tutorial |
| 18 | [ISIC Archive](18-PRD-ISICArchive-PMS-Integration.md) | Backend / AI Models / Edge | Backend, Web, Edge | 13-Gemma 3 | PRD, Setup, Tutorial |
| 19 | [Superpowers](19-PRD-Superpowers-PMS-Integration.md) | Dev Tooling | Dev | None | PRD, Setup, Tutorial |
| 20 | [Qwen 3.5](20-PRD-Qwen35-PMS-Integration.md) | Backend / AI Models | Backend | 13-Gemma 3 | PRD, Setup, Tutorial |
| 21 | [Voxtral Transcribe 2](21-PRD-VoxtralTranscribe2-PMS-Integration.md) | Backend / AI Models | Backend, Web | None | PRD, Setup, Tutorial |
| 22 | [Patient Safety AI Ref](22-PMS_AI_Extension_Ideas.md) | Reference / Analysis | Cross | None | Reference |
| 23 | [Atlas Agentic AI](23-Atlas-Agentic-AI-Healthcare-Synergies.md) | Reference / Analysis | Cross | None | Reference |
| 24 | [Knowledge Work Plugins](24-PRD-KnowledgeWorkPlugins-PMS-Integration.md) | Dev Tooling | Dev | 19-Superpowers, 14-Agent Teams | PRD, Setup, Tutorial |
| 25 | [Edge Vision Stream](25-PRD-EdgeVisionStream-PMS-Integration.md) | Edge / AI Models | Edge, Android | 18-ISIC, 13-Gemma 3 | PRD, Setup, Tutorial, Build Guide |
| 26 | [LangGraph](26-PRD-LangGraph-PMS-Integration.md) | Backend / AI Agents | Backend, Web | 09-MCP, 05-OpenClaw | PRD, Setup, Tutorial |
| 27 | [Claude Code](27-ClaudeCode-Developer-Tutorial.md) | Dev Tooling | Dev | None | Tutorial |

---

## 3. Master Dependency Graph

```mermaid
flowchart TD
    %% ── Subgraph: UI Tools ──
    subgraph UI["UI Tools"]
        E01["01 Storybook"]
        E02["02 v0"]
        E03["03 Banani"]
        E00["00 Tambo"]
    end

    %% ── Subgraph: AI Infrastructure ──
    subgraph INFRA["AI Infrastructure"]
        E09["09 MCP"]
        E08["08 Adaptive Thinking"]
        E15["15 Claude Model Selection"]
    end

    %% ── Subgraph: On-Premise Models ──
    subgraph MODELS["On-Premise Models"]
        E06["06 Minimax M25"]
        E13["13 Gemma 3"]
        E20["20 Qwen 3.5"]
    end

    %% ── Subgraph: Speech & NLP ──
    subgraph SPEECH["Speech & NLP"]
        E07["07 MedASR"]
        E10["10 Speechmatics"]
        E21["21 Voxtral Transcribe 2"]
    end

    %% ── Subgraph: Clinical Decision Support ──
    subgraph CDS["Clinical Decision Support"]
        E11["11 Sanford Guide"]
        E18["18 ISIC Archive"]
    end

    %% ── Subgraph: Interoperability ──
    subgraph INTEROP["Interoperability"]
        E16["16 FHIR"]
        E17["17 HL7v2 LIS"]
    end

    %% ── Subgraph: Agentic AI ──
    subgraph AGENTS["Agentic AI"]
        E05["05 OpenClaw"]
        E26["26 LangGraph"]
    end

    %% ── Subgraph: Edge Computing ──
    subgraph EDGE["Edge Computing"]
        E25["25 Edge Vision Stream"]
    end

    %% ── Subgraph: Dev Tooling ──
    subgraph DEVTOOL["Dev Tooling"]
        E12["12 AI Zero-Day Scan"]
        E14["14 Agent Teams"]
        E19["19 Superpowers"]
        E24["24 Knowledge Work Plugins"]
        E27["27 Claude Code"]
    end

    %% ── Subgraph: Reference & Analysis ──
    subgraph REF["Reference & Analysis"]
        E04["04 POC Gap Analysis"]
        E22["22 Patient Safety AI Ref"]
        E23["23 Atlas Agentic AI"]
    end

    %% ── Hard Dependencies (solid arrows) ──
    E01 --> E02
    E01 --> E03
    E09 --> E00
    E09 --> E05
    E09 --> E08
    E09 --> E26
    E05 --> E26
    E08 --> E15
    E09 --> E15
    E13 --> E20
    E13 --> E18
    E16 --> E17
    E16 --> E11
    E18 --> E25
    E13 --> E25
    E19 --> E14
    E19 --> E24
    E14 --> E24
    E27 --> E19
    E27 --> E14

    %% ── Complementary / Enhances (dashed arrows) ──
    E07 -.->|enhances| E10
    E07 -.->|enhances| E21
    E10 -.->|complements| E21
    E13 -.->|enhances| E07
    E20 -.->|enhances| E11
    E05 -.->|enhances| E00
    E16 -.->|enhances| E05
    E26 -.->|enhances| E05
    E12 -.->|parallel| E19
    E08 -.->|enhances| E05
    E23 -.->|informs| E05
    E22 -.->|informs| E04
    E04 -.->|informs| E09

    %% ── Color Classes ──
    classDef ui fill:#818cf8,stroke:#4f46e5,color:#fff
    classDef infra fill:#38bdf8,stroke:#0284c7,color:#fff
    classDef models fill:#34d399,stroke:#059669,color:#fff
    classDef speech fill:#fbbf24,stroke:#d97706,color:#000
    classDef cds fill:#f87171,stroke:#dc2626,color:#fff
    classDef interop fill:#a78bfa,stroke:#7c3aed,color:#fff
    classDef agents fill:#fb923c,stroke:#ea580c,color:#fff
    classDef edge fill:#2dd4bf,stroke:#0d9488,color:#fff
    classDef devtool fill:#94a3b8,stroke:#64748b,color:#fff
    classDef ref fill:#e2e8f0,stroke:#94a3b8,color:#334155

    class E00,E01,E02,E03 ui
    class E09,E08,E15 infra
    class E06,E13,E20 models
    class E07,E10,E21 speech
    class E11,E18 cds
    class E16,E17 interop
    class E05,E26 agents
    class E25 edge
    class E12,E14,E19,E24,E27 devtool
    class E04,E22,E23 ref
```

**Legend:** Solid arrows = hard dependency (must be implemented first). Dashed arrows = complementary/enhances (benefits from but does not require).

---

## 4. Recommended Execution Tiers

### Tier 0 — Foundation (Weeks 1–2)

Establish infrastructure, standards, and context. These experiments have **zero dependencies** and are prerequisites for most later work.

| # | Experiment | Rationale |
|---|-----------|-----------|
| 04 | POC Gap Analysis | Understand current coverage gaps before building |
| 09 | MCP | Foundation protocol — 6 experiments depend on it |
| 16 | FHIR | Interoperability backbone — gates HL7v2 and Sanford Guide |
| 01 | Storybook | Component infrastructure — gates v0 and Banani |
| 19 | Superpowers | Dev workflow — gates Agent Teams and Knowledge Work Plugins |
| 22 | Patient Safety AI Ref | Reference — informs prioritization |
| 23 | Atlas Agentic AI | Reference — maps 50 use cases to PMS subsystems |
| 27 | Claude Code | Developer prerequisite — master the primary development tool before all experiments |

### Tier 1 — Core Capabilities (Weeks 3–5)

Build on Tier 0 foundations. These experiments provide core AI, interop, and security capabilities.

| # | Experiment | Dependencies |
|---|-----------|-------------|
| 08 | Adaptive Thinking | 09-MCP |
| 13 | Gemma 3 | None (but benefits from Tier 0 context) |
| 15 | Claude Model Selection | 09-MCP, 08-Adaptive |
| 17 | HL7v2 LIS | 16-FHIR |
| 07 | MedASR | None (standalone, but position here for clinical pipeline) |
| 12 | AI Zero-Day Scan | None (parallel security track) |

### Tier 2 — Integration & Expansion (Weeks 6–9)

Combine Tier 1 capabilities into integrated workflows. Multiple experiments can run in parallel.

| # | Experiment | Dependencies |
|---|-----------|-------------|
| 05 | OpenClaw | 09-MCP |
| 10 | Speechmatics Medical | None (compare with 07-MedASR) |
| 20 | Qwen 3.5 | 13-Gemma 3 |
| 11 | Sanford Guide | 16-FHIR |
| 00 | Tambo | 09-MCP |
| 02 | v0 | 01-Storybook |
| 03 | Banani | 01-Storybook |
| 14 | Agent Teams | 19-Superpowers |
| 21 | Voxtral Transcribe 2 | None (compare with 07, 10) |

### Tier 3 — Advanced Capabilities (Weeks 10–12)

Complex integrations requiring multiple Tier 1–2 foundations.

| # | Experiment | Dependencies |
|---|-----------|-------------|
| 18 | ISIC Archive (DermaCheck) | 13-Gemma 3 |
| 25 | Edge Vision Stream | 18-ISIC, 13-Gemma 3 |
| 26 | LangGraph | 09-MCP, 05-OpenClaw |
| 24 | Knowledge Work Plugins | 19-Superpowers, 14-Agent Teams |

### Tier 4 — Capstone Integrations (Week 13+)

Full end-to-end clinical workflows combining multiple experiments.

| Pipeline | Experiments Combined | Description |
|----------|---------------------|-------------|
| Clinical Documentation Pipeline | 07/10/21 + 13/20 + 05 + 26 | Transcribe → Structure → Approve → File |
| Full DermaCheck + Edge | 18 + 25 + 13 + 09 + 16 | Capture → Classify → Risk Score → FHIR Export |
| Autonomous Care Coordination | 05 + 26 + 16 + 11 + 15 | Multi-step agent with HITL, FHIR interop, model routing |

### Execution Timeline (Gantt)

```mermaid
gantt
    title Experiment Execution Tiers
    dateFormat YYYY-MM-DD
    axisFormat %b %d

    section Tier 0 — Foundation
    04 POC Gap Analysis        :t04, 2026-03-09, 3d
    09 MCP                     :t09, 2026-03-09, 10d
    16 FHIR                    :t16, 2026-03-09, 10d
    01 Storybook               :t01, 2026-03-09, 5d
    19 Superpowers             :t19, 2026-03-09, 5d
    22 Patient Safety Ref      :t22, 2026-03-09, 2d
    23 Atlas Agentic AI        :t23, 2026-03-09, 2d
    27 Claude Code             :t27, 2026-03-09, 3d

    section Tier 1 — Core
    08 Adaptive Thinking       :t08, after t09, 7d
    13 Gemma 3                 :t13, 2026-03-16, 10d
    15 Claude Model Selection  :t15, after t08, 5d
    17 HL7v2 LIS               :t17, after t16, 7d
    07 MedASR                  :t07, 2026-03-16, 7d
    12 AI Zero-Day Scan        :t12, 2026-03-16, 5d

    section Tier 2 — Integration
    05 OpenClaw                :t05, after t09, 10d
    10 Speechmatics            :t10, after t07, 5d
    20 Qwen 3.5                :t20, after t13, 7d
    11 Sanford Guide           :t11, after t16, 7d
    00 Tambo                   :t00, after t09, 7d
    02 v0                      :t02, after t01, 5d
    03 Banani                  :t03, after t01, 5d
    14 Agent Teams             :t14, after t19, 5d
    21 Voxtral Transcribe 2    :t21, after t07, 5d

    section Tier 3 — Advanced
    18 ISIC Archive            :t18, after t13, 10d
    25 Edge Vision Stream      :t25, after t18, 10d
    26 LangGraph               :t26, after t05, 10d
    24 Knowledge Work Plugins  :t24, after t14, 7d

    section Tier 4 — Capstone
    Clinical Doc Pipeline      :t_cdp, after t26, 14d
    Full DermaCheck + Edge     :t_dce, after t25, 14d
```

---

## 5. Parallel Execution Tracks

Five independent tracks that can be staffed and executed simultaneously. Cross-track dependencies are minimal and noted explicitly.

### Track A — UI/UX
```
01-Storybook → 02-v0 → 03-Banani → 00-Tambo
                                       ↑
                                  (needs 09-MCP from Track D)
```

### Track B — Clinical AI
```
{07-MedASR, 10-Speechmatics, 21-Voxtral}  →  {13-Gemma 3, 20-Qwen 3.5}  →  18-ISIC  →  25-Edge Vision
     (independent ASR comparisons)              (on-premise model stack)       (CDS)       (edge deploy)
```

### Track C — Interoperability
```
16-FHIR → {17-HL7v2 LIS, 11-Sanford Guide}
```

### Track D — AI Infrastructure & Agents
```
09-MCP → {08-Adaptive Thinking, 05-OpenClaw} → {15-Claude Model Selection, 26-LangGraph}
```

### Track E — Developer Experience
```
27-Claude Code → 19-Superpowers → 14-Agent Teams → 24-Knowledge Work Plugins
                                                      (+ 12-AI Zero-Day Scan runs in parallel)
```

### Cross-Track Dependencies

```mermaid
flowchart LR
    subgraph A["Track A: UI/UX"]
        A1["01 Storybook"] --> A2["02 v0"]
        A1 --> A3["03 Banani"]
        A4["00 Tambo"]
    end

    subgraph B["Track B: Clinical AI"]
        B1["07 MedASR"]
        B2["10 Speechmatics"]
        B3["21 Voxtral"]
        B4["13 Gemma 3"]
        B5["20 Qwen 3.5"]
        B6["18 ISIC"]
        B7["25 Edge Vision"]
        B1 --> B4
        B4 --> B5
        B4 --> B6
        B6 --> B7
    end

    subgraph C["Track C: Interop"]
        C1["16 FHIR"]
        C2["17 HL7v2 LIS"]
        C3["11 Sanford Guide"]
        C1 --> C2
        C1 --> C3
    end

    subgraph D["Track D: AI Infra"]
        D1["09 MCP"]
        D2["08 Adaptive"]
        D3["05 OpenClaw"]
        D4["15 Model Selection"]
        D5["26 LangGraph"]
        D1 --> D2
        D1 --> D3
        D2 --> D4
        D3 --> D5
    end

    subgraph E["Track E: Dev Experience"]
        E0["27 Claude Code"]
        E1["19 Superpowers"]
        E2["14 Agent Teams"]
        E3["24 Knowledge Plugins"]
        E4["12 Zero-Day Scan"]
        E0 --> E1
        E1 --> E2
        E2 --> E3
    end

    %% Cross-track dependencies
    D1 -.->|"required"| A4
    C1 -.->|"enhances"| D3
    D3 -.->|"required"| D5
    B4 -.->|"required"| B7

    style A fill:#eef2ff,stroke:#818cf8
    style B fill:#ecfdf5,stroke:#34d399
    style C fill:#f5f3ff,stroke:#a78bfa
    style D fill:#f0f9ff,stroke:#38bdf8
    style E fill:#f8fafc,stroke:#94a3b8
```

---

## 6. Interconnection Matrix

Relationship types: **D** = Dependency, **C** = Complementary, **S** = Same Domain, **E** = Enhances

|  | 00 | 01 | 02 | 03 | 05 | 07 | 08 | 09 | 10 | 11 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 24 | 25 | 26 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **00 Tambo** | — | | | | E | | | D | | | | | | | | | | | | | | |
| **01 Storybook** | | — | D | D | | | | | | | | | | | | | | | | | | |
| **02 v0** | | D | — | S | | | | | | | | | | | | | | | | | | |
| **03 Banani** | | D | S | — | | | | | | | | | | | | | | | | | | |
| **05 OpenClaw** | E | | | | — | | E | D | | | | | | E | | | | | | | | E |
| **07 MedASR** | | | | | | — | | | S | | E | | | | | | | | S | | | |
| **08 Adaptive** | | | | | E | | — | D | | | | | D | | | | | | | | | |
| **09 MCP** | D | | | | D | | D | — | | | | | D | | | | | | | | | D |
| **10 Speechmatics** | | | | | | S | | | — | | | | | | | | | | C | | | |
| **11 Sanford Guide** | | | | | | | | | | — | | | | D | | | | E | | | | |
| **13 Gemma 3** | | | | | | E | | | | | — | | | | | D | | D | | | D | |
| **14 Agent Teams** | | | | | | | | | | | | — | | | | | D | | | D | | |
| **15 Model Select** | | | | | | | D | D | | | | | — | | | | | | | | | |
| **16 FHIR** | | | | | E | | | | | D | | | | — | D | | | | | | | |
| **17 HL7v2 LIS** | | | | | | | | | | | | | | D | — | | | | | | | |
| **18 ISIC** | | | | | | | | | | | D | | | | | — | | | | | D | |
| **19 Superpowers** | | | | | | | | | | | | D | | | | | — | | | D | | |
| **20 Qwen 3.5** | | | | | | | | | | E | D | | | | | | | — | | | | |
| **21 Voxtral** | | | | | | S | | | C | | | | | | | | | | — | | | |
| **24 Knowledge Plugins** | | | | | | | | | | | | D | | | | | D | | | — | | |
| **25 Edge Vision** | | | | | | | | | | | D | | | | | D | | | | | — | |
| **26 LangGraph** | | | | | D | | | D | | | | | | | | | | | | | | — |

_Sparse matrix — only non-empty cells are shown. Experiments 04, 06, 12, 22, 23 omitted (zero or reference-only relationships)._

---

## 7. Critical Path Analysis

### Longest Dependency Chain

The critical path — the longest sequence of dependent experiments — determines the minimum time to reach full capability:

```
09-MCP → 05-OpenClaw → 26-LangGraph → Clinical Documentation Pipeline (Tier 4)
  10d        10d           10d                   14d                      = 44 days
```

### Bottleneck Experiments

These experiments **gate the most downstream work** and should be prioritized:

| Experiment | Downstream Count | Blocks |
|-----------|-----------------|--------|
| **09 MCP** | 6 | 00-Tambo, 05-OpenClaw, 08-Adaptive, 15-Model Selection, 26-LangGraph, (+ Tier 4 pipelines) |
| **13 Gemma 3** | 3 | 18-ISIC, 20-Qwen 3.5, 25-Edge Vision |
| **16 FHIR** | 2 | 11-Sanford Guide, 17-HL7v2 LIS |
| **01 Storybook** | 2 | 02-v0, 03-Banani |
| **19 Superpowers** | 2 | 14-Agent Teams, 24-Knowledge Work Plugins |

### Critical Path Diagram

```mermaid
flowchart LR
    E09["09 MCP<br/>10d"]:::critical --> E05["05 OpenClaw<br/>10d"]:::critical
    E05 --> E26["26 LangGraph<br/>10d"]:::critical
    E26 --> CAP["Clinical Doc<br/>Pipeline<br/>14d"]:::critical

    E09 --> E08["08 Adaptive<br/>7d"]
    E08 --> E15["15 Model Selection<br/>5d"]

    E13["13 Gemma 3<br/>10d"]:::bottleneck --> E18["18 ISIC<br/>10d"]
    E18 --> E25["25 Edge Vision<br/>10d"]
    E25 --> CAP2["DermaCheck+Edge<br/>14d"]

    E16["16 FHIR<br/>10d"]:::bottleneck --> E17["17 HL7v2 LIS<br/>7d"]

    classDef critical fill:#dc2626,stroke:#991b1b,color:#fff
    classDef bottleneck fill:#f59e0b,stroke:#d97706,color:#000
```

---

## 8. Quick Start Recommendations

### 1-Week Sprint

**Goal:** Establish foundation context and begin core infrastructure.

| Day | Activity |
|-----|----------|
| 1 | Read reference docs: [04-POC Gap Analysis](04-POC-Gap-Analysis.md), [22-Patient Safety AI Ref](22-PMS_AI_Extension_Ideas.md), [23-Atlas Agentic AI](23-Atlas-Agentic-AI-Healthcare-Synergies.md) |
| 2–3 | Begin [09-MCP](09-PRD-MCP-PMS-Integration.md): PRD review, FastMCP server skeleton |
| 4–5 | Begin [16-FHIR](16-PRD-FHIR-PMS-Integration.md): PRD review, FHIR Facade skeleton |

### 1-Month Plan

| Week | Focus | Experiments |
|------|-------|-------------|
| 1 | Infrastructure | 09-MCP + 16-FHIR (parallel) |
| 2 | AI Foundation | 13-Gemma 3 + 08-Adaptive Thinking (parallel) |
| 3 | Agents + Speech | 05-OpenClaw + 07-MedASR (parallel) |
| 4 | Dev + UI | 01-Storybook + 19-Superpowers (parallel) |

### 1-Quarter Plan (13 Weeks)

| Weeks | Tier | Experiments |
|-------|------|-------------|
| 1–2 | 0 — Foundation | 04, 09, 16, 01, 19, 22, 23, 27 |
| 3–5 | 1 — Core | 08, 13, 15, 17, 07, 12 |
| 6–9 | 2 — Integration | 05, 10, 20, 11, 00, 02, 03, 14, 21 |
| 10–12 | 3 — Advanced | 18, 25, 26, 24 |
| 13 | 4 — Capstone | Clinical Doc Pipeline, DermaCheck+Edge |

---

## 9. Platform Coverage Matrix

| Experiment | Backend | Web | Android | Database | AI Models | Edge | External APIs | Dev Tooling |
|-----------|---------|-----|---------|----------|-----------|------|---------------|-------------|
| 00 Tambo | | X | | | | | | |
| 01 Storybook | | X | | | | | | X |
| 02 v0 | | X | | | | | | |
| 03 Banani | | X | | | | | | |
| 04 POC Gap Analysis | X | X | X | X | | | | |
| 05 OpenClaw | X | X | | X | | | | |
| 06 Minimax M25 | X | | | | X | | | |
| 07 MedASR | X | X | | | X | | | |
| 08 Adaptive Thinking | X | | | | X | | | |
| 09 MCP | X | X | X | | | | | |
| 10 Speechmatics | X | X | | | | | X | |
| 11 Sanford Guide | X | X | | X | | | X | |
| 12 AI Zero-Day Scan | | | | | X | | | X |
| 13 Gemma 3 | X | X | | | X | | | |
| 14 Agent Teams | | | | | | | | X |
| 15 Claude Model Selection | X | | | X | X | | | |
| 16 FHIR | X | X | | X | | | | |
| 17 HL7v2 LIS | X | X | | X | | | | |
| 18 ISIC Archive | X | X | | X | X | X | | |
| 19 Superpowers | | | | | | | | X |
| 20 Qwen 3.5 | X | | | | X | | | |
| 21 Voxtral Transcribe 2 | X | X | | | X | | | |
| 22 Patient Safety Ref | X | X | X | X | X | | | |
| 23 Atlas Agentic AI | X | X | X | | X | | | |
| 24 Knowledge Work Plugins | | | | | | | | X |
| 25 Edge Vision Stream | | | X | | X | X | | |
| 26 LangGraph | X | X | | X | X | | | |
| 27 Claude Code | | | | | | | | X |
| **Total** | **18** | **16** | **5** | **9** | **14** | **3** | **2** | **6** |

---

## 10. Category Legend & Color Key

Reference for Mermaid diagram styling in Section 3.

| Category | Color | Hex | Experiments |
|----------|-------|-----|-------------|
| UI Tools | Indigo | `#818cf8` | 00, 01, 02, 03 |
| AI Infrastructure | Sky Blue | `#38bdf8` | 08, 09, 15 |
| On-Premise Models | Emerald | `#34d399` | 06, 13, 20 |
| Speech & NLP | Amber | `#fbbf24` | 07, 10, 21 |
| Clinical Decision Support | Red | `#f87171` | 11, 18 |
| Interoperability | Violet | `#a78bfa` | 16, 17 |
| Agentic AI | Orange | `#fb923c` | 05, 26 |
| Edge Computing | Teal | `#2dd4bf` | 25 |
| Dev Tooling | Slate | `#94a3b8` | 12, 14, 19, 24, 27 |
| Reference & Analysis | Light Gray | `#e2e8f0` | 04, 22, 23 |

---

## 11. Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.1 | 2026-03-02 | Ammar | Added Experiment 27 (Claude Code Mastery) |
| 1.0 | 2026-03-02 | Ammar | Initial roadmap covering experiments 00–26 |
