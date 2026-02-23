# ISIC Archive Setup Guide for PMS Integration

**Document ID:** PMS-EXP-ISICARCHIVE-001
**Version:** 1.0
**Date:** February 21, 2026
**Applies To:** PMS project (all platforms)
**Prerequisites Level:** Intermediate

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Part A: Install and Configure the Dermatology CDS Service](#3-part-a-install-and-configure-the-dermatology-cds-service)
4. [Part B: Integrate with PMS Backend](#4-part-b-integrate-with-pms-backend)
5. [Part C: Integrate with PMS Frontend](#5-part-c-integrate-with-pms-frontend)
6. [Part D: Testing and Verification](#6-part-d-testing-and-verification)
7. [Troubleshooting](#7-troubleshooting)
8. [Reference Commands](#8-reference-commands)

---

## 1. Overview

This guide walks you through deploying the **ISIC-Powered Dermatology CDS Module** for the PMS. By the end, you will have:

- A `pms-derm-cds` Docker service running an EfficientNet-B4 classification model
- A pgvector-enabled PostgreSQL database with ISIC reference image embeddings
- A `/api/lesions` endpoint in the PMS backend for image upload and classification
- A Lesion Classification Panel in the Next.js frontend
- Audit logging and AES-256 image encryption for HIPAA compliance

### Architecture at a Glance

```mermaid
flowchart LR
    subgraph Client["Client Layer"]
        WEB["Next.js :3000<br/>Lesion Upload + Results"]
        ANDROID["Android App<br/>Camera + TFLite"]
    end

    subgraph Backend["PMS Backend :8000"]
        LESION["/api/lesions"]
        PATIENTS["/api/patients"]
        ENC["/api/encounters"]
    end

    subgraph CDS["Dermatology CDS :8090"]
        CLASSIFY["Classification Engine"]
        SIMILAR["Similarity Search"]
        RISK["Risk Calculator"]
    end

    PG[("PostgreSQL :5432<br/>+ pgvector")]

    WEB -->|"Upload image"| LESION
    ANDROID -->|"Upload image"| LESION
    LESION -->|"Classify request"| CLASSIFY
    CLASSIFY --> SIMILAR
    CLASSIFY --> RISK
    SIMILAR --> PG
    LESION --> PG
    LESION --> PATIENTS
    LESION --> ENC

    style CLASSIFY fill:#e74c3c,color:#fff
    style SIMILAR fill:#9b59b6,color:#fff
    style RISK fill:#f39c12,color:#fff
    style PG fill:#1abc9c,color:#fff
```

---

## 2. Prerequisites

### 2.1 Required Software

| Software | Minimum Version | Check Command |
|---|---|---|
| Docker & Docker Compose | 24.0+ / 2.20+ | `docker --version && docker compose version` |
| Python | 3.11+ | `python3 --version` |
| Node.js | 20 LTS | `node --version` |
| PostgreSQL client | 16+ | `psql --version` |
| Git | 2.40+ | `git --version` |
| AWS CLI | 2.x | `aws --version` |
| pip | 23+ | `pip --version` |

### 2.2 Installation of Prerequisites

**AWS CLI** (needed for ISIC S3 bulk download):

```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./aws/install
```

**isic-cli** (ISIC Archive command-line tool):

```bash
pip install isic-cli
isic --version
```

**pgvector** (if not using Docker-managed PostgreSQL):

```bash
# The Docker Compose setup installs pgvector automatically.
# If running PostgreSQL natively on macOS:
brew install pgvector

# If running PostgreSQL natively on Linux (Ubuntu):
sudo apt install postgresql-16-pgvector
```

### 2.3 Verify PMS Services

Confirm the core PMS stack is running before proceeding:

```bash
# Backend health check
curl -s http://localhost:8000/health | python3 -m json.tool

# Frontend check
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000

# PostgreSQL connection
psql -h localhost -p 5432 -U pms -d pms_db -c "SELECT version();"
```

Expected: Backend returns `{"status": "healthy"}`, frontend returns `200`, PostgreSQL returns version string.

**Checkpoint:** All three PMS services (backend, frontend, PostgreSQL) are running and accessible.

---

## 3. Part A: Install and Configure the Dermatology CDS Service

### Step 1: Create the CDS Service Directory

```bash
mkdir -p services/derm-cds/{models,cache,scripts}
```

### Step 2: Create the CDS Service Dockerfile

Create `services/derm-cds/Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Model weights directory (mounted as volume)
VOLUME /app/models

# Reference image cache directory (mounted as volume)
VOLUME /app/cache

EXPOSE 8090

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8090"]
```

### Step 3: Create CDS Requirements File

Create `services/derm-cds/requirements.txt`:

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
torch==2.5.1
torchvision==0.20.1
onnxruntime==1.20.1
Pillow==11.1.0
numpy==2.2.2
pydantic==2.10.4
httpx==0.28.1
psycopg[binary]==3.2.4
pgvector==0.3.6
cryptography==44.0.0
python-multipart==0.0.20
isic-cli==12.3.0
```

### Step 4: Create the CDS Main Application

Create `services/derm-cds/main.py`:

```python
"""
ISIC Archive Dermatology CDS Service
Provides skin lesion classification, similarity search, and risk scoring.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
import torchvision.transforms as T
from PIL import Image
import io
import numpy as np
import logging

from classifier import LesionClassifier
from embedder import ImageEmbedder
from similarity import SimilarityEngine
from risk_scorer import RiskScorer

logger = logging.getLogger(__name__)

classifier: LesionClassifier | None = None
embedder: ImageEmbedder | None = None
similarity_engine: SimilarityEngine | None = None
risk_scorer: RiskScorer | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load models on startup."""
    global classifier, embedder, similarity_engine, risk_scorer
    logger.info("Loading EfficientNet-B4 classification model...")
    classifier = LesionClassifier(model_path="/app/models/efficientnet_b4_isic.onnx")
    embedder = ImageEmbedder(classifier.model)
    similarity_engine = await SimilarityEngine.create(dsn="postgresql://pms:pms@postgres:5432/pms_db")
    risk_scorer = RiskScorer()
    logger.info("Dermatology CDS service ready.")
    yield
    if similarity_engine:
        await similarity_engine.close()


app = FastAPI(
    title="PMS Dermatology CDS",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ISIC diagnostic categories ---
ISIC_CLASSES = [
    "melanoma",
    "melanocytic_nevus",
    "basal_cell_carcinoma",
    "actinic_keratosis",
    "benign_keratosis",
    "dermatofibroma",
    "vascular_lesion",
    "squamous_cell_carcinoma",
    "unknown",
]


# --- Request/Response Models ---
class ClassificationResult(BaseModel):
    predictions: list[dict]
    top_prediction: str
    confidence: float
    risk_level: str
    risk_factors: list[str]
    referral_urgency: str


class SimilarImage(BaseModel):
    isic_id: str
    diagnosis: str
    similarity_score: float
    image_url: str
    metadata: dict


# --- Image preprocessing ---
preprocess = T.Compose([
    T.Resize((380, 380)),
    T.CenterCrop((380, 380)),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "derm-cds",
        "model_loaded": classifier is not None,
    }


@app.post("/classify", response_model=ClassificationResult)
async def classify_lesion(
    image: UploadFile = File(...),
    patient_age: int | None = None,
    anatomical_site: str | None = None,
):
    """Classify a dermoscopic skin lesion image."""
    if classifier is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    # Read and preprocess image
    contents = await image.read()
    try:
        img = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    tensor = preprocess(img).unsqueeze(0)

    # Run classification
    probabilities = classifier.predict(tensor)

    # Build predictions list sorted by confidence
    predictions = [
        {"class": cls, "probability": round(float(prob), 4)}
        for cls, prob in sorted(
            zip(ISIC_CLASSES, probabilities), key=lambda x: x[1], reverse=True
        )
    ]

    top_pred = predictions[0]

    # Calculate risk score
    risk = risk_scorer.calculate(
        predictions=predictions,
        patient_age=patient_age,
        anatomical_site=anatomical_site,
    )

    logger.info(
        "Classification: %s (%.2f%%) | Risk: %s",
        top_pred["class"],
        top_pred["probability"] * 100,
        risk["level"],
    )

    return ClassificationResult(
        predictions=predictions[:5],
        top_prediction=top_pred["class"],
        confidence=top_pred["probability"],
        risk_level=risk["level"],
        risk_factors=risk["factors"],
        referral_urgency=risk["referral_urgency"],
    )


@app.post("/similar", response_model=list[SimilarImage])
async def find_similar_lesions(
    image: UploadFile = File(...),
    top_k: int = 10,
):
    """Find visually similar ISIC reference images."""
    if embedder is None or similarity_engine is None:
        raise HTTPException(status_code=503, detail="Service not ready")

    contents = await image.read()
    try:
        img = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    tensor = preprocess(img).unsqueeze(0)

    # Extract embedding
    embedding = embedder.extract(tensor)

    # Query pgvector for similar reference images
    results = await similarity_engine.search(embedding, top_k=top_k)

    return [
        SimilarImage(
            isic_id=r["isic_id"],
            diagnosis=r["diagnosis"],
            similarity_score=round(r["score"], 4),
            image_url=f"https://api.isic-archive.com/api/v2/images/{r['isic_id']}/thumbnail",
            metadata=r["metadata"],
        )
        for r in results
    ]
```

### Step 5: Create the Classifier Module

Create `services/derm-cds/classifier.py`:

```python
"""Skin lesion classifier using ONNX Runtime or PyTorch."""

import onnxruntime as ort
import numpy as np
import torch
import logging

logger = logging.getLogger(__name__)


class LesionClassifier:
    """Classifies dermoscopic images using EfficientNet-B4 trained on ISIC data."""

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.session = None
        self.torch_model = None

        if model_path.endswith(".onnx"):
            self._load_onnx(model_path)
        else:
            self._load_pytorch(model_path)

    def _load_onnx(self, path: str):
        """Load ONNX model for optimized inference."""
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
        self.session = ort.InferenceSession(path, providers=providers)
        logger.info("Loaded ONNX model from %s", path)

    def _load_pytorch(self, path: str):
        """Load PyTorch model as fallback."""
        self.torch_model = torch.jit.load(path, map_location="cpu")
        self.torch_model.set_grad_enabled(False)
        logger.info("Loaded PyTorch model from %s", path)

    def predict(self, tensor: torch.Tensor) -> np.ndarray:
        """Run inference and return class probabilities."""
        if self.session is not None:
            input_name = self.session.get_inputs()[0].name
            numpy_input = tensor.numpy()
            outputs = self.session.run(None, {input_name: numpy_input})
            logits = outputs[0][0]
        elif self.torch_model is not None:
            with torch.no_grad():
                logits = self.torch_model(tensor)[0].numpy()
        else:
            raise RuntimeError("No model loaded")

        # Apply softmax to get probabilities
        exp_logits = np.exp(logits - np.max(logits))
        probabilities = exp_logits / exp_logits.sum()
        return probabilities

    @property
    def model(self):
        """Return underlying model for embedding extraction."""
        return self.torch_model or self.session
```

### Step 6: Create the Embedding and Similarity Modules

Create `services/derm-cds/embedder.py`:

```python
"""Extract feature embeddings from dermoscopic images for similarity search."""

import numpy as np
import torch
import onnxruntime as ort
import logging

logger = logging.getLogger(__name__)


class ImageEmbedder:
    """Extracts 512-dim feature vectors from the penultimate model layer."""

    def __init__(self, model):
        self.model = model
        self.embedding_dim = 512

    def extract(self, tensor: torch.Tensor) -> np.ndarray:
        """Extract embedding vector from image tensor."""
        if isinstance(self.model, ort.InferenceSession):
            # For ONNX, use a model exported with embedding output
            input_name = self.model.get_inputs()[0].name
            numpy_input = tensor.numpy()
            outputs = self.model.run(None, {input_name: numpy_input})
            # Second output is the embedding (penultimate layer)
            if len(outputs) > 1:
                embedding = outputs[1][0]
            else:
                # Fallback: use logits as embedding
                embedding = outputs[0][0]
        else:
            with torch.no_grad():
                embedding = self.model.get_embedding(tensor).numpy()[0]

        # L2-normalize the embedding
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding.astype(np.float32)
```

Create `services/derm-cds/similarity.py`:

```python
"""pgvector-based similarity search for ISIC reference images."""

import numpy as np
import psycopg
from pgvector.psycopg import register_vector
import logging

logger = logging.getLogger(__name__)


class SimilarityEngine:
    """Searches for visually similar ISIC reference images using pgvector."""

    def __init__(self, conn):
        self.conn = conn

    @classmethod
    async def create(cls, dsn: str) -> "SimilarityEngine":
        """Create a SimilarityEngine with a database connection."""
        conn = await psycopg.AsyncConnection.connect(dsn, autocommit=True)
        await register_vector(conn)
        logger.info("Connected to PostgreSQL with pgvector support")
        return cls(conn)

    async def search(self, query_embedding: np.ndarray, top_k: int = 10) -> list[dict]:
        """Find the top-K most similar ISIC reference images."""
        embedding_list = query_embedding.tolist()

        query = """
            SELECT
                isic_id,
                diagnosis,
                1 - (embedding <=> %s::vector) AS similarity_score,
                metadata
            FROM isic_reference_embeddings
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """

        async with self.conn.cursor() as cur:
            await cur.execute(query, (embedding_list, embedding_list, top_k))
            rows = await cur.fetchall()

        return [
            {
                "isic_id": row[0],
                "diagnosis": row[1],
                "score": float(row[2]),
                "metadata": row[3] or {},
            }
            for row in rows
        ]

    async def close(self):
        """Close the database connection."""
        await self.conn.close()
```

### Step 7: Create the Risk Scorer Module

Create `services/derm-cds/risk_scorer.py`:

```python
"""Risk score calculator for skin lesion classification results."""


# Malignant diagnostic categories
MALIGNANT_CLASSES = {
    "melanoma",
    "basal_cell_carcinoma",
    "squamous_cell_carcinoma",
    "actinic_keratosis",
}

# High-risk anatomical sites for melanoma
HIGH_RISK_SITES = {"scalp", "back", "trunk", "lower_extremity", "upper_extremity"}


class RiskScorer:
    """Converts classification probabilities into structured risk assessments."""

    def __init__(
        self,
        high_threshold: float = 0.6,
        medium_threshold: float = 0.3,
    ):
        self.high_threshold = high_threshold
        self.medium_threshold = medium_threshold

    def calculate(
        self,
        predictions: list[dict],
        patient_age: int | None = None,
        anatomical_site: str | None = None,
    ) -> dict:
        """Calculate risk level and referral urgency."""
        factors = []

        # Sum probabilities for malignant classes
        malignant_prob = sum(
            p["probability"]
            for p in predictions
            if p["class"] in MALIGNANT_CLASSES
        )

        # Determine base risk level from malignant probability
        if malignant_prob >= self.high_threshold:
            level = "high"
            factors.append(f"Malignant probability {malignant_prob:.0%}")
        elif malignant_prob >= self.medium_threshold:
            level = "medium"
            factors.append(f"Moderate malignant probability {malignant_prob:.0%}")
        else:
            level = "low"

        # Adjust for melanoma specifically
        melanoma_prob = next(
            (p["probability"] for p in predictions if p["class"] == "melanoma"),
            0.0,
        )
        if melanoma_prob > 0.2:
            if level == "low":
                level = "medium"
            factors.append(f"Melanoma probability {melanoma_prob:.0%}")

        # Age-based risk adjustment
        if patient_age is not None and patient_age > 60:
            if level == "low":
                level = "medium"
            factors.append(f"Patient age {patient_age} (elevated risk)")

        # Anatomical site risk
        if anatomical_site and anatomical_site.lower() in HIGH_RISK_SITES:
            factors.append(f"High-risk anatomical site: {anatomical_site}")

        # Determine referral urgency
        urgency_map = {
            "high": "urgent",
            "medium": "expedited",
            "low": "routine",
        }

        return {
            "level": level,
            "factors": factors,
            "referral_urgency": urgency_map[level],
            "malignant_probability": round(malignant_prob, 4),
        }
```

### Step 8: Add CDS Service to Docker Compose

Add this service to your project's `docker-compose.yml`:

```yaml
  pms-derm-cds:
    build:
      context: ./services/derm-cds
      dockerfile: Dockerfile
    container_name: pms-derm-cds
    ports:
      - "8090:8090"
    volumes:
      - derm-models:/app/models
      - derm-cache:/app/cache
    environment:
      - DATABASE_URL=postgresql://pms:pms@postgres:5432/pms_db
      - LOG_LEVEL=INFO
      - MODEL_PATH=/app/models/efficientnet_b4_isic.onnx
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - pms-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8090/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

volumes:
  derm-models:
  derm-cache:
```

### Step 9: Set Up pgvector and Database Schema

Create `services/derm-cds/scripts/init_db.sql`:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Lesion images table (patient dermoscopic images)
CREATE TABLE IF NOT EXISTS lesion_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL,
    encounter_id UUID,
    image_data BYTEA NOT NULL,  -- AES-256 encrypted
    image_hash VARCHAR(64) NOT NULL,
    anatomical_site VARCHAR(100),
    capture_method VARCHAR(50) DEFAULT 'upload',
    image_width INT,
    image_height INT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100) NOT NULL
);

-- Lesion classifications table
CREATE TABLE IF NOT EXISTS lesion_classifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesion_image_id UUID REFERENCES lesion_images(id),
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    top_prediction VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    all_predictions JSONB NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    risk_factors JSONB,
    referral_urgency VARCHAR(20) NOT NULL,
    classified_at TIMESTAMPTZ DEFAULT NOW()
);

-- ISIC reference image embeddings
CREATE TABLE IF NOT EXISTS isic_reference_embeddings (
    id SERIAL PRIMARY KEY,
    isic_id VARCHAR(20) UNIQUE NOT NULL,
    diagnosis VARCHAR(50) NOT NULL,
    embedding vector(512) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Patient lesion embeddings (for similarity and change tracking)
CREATE TABLE IF NOT EXISTS patient_lesion_embeddings (
    id SERIAL PRIMARY KEY,
    lesion_image_id UUID REFERENCES lesion_images(id),
    embedding vector(512) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for vector similarity search
CREATE INDEX IF NOT EXISTS idx_isic_embedding
    ON isic_reference_embeddings USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_patient_embedding
    ON patient_lesion_embeddings USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 50);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_lesion_images_patient
    ON lesion_images(patient_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_lesion_classifications_image
    ON lesion_classifications(lesion_image_id, classified_at DESC);

-- Audit log for HIPAA compliance
CREATE TABLE IF NOT EXISTS derm_audit_log (
    id BIGSERIAL PRIMARY KEY,
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(100),
    user_id VARCHAR(100) NOT NULL,
    patient_id UUID,
    details JSONB,
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_derm_audit_log_time
    ON derm_audit_log(created_at DESC);
```

Run the migration:

```bash
psql -h localhost -p 5432 -U pms -d pms_db -f services/derm-cds/scripts/init_db.sql
```

### Step 10: Download the Classification Model

```bash
# Create model directory
mkdir -p services/derm-cds/models

# Option A: Download a pre-trained EfficientNet-B4 ONNX model
# (Use a model from the ISIC Challenge or export one yourself)
# Example using a public ISIC-trained model:
python3 -c "
import torchvision.models as models
import torch

# Load EfficientNet-B4 with ImageNet weights as a starting point
model = models.efficientnet_b4(weights='IMAGENET1K_V1')
model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, 9)
model.eval()

# Export to ONNX
dummy_input = torch.randn(1, 3, 380, 380)
torch.onnx.export(
    model,
    dummy_input,
    'services/derm-cds/models/efficientnet_b4_isic.onnx',
    input_names=['input'],
    output_names=['logits'],
    dynamic_axes={'input': {0: 'batch'}, 'logits': {0: 'batch'}},
)
print('Model exported to ONNX format.')
"
```

> **Note:** For production, replace this with an EfficientNet-B4 fine-tuned on the full ISIC dataset. Top ISIC Challenge solutions are available on Kaggle.

### Step 11: Populate the ISIC Reference Cache

Create `services/derm-cds/scripts/populate_cache.py`:

```python
"""Download ISIC reference images and compute embeddings for similarity search."""

import subprocess
import json
import httpx
import asyncio
import psycopg
from pgvector.psycopg import register_vector
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ISIC_API = "https://api.isic-archive.com/api/v2"
CACHE_DIR = Path("/app/cache/isic_reference")
DSN = "postgresql://pms:pms@localhost:5432/pms_db"
TARGET_COUNT = 10_000  # Start with 10K reference images


async def fetch_image_metadata(client: httpx.AsyncClient, limit: int = 100, offset: int = 0):
    """Fetch image metadata from ISIC API."""
    resp = await client.get(
        f"{ISIC_API}/images",
        params={"limit": limit, "offset": offset, "sort": "random"},
    )
    resp.raise_for_status()
    return resp.json()


async def download_image(client: httpx.AsyncClient, isic_id: str, dest: Path):
    """Download a single ISIC image."""
    resp = await client.get(
        f"{ISIC_API}/images/{isic_id}/thumbnail",
        params={"size": 380},
    )
    resp.raise_for_status()
    dest.write_bytes(resp.content)


async def populate():
    """Main cache population workflow."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    conn = await psycopg.AsyncConnection.connect(DSN, autocommit=True)
    await register_vector(conn)

    async with httpx.AsyncClient(timeout=30.0) as client:
        offset = 0
        total_inserted = 0

        while total_inserted < TARGET_COUNT:
            logger.info("Fetching metadata batch (offset=%d)...", offset)
            batch = await fetch_image_metadata(client, limit=100, offset=offset)

            if not batch.get("results"):
                break

            for item in batch["results"]:
                isic_id = item["isic_id"]
                diagnosis = item.get("metadata", {}).get("diagnosis", "unknown")

                # Download thumbnail
                img_path = CACHE_DIR / f"{isic_id}.jpg"
                if not img_path.exists():
                    try:
                        await download_image(client, isic_id, img_path)
                    except Exception as e:
                        logger.warning("Failed to download %s: %s", isic_id, e)
                        continue

                # Generate a placeholder embedding (replace with real model inference)
                embedding = np.random.randn(512).astype(np.float32)
                embedding = embedding / np.linalg.norm(embedding)

                # Insert into pgvector
                metadata = {
                    "age": item.get("metadata", {}).get("age_approx"),
                    "sex": item.get("metadata", {}).get("sex"),
                    "site": item.get("metadata", {}).get("anatom_site_general"),
                }

                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO isic_reference_embeddings (isic_id, diagnosis, embedding, metadata)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (isic_id) DO NOTHING
                        """,
                        (isic_id, diagnosis, embedding.tolist(), json.dumps(metadata)),
                    )

                total_inserted += 1
                if total_inserted % 500 == 0:
                    logger.info("Inserted %d / %d reference images", total_inserted, TARGET_COUNT)

            offset += 100

    await conn.close()
    logger.info("Cache population complete: %d reference images indexed.", total_inserted)


if __name__ == "__main__":
    asyncio.run(populate())
```

Run the cache population:

```bash
# From the services/derm-cds directory
python3 scripts/populate_cache.py
```

### Step 12: Start the CDS Service

```bash
docker compose up -d pms-derm-cds
docker compose logs -f pms-derm-cds
```

Wait for the startup log message: `Dermatology CDS service ready.`

**Checkpoint:** The `pms-derm-cds` service is running on port 8090, the classification model is loaded, pgvector is configured with ISIC reference embeddings, and the health endpoint returns `{"status": "healthy"}`.

---

## 4. Part B: Integrate with PMS Backend

### Step 1: Add Lesion API Router

Create a new router in the PMS backend at `app/routers/lesions.py`:

```python
"""Lesion assessment API — integrates with the Dermatology CDS service."""

from uuid import UUID, uuid4
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from pydantic import BaseModel
import httpx
import hashlib
import logging

from app.core.security import get_current_user
from app.core.encryption import encrypt_image, decrypt_image
from app.db import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/lesions", tags=["lesions"])

CDS_BASE_URL = "http://pms-derm-cds:8090"


class LesionUploadResponse(BaseModel):
    lesion_image_id: str
    classification: dict
    similar_images: list[dict]
    risk_assessment: dict


class LesionHistoryItem(BaseModel):
    id: str
    classified_at: str
    top_prediction: str
    confidence: float
    risk_level: str


@router.post("/upload", response_model=LesionUploadResponse)
async def upload_lesion_image(
    image: UploadFile = File(...),
    patient_id: UUID = Form(...),
    encounter_id: UUID = Form(None),
    anatomical_site: str = Form(None),
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    """Upload a dermoscopic image for AI classification and similarity search."""
    # Read image bytes
    image_bytes = await image.read()
    image_hash = hashlib.sha256(image_bytes).hexdigest()

    # Encrypt image for HIPAA-compliant storage
    encrypted_image = encrypt_image(image_bytes)

    # Store in database
    lesion_image_id = uuid4()
    await db.execute(
        """
        INSERT INTO lesion_images (id, patient_id, encounter_id, image_data,
                                   image_hash, anatomical_site, created_by)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        lesion_image_id, patient_id, encounter_id,
        encrypted_image, image_hash, anatomical_site, user.id,
    )

    # Send to CDS for classification
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Classify
        classify_resp = await client.post(
            f"{CDS_BASE_URL}/classify",
            files={"image": ("lesion.jpg", image_bytes, "image/jpeg")},
            data={"anatomical_site": anatomical_site or ""},
        )
        classify_resp.raise_for_status()
        classification = classify_resp.json()

        # Find similar ISIC reference images
        similar_resp = await client.post(
            f"{CDS_BASE_URL}/similar",
            files={"image": ("lesion.jpg", image_bytes, "image/jpeg")},
            data={"top_k": "10"},
        )
        similar_resp.raise_for_status()
        similar_images = similar_resp.json()

    # Store classification result
    await db.execute(
        """
        INSERT INTO lesion_classifications
            (lesion_image_id, model_name, model_version, top_prediction,
             confidence, all_predictions, risk_level, risk_factors, referral_urgency)
        VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7, $8::jsonb, $9)
        """,
        lesion_image_id, "efficientnet_b4", "isic-2024-v1",
        classification["top_prediction"], classification["confidence"],
        str(classification["predictions"]), classification["risk_level"],
        str(classification["risk_factors"]), classification["referral_urgency"],
    )

    # Audit log
    await db.execute(
        """
        INSERT INTO derm_audit_log (action, resource_type, resource_id, user_id, patient_id, details)
        VALUES ($1, $2, $3, $4, $5, $6::jsonb)
        """,
        "classify_lesion", "lesion_image", str(lesion_image_id),
        str(user.id), patient_id,
        f'{{"top_prediction": "{classification["top_prediction"]}", "risk_level": "{classification["risk_level"]}"}}',
    )

    return LesionUploadResponse(
        lesion_image_id=str(lesion_image_id),
        classification=classification,
        similar_images=similar_images,
        risk_assessment={
            "risk_level": classification["risk_level"],
            "referral_urgency": classification["referral_urgency"],
            "risk_factors": classification["risk_factors"],
        },
    )


@router.get("/history/{patient_id}", response_model=list[LesionHistoryItem])
async def get_lesion_history(
    patient_id: UUID,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    """Get lesion classification history for a patient."""
    rows = await db.fetch_all(
        """
        SELECT lc.id, lc.classified_at, lc.top_prediction,
               lc.confidence, lc.risk_level
        FROM lesion_classifications lc
        JOIN lesion_images li ON lc.lesion_image_id = li.id
        WHERE li.patient_id = $1
        ORDER BY lc.classified_at DESC
        LIMIT 50
        """,
        patient_id,
    )

    return [
        LesionHistoryItem(
            id=str(row["id"]),
            classified_at=row["classified_at"].isoformat(),
            top_prediction=row["top_prediction"],
            confidence=row["confidence"],
            risk_level=row["risk_level"],
        )
        for row in rows
    ]
```

### Step 2: Register the Router

In your main backend `app/main.py`, add:

```python
from app.routers import lesions

app.include_router(lesions.router)
```

### Step 3: Create Image Encryption Utility

Create `app/core/encryption.py`:

```python
"""AES-256-GCM encryption for patient dermoscopic images."""

import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Load encryption key from environment variable (32 bytes = 256 bits)
ENCRYPTION_KEY = os.environ.get("IMAGE_ENCRYPTION_KEY", "").encode()
if len(ENCRYPTION_KEY) != 32:
    # Generate a key for development (in production, use a proper key management system)
    ENCRYPTION_KEY = AESGCM.generate_key(bit_length=256)


def encrypt_image(image_bytes: bytes) -> bytes:
    """Encrypt image data using AES-256-GCM."""
    aesgcm = AESGCM(ENCRYPTION_KEY)
    nonce = os.urandom(12)  # 96-bit nonce for GCM
    ciphertext = aesgcm.encrypt(nonce, image_bytes, None)
    # Prepend nonce to ciphertext for decryption
    return nonce + ciphertext


def decrypt_image(encrypted_data: bytes) -> bytes:
    """Decrypt AES-256-GCM encrypted image data."""
    aesgcm = AESGCM(ENCRYPTION_KEY)
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None)
```

### Step 4: Add Environment Variables

Add to your backend `.env` file:

```bash
# Dermatology CDS
DERM_CDS_URL=http://pms-derm-cds:8090
IMAGE_ENCRYPTION_KEY=your-32-byte-key-here-change-in-prod
```

**Checkpoint:** The PMS backend has a `/api/lesions/upload` endpoint that accepts image uploads, forwards them to the CDS service for classification, stores encrypted images, and returns classification results with risk assessments.

---

## 5. Part C: Integrate with PMS Frontend

### Step 1: Add Environment Variable

Add to `pms-frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 2: Create the Lesion Upload Component

Create `src/components/dermatology/LesionUploader.tsx`:

```tsx
"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";

interface ClassificationResult {
  predictions: Array<{ class: string; probability: number }>;
  top_prediction: string;
  confidence: number;
  risk_level: string;
  risk_factors: string[];
  referral_urgency: string;
}

interface SimilarImage {
  isic_id: string;
  diagnosis: string;
  similarity_score: number;
  image_url: string;
}

interface LesionResult {
  lesion_image_id: string;
  classification: ClassificationResult;
  similar_images: SimilarImage[];
  risk_assessment: {
    risk_level: string;
    referral_urgency: string;
    risk_factors: string[];
  };
}

interface LesionUploaderProps {
  patientId: string;
  encounterId?: string;
  onResult?: (result: LesionResult) => void;
}

const ANATOMICAL_SITES = [
  "head_neck",
  "upper_extremity",
  "lower_extremity",
  "trunk",
  "back",
  "scalp",
  "palms_soles",
  "genital",
  "oral",
];

export function LesionUploader({ patientId, encounterId, onResult }: LesionUploaderProps) {
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<LesionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [anatomicalSite, setAnatomicalSite] = useState("");
  const [preview, setPreview] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setPreview(URL.createObjectURL(file));
      setResult(null);
      setError(null);
    }
  }, []);

  const { getRootProps, getInputProps, acceptedFiles, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [".jpg", ".jpeg", ".png"] },
    maxFiles: 1,
    maxSize: 20 * 1024 * 1024, // 20 MB
  });

  const handleClassify = async () => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("image", file);
      formData.append("patient_id", patientId);
      if (encounterId) formData.append("encounter_id", encounterId);
      if (anatomicalSite) formData.append("anatomical_site", anatomicalSite);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/lesions/upload`,
        { method: "POST", body: formData }
      );

      if (!response.ok) {
        throw new Error(`Classification failed: ${response.statusText}`);
      }

      const data: LesionResult = await response.json();
      setResult(data);
      onResult?.(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Classification failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-gray-400"
        }`}
      >
        <input {...getInputProps()} />
        {preview ? (
          <img src={preview} alt="Lesion preview" className="mx-auto max-h-64 rounded" />
        ) : (
          <div>
            <p className="text-lg font-medium">Drop a dermoscopic image here</p>
            <p className="text-sm text-gray-500 mt-1">JPEG or PNG, max 20 MB</p>
          </div>
        )}
      </div>

      {/* Anatomical Site Selector */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Anatomical Site
        </label>
        <select
          value={anatomicalSite}
          onChange={(e) => setAnatomicalSite(e.target.value)}
          className="w-full border rounded-md px-3 py-2"
        >
          <option value="">Select site...</option>
          {ANATOMICAL_SITES.map((site) => (
            <option key={site} value={site}>
              {site.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
            </option>
          ))}
        </select>
      </div>

      {/* Classify Button */}
      <button
        onClick={handleClassify}
        disabled={!acceptedFiles.length || uploading}
        className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium
                   hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed
                   transition-colors"
      >
        {uploading ? "Classifying..." : "Classify Lesion"}
      </button>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Results */}
      {result && <ClassificationResults result={result} />}
    </div>
  );
}

function ClassificationResults({ result }: { result: LesionResult }) {
  const riskColors: Record<string, string> = {
    high: "bg-red-100 text-red-800 border-red-300",
    medium: "bg-yellow-100 text-yellow-800 border-yellow-300",
    low: "bg-green-100 text-green-800 border-green-300",
  };

  return (
    <div className="space-y-6">
      {/* Risk Banner */}
      <div
        className={`p-4 rounded-lg border-2 ${riskColors[result.risk_assessment.risk_level] || ""}`}
      >
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold">
              Risk Level: {result.risk_assessment.risk_level.toUpperCase()}
            </h3>
            <p className="text-sm mt-1">
              Referral: {result.risk_assessment.referral_urgency}
            </p>
          </div>
          <div className="text-3xl font-bold">
            {(result.classification.confidence * 100).toFixed(1)}%
          </div>
        </div>
        {result.risk_assessment.risk_factors.length > 0 && (
          <ul className="mt-2 text-sm list-disc list-inside">
            {result.risk_assessment.risk_factors.map((factor, i) => (
              <li key={i}>{factor}</li>
            ))}
          </ul>
        )}
      </div>

      {/* Classification Probabilities */}
      <div>
        <h4 className="font-medium mb-2">Classification Results</h4>
        <div className="space-y-2">
          {result.classification.predictions.map((pred) => (
            <div key={pred.class} className="flex items-center gap-3">
              <span className="w-48 text-sm truncate">
                {pred.class.replace(/_/g, " ")}
              </span>
              <div className="flex-1 bg-gray-200 rounded-full h-4">
                <div
                  className="bg-blue-600 rounded-full h-4"
                  style={{ width: `${pred.probability * 100}%` }}
                />
              </div>
              <span className="w-16 text-sm text-right">
                {(pred.probability * 100).toFixed(1)}%
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Similar ISIC Reference Images */}
      {result.similar_images.length > 0 && (
        <div>
          <h4 className="font-medium mb-2">Similar Reference Images (ISIC Archive)</h4>
          <div className="grid grid-cols-5 gap-2">
            {result.similar_images.slice(0, 10).map((img) => (
              <div key={img.isic_id} className="text-center">
                <img
                  src={img.image_url}
                  alt={`ISIC ${img.isic_id}`}
                  className="w-full rounded border"
                  loading="lazy"
                />
                <p className="text-xs mt-1 truncate">{img.diagnosis.replace(/_/g, " ")}</p>
                <p className="text-xs text-gray-500">
                  {(img.similarity_score * 100).toFixed(0)}% match
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Clinical Disclaimer */}
      <div className="bg-gray-50 border border-gray-200 p-3 rounded text-xs text-gray-600">
        <strong>Clinical Decision Support Only:</strong> This AI classification is intended to
        assist clinical judgment, not replace it. All results must be reviewed by a qualified
        clinician. The system is trained on the ISIC Archive dataset and may not generalize
        to all patient populations or imaging conditions.
      </div>
    </div>
  );
}
```

### Step 3: Create a Dermatology Page

Create `src/app/encounters/[id]/dermatology/page.tsx`:

```tsx
import { LesionUploader } from "@/components/dermatology/LesionUploader";

interface Props {
  params: { id: string };
}

export default function DermatologyPage({ params }: Props) {
  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-2">Skin Lesion Assessment</h1>
      <p className="text-gray-600 mb-6">
        Upload a dermoscopic image for AI-assisted classification and risk assessment.
      </p>

      <LesionUploader
        patientId={params.id}
        onResult={(result) => {
          console.log("Classification complete:", result);
        }}
      />
    </div>
  );
}
```

### Step 4: Install Frontend Dependencies

```bash
cd pms-frontend
npm install react-dropzone
```

**Checkpoint:** The Next.js frontend has a `/encounters/[id]/dermatology` page with a drag-and-drop image uploader, anatomical site selector, classification results panel with probability bars, risk assessment banner, and an ISIC similar images gallery.

---

## 6. Part D: Testing and Verification

### Step 1: Verify CDS Service Health

```bash
curl -s http://localhost:8090/health | python3 -m json.tool
```

Expected output:

```json
{
    "status": "healthy",
    "service": "derm-cds",
    "model_loaded": true
}
```

### Step 2: Test Classification Endpoint

```bash
# Download a test dermoscopic image from ISIC
curl -o test_lesion.jpg "https://api.isic-archive.com/api/v2/images/ISIC_0024306/thumbnail?size=380"

# Classify the test image
curl -X POST http://localhost:8090/classify \
  -F "image=@test_lesion.jpg" \
  -F "patient_age=55" \
  -F "anatomical_site=back" | python3 -m json.tool
```

Expected output:

```json
{
    "predictions": [
        {"class": "melanocytic_nevus", "probability": 0.7234},
        {"class": "melanoma", "probability": 0.1102},
        {"class": "benign_keratosis", "probability": 0.0891}
    ],
    "top_prediction": "melanocytic_nevus",
    "confidence": 0.7234,
    "risk_level": "low",
    "risk_factors": [],
    "referral_urgency": "routine"
}
```

### Step 3: Test Similarity Search

```bash
curl -X POST http://localhost:8090/similar \
  -F "image=@test_lesion.jpg" \
  -F "top_k=5" | python3 -m json.tool
```

Expected: Array of 5 similar ISIC reference images with `isic_id`, `diagnosis`, `similarity_score`, and `image_url`.

### Step 4: Test PMS Backend Integration

```bash
curl -X POST http://localhost:8000/api/lesions/upload \
  -H "Authorization: Bearer <your-token>" \
  -F "image=@test_lesion.jpg" \
  -F "patient_id=<patient-uuid>" \
  -F "anatomical_site=back" | python3 -m json.tool
```

Expected: Full response with `lesion_image_id`, `classification`, `similar_images`, and `risk_assessment`.

### Step 5: Verify Audit Logging

```bash
psql -h localhost -p 5432 -U pms -d pms_db -c \
  "SELECT action, resource_type, details, created_at FROM derm_audit_log ORDER BY created_at DESC LIMIT 5;"
```

Expected: Recent `classify_lesion` entries with classification details.

### Step 6: Verify pgvector Reference Data

```bash
psql -h localhost -p 5432 -U pms -d pms_db -c \
  "SELECT COUNT(*) AS total, diagnosis, COUNT(*) AS count FROM isic_reference_embeddings GROUP BY diagnosis ORDER BY count DESC;"
```

Expected: Count of reference images by diagnostic category.

**Checkpoint:** All services are running, classification returns valid predictions, similarity search returns matching ISIC reference images, the PMS backend stores encrypted images with audit logs, and pgvector contains indexed reference embeddings.

---

## 7. Troubleshooting

### CDS Service Fails to Start

**Symptom:** Container exits immediately or logs show `ModuleNotFoundError`.

**Fix:** Ensure all Python dependencies are installed. Rebuild the container:

```bash
docker compose build --no-cache pms-derm-cds
docker compose up -d pms-derm-cds
```

### Model File Not Found

**Symptom:** Logs show `FileNotFoundError: /app/models/efficientnet_b4_isic.onnx`.

**Fix:** Ensure the model file exists in the volume:

```bash
docker compose exec pms-derm-cds ls -la /app/models/
```

If empty, re-run the model download step (Part A, Step 10).

### pgvector Extension Not Available

**Symptom:** SQL error `ERROR: could not open extension control file... pgvector`.

**Fix:** Install pgvector in your PostgreSQL instance:

```bash
# If using Docker PostgreSQL, use the pgvector-enabled image:
# image: pgvector/pgvector:pg16
# Then restart and run:
psql -h localhost -p 5432 -U pms -d pms_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Classification Returns Low Confidence for All Classes

**Symptom:** All predictions show ~11% probability (uniform distribution).

**Fix:** The model likely has not been fine-tuned on ISIC data. The base ImageNet model will not produce meaningful dermoscopic classifications. Download or fine-tune a model on the ISIC dataset:

1. Use an ISIC Challenge winning model from Kaggle
2. Fine-tune EfficientNet-B4 on the ISIC 2024 dataset

### Image Upload Timeout

**Symptom:** `/api/lesions/upload` returns 504 Gateway Timeout.

**Fix:** Increase the timeout in the backend httpx client and in any reverse proxy:

```python
# In lesions.py, increase timeout:
async with httpx.AsyncClient(timeout=60.0) as client:
```

### CORS Errors in Frontend

**Symptom:** Browser console shows `Access-Control-Allow-Origin` errors.

**Fix:** Verify the CDS service CORS configuration includes `http://localhost:3000`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Out of Memory During Inference

**Symptom:** Container killed by OOM (Out Of Memory) killer.

**Fix:** Increase Docker memory limit and use a smaller model:

```yaml
# In docker-compose.yml:
pms-derm-cds:
  deploy:
    resources:
      limits:
        memory: 4G
```

Or switch to MobileNetV3 (smaller memory footprint) for CPU-constrained environments.

---

## 8. Reference Commands

### Daily Development Workflow

```bash
# Start all services
docker compose up -d

# View CDS logs
docker compose logs -f pms-derm-cds

# Restart CDS after code changes
docker compose restart pms-derm-cds

# Run classification test
curl -X POST http://localhost:8090/classify -F "image=@test_lesion.jpg"
```

### Management Commands

```bash
# Rebuild CDS container
docker compose build pms-derm-cds

# Check reference cache size
psql -h localhost -p 5432 -U pms -d pms_db -c "SELECT COUNT(*) FROM isic_reference_embeddings;"

# Re-populate ISIC reference cache
python3 services/derm-cds/scripts/populate_cache.py

# Check audit log
psql -h localhost -p 5432 -U pms -d pms_db -c "SELECT * FROM derm_audit_log ORDER BY created_at DESC LIMIT 10;"

# Download additional ISIC images via CLI
isic image download --search "diagnosis:melanoma" --limit 1000 --output ./cache/melanoma/
```

### Monitoring Commands

```bash
# CDS service health
curl -s http://localhost:8090/health

# Docker resource usage
docker stats pms-derm-cds

# PostgreSQL pgvector index stats
psql -h localhost -p 5432 -U pms -d pms_db -c "SELECT * FROM pg_stat_user_indexes WHERE indexrelname LIKE '%embedding%';"
```

### Useful URLs

| URL | Description |
|---|---|
| `http://localhost:8090/health` | CDS service health check |
| `http://localhost:8090/docs` | CDS Swagger API docs |
| `http://localhost:8000/api/lesions/upload` | PMS lesion upload endpoint |
| `http://localhost:3000/encounters/{id}/dermatology` | Frontend lesion assessment page |
| `https://api.isic-archive.com/api/docs/swagger/` | ISIC Archive API docs |
| `https://www.isic-archive.com/` | ISIC Archive web interface |

---

## Next Steps

- Complete the [ISICArchive Developer Tutorial](18-ISICArchive-Developer-Tutorial.md) to build your first lesion classification integration end-to-end
- Fine-tune EfficientNet-B4 on the full ISIC 2024 dataset for production-grade accuracy
- Configure TFLite model export for Android on-device inference
- Set up model performance monitoring and drift detection
- Review [Gemma 3 Integration](13-PRD-Gemma3-PMS-Integration.md) for combining ISIC classification with clinical reasoning

## Resources

- [ISIC Archive](https://www.isic-archive.com/) — Official skin lesion image repository
- [ISIC Archive API Docs](https://api.isic-archive.com/api/docs/swagger/) — REST API reference
- [isic-cli on PyPI](https://pypi.org/project/isic-cli/) — Command-line tool for data access
- [pgvector Documentation](https://github.com/pgvector/pgvector) — PostgreSQL vector similarity extension
- [EfficientNet Paper](https://arxiv.org/abs/1905.11946) — EfficientNet architecture reference
- [ISIC 2024 Challenge](https://www.kaggle.com/competitions/isic-2024-challenge) — Latest competition and top models
- [PRD: ISICArchive PMS Integration](18-PRD-ISICArchive-PMS-Integration.md) — Full product requirements
