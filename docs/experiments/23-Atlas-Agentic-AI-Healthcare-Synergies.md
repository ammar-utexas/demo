# Atlas — Agentic AI in Healthcare: PMS Synergy Analysis

**Source:** Health Innovation Toolbox, *Atlas — Agentic AI in Healthcare: 50 Use Cases* (January 2026)
**Date:** 2026-02-24
**Author:** Extracted & mapped by Claude for Ammar Darkazanli

---

## Overview

The Atlas publication catalogs 50 agentic AI use cases across healthcare, organized into six categories. This document maps each Atlas agent against the PMS architecture, existing experiments (00–22), and subsystem requirements to identify high-value synergies and net-new opportunities.

**Atlas Categories (50 agents total):**
1. Clinical Agents (10)
2. Operational Agents (10)
3. Administrative & System Agents (10)
4. Patient-Facing Agents (10)
5. Payer & Insurance Agents (5)
6. Population Health & Analytics Agents (5)

**PMS Subsystems:** Patient Records (SUB-PR), Clinical Workflow (SUB-CW), Medication Management (SUB-MM), Reporting & Analytics (SUB-RA), Prompt Management (SUB-PM)

---

## Synergy Rating Key

| Rating | Meaning |
|--------|---------|
| **Direct** | Atlas agent maps 1:1 to an existing PMS experiment or subsystem requirement |
| **Extend** | Atlas agent extends an existing PMS capability with new scope |
| **New** | Atlas agent represents net-new functionality for the PMS |

---

## Category 1: Clinical Agents

### 1. Clinical Documentation Agent
- **Atlas:** Ambient listening during encounters, generating structured clinical notes (SOAP, H&P) with auto-coding
- **PMS Synergy:** **Direct** — Maps to Experiments 07 (MedASR), 10 (Speechmatics), 21 (Voxtral Transcribe 2)
- **Subsystems:** SUB-CW, SUB-PR
- **Gap:** PMS has speech-to-text but lacks the full agentic loop: listen → transcribe → structure → code → sign-off. The Atlas agent adds auto-ICD/CPT coding and clinician approval workflow
- **Opportunity:** Compose MedASR/Voxtral (transcription) + Gemma 3/Qwen 3.5 (structuring) + OpenClaw (approval workflow) into a single agentic clinical documentation pipeline

### 2. Diagnostic Decision Support Agent
- **Atlas:** Integrates patient data, lab results, imaging, and guidelines to suggest differential diagnoses and recommend next tests
- **PMS Synergy:** **Direct** — Maps to Experiment 18 (ISIC/DermaCheck) for dermatology; extends to general CDS
- **Subsystems:** SUB-CW, SUB-PR
- **Gap:** DermaCheck covers dermatology only. Atlas envisions a generalized diagnostic agent across all specialties
- **Opportunity:** Use the DermaCheck pattern (AI model + pgvector similarity + risk scoring) as a template for other specialties. Qwen 3.5 reasoning chains can power differential diagnosis beyond dermatology

### 3. Medication Reconciliation Agent
- **Atlas:** Compares medication lists across care settings, flags duplicates/interactions/omissions, suggests consolidated regimen
- **PMS Synergy:** **Direct** — Maps to SUB-MM (Medication Management), Experiment 11 (Sanford Guide), Experiment 13 (Gemma 3 medication pipeline)
- **Subsystems:** SUB-MM
- **Gap:** Sanford Guide covers antimicrobial CDS; Gemma 3 tutorial includes drug interaction checking. Atlas adds cross-setting reconciliation (hospital ↔ outpatient ↔ pharmacy)
- **Opportunity:** Extend SUB-MM with FHIR MedicationStatement import (Experiment 16) to pull external med lists, then use Qwen 3.5 reasoning for conflict detection

### 4. Care Coordination Agent
- **Atlas:** Orchestrates multi-provider care plans, tracks referrals, ensures follow-up compliance, escalates overdue actions
- **PMS Synergy:** **Extend** — Maps to SUB-CW (Clinical Workflow) + Experiment 05 (OpenClaw)
- **Subsystems:** SUB-CW
- **Gap:** OpenClaw has care coordination skills but SUB-CW is at 0% implementation. Atlas provides a comprehensive agent pattern for multi-provider orchestration
- **Opportunity:** Use OpenClaw's approval-tiered skill framework to build care coordination workflows with escalation rules. FHIR CarePlan resource (Experiment 16) provides interoperability

### 5. Clinical Trial Matching Agent
- **Atlas:** Screens patient records against trial eligibility criteria, notifies providers, assists enrollment
- **PMS Synergy:** **New**
- **Subsystems:** SUB-PR, SUB-RA
- **Gap:** PMS has no clinical trial functionality
- **Opportunity:** pgvector similarity search on patient records against trial criteria embeddings. Low priority for current PMS scope but high value for academic medical center deployment

### 6. Genomics Interpretation Agent
- **Atlas:** Interprets genomic panel results, maps variants to clinical significance, suggests targeted therapies
- **PMS Synergy:** **New**
- **Subsystems:** N/A (out of current scope)
- **Gap:** PMS has no genomics integration
- **Opportunity:** Defer — requires specialized data models and regulatory framework. Could leverage HL7 v2 LIS (Experiment 17) for lab result ingestion if genomic panels come via LIS

### 7. Radiology Assist Agent
- **Atlas:** Pre-reads imaging studies, flags anomalies, generates preliminary reports for radiologist review
- **PMS Synergy:** **Extend** — Builds on edge vision capabilities (Jetson Thor deployment, ADR-0007)
- **Subsystems:** SUB-CW
- **Gap:** Jetson Thor has vision inference but focused on wound assessment and document OCR, not radiology
- **Opportunity:** The ONNX Runtime + TensorRT inference pipeline from DermaCheck could support radiology models. DICOM integration would be needed

### 8. Pathology AI Agent
- **Atlas:** Analyzes digital pathology slides, identifies abnormal regions, provides quantitative measurements
- **PMS Synergy:** **Extend** — Similar architecture pattern to DermaCheck (Experiment 18)
- **Subsystems:** SUB-CW
- **Gap:** No digital pathology support currently
- **Opportunity:** Reuse the image classification + pgvector reference cache architecture from DermaCheck. Would need whole-slide imaging (WSI) viewer integration

### 9. Nursing Assessment Agent
- **Atlas:** Guides structured nursing assessments, auto-scores acuity scales, triggers care protocols
- **PMS Synergy:** **Extend** — Maps to SUB-CW encounter workflows
- **Subsystems:** SUB-CW
- **Gap:** PMS encounters are physician-centric. Atlas adds nursing-specific assessment workflows
- **Opportunity:** Add nursing assessment templates to SUB-CW with auto-scoring via Gemma 3. OpenClaw can trigger protocol-based actions on critical scores

### 10. Behavioral Health Screening Agent
- **Atlas:** Administers standardized screening instruments (PHQ-9, GAD-7, AUDIT), scores responses, flags severity
- **PMS Synergy:** **Extend** — Maps to SUB-CW intake workflows
- **Subsystems:** SUB-CW, SUB-PR
- **Gap:** No behavioral health screening in PMS
- **Opportunity:** Low-lift integration — questionnaire-based with auto-scoring. Can run on Android (SUB-AND) for patient self-administration. Aligns with patient-facing chatbot idea from Experiment 22

---

## Category 2: Operational Agents

### 11. Scheduling Optimization Agent
- **Atlas:** Manages appointment booking, cancellation prediction, double-booking resolution, provider workload balancing
- **PMS Synergy:** **New** — Aligns with Experiment 22 (appointment scheduling assistant idea)
- **Subsystems:** New (operational scope)
- **Gap:** PMS has no scheduling module
- **Opportunity:** If scheduling is added to PMS, the Atlas agent pattern provides a comprehensive design. OpenClaw could handle the agentic scheduling workflow

### 12. Revenue Cycle Management Agent
- **Atlas:** Automates charge capture, claim scrubbing, denial management, and follow-up
- **PMS Synergy:** **New**
- **Subsystems:** New (billing scope)
- **Gap:** PMS has no billing/revenue cycle module
- **Opportunity:** Defer — significant domain complexity. Would benefit from FHIR Claim resources if built

### 13. Supply Chain & Inventory Agent
- **Atlas:** Forecasts supply needs, automates reorder triggers, tracks expiration dates, optimizes par levels
- **PMS Synergy:** **New**
- **Subsystems:** N/A (out of scope)
- **Opportunity:** Defer — operational scope beyond clinical PMS

### 14. Staff Rostering & Credentialing Agent
- **Atlas:** Optimizes shift scheduling, tracks credential expirations, ensures compliance with staffing ratios
- **PMS Synergy:** **New**
- **Subsystems:** N/A (out of scope)
- **Opportunity:** Defer — HR/workforce management scope

### 15. Bed Management Agent
- **Atlas:** Real-time bed availability, discharge prediction, patient flow optimization
- **PMS Synergy:** **New**
- **Subsystems:** N/A (out of scope)
- **Opportunity:** Defer — inpatient facility management scope

### 16. Quality Metrics Agent
- **Atlas:** Continuously monitors clinical quality measures (HEDIS, CMS Stars), identifies gaps, triggers interventions
- **PMS Synergy:** **Extend** — Maps to SUB-RA (Reporting & Analytics)
- **Subsystems:** SUB-RA
- **Gap:** SUB-RA is at 0% implementation. Atlas provides a quality metrics monitoring pattern
- **Opportunity:** Tambo conversational analytics (Experiment 00) + Qwen 3.5 reasoning for quality measure gap detection. FHIR MeasureReport resources for interoperability

### 17. Environmental Monitoring Agent
- **Atlas:** Tracks infection control metrics, air quality, equipment sterilization compliance
- **PMS Synergy:** **New**
- **Subsystems:** N/A (out of scope)
- **Opportunity:** Defer — IoT/facility management scope

### 18. Transport & Logistics Agent
- **Atlas:** Coordinates patient transport, specimen delivery, equipment movement
- **PMS Synergy:** **New**
- **Subsystems:** N/A (out of scope)
- **Opportunity:** Defer — hospital logistics scope

### 19. Emergency Preparedness Agent
- **Atlas:** Monitors surge capacity, activates disaster protocols, manages resource allocation during crises
- **PMS Synergy:** **New**
- **Subsystems:** N/A (out of scope)
- **Opportunity:** Defer — emergency management scope

### 20. Pharmacy Coordination Agent
- **Atlas:** Manages formulary checks, therapeutic substitutions, compounding queues, refill authorization
- **PMS Synergy:** **Direct** — Maps to SUB-MM + Experiment 11 (Sanford Guide)
- **Subsystems:** SUB-MM
- **Gap:** Sanford Guide covers antimicrobial recommendations. Atlas adds pharmacy workflow automation (formulary, substitution, refill)
- **Opportunity:** Extend SUB-MM with OpenClaw-powered pharmacy workflow skills: formulary check → therapeutic substitution recommendation → provider approval → dispense

---

## Category 3: Administrative & System Agents

### 21. Prior Authorization Agent
- **Atlas:** Automates PA submissions, checks medical necessity criteria, tracks approvals/denials, handles appeals
- **PMS Synergy:** **Direct** — Maps to Experiment 05 (OpenClaw) which explicitly includes prior auth as a use case
- **Subsystems:** SUB-CW
- **Gap:** OpenClaw PRD includes prior auth workflow but it is not yet implemented
- **Opportunity:** Highest-value administrative automation. OpenClaw skill + FHIR CoverageEligibilityRequest. Claude model selection (Experiment 15) for cost-optimal PA document analysis

### 22. Medical Coding Agent
- **Atlas:** Auto-assigns ICD-10/CPT codes from clinical documentation, flags coding discrepancies, ensures compliance
- **PMS Synergy:** **Extend** — Complements Clinical Documentation Agent (#1)
- **Subsystems:** SUB-CW
- **Gap:** PMS has no coding module
- **Opportunity:** Qwen 3.5 reasoning for code assignment from structured notes. Can chain after speech-to-text → SOAP note → auto-coding pipeline

### 23. Compliance Monitoring Agent
- **Atlas:** Continuously audits for regulatory compliance (HIPAA, Joint Commission), flags violations, generates remediation tasks
- **PMS Synergy:** **Extend** — Maps to Experiment 12 (AI Zero-Day Scan) + quality management system
- **Subsystems:** Cross-cutting
- **Gap:** AI Zero-Day Scan covers code security. Atlas adds operational compliance monitoring (access patterns, documentation completeness, consent tracking)
- **Opportunity:** Extend audit logging infrastructure to detect HIPAA access anomalies. OpenClaw can trigger CAPA workflows on compliance findings

### 24. Patient Identity Resolution Agent
- **Atlas:** Deduplicates patient records, resolves identity conflicts across systems, maintains master patient index
- **PMS Synergy:** **Extend** — Maps to SUB-PR + FHIR Patient resource (Experiment 16)
- **Subsystems:** SUB-PR
- **Gap:** PMS has single-system patient records. Atlas adds cross-system identity resolution
- **Opportunity:** pgvector embeddings on patient demographics for fuzzy matching. FHIR Patient resource provides the interoperability layer for cross-system matching

### 25. Interoperability Bridge Agent
- **Atlas:** Translates between healthcare data standards (HL7v2, FHIR, CDA), validates data quality, handles format conversions
- **PMS Synergy:** **Direct** — Maps to Experiments 16 (FHIR) + 17 (HL7v2 LIS)
- **Subsystems:** Cross-cutting
- **Gap:** FHIR and HL7v2 are implemented separately. Atlas envisions a unified translation agent
- **Opportunity:** Build an agentic wrapper using OpenClaw that routes incoming messages to the correct parser (FHIR Facade vs. HL7v2 MLLP listener) and handles bidirectional translation

### 26. Report Generation Agent
- **Atlas:** Auto-generates clinical and operational reports from structured data, supports natural language queries
- **PMS Synergy:** **Direct** — Maps to SUB-RA + Experiment 00 (Tambo conversational analytics)
- **Subsystems:** SUB-RA
- **Gap:** Tambo provides conversational analytics UI. Atlas adds automated scheduled report generation
- **Opportunity:** Tambo for interactive queries + scheduled report generation via Gemma 3/Qwen 3.5 for batch analytics. MCP server (Experiment 09) exposes reporting endpoints

### 27. Consent Management Agent
- **Atlas:** Tracks patient consent across studies, treatments, and data sharing; enforces consent-based access controls
- **PMS Synergy:** **Extend** — Maps to SUB-PR patient records
- **Subsystems:** SUB-PR
- **Gap:** PMS has basic consent tracking. Atlas adds granular consent management with enforcement
- **Opportunity:** FHIR Consent resource for interoperable consent records. Access control enforcement at API layer

### 28. Document Processing Agent
- **Atlas:** OCR + NLP extraction from scanned documents, insurance cards, referral letters, lab faxes
- **PMS Synergy:** **Direct** — Maps to Jetson Thor edge vision capabilities (document OCR) + patient ID verification
- **Subsystems:** SUB-PR
- **Gap:** Jetson has document OCR for edge deployment. Atlas adds broader document processing (insurance cards, referrals, faxes)
- **Opportunity:** Extend edge vision pipeline to process insurance cards and referral documents. Gemma 3 multimodal can extract structured data from scanned documents

### 29. Audit Trail Agent
- **Atlas:** Maintains tamper-proof audit logs, detects suspicious access patterns, generates compliance reports
- **PMS Synergy:** **Extend** — Builds on existing HIPAA audit logging infrastructure
- **Subsystems:** Cross-cutting
- **Gap:** PMS has audit logging but lacks intelligent anomaly detection on access patterns
- **Opportunity:** Use pgvector to embed access patterns and detect anomalies. Complements AI Zero-Day Scan (Experiment 12) with runtime access monitoring

### 30. System Health Monitor Agent
- **Atlas:** Monitors application performance, predicts failures, auto-scales resources, manages alerts
- **PMS Synergy:** **Extend** — Maps to DevOps/infrastructure
- **Subsystems:** Cross-cutting
- **Gap:** PMS has CI/CD (GitHub Actions) but no intelligent health monitoring
- **Opportunity:** Low priority for PMS scope. Standard observability tools (Prometheus, Grafana) cover most needs

---

## Category 4: Patient-Facing Agents

### 31. Symptom Checker / Triage Agent
- **Atlas:** Patient-facing conversational symptom assessment with severity scoring and routing recommendations
- **PMS Synergy:** **Direct** — Maps to Experiment 22 (symptom triage chatbot idea)
- **Subsystems:** New (patient-facing)
- **Gap:** Identified as an idea in Experiment 22 but not yet designed
- **Opportunity:** Build using Tambo conversational UI (Experiment 00) + Qwen 3.5 medical reasoning. OpenClaw escalation workflow for urgent cases. Android app delivery via SUB-AND

### 32. Patient Education Agent
- **Atlas:** Generates personalized health education materials at appropriate literacy levels, tracks comprehension
- **PMS Synergy:** **Extend** — Maps to Experiment 22 (patient-facing simplified summaries idea)
- **Subsystems:** SUB-PR (patient-facing)
- **Gap:** Experiment 22 proposes plain-language summaries. Atlas adds personalized education with comprehension tracking
- **Opportunity:** Gemma 3 for content generation at adjustable reading levels. Can integrate with after-visit summary workflow in SUB-CW

### 33. Appointment Management Agent
- **Atlas:** Patient self-service scheduling, rescheduling, cancellation with intelligent slot suggestions
- **PMS Synergy:** **Direct** — Maps to Experiment 22 (appointment scheduling assistant idea)
- **Subsystems:** New (patient-facing)
- **Opportunity:** Conversational scheduling via Tambo UI on web + Android. Complements Scheduling Optimization Agent (#11)

### 34. Medication Adherence Agent
- **Atlas:** Personalized medication reminders, refill tracking, side-effect monitoring, adherence scoring
- **PMS Synergy:** **Extend** — Maps to SUB-MM
- **Subsystems:** SUB-MM, SUB-AND (mobile delivery)
- **Gap:** SUB-MM covers medication management from provider side. Atlas adds patient-facing adherence support
- **Opportunity:** Android push notifications for medication reminders. Side-effect reporting flows back to SUB-MM for provider review

### 35. Chronic Disease Management Agent
- **Atlas:** Personalized care plans for chronic conditions, tracks vitals/symptoms, adjusts recommendations, alerts on deterioration
- **PMS Synergy:** **Extend** — Builds on SUB-CW + SUB-PR longitudinal data
- **Subsystems:** SUB-CW, SUB-PR, SUB-AND
- **Gap:** PMS has encounter-based workflow. Atlas adds continuous chronic disease monitoring between encounters
- **Opportunity:** Android app for patient self-reporting + pgvector trajectory analysis for deterioration detection (aligns with Experiment 22 "early deterioration detection" idea)

### 36. Mental Health Support Agent
- **Atlas:** Guided CBT exercises, mood tracking, crisis detection with escalation to human providers
- **PMS Synergy:** **Extend** — Complements Behavioral Health Screening Agent (#10)
- **Subsystems:** New (patient-facing)
- **Gap:** No mental health support features in PMS
- **Opportunity:** Android app delivery for mood tracking. Crisis detection requires careful safety design — escalation via OpenClaw to on-call provider

### 37. Health Literacy Agent
- **Atlas:** Translates medical jargon, explains lab results in plain language, provides visual aids
- **PMS Synergy:** **Extend** — Maps to patient-facing simplified summaries (Experiment 22)
- **Subsystems:** SUB-PR (patient-facing)
- **Opportunity:** Gemma 3 multimodal for generating visual explanations. Lab result interpretation via HL7v2 LIS data (Experiment 17)

### 38. Caregiver Coordination Agent
- **Atlas:** Keeps family/caregivers informed, manages shared care responsibilities, tracks delegated tasks
- **PMS Synergy:** **New**
- **Subsystems:** New (patient-facing)
- **Opportunity:** Defer — requires caregiver roles/permissions model. Could build on FHIR RelatedPerson resource

### 39. Post-Discharge Follow-Up Agent
- **Atlas:** Automated check-ins after discharge, monitors recovery, flags complications, schedules follow-ups
- **PMS Synergy:** **Extend** — Maps to SUB-CW + patient-facing channels
- **Subsystems:** SUB-CW, SUB-AND
- **Gap:** PMS has no post-discharge workflow
- **Opportunity:** OpenClaw-orchestrated follow-up sequence: discharge → scheduled check-ins via Android app → symptom assessment → escalation if needed. High value for readmission reduction

### 40. Accessibility Agent
- **Atlas:** Adapts interfaces for visual/hearing/cognitive impairments, provides multilingual support, ensures ADA compliance
- **PMS Synergy:** **Extend** — Cross-cutting accessibility across SUB-WEB and SUB-AND
- **Subsystems:** Cross-cutting
- **Opportunity:** Voxtral/Speechmatics for voice-driven navigation. Gemma 3 for real-time translation. Important for equitable care

---

## Category 5: Payer & Insurance Agents

### 41. Claims Processing Agent
- **Atlas:** Auto-adjudicates claims, detects billing errors, ensures coding compliance
- **PMS Synergy:** **New** (payer-side)
- **Opportunity:** Defer — payer-side functionality. PMS could generate clean claims via Medical Coding Agent (#22) to reduce denials

### 42. Benefits Verification Agent
- **Atlas:** Real-time eligibility checks, coverage details, out-of-pocket estimates
- **PMS Synergy:** **Extend** — Complements Prior Authorization Agent (#21)
- **Subsystems:** SUB-CW
- **Opportunity:** FHIR CoverageEligibilityRequest/Response (Experiment 16). Can run pre-visit to inform patients of costs

### 43. Fraud Detection Agent
- **Atlas:** Pattern analysis on claims data to detect billing fraud, abuse, and waste
- **PMS Synergy:** **New** (payer-side)
- **Opportunity:** Defer — payer-side analytics

### 44. Member Engagement Agent
- **Atlas:** Proactive member outreach for preventive care, wellness programs, care gap closure
- **PMS Synergy:** **Extend** — Overlaps with Chronic Disease Management (#35) and Quality Metrics (#16)
- **Subsystems:** SUB-RA
- **Opportunity:** Population health outreach using reporting analytics. Low priority for initial PMS scope

### 45. Utilization Review Agent
- **Atlas:** Reviews service utilization against clinical guidelines, flags over/under-utilization
- **PMS Synergy:** **New** (payer-side)
- **Opportunity:** Defer — payer-side review process

---

## Category 6: Population Health & Analytics Agents

### 46. Population Risk Stratification Agent
- **Atlas:** Analyzes population-level data to identify high-risk cohorts, predict disease trends, allocate resources
- **PMS Synergy:** **Extend** — Maps to SUB-RA
- **Subsystems:** SUB-RA
- **Opportunity:** pgvector patient embeddings + Tambo analytics for population-level dashboards. Qwen 3.5 reasoning for risk model interpretation

### 47. Social Determinants of Health (SDOH) Agent
- **Atlas:** Collects and analyzes SDOH data, connects patients with community resources, tracks social risk factors
- **PMS Synergy:** **Extend** — Maps to SUB-PR patient demographics
- **Subsystems:** SUB-PR
- **Opportunity:** FHIR Observation resources for SDOH screening data. Important for health equity

### 48. Epidemiological Surveillance Agent
- **Atlas:** Real-time disease surveillance, outbreak detection, reporting to public health authorities
- **PMS Synergy:** **New**
- **Subsystems:** SUB-RA
- **Opportunity:** Defer — public health scope. Could contribute anonymized aggregate data via FHIR bulk export

### 49. Research Data Agent
- **Atlas:** Identifies research-eligible patients, facilitates data extraction for studies, ensures IRB compliance
- **PMS Synergy:** **Extend** — Complements Clinical Trial Matching Agent (#5)
- **Subsystems:** SUB-RA, SUB-PR
- **Opportunity:** Academic medical center use case. pgvector similarity search on de-identified records

### 50. Predictive Analytics Agent
- **Atlas:** ML-driven predictions for readmission, no-shows, length of stay, resource utilization
- **PMS Synergy:** **Extend** — Maps to SUB-RA
- **Subsystems:** SUB-RA
- **Opportunity:** Tambo conversational analytics for prediction exploration. Qwen 3.5 for interpretable predictions

---

## Priority Synergy Matrix

The table below ranks Atlas agents by implementation priority based on: (1) alignment with existing PMS infrastructure, (2) clinical value, and (3) implementation complexity.

### Tier 1 — High Priority (Direct alignment, high value, existing infrastructure)

| # | Atlas Agent | PMS Experiments Leveraged | Target Subsystem | Key Action |
|---|-------------|--------------------------|------------------|------------|
| 1 | Clinical Documentation Agent | 07, 10, 21, 13, 20, 05 | SUB-CW | Compose transcription + structuring + coding into agentic pipeline |
| 21 | Prior Authorization Agent | 05 (OpenClaw), 16 (FHIR), 15 (Model Selection) | SUB-CW | Implement OpenClaw PA skill with FHIR eligibility check |
| 3 | Medication Reconciliation Agent | 11 (Sanford), 13 (Gemma 3), 16 (FHIR) | SUB-MM | Cross-setting med reconciliation with FHIR MedicationStatement |
| 2 | Diagnostic Decision Support Agent | 18 (DermaCheck), 20 (Qwen 3.5) | SUB-CW | Generalize DermaCheck pattern to multi-specialty CDS |
| 25 | Interoperability Bridge Agent | 16 (FHIR), 17 (HL7v2) | Cross-cutting | Unified agentic translation layer across standards |

### Tier 2 — Medium Priority (Extends existing capabilities)

| # | Atlas Agent | PMS Experiments Leveraged | Target Subsystem | Key Action |
|---|-------------|--------------------------|------------------|------------|
| 4 | Care Coordination Agent | 05 (OpenClaw), 16 (FHIR) | SUB-CW | OpenClaw multi-provider orchestration skills |
| 20 | Pharmacy Coordination Agent | 11 (Sanford), 13 (Gemma 3) | SUB-MM | Formulary check + substitution workflow |
| 22 | Medical Coding Agent | 13 (Gemma 3), 20 (Qwen 3.5) | SUB-CW | Auto-ICD/CPT from structured notes |
| 26 | Report Generation Agent | 00 (Tambo), 13 (Gemma 3) | SUB-RA | Scheduled + conversational reporting |
| 31 | Symptom Checker / Triage Agent | 00 (Tambo), 20 (Qwen 3.5) | Patient-facing | Conversational symptom assessment |
| 39 | Post-Discharge Follow-Up Agent | 05 (OpenClaw) | SUB-CW | Automated recovery check-in sequences |
| 10 | Behavioral Health Screening Agent | — | SUB-CW | Questionnaire-based screening with auto-scoring |
| 23 | Compliance Monitoring Agent | 12 (AI Zero-Day Scan) | Cross-cutting | Runtime access anomaly detection |

### Tier 3 — Lower Priority (New scope or deferred)

| # | Atlas Agent | Reason for Deferral |
|---|-------------|-------------------|
| 5 | Clinical Trial Matching | Out of current scope; academic deployment use case |
| 6 | Genomics Interpretation | Requires specialized data models |
| 7 | Radiology Assist | Needs DICOM integration |
| 8 | Pathology AI | Needs WSI viewer integration |
| 11 | Scheduling Optimization | No scheduling module in PMS yet |
| 12 | Revenue Cycle Management | Billing scope beyond clinical PMS |
| 13-15, 17-19 | Operational (Supply, Staff, Bed, Environment, Transport, Emergency) | Facility management scope |
| 41, 43, 45 | Payer-side (Claims, Fraud, Utilization) | Payer-side functionality |
| 48 | Epidemiological Surveillance | Public health scope |

---

## New Agentic Ideas for PMS (Inspired by Atlas Patterns)

Based on Atlas agent patterns applied to PMS-specific context:

### Idea A: Agentic Encounter Pipeline
**Compose:** MedASR/Voxtral → Gemma 3 SOAP structuring → Qwen 3.5 ICD coding → OpenClaw approval workflow
**Value:** End-to-end encounter documentation without manual data entry
**Subsystems:** SUB-CW, SUB-PR, SUB-MM

### Idea B: Cross-Standard Interoperability Agent
**Compose:** FHIR Facade + HL7v2 MLLP + OpenClaw routing
**Value:** Unified agent that auto-detects incoming message format and routes to the correct parser/builder
**Subsystems:** Cross-cutting

### Idea C: Patient-Facing Health Companion (Android)
**Compose:** Tambo conversational UI + Qwen 3.5 symptom reasoning + medication reminders + OpenClaw escalation
**Value:** Single patient app experience covering triage, education, adherence, and post-discharge follow-up
**Subsystems:** SUB-AND, patient-facing

### Idea D: Population Health Dashboard Agent
**Compose:** Tambo analytics + pgvector patient embeddings + Qwen 3.5 risk stratification
**Value:** Conversational exploration of population-level trends with predictive insights
**Subsystems:** SUB-RA

### Idea E: Regulatory Compliance Agent
**Compose:** AI Zero-Day Scan (code) + audit log anomaly detection (runtime) + OpenClaw CAPA workflow
**Value:** Continuous compliance assurance spanning code security and operational access patterns
**Subsystems:** Cross-cutting

---

## Implementation Approach

For Tier 1 agents, the recommended approach leverages the existing experiment infrastructure:

1. **OpenClaw (Experiment 05)** serves as the agentic orchestration layer — each Atlas agent maps to one or more OpenClaw skills with approval tiers
2. **MCP Server (Experiment 09)** exposes PMS APIs as discoverable tools for agent consumption
3. **Claude Model Selection (Experiment 15)** routes agent subtasks to cost-optimal models (Haiku for extraction, Sonnet for summarization, Opus for complex reasoning)
4. **Gemma 3 / Qwen 3.5 (Experiments 13, 20)** handle on-premise inference for PHI-sensitive operations
5. **FHIR / HL7v2 (Experiments 16, 17)** provide interoperability for cross-system agent workflows

This architecture means most Atlas agents can be implemented as **new OpenClaw skills** rather than standalone services, reducing infrastructure complexity while maintaining the agentic autonomy patterns described in the Atlas publication.

---

## References

- Health Innovation Toolbox. *Atlas — Agentic AI in Healthcare: 50 Use Cases.* January 2026.
- PMS Experiments 00–22: See [docs/index.md](../index.md) for full experiment listing.
- PMS Requirements: [SYS-REQ](../specs/requirements/SYS-REQ.md), [SUB-PR](../specs/requirements/domain/SUB-PR.md), [SUB-CW](../specs/requirements/domain/SUB-CW.md), [SUB-MM](../specs/requirements/domain/SUB-MM.md), [SUB-RA](../specs/requirements/domain/SUB-RA.md), [SUB-PM](../specs/requirements/domain/SUB-PM.md).
