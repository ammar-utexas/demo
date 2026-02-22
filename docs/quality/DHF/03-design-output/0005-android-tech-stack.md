# ADR-0005: Android Tech Stack — Kotlin with Jetpack Compose

**Date:** 2026-02-15
**Status:** Accepted

## Context

The PMS Android app provides mobile access for clinical staff in the field. It must integrate with the same FastAPI backend and support offline access for patient data.

## Options Considered

1. **Kotlin + Jetpack Compose** — Modern declarative UI with Kotlin-first ecosystem.
   - Pros: Declarative UI, Kotlin coroutines, strong Google/JetBrains support, Material 3.
   - Cons: Compose-specific learning curve.

2. **Kotlin + XML Views** — Traditional Android UI.
   - Pros: Mature, well-documented.
   - Cons: Verbose, imperative, harder to test UI.

3. **Flutter / React Native** — Cross-platform frameworks.
   - Pros: Single codebase for iOS + Android.
   - Cons: Extra abstraction layer, less native API access, separate ecosystem.

## Decision

Use **Kotlin with Jetpack Compose, Hilt, Retrofit, and Room**.

## Key Dependencies

| Library | Purpose |
|---|---|
| Jetpack Compose + Material 3 | Declarative UI |
| Hilt | Dependency injection |
| Retrofit + kotlinx.serialization | REST API client |
| Room | Local SQLite database (offline cache) |
| DataStore Preferences | Auth token storage |
| Navigation Compose | Screen navigation |
| Kotlin Coroutines | Async operations |

## Architecture

Clean architecture with three layers:

```
ui/          → Compose screens + ViewModels (presentation)
domain/      → Data classes shared across layers
data/
├── api/     → Retrofit interface + auth interceptor
├── local/   → Room database, DAOs, entities
└── repository/ → Mediates between API and local cache
di/          → Hilt module providing all dependencies
```

**Data flow**: Screen → ViewModel → Repository → (API + Room)

## Offline Support

- `PatientRepository` uses Room as offline cache with an API-first refresh strategy.
- `TokenStore` uses DataStore Preferences for persistent auth token storage.
- ViewModels catch network errors and fall back to cached data.

## Consequences

- Room entities must have `toDomain()`/`fromDomain()` mappers.
- Domain models use `@Serializable` with snake_case fields matching the backend.
- One ViewModel per screen, injected via `hiltViewModel()`.
