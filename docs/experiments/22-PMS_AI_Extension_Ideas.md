# PMS Project — AI Extension Ideas
**Source:** IHI Lucian Leape Institute, *Patient Safety and Artificial Intelligence: Opportunities and Challenges for Care Delivery* (2024)  
**Date:** 2026-02-23  
**Author:** Extracted & mapped by Claude for Ammar Darkazanli  

---

## Overview

The IHI report validates and extends several AI directions already present in the PMS architecture. The ideas below are mapped to existing subsystems where applicable, and flagged as new where they represent net-new scope.

---

## 1. Clinical Decision Support

*Aligns with DermaCheck architecture (SUB-PR), encounter workflow (SUB-CW), and medication management (SUB-MM)*

| Idea | Description | Relevant Subsystem |
|---|---|---|
| **Confidence scoring on AI outputs** | Color-coded indicators showing model certainty on each recommendation or classification result | SUB-PR (DermaCheck) |
| **Differential diagnosis suggestions** | Extend CDS concept beyond dermatology to general clinical reasoning at point of encounter | SUB-CW |
| **Comorbidity-aware drug interaction scoring** | Elevate existing interaction checker stub to factor in patient-specific conditions (e.g., renal failure + drug dosing) | SUB-MM |
| **Early deterioration detection** | Use longitudinal encounter data + pgvector to detect worsening patient trajectories before acute events | SUB-PR, SUB-CW |

---

## 2. Documentation & Ambient Intelligence

*Aligns with encounter workflow (SUB-CW) and patient records (SUB-PR)*

| Idea | Description | Relevant Subsystem |
|---|---|---|
| **AI-generated clinical note drafts** | Auto-draft SOAP notes from encounter data; clinician reviews and approves | SUB-CW |
| **Automated chart summarization** | Surface patient history, meds, and recent encounters as a digest at encounter start | SUB-PR, SUB-CW |
| **Medication reconciliation discrepancy detection** | Flag conflicts between prescribed, dispensed, and active medications | SUB-MM |
| **Patient-facing simplified summaries** | Plain-language record summaries with adjustable reading level for patient portal | SUB-PR (new: patient-facing) |

---

## 3. Patient-Facing Features

*New scope — web and Android surfaces*

| Idea | Description | Relevant Subsystem |
|---|---|---|
| **Symptom triage chatbot** | Patient-initiated symptom intake with guided questioning before or between encounters | New (SUB-CW adjacent) |
| **Escalation pathway logic** | Chatbot that intelligently routes to clinician vs. self-care guidance based on symptom severity | New |
| **Appointment scheduling assistant** | Conversational scheduling with basic pre-visit intake collection | New |

---

## 4. Safety & Audit Intelligence

*Aligns with Reporting & Analytics (SUB-RA) — currently 0% implemented*

| Idea | Description | Relevant Subsystem |
|---|---|---|
| **Proactive adverse event signal detection** | Continuously scan EHR data for safety signals rather than relying on manual incident reports | SUB-RA |
| **Real-time audit anomaly flagging** | Detect unusual access patterns, medication deviations, or documentation gaps | SUB-RA, existing audit middleware |
| **Root cause analysis assist** | GenAI-summarized incident clusters with contributing factor identification | SUB-RA |
| **Clinician override tracking** | Monitor when clinicians reject AI suggestions; surface patterns to QA dashboard | SUB-RA, SUB-PM |

---

## 5. Prompt Management & Governance

*Aligns with SUB-PM — currently 0% implemented; report directly validates this subsystem as a patient safety requirement*

| Idea | Description | Relevant Subsystem |
|---|---|---|
| **Centralized prompt versioning** | Full CRUD + version history for every clinical prompt in the system | SUB-PM |
| **Prompt A/B testing** | Compare clinical outputs across prompt variants with outcome tracking | SUB-PM |
| **Audit trail of prompt → output** | Log which prompt version produced which clinical recommendation, with timestamp and user | SUB-PM |
| **LLM-powered prompt comparison** | Use an LLM to explain semantic differences between prompt versions (already in scope per overview) | SUB-PM |

---

## 6. AI Explainability & Compliance

*Cross-cutting — strengthens HIPAA audit trail and supports SYS-REQ-0003*

| Idea | Description | Relevant Subsystem |
|---|---|---|
| **AI explainability module** | Every AI recommendation logged with rationale, model version, confidence score, and source data | SUB-PR, SUB-PM, audit middleware |
| **Patient consent tracking for AI features** | Per-patient opt-in/opt-out for AI-assisted features, stored and auditable | SUB-PR, auth/RBAC |
| **Clinician feedback loop** | Thumbs up/down on AI suggestions fed into model performance monitoring | SUB-PM, SUB-RA |
| **Deskilling mitigation prompts** | Periodic encounters that bypass AI output to test clinician independent judgment | New (governance layer) |

---

## 7. Bias & Equity Monitoring

*New scope — aligns with compliance roadmap and HIPAA equity considerations*

| Idea | Description | Relevant Subsystem |
|---|---|---|
| **Demographic disaggregation of model outputs** | Track DermaCheck classifier performance across skin tones, ages, gender | SUB-PR, SUB-RA |
| **Dataset representation auditing** | Audit ISIC reference cache for demographic coverage gaps before and after cache population | SUB-PR (DermaCheck pipeline) |

---

## Priority Recommendations

Based on current PMS architecture and implementation status, the highest-leverage extensions are:

1. **Confidence scoring on DermaCheck outputs** — low effort given existing pipeline architecture (ADR-0022), high patient safety value
2. **AI clinical note drafting in SUB-CW** — encounter workflow is the most natural home; reduces clinician burden immediately
3. **Proactive safety signal detection in SUB-RA** — transforms reporting from reactive to proactive; report frames this as the future of patient safety
4. **Complete SUB-PM with governance hooks** — the IHI report makes the case that prompt governance is a patient safety requirement; this subsystem being at 0% is a gap worth closing before scaling AI features
5. **Clinician feedback loop on AI suggestions** — lightweight to implement, critical for monitoring model drift and building clinician trust over time

---

*Source document: IHI Lucian Leape Institute. Patient Safety and Artificial Intelligence: Opportunities and Challenges for Care Delivery. Boston: IHI; 2024. Available at ihi.org*
