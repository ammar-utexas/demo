# Product Requirements Document: Qwen 3.5 Integration into Patient Management System (PMS)

**Document ID:** PRD-PMS-QWEN35-001
**Version:** 1.2
**Date:** March 9, 2026
**Author:** Ammar (CEO, MPS Inc.)
**Status:** Draft

---

## 1. Executive Summary

Qwen 3.5 is Alibaba Cloud's open-weight Mixture-of-Experts (MoE) language model family, with the flagship Qwen3.5-397B-A17B released on February 16, 2026 and the full family (0.8B through 397B) completed by March 2, 2026. The flagship contains 397 billion total parameters but activates only 17 billion per forward pass through a sparse MoE architecture with 512 experts, using a novel hybrid of Gated DeltaNet (linear attention) and standard attention layers. This achieves near-frontier performance — 83.6 on LiveCodeBench v6, 91.3 on AIME26, 88.4 on GPQA Diamond, 76.4 on SWE-bench Verified, and 99.0 on HumanEval — while consuming a fraction of the compute of dense models. The model supports a 262K native context window (extendable to 1M+ via YaRN RoPE scaling), native multimodal input (text + image + video) via early fusion, and 201 languages, all under the permissive Apache 2.0 license.

Integrating Qwen 3.5 into the PMS provides a **high-performance on-premise reasoning and code generation engine** that complements the existing Gemma 3 integration (Experiment 13). While Gemma 3 excels at clinical multimodal tasks (medical imaging, encounter summarization, MedGemma clinical QA), Qwen 3.5 fills a distinct gap: complex clinical reasoning, structured data transformation, agentic workflow automation, and code generation for clinical rule engines. With only 17B active parameters per token, it achieves inference efficiency comparable to much smaller models while delivering frontier-class reasoning.

This PRD proposes deploying Qwen 3.5 alongside Gemma 3 in the PMS on-premise AI layer, exposed through the same AI Gateway (FastAPI :8001) with intelligent task-based routing. Qwen 3.5 handles reasoning-heavy tasks (differential diagnosis support, clinical protocol navigation, ICD-10/CPT code suggestion, medication interaction analysis) while Gemma 3 and MedGemma handle multimodal clinical tasks (medical imaging, CXR analysis, pathology). This dual-model strategy maximizes clinical AI capability while maintaining zero PHI data egress.

## 2. Problem Statement

The PMS on-premise AI layer (Experiment 13 — Gemma 3) provides clinical summarization, medical document understanding, and structured data extraction. However, three capability gaps remain:

1. **Complex Reasoning Ceiling:** Gemma 3 27B, while strong for summarization and multimodal tasks, underperforms on tasks requiring deep multi-step reasoning — differential diagnosis chains, medication interaction cascades with 5+ drugs, and complex clinical protocol navigation. Qwen 3.5's 83.6 LiveCodeBench and 91.3 AIME26 scores indicate substantially stronger reasoning capabilities with its thinking mode.

2. **Agentic Code Generation:** The PMS requires automated generation of clinical rule engine code (medication alerts, order set logic, clinical pathway automation). Gemma 3 produces adequate but not exceptional code. Qwen 3.5's top-1% CodeForces performance and dedicated thinking mode for code generation produce significantly more reliable structured outputs for programmatic clinical rules.

3. **Long-Context Clinical Analysis:** Patient histories spanning years of encounters, multi-page referral letters, and longitudinal medication records can exceed 128K tokens. Qwen 3.5's 1M token context window (vs Gemma 3's 128K) enables whole-patient-history reasoning without chunking or summarization loss.

4. **Cost-Efficient Reasoning at Scale:** Running a dense 27B model for every request wastes compute on simple tasks. Qwen 3.5's MoE architecture activates only 17B parameters per token, providing 8.6x–19x faster decoding than equivalent dense models — enabling high-throughput reasoning at lower GPU cost per request.

## 3. Proposed Solution

### 3.1 Architecture Overview

```mermaid
flowchart TB
    subgraph Client["Client Layer"]
        FE["PMS Frontend<br/>Next.js :3000"]
        AND["Android App<br/>Kotlin/Compose"]
    end

    subgraph Backend["PMS Backend Layer"]
        API["PMS API Server<br/>FastAPI :8000"]
        DB[(PostgreSQL<br/>:5432)]
    end

    subgraph AI["On-Premise AI Layer"]
        GW["AI Gateway<br/>FastAPI :8001"]
        OLLAMA["Ollama Server<br/>:11434"]
        VLLM["vLLM Server<br/>:8080"]
        subgraph QwenModels["Qwen 3.5 Models"]
            Q397["Qwen3.5-397B-A17B<br/>Complex Reasoning"]
            Q32["Qwen3-32B<br/>Standard Tasks"]
            Q8["Qwen3-8B<br/>Real-Time Tasks"]
        end
        subgraph GemmaModels["Gemma 3 Models (Exp 13)"]
            G27["Gemma 3 27B-IT<br/>Clinical Multimodal"]
            MG["MedGemma 27B<br/>Medical Specialist"]
        end
    end

    subgraph Storage["Secure Storage"]
        MSTORE["Model Files<br/>/opt/pms/models"]
        LOGS["Audit Logs<br/>/var/log/pms-ai"]
        CACHE["Response Cache<br/>Redis :6379"]
    end

    FE -->|"REST/SSE"| API
    AND -->|"REST/SSE"| API
    API -->|"/v1/chat/completions"| GW
    GW -->|"Reasoning tasks"| VLLM
    GW -->|"Clinical tasks"| OLLAMA
    VLLM --> QwenModels
    OLLAMA --> GemmaModels
    API --> DB
    GW --> CACHE
    GW --> LOGS

    style FE fill:#4FC3F7,stroke:#0288D1,color:#000
    style AND fill:#4FC3F7,stroke:#0288D1,color:#000
    style API fill:#81C784,stroke:#388E3C,color:#000
    style DB fill:#FFB74D,stroke:#F57C00,color:#000
    style GW fill:#CE93D8,stroke:#7B1FA2,color:#000
    style OLLAMA fill:#F48FB1,stroke:#C2185B,color:#000
    style VLLM fill:#F48FB1,stroke:#C2185B,color:#000
    style Q397 fill:#B3E5FC,stroke:#0277BD,color:#000
    style Q32 fill:#B3E5FC,stroke:#0277BD,color:#000
    style Q8 fill:#B3E5FC,stroke:#0277BD,color:#000
    style G27 fill:#FFF59D,stroke:#F9A825,color:#000
    style MG fill:#FFF59D,stroke:#F9A825,color:#000
    style CACHE fill:#A5D6A7,stroke:#2E7D32,color:#000
```

### 3.2 Deployment Model

**Self-Hosted, Air-Gapped Capable:**
- All Qwen 3.5 model weights stored locally alongside existing Gemma 3 models
- No internet connectivity required after initial model download from Hugging Face
- Qwen 3.5 served via **vLLM** (optimal for MoE models with tensor parallelism) while Gemma 3 continues via Ollama
- Docker Compose deployment with GPU passthrough (NVIDIA Container Toolkit)
- AI Gateway routes requests to the appropriate model/backend based on task type

**HIPAA Security Envelope:**
- PHI never leaves the local network — all inference happens on-premise
- Qwen 3.5 runs under Apache 2.0 license — no usage reporting or telemetry
- AI Gateway logs every prompt/response with de-identified metadata for audit trails
- TLS 1.3 encryption for all internal service-to-service communication
- Same RBAC controls as Gemma 3 integration (Experiment 13)

**Qwen 3.5 Model Family (as of March 9, 2026):**

The full Qwen 3.5 family spans three series — **Flagship/Medium** (MoE, Feb 16–24), **Medium Dense** (Feb 24), and **Small** (Dense, Feb 27–Mar 2) — all sharing the same Gated DeltaNet hybrid architecture, native multimodal input (text + image + video via early fusion), 262K native context (extendable to 1M+), and Apache 2.0 license.

| Model | Series | Architecture | Active Params | VRAM (Q4) | Context | Key Benchmarks | PMS Use Case |
|-------|--------|-------------|---------------|-----------|---------|----------------|-------------|
| Qwen3.5-397B-A17B | Flagship | MoE (512 experts) | 17B | ~214 GB (4-8x GPU) | 262K–1M+ | AIME26 91.3, GPQA 88.4, SWE-bench 76.4 | Complex reasoning, differential diagnosis, long-context |
| Qwen3.5-122B-A10B | Medium | MoE (128 experts) | 10B | ~81 GB (2x GPU) | 262K–1M+ | BFCL-V4 72.2 | Mid-tier reasoning, tool use, agentic workflows |
| Qwen3.5-35B-A3B | Medium | MoE (128 experts) | 3B | ~24 GB (1x GPU) | 262K | Surpasses prev Qwen3-235B | **Consumer MoE sweet spot** — reasoning on single GPU |
| Qwen3.5-27B | Medium | Dense | 27B | ~17 GB | 262K–800K+ | SWE-bench 72.4 | Dense alternative, ties GPT-5 mini |
| **Qwen3.5-9B** | **Small** | **Dense** | **9B** | **~5 GB** | **262K** | **GPQA 81.7, MMLU-Pro 82.5, MMMU-Pro 70.1** | **Single-GPU workhorse — beats GPT-OSS-120B (13x larger)** |
| **Qwen3.5-4B** | **Small** | **Dense** | **4B** | **~2.5 GB** | **262K** | **Strong multimodal, doc understanding** | **Lightweight multimodal agent, edge deployment** |
| **Qwen3.5-2B** | **Small** | **Dense** | **2B** | **~1.3 GB** | **262K** | **First 2B with video processing** | **Mobile agent, structured extraction on-device** |
| **Qwen3.5-0.8B** | **Small** | **Dense** | **0.8B** | **~0.5 GB** | **262K** | **First 0.8B with video** | **Phone/IoT, text classification, triage routing** |
| Gemma 3 27B-IT | — | Dense | 27B | ~14.1 GB | 128K | Strong summarization | Clinical summarization, multimodal imaging (Exp 13) |
| MedGemma 27B | — | Dense | 27B | ~14.1 GB | 128K | 87.7% MedQA | Medical QA, CXR analysis, pathology (Exp 13) |

> **Small Series highlights (March 2, 2026):**
> - All four small models are **dense** (not MoE) — simpler deployment, no expert routing overhead
> - **Qwen3.5-9B** is the standout: GPQA Diamond 81.7 beats GPT-OSS-120B (71.5) — a model 13x its size; MMMU-Pro 70.1 beats Gemini 2.5 Flash-Lite (59.7); OmniDocBench v1.5 87.7 (best-in-class document understanding)
> - All small models support **thinking mode** (reasoning chains) and **non-thinking mode** (fast responses)
> - **Native multimodal from 0.8B up** — the first model family where a sub-1B model can process video (up to 60s at 8 FPS)
> - 248K-token vocabulary covering 201 languages; multi-token prediction for faster inference
>
> **Recommendation update:** For single-GPU consumer deployments, choose based on task complexity:
> - **Qwen3.5-9B** (~5 GB Q4) for reasoning-heavy tasks where you want near-frontier quality at minimal cost
> - **Qwen3.5-35B-A3B** (~24 GB Q4) when you need MoE-class reasoning and have a full RTX 4090
> - **Qwen3.5-4B** (~2.5 GB Q4) for lightweight multimodal agents and edge kiosks
> - **Qwen3.5-0.8B/2B** for phone-based patient intake forms and on-device triage

### Qwen 3.5 Model Selection Guide — "What to Use When"

```mermaid
flowchart TD
    START["What is your deployment target?"] --> PHONE["Phone / IoT / Embedded"]
    START --> EDGE["Edge Kiosk / Tablet / Laptop"]
    START --> GPU1["Single Consumer GPU<br/>(12–24 GB)"]
    START --> WS["Workstation<br/>(1–2x A100/H100)"]
    START --> SERVER["Multi-GPU Server<br/>(4–8x H100)"]

    PHONE --> Q08["Qwen3.5-0.8B or 2B<br/>0.5–1.3 GB VRAM"]
    Q08 --> Q08USE["• Text classification, triage<br/>• Patient intake forms<br/>• On-device video summarization"]

    EDGE --> Q4B["Qwen3.5-4B<br/>2.5 GB VRAM"]
    Q4B --> Q4BUSE["• Multimodal agent<br/>• Document OCR + extraction<br/>• Offline clinical forms"]

    GPU1 --> CHOICE{"Need best<br/>quality/VRAM ratio?"}
    CHOICE -->|"Yes — 5 GB"| Q9B["Qwen3.5-9B<br/>GPQA 81.7"]
    CHOICE -->|"Have full 24 GB"| Q35B["Qwen3.5-35B-A3B<br/>MoE-class reasoning"]

    WS --> WSCHOICE{"Primary need?"}
    WSCHOICE -->|"Dense reasoning"| Q27B["Qwen3.5-27B<br/>17 GB"]
    WSCHOICE -->|"Agentic tool use"| Q122B["Qwen3.5-122B-A10B<br/>81 GB"]

    SERVER --> Q397["Qwen3.5-397B-A17B<br/>214+ GB"]
    Q397 --> Q397USE["• Frontier reasoning<br/>• 1M token long-context<br/>• Differential diagnosis + code gen"]

    style Q08 fill:#C8E6C9,stroke:#2E7D32,color:#000
    style Q4B fill:#C8E6C9,stroke:#2E7D32,color:#000
    style Q9B fill:#B3E5FC,stroke:#0277BD,color:#000
    style Q35B fill:#B3E5FC,stroke:#0277BD,color:#000
    style Q27B fill:#CE93D8,stroke:#7B1FA2,color:#000
    style Q122B fill:#CE93D8,stroke:#7B1FA2,color:#000
    style Q397 fill:#FFCCBC,stroke:#BF360C,color:#000
```

**Task Routing Matrix (updated with Small Series):**

| Task Category | Primary Model | Fallback | Rationale |
|---------------|--------------|----------|-----------|
| Differential diagnosis | Qwen3.5-397B | **Qwen3.5-9B** | Multi-step reasoning with thinking mode; 9B achieves GPQA 81.7 as fallback |
| Medication interaction analysis | Qwen3.5-397B | **Qwen3.5-9B** | Complex cascade analysis; 9B handles 3-5 drug interactions well |
| ICD-10/CPT code suggestion | **Qwen3.5-9B** | Qwen3.5-4B | Structured extraction with JSON mode; 9B's MMLU-Pro 82.5 is excellent |
| Clinical rule engine code gen | Qwen3.5-397B | Qwen3.5-35B-A3B | Top-1% CodeForces code quality |
| Clinical note summarization | Gemma 3 27B | Qwen3.5-9B | Gemma excels at summarization |
| Medical image analysis | MedGemma 27B | Gemma 3 27B | MedGemma trained on clinical images |
| Real-time autocomplete | **Qwen3.5-4B** | Qwen3.5-0.8B | 4B: strong quality at 2.5 GB; 0.8B: ultra-fast for simple completions |
| Longitudinal patient analysis | Qwen3.5-397B | Qwen3.5-9B | 1M context; 9B handles 262K natively |
| **Document OCR + extraction** | **Qwen3.5-9B** | Qwen3.5-4B | OmniDocBench 87.7 — best-in-class; replaces separate OCR pipeline |
| **On-device patient intake** | **Qwen3.5-2B** | Qwen3.5-0.8B | Mobile-friendly; handles forms + basic image input |
| **Waiting room kiosk triage** | **Qwen3.5-4B** | Qwen3.5-2B | Multimodal agent on tablet; no network dependency |
| **Vitals/labs classification** | **Qwen3.5-0.8B** | — | Ultra-lightweight; fast classification on any hardware |

## 4. PMS Data Sources

Qwen 3.5 interacts with the following PMS APIs through the AI Gateway:

### Patient Records API (`/api/patients`)
- **Input:** Full patient demographics, medical history, allergies, problem list, longitudinal encounter history
- **Use:** Whole-patient reasoning across 1M token context; differential diagnosis support using complete history; care gap identification
- **Advantage over Gemma 3:** 1M token context allows processing years of patient history without chunking

### Encounter Records API (`/api/encounters`)
- **Input:** Visit notes, chief complaints, assessments, plans, linked orders and results
- **Use:** Complex clinical reasoning across multiple encounters; protocol adherence checking; discharge summary generation with reasoning chains
- **Thinking Mode:** Qwen 3.5's thinking mode produces explicit reasoning chains — valuable for clinical audit trails

### Medication & Prescription API (`/api/prescriptions`)
- **Input:** Active medications, dosages, allergies, renal/hepatic function, drug interaction databases
- **Use:** Multi-drug interaction cascade analysis (5+ medications); dose optimization with explicit pharmacokinetic reasoning; formulary substitution suggestions with clinical rationale
- **Function Calling:** Qwen 3.5 supports tool use for structured database lookups during reasoning

### Reporting API (`/api/reports`)
- **Input:** Aggregate clinical data, quality metrics, utilization patterns, compliance dashboards
- **Use:** Generate clinical rule engine code for automated quality reporting; complex analytical queries in natural language; trend analysis with statistical reasoning

## 5. Component/Module Definitions

### 5.1 AI Gateway Extension — Qwen 3.5 Routing
- **Description:** Extends the existing AI Gateway (Experiment 13) with Qwen 3.5 model routing via vLLM backend
- **Input:** Chat completion requests with task-type hints for intelligent routing
- **Output:** OpenAI-compatible responses, optionally including reasoning chains from thinking mode
- **Key Change:** `MODEL_MAP` extended with Qwen models; task-type header (`X-Task-Type`) enables automatic model selection

### 5.2 Clinical Reasoning Engine
- **Description:** Provides multi-step clinical reasoning with explicit thinking chains. Uses Qwen 3.5's thinking mode to produce auditable reasoning for clinical decisions.
- **Input:** Patient context JSON from `/api/patients` + clinical question or scenario
- **Output:** Structured reasoning output: `{reasoning_chain: [...], conclusion: "...", confidence: 0.XX, references: [...]}`
- **Model:** Qwen3.5-397B-A17B (thinking mode enabled)
- **PMS APIs Used:** `/api/patients`, `/api/encounters`, `/api/prescriptions`

### 5.3 Differential Diagnosis Module
- **Description:** Given symptoms, history, and test results, generates a ranked differential diagnosis with reasoning for each candidate
- **Input:** Symptom list, patient history, lab results, imaging findings
- **Output:** Ranked list of diagnoses with probability estimates and reasoning chains
- **Model:** Qwen3.5-397B-A17B (thinking mode)
- **Safety:** All outputs labeled "AI-Suggested — Requires Physician Review"

### 5.4 Clinical Rule Code Generator
- **Description:** Generates executable Python code for clinical alert rules, order set logic, and pathway automation based on natural language specifications
- **Input:** Natural language rule description (e.g., "Alert if creatinine rises >0.3 mg/dL within 48 hours")
- **Output:** Python function with type hints, validation, and unit tests
- **Model:** Qwen3.5-397B-A17B or Qwen3-32B
- **Safety:** Generated code requires human review and testing before deployment

### 5.5 Long-Context Patient Analysis Module
- **Description:** Processes complete patient histories (up to 1M tokens) for longitudinal analysis, care gap identification, and trend detection
- **Input:** Full patient record JSON spanning multiple years of encounters
- **Output:** Longitudinal summary, identified trends, care gaps, recommended follow-ups
- **Model:** Qwen3.5-397B-A17B (1M context)
- **PMS APIs Used:** `/api/patients` (full history), `/api/encounters` (all encounters), `/api/prescriptions` (medication history)

### 5.6 Structured Code Extraction Module
- **Description:** Extracts ICD-10, CPT, SNOMED codes from clinical narratives with higher accuracy than Gemma 3, using Qwen 3.5's JSON schema mode
- **Input:** Free-text clinical notes from `/api/encounters`
- **Output:** JSON conforming to PMS schema with extracted codes, medications, vitals
- **Model:** Qwen3-32B (JSON schema mode in non-thinking mode)
- **Advantage:** JSON schema enforcement ensures structurally valid output without post-processing

## 6. Non-Functional Requirements

### 6.1 Security and HIPAA Compliance

| Requirement | Implementation |
|-------------|---------------|
| PHI Isolation | All inference runs on-premise; no PHI transmitted to Alibaba Cloud or any external service |
| License | Apache 2.0 — no usage reporting, no telemetry, no restrictions on commercial healthcare use |
| Encryption at Rest | Model files and audit logs encrypted with AES-256 on encrypted filesystem |
| Encryption in Transit | TLS 1.3 for all service-to-service communication within the AI layer |
| Access Control | Same RBAC as Gemma 3 on AI Gateway — clinicians, nurses, admins have different model access |
| Audit Logging | Every prompt/response logged with timestamp, user ID, model used, token count, thinking mode status (PHI redacted) |
| Data Retention | AI inference logs retained for 7 years per HIPAA; response cache TTL of 24 hours |
| Model Integrity | SHA-256 checksums verified on model load; read-only model storage |
| BAA Not Required | No third-party data processor — Qwen 3.5 runs within the covered entity's infrastructure |
| Thinking Chain Audit | When thinking mode is used, the full reasoning chain is logged for clinical decision audit trails |

### 6.2 Performance

| Metric | Target | Notes |
|--------|--------|-------|
| Time to First Token (TTFT) | < 300ms (8B), < 800ms (32B), < 1.5s (397B) | MoE sparsity accelerates 397B |
| Tokens per Second | > 50 tok/s (8B), > 25 tok/s (32B), > 15 tok/s (397B int4) | 8.6x–19x faster decoding than dense equivalent |
| Concurrent Users | 10 simultaneous inference requests | vLLM continuous batching |
| Context Window | Up to 1M tokens for longitudinal analysis | Requires sufficient KV cache memory |
| Thinking Mode Overhead | < 2x latency vs non-thinking mode | Acceptable for non-real-time reasoning tasks |

### 6.3 Infrastructure

| Component | Requirement |
|-----------|------------|
| GPU (397B FP8) | 8x H200 80GB or 4x GB200 (tensor + expert parallel) |
| GPU (397B NVFP4) | 4x H100 80GB (~200 GB) |
| GPU (397B Q4 GGUF) | 214–256 GB combined (e.g., 4x A100 80GB) |
| GPU (122B-A10B) | 2x A100 80GB |
| GPU (35B-A3B Q4) | 1x RTX 4090 24GB — **MoE sweet spot** |
| GPU (27B Q4) | 1x RTX 4090 or RTX 3090 24GB (~17 GB) |
| **GPU (9B Q4)** | **1x RTX 3060 12GB (~5 GB) — Small Series flagship** |
| **GPU (4B Q4)** | **1x RTX 3060 or integrated GPU (~2.5 GB) — edge/kiosk** |
| **GPU (2B Q4)** | **Apple M1/M2/M3 or any 4GB+ GPU (~1.3 GB) — mobile** |
| **GPU (0.8B Q4)** | **CPU-only viable (~0.5 GB) — phone/IoT** |
| RAM | 64 GB system RAM minimum (128 GB recommended for 397B); 8 GB for small models |
| Storage | 250 GB for Qwen model files + existing Gemma storage (small models add ~15 GB) |
| vLLM | vLLM nightly (0.17.0 pending GA) with MoE/expert parallel support |
| Ollama | Ollama 0.6+ — preferred for small models (simpler deployment, auto model swapping) |
| Docker | Docker 24+ with NVIDIA Container Toolkit |
| OS | Ubuntu 22.04 LTS or later; macOS 14+ for Apple Silicon deployment |
| Supported GPUs | NVIDIA H200, H100, A100, L40, RTX 4090/3090/3060; AMD MI300X/MI325X/MI35X; Apple M-series |

## 7. Implementation Phases

### Phase 1: Foundation (Sprints 1-2, 4 weeks)
- Deploy vLLM (nightly/0.17.0) with Qwen3.5-35B-A3B (single GPU) and Qwen3.5-9B in Docker
- Deploy Qwen3.5-4B and Qwen3.5-0.8B via Ollama for edge/mobile testing
- Extend AI Gateway with Qwen model routing and task-type headers
- Implement Clinical Reasoning Engine with thinking mode
- Add Qwen models to model health checks and audit logging
- Integration tests with PMS Backend via existing `/api/ai/*` endpoints

### Phase 2: Core Integration (Sprints 3-5, 6 weeks)
- Deploy Qwen3.5-397B-A17B with tensor parallelism across 2 GPUs
- Build Differential Diagnosis Module
- Build Clinical Rule Code Generator
- Build Structured Code Extraction Module with JSON schema mode
- Implement task-based routing in AI Gateway (auto-select Qwen vs Gemma based on task type)
- Frontend: Add reasoning chain display component for thinking mode outputs

### Phase 3: Advanced Features (Sprints 6-8, 6 weeks)
- Enable 1M token context for Long-Context Patient Analysis Module
- Fine-tune Qwen3-32B with LoRA on de-identified clinical reasoning examples
- Build A/B comparison pipeline (Qwen vs Gemma on clinical tasks) for accuracy benchmarking
- Implement intelligent model fallback (397B → 32B → 8B) based on GPU load
- Clinical validation study with physician review panel on differential diagnosis output
- Performance optimization: KV cache management, speculative decoding, batch scheduling

## 8. Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Reasoning Accuracy | > 85% physician agreement on differential diagnosis | Blinded review of 200 AI-generated differentials |
| Code Generation Quality | > 90% of generated clinical rules pass unit tests on first attempt | Automated test execution |
| ICD-10 Extraction F1 | > 0.93 F1 score (vs Gemma 3's 0.90 target) | Comparison with manual coding on 500 notes |
| Inference Latency (P95) | < 5 seconds for 397B reasoning task | AI Gateway latency metrics |
| Context Utilization | Successfully process 500K+ token patient histories | Integration test with synthetic long histories |
| GPU Utilization | < 70% average across both GPUs during normal load | nvidia-smi monitoring |
| Cost per Inference | < $0.002 per reasoning request (amortized GPU cost) | Monthly hardware cost / request count |
| Thinking Chain Completeness | 100% of reasoning tasks produce auditable chains | Audit log inspection |

## 9. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| 397B model requires 2x A100/H100 GPUs ($20,000-$60,000) | High upfront CapEx | Start with Qwen3-32B on existing GPU; upgrade when ROI justified |
| MoE architecture has higher memory bandwidth requirements | Inference slower than expected | Use vLLM with optimized MoE kernels; enable tensor parallelism |
| Qwen 3.5 not trained specifically on medical data | Lower clinical accuracy than MedGemma | Use for reasoning/coding tasks, not clinical QA; MedGemma handles medical-specific tasks. Community medical fine-tunes available (Qwen-3-32B-Medical-Reasoning) for evaluation |
| MCP tool calling regression on long requests | Multi-step agentic workflows may fail | Monitor [GitHub issue #12](https://github.com/QwenLM/Qwen3.5/issues/12); fall back to direct API calls for critical paths |
| 1M token context requires significant KV cache memory | OOM on long patient histories | Implement progressive context loading; fall back to chunked analysis |
| Thinking mode produces verbose reasoning chains | Storage bloat in audit logs | Compress thinking chains after 90-day retention; summarize for long-term archive |
| Alibaba Cloud model — geopolitical/supply chain risk | Model access restricted | Download and archive all weights offline under Apache 2.0; no cloud dependency |
| Model hallucination in clinical reasoning | Patient safety risk | All outputs labeled "AI-Suggested — Requires Physician Review"; thinking chains enable clinician verification |
| Dual-model (Qwen + Gemma) complexity | Operational overhead | Unified AI Gateway abstracts model selection; single monitoring dashboard |

## 10. Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| Qwen3.5-397B-A17B weights | Model | Downloaded from Hugging Face; FP8 or NVFP4 recommended |
| Qwen3.5-35B-A3B weights | Model | Consumer-friendly MoE model (24 GB Q4, fits RTX 4090) |
| Qwen3.5-27B weights | Model | Dense alternative (17 GB Q4) |
| Qwen3.5-9B weights | Model | Small Series flagship — 5 GB Q4, beats GPT-OSS-120B |
| Qwen3.5-4B weights | Model | Small Series — 2.5 GB Q4, edge/kiosk multimodal agent |
| Qwen3.5-2B weights | Model | Small Series — 1.3 GB Q4, mobile deployment |
| Qwen3.5-0.8B weights | Model | Small Series — 0.5 GB Q4, phone/IoT, CPU-viable |
| vLLM | Inference Runtime | Nightly/0.17.0+; Apache 2.0; `--enable-expert-parallel` for MoE |
| NVIDIA GPU (4-8x H100/H200 for 397B) | Hardware | Tensor + expert parallelism for flagship model |
| PMS Backend API | Internal | FastAPI endpoints for patients, encounters, prescriptions |
| AI Gateway (Experiment 13) | Internal | Existing OpenAI-compatible proxy — extended, not replaced |
| Redis | Cache | Response caching (shared with Gemma 3 setup) |
| Docker + Docker Compose | Infrastructure | Container orchestration |
| Gemma 3 integration (Experiment 13) | Internal | Complementary — Gemma handles multimodal clinical tasks |

## 11. Comparison with Existing Experiments

### vs. Experiment 13 — Gemma 3 (On-Premise Clinical AI) — COMPLEMENTARY

This is the primary comparison. Qwen 3.5 and Gemma 3 serve **different roles** in the on-premise AI stack:

| Dimension | Gemma 3 (Exp 13) | Qwen 3.5 (This PRD) |
|-----------|------------------|---------------------|
| **Primary Strength** | Multimodal clinical (text + image) | Complex reasoning + code generation |
| **Healthcare Variant** | MedGemma (87.7% MedQA) | None — general-purpose |
| **Context Window** | 128K tokens | 1M tokens |
| **Architecture** | Dense (27B) | MoE (397B total, 17B active) |
| **Coding Benchmark** | Good | Top-1% CodeForces (Elo 2056) |
| **Reasoning Benchmark** | Good | 91.3 AIME26, 88.4 GPQA Diamond |
| **Inference Backend** | Ollama | vLLM (MoE-optimized) |
| **License** | Google Gemma Terms | Apache 2.0 |
| **Best PMS Use** | Summarization, medical imaging, extraction | Differential diagnosis, rule generation, long-context |

**Deployment strategy:** Both models coexist behind the AI Gateway. Task-type routing sends clinical multimodal tasks to Gemma/MedGemma and reasoning/coding tasks to Qwen 3.5.

### vs. Experiment 08 — Adaptive Thinking (Claude API)
Adaptive Thinking routes between Claude effort levels for cloud-based reasoning. Qwen 3.5's thinking mode provides **similar effort-routing locally** — the AI Gateway can toggle thinking mode on/off based on task complexity, achieving the same cost optimization without cloud dependency.

### vs. Experiment 12 — AI Zero-Day Scan
AI Zero-Day Scan uses Claude for security analysis. Qwen 3.5's top-1% coding performance makes it a viable **on-premise replacement** for code security analysis, eliminating cloud API dependency for security scanning of PMS source code.

### vs. Experiment 15 — Claude Model Selection
Claude Model Selection optimizes cost across Claude model tiers. Qwen 3.5's expanded model family (4B/9B/27B/35B-A3B/122B-A10B/397B-A17B) provides an **even richer local tier structure** — the same routing logic applies with more granularity.

### vs. Experiment 09 — MCP (Model Context Protocol)
Qwen 3.5 now supports MCP via the [Qwen-Agent framework](https://qwenlm.github.io/Qwen-Agent/en/guide/core_moduls/mcp/) (`pip install -U "qwen-agent[mcp]"`). This means PMS MCP servers (Experiment 09) can be used with Qwen 3.5 as the model backend — providing on-premise, zero-PHI-egress tool discovery and invocation. Note: a [known issue](https://github.com/QwenLM/Qwen3.5/issues/12) with tool calling regression on longer multi-step requests is being tracked.

### vs. Experiment 27 — Claude Code / Experiment 28 — AI Coding Tools
The open-source [Qwen-Code](https://github.com/QwenLM/qwen-code) terminal agent provides a Claude Code-equivalent experience backed by Qwen models, with native MCP support. This is a key component of the emergency transition playbook documented in [Experiment 28](28-AI-Coding-Tools-Landscape-2026.md).

## 12. Research Sources

### Official Documentation
- [Qwen3.5 GitHub Repository](https://github.com/QwenLM/Qwen3.5) — Full model family, releases, deployment examples
- [Qwen3.5-397B-A17B on Hugging Face](https://huggingface.co/Qwen/Qwen3.5-397B-A17B) — Model card, 1.1M+ downloads, 28 community quantizations
- [Qwen3.5 Ollama Registry](https://ollama.com/library/qwen3.5) — 12 model tags including 27B, 35B, 122B, cloud variants
- [Qwen3.5 vLLM Usage Guide](https://docs.vllm.ai/projects/recipes/en/latest/Qwen/Qwen3.5.html) — vLLM nightly/0.17.0 deployment with expert parallelism, FP8/NVFP4
- [Qwen-Agent MCP Documentation](https://qwenlm.github.io/Qwen-Agent/en/guide/core_moduls/mcp/) — MCP server integration via Qwen-Agent framework
- [Qwen-Code Terminal Agent](https://github.com/QwenLM/qwen-code) — Open-source Claude Code alternative with MCP support

### Small Series
- [Qwen3.5-9B on Hugging Face](https://huggingface.co/Qwen/Qwen3.5-9B) — Small Series flagship, 1M+ downloads
- [Qwen3.5-4B on Hugging Face](https://huggingface.co/Qwen/Qwen3.5-4B) — Edge/kiosk multimodal agent
- [Qwen3.5-2B on Hugging Face](https://huggingface.co/Qwen/Qwen3.5-2B) — Mobile deployment
- [Qwen3.5-0.8B on Hugging Face](https://huggingface.co/Qwen/Qwen3.5-0.8B) — Phone/IoT, first sub-1B with video
- [VentureBeat — Qwen3.5-9B Beats GPT-OSS-120B](https://venturebeat.com/technology/alibabas-small-open-source-qwen3-5-9b-beats-openais-gpt-oss-120b-and-can-run) — 9B performance analysis
- [MarkTechPost — Qwen 3.5 Small Models for On-Device](https://www.marktechpost.com/2026/03/02/alibaba-just-released-qwen-3-5-small-models-a-family-of-0-8b-to-9b-parameters-built-for-on-device-applications/) — Edge deployment overview
- [Artificial Analysis — Qwen3.5 Small Models: Everything You Need to Know](https://artificialanalysis.ai/articles/qwen3-5-small-models) — Comprehensive benchmarks and analysis
- [Kaitchup — GPU Requirements, VRAM Usage & KV Cache Breakdown](https://kaitchup.substack.com/p/qwen35-9b-4b-2b-and-08b-gpu-requirements) — Detailed VRAM analysis for all small models

### Architecture & Benchmarks
- [Qwen 3.5 Complete Guide — Digital Applied](https://www.digitalapplied.com/blog/qwen-3-5-agentic-ai-benchmarks-guide) — 397B MoE benchmarks, pricing, agentic capabilities
- [Qwen 3.5 Medium Series — Digital Applied](https://www.digitalapplied.com/blog/qwen-3-5-medium-model-series-benchmarks-pricing-guide) — 27B/35B/122B benchmarks and pricing
- [Qwen 3.5 NVIDIA NIM Model Card](https://build.nvidia.com/qwen/qwen3.5-397b-a17b/modelcard) — Hardware requirements, NVIDIA deployment
- [VentureBeat — Qwen 3.5 Medium Models](https://venturebeat.com/technology/alibabas-new-open-source-qwen3-5-medium-models-offer-sonnet-4-5-performance) — Medium series achieves Sonnet-class performance
- [Best AI for Coding 2026 — Marc0.dev](https://www.marc0.dev/en/blog/best-ai-for-coding-2026-swe-bench-breakdown-opus-4-6-qwen3-coder-next-gpt-5-3-and-what-actually-matters-1770387434111) — SWE-bench breakdown across all models
- [AMD Day-0 Support for Qwen 3.5](https://www.amd.com/en/developer/resources/technical-articles/2026/day-0-support-for-qwen-3-5-on-amd-instinct-gpus.html) — MI300X/MI325X/MI35X verified

### Medical AI & Fine-Tuning
- [Qwen-3-32B-Medical-Reasoning — Hugging Face](https://huggingface.co/nicoboss/Qwen-3-32B-Medical-Reasoning) — Community medical reasoning fine-tune
- [Fine-Tuning Qwen3-8B for Medical Reasoning — E2E Networks](https://www.e2enetworks.com/blog/fine-tuning-qwen3-8b-medical-reasoning-qlora-e2e-networks-a100) — QLoRA medical fine-tune guide (<$3 training cost)
- [Qwen3-Medical-SFT GitHub](https://github.com/Zeyi-Lin/Qwen3-Medical-SFT) — R1-style medical chat fine-tune

### Coding Capabilities
- [Qwen3-Coder-Next Blog](https://qwen.ai/blog?id=qwen3-coder-next) — 80B-A3B dedicated coding model (70.6 SWE-bench)
- [Qwen Function Calling Documentation](https://qwen.readthedocs.io/en/latest/framework/function_call.html) — Tool use and function calling guide
- [Qwen Structured Output — Alibaba Cloud](https://www.alibabacloud.com/help/en/model-studio/qwen-structured-output) — JSON mode and schema enforcement

### Comparison
- [Gemma 3 vs Qwen 3 Comparison — CoderSera](https://codersera.com/blog/gemma-3-vs-qwen-3-in-depth-comparison-of-two-leading-open-source-llms) — Feature-by-feature comparison
- [Kimi 2.5 vs Qwen 3.5 vs DeepSeek R2 — Index.dev](https://www.index.dev/blog/kimi-2-5-vs-qwen-3-5-vs-deepseek-r2) — Frontier open-weight model comparison

## 13. Appendix: Related Documents

- [Qwen 3.5 Setup Guide for PMS Integration](20-Qwen35-PMS-Developer-Setup-Guide.md)
- [Qwen 3.5 Developer Onboarding Tutorial](20-Qwen35-Developer-Tutorial.md)
- [Gemma 3 PRD — Experiment 13](13-PRD-Gemma3-PMS-Integration.md)
- [Gemma 3 Setup Guide — Experiment 13](13-Gemma3-PMS-Developer-Setup-Guide.md)
- [Qwen3.5-397B-A17B on Hugging Face](https://huggingface.co/Qwen/Qwen3.5-397B-A17B)
- [Qwen3.5 GitHub Repository](https://github.com/QwenLM/Qwen3.5)
- [vLLM Documentation](https://docs.vllm.ai/)
- [Ollama Qwen 3.5 Registry](https://ollama.com/library/qwen3.5)
