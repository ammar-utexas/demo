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
| bcrypt | >=4.0.0 | Password hashing |
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
| zod | ^4.3.6 | Schema validation (forms, auth tokens) |
| react-hook-form | ^7.71.1 | Form state management |
| @hookform/resolvers | ^5.2.2 | Zod resolver for react-hook-form |
| @radix-ui/react-* | ^1.1–2.2 | Accessible UI primitives (dialog, label, select, tabs, tooltip, etc.) |
| lucide-react | ^0.564.0 | Icon library |
| class-variance-authority | ^0.7.1 | Component variant management |
| sonner | ^2.0.7 | Toast notifications |
| clsx | ^2.1.1 | Conditional classes |
| tailwind-merge | ^3.0.0 | Tailwind class deduplication |
| tailwindcss-animate | ^1.0.7 | Tailwind animation utilities |
| date-fns | ^4.1.0 | Date formatting |
| react-day-picker | ^9.13.2 | Date picker component |
| recharts | ^3.7.0 | Chart components |
| tailwindcss | ^3.4.17 | Utility-first CSS (dev) |
| typescript | ^5.7.0 | Type safety (dev) |
| vitest | ^3.0.0 | Testing (dev) |
| @vitest/coverage-v8 | ~3.2.0 | Code coverage (dev) |
| @testing-library/react | ^16.3.0 | Component testing (dev) |
| @testing-library/jest-dom | ^6.6.0 | DOM matchers for tests (dev) |
| @vitejs/plugin-react | ^4.4.0 | React support for Vitest (dev) |
| jsdom | ^26.0.0 | DOM environment for tests (dev) |
| eslint-config-next | ^15.3.0 | Linting (dev) |

**Why these choices:**
- Next.js over Vite SPA: file-based routing, server components, built-in optimization (see [ADR-0004](../architecture/0004-frontend-tech-stack.md)).
- Tailwind over CSS modules: utility-first, consistent design tokens, no naming overhead.
- Vitest over Jest: faster, native ESM, Vite-compatible.
- Zod over Yup/Joi: TypeScript-first, smaller bundle, Zod 4 schema inference.
- react-hook-form over Formik: smaller bundle, better performance with uncontrolled inputs.
- Radix UI over Headless UI: more complete primitive set, better accessibility defaults.
- lucide-react over heroicons: broader icon set, tree-shakeable, consistent stroke style.

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
