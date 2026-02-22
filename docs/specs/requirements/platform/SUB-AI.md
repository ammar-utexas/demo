# Platform Requirements: AI Infrastructure (SUB-AI)

**Version:** 1.0
**Date:** 2026-02-21
**Platform:** AI Infrastructure (AI) — 7 requirements across 2 domains
**Repository:** pms-derm-cds
**Technology:** Python, ONNX Runtime, TensorRT (Jetson), TFLite (Android), pgvector, EfficientNet-B4, MobileNetV3

---

## Summary

| Domain | Req Count | Status Breakdown |
|--------|-----------|-----------------|
| Patient Records (PR) | 6 | 6 Not Started |
| Prompt Management (PM) | 1 | 1 Not Started |
| **Total** | **7** | |

---

## Patient Records (SUB-PR)

**Parent:** [SUB-PR (Domain)](../domain/SUB-PR.md)

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-PR-0009-AI | SUB-PR-0009 | Wound severity classification model (edge deployment) | — | TST-PR-0009-AI | Not Started |
| SUB-PR-0010-AI | SUB-PR-0010 | Face/ID verification embedding model (edge deployment) | — | TST-PR-0010-AI | Not Started |
| SUB-PR-0011-AI | SUB-PR-0011 | Document OCR model (edge deployment) | — | TST-PR-0011-AI | Not Started |
| SUB-PR-0013-AI | SUB-PR-0013 | EfficientNet-B4 classification model deployment via ONNX Runtime in `pms-derm-cds` Docker service. Model accepts 380x380 image tensor, outputs probability distribution across 9 ISIC diagnostic categories. Must maintain a model compatibility matrix in `model-manifest.json` (ADR-0013): server EfficientNet-B4 and mobile MobileNetV3 must be trained on the same ISIC dataset version and validated to produce concordant top-1 predictions on a reference test set (target: ≥90% agreement rate). When server classification differs from on-device result, the API response must include a `classification_changed` flag (PC-AI-01). | `services/derm-cds/classifier.py`, `services/derm-cds/model-manifest.json` | TST-PR-0013-AI | Not Started |
| SUB-PR-0014-AI | SUB-PR-0014 | Image embedding generation (512-dim float32 vector from penultimate CNN layer) and pgvector index management for ISIC reference cache (IVFFlat index, cosine distance) | `services/derm-cds/embedder.py`, `services/derm-cds/similarity.py` | TST-PR-0014-AI | Not Started |
| SUB-PR-0017-AI | SUB-PR-0017 | DermaCheck parallel fan-out orchestration inside the CDS service (`POST /classify`). EfficientNet-B4 classification runs first, producing probabilities and a 512-dim embedding. Then `asyncio.gather()` runs three concurrent stages: (1) Gemma 3 clinical narrative via AI Gateway (:8001), (2) pgvector similarity search using the embedding, (3) risk score calculation from probabilities and patient history. Per-stage timeouts: Gemma 3 = 5s, similarity = 2s, risk = 1s. Assemble results into atomic `DermaCheckResult` payload. If a non-critical stage fails or times out, set its field to null and `degraded = true`. EfficientNet-B4 failure returns HTTP 500 (hard-fail). | `services/derm-cds/orchestrator.py`, `services/derm-cds/classifier.py`, `services/derm-cds/similarity.py`, `services/derm-cds/risk_scorer.py` | TST-PR-0017-AI | Not Started |

---

## Prompt Management (SUB-PM)

**Parent:** [SUB-PM (Domain)](../domain/SUB-PM.md)

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-PM-0007-AI | SUB-PM-0007 | Anthropic Claude API integration for prompt version comparison. Uses `claude-sonnet-4-20250514` model. Prompt text is NOT PHI — external API calls are acceptable. The comparison template is itself a managed prompt bootstrapped via migration. | `services/llm_service.py` | TST-PM-0007-AI | Not Started |
