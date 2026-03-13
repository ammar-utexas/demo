# Dependencies Overview

## pms-backend (Python)

| Package | Version | Purpose |
|---|---|---|
| fastapi | >=0.115.0 | Web framework |
| uvicorn[standard] | >=0.32.0 | ASGI server |
| sqlalchemy[asyncio] | >=2.0.36 | Async ORM |
| asyncpg | >=0.30.0 | PostgreSQL async driver |
| pydantic-settings | >=2.6.0 | Environment config |
| python-jose[cryptography] | >=3.3.0 | JWT tokens |
| passlib[bcrypt] | >=1.7.4 | Password hashing |
| alembic | >=1.14.0 | Database migrations |
| pytest | >=8.3.0 | Testing (dev) |
| pytest-asyncio | >=0.24.0 | Async test support (dev) |
| httpx | >=0.28.0 | Test HTTP client (dev) |
| ruff | >=0.8.0 | Linting (dev) |

**Why these choices:**
- FastAPI over Django: async-native, automatic OpenAPI, lighter weight (see [ADR-0003](../architecture/0003-backend-tech-stack.md)).
- asyncpg over psycopg2: full async PostgreSQL support.
- python-jose over PyJWT: cryptography backend support for RS256 if needed later.

## pms-frontend (Node.js)

| Package | Version | Purpose |
|---|---|---|
| next | ^15.3.0 | React framework |
| react / react-dom | ^19.1.0 | UI library |
| clsx | ^2.1.1 | Conditional classes |
| tailwind-merge | ^3.0.0 | Tailwind class deduplication |
| tailwindcss | ^3.4.17 | Utility-first CSS (dev) |
| typescript | ^5.7.0 | Type safety (dev) |
| vitest | ^3.0.0 | Testing (dev) |
| @testing-library/react | ^16.3.0 | Component testing (dev) |
| eslint-config-next | ^15.3.0 | Linting (dev) |

**Why these choices:**
- Next.js over Vite SPA: file-based routing, server components, built-in optimization (see [ADR-0004](../architecture/0004-frontend-tech-stack.md)).
- Tailwind over CSS modules: utility-first, consistent design tokens, no naming overhead.
- Vitest over Jest: faster, native ESM, Vite-compatible.

## pms-android (Kotlin/Gradle)

| Library | Version | Purpose |
|---|---|---|
| Jetpack Compose BOM | 2024.12.01 | Declarative UI |
| Material 3 | (via BOM) | Design system |
| Hilt | 2.53.1 | Dependency injection |
| Retrofit | 2.11.0 | REST client |
| kotlinx.serialization | 1.7.3 | JSON serialization |
| OkHttp | 4.12.0 | HTTP client + logging |
| Room | 2.6.1 | Local SQLite database |
| DataStore | 1.1.1 | Key-value preferences |
| Navigation Compose | 2.8.5 | Screen navigation |
| Kotlin Coroutines | 1.9.0 | Async operations |
| JUnit 4 | 4.13.2 | Unit testing |

**Why these choices:**
- Jetpack Compose over XML Views: declarative, less boilerplate, testable (see [ADR-0005](../architecture/0005-android-tech-stack.md)).
- Hilt over manual DI: compile-time safety, Android lifecycle awareness.
- Room over raw SQLite: type-safe queries, Flow integration, migration support.
- kotlinx.serialization over Gson: Kotlin-native, multiplatform, no reflection.

## pms-ai (AI Platform)

| Package | Version | Purpose |
|---|---|---|
| fastapi | >=0.115.0 | Web framework for AI service APIs |
| uvicorn[standard] | >=0.32.0 | ASGI server |
| onnxruntime | >=1.17.0 | EfficientNet-B4 inference runtime |
| pgvector | >=0.3.0 | PostgreSQL vector similarity search |
| numpy | >=1.26.0 | Numerical computation for embeddings |
| pillow | >=10.0.0 | Image loading and preprocessing |
| psycopg2-binary | >=2.9.0 | PostgreSQL driver |
| sqlalchemy[asyncio] | >=2.0.36 | Async ORM |
| asyncpg | >=0.30.0 | PostgreSQL async driver |
| alembic | >=1.14.0 | Database migrations (pgvector tables, lesion schema) |
| pydantic-settings | >=2.6.0 | Environment config |
| pytest | >=8.3.0 | Testing (dev) |
| pytest-asyncio | >=0.24.0 | Async test support (dev) |
| httpx | >=0.28.0 | Test HTTP client (dev) |
| ruff | >=0.8.0 | Linting (dev) |

**Why these choices:**
- ONNX Runtime over TorchServe: lighter weight, no PyTorch dependency, cross-platform (see [ADR-0009](../architecture/0009-ai-inference-runtime.md)).
- pgvector over Pinecone/Weaviate: same PostgreSQL instance, zero additional infrastructure, HIPAA-compliant on-premise (see [ADR-0011](../architecture/0011-vector-database-pgvector.md)).
- EfficientNet-B4 over ResNet/ViT: best accuracy-to-size ratio for ISIC classification (see [ADR-0008](../architecture/0008-derm-cds-microservice-architecture.md)).
- FastAPI shared with backend: same framework expertise, async-native, OpenAPI docs.
