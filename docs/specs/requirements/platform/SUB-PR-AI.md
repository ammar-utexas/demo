# Platform Requirements: Patient Records — AI Infrastructure (SUB-PR-AI)

**Parent:** [SUB-PR (Domain)](../domain/SUB-PR.md)
**Platform:** AI Infrastructure (AI) — 5 requirements

---

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
|---|---|---|---|---|---|
| SUB-PR-0009-AI | SUB-PR-0009 | Wound severity classification model (edge deployment) | — | TST-PR-0009-AI | Not Started |
| SUB-PR-0010-AI | SUB-PR-0010 | Face/ID verification embedding model (edge deployment) | — | TST-PR-0010-AI | Not Started |
| SUB-PR-0011-AI | SUB-PR-0011 | Document OCR model (edge deployment) | — | TST-PR-0011-AI | Not Started |
| SUB-PR-0013-AI | SUB-PR-0013 | EfficientNet-B4 classification model deployment via ONNX Runtime in `pms-derm-cds` Docker service. Model accepts 380x380 image tensor, outputs probability distribution across 9 ISIC diagnostic categories. | `services/derm-cds/classifier.py` | TST-PR-0013-AI | Not Started |
| SUB-PR-0014-AI | SUB-PR-0014 | Image embedding generation (512-dim float32 vector from penultimate CNN layer) and pgvector index management for ISIC reference cache (IVFFlat index, cosine distance) | `services/derm-cds/embedder.py`, `services/derm-cds/similarity.py` | TST-PR-0014-AI | Not Started |
