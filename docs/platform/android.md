# Platform: Android

**Tech Stack:** Kotlin, Jetpack Compose, Hilt (DI), Retrofit (HTTP), Room (local DB), DataStore (preferences), offline-first architecture

## Architecture

| Document | Summary |
|----------|---------|
| [ADR-0005: Android Tech Stack](../architecture/0005-android-tech-stack.md) | Tech stack selection: Kotlin, Jetpack Compose, Hilt, Retrofit, Room, DataStore |
| [ADR-0002: Multi-Repo Structure](../architecture/0002-multi-repo-structure.md) | Android as independent repo with own release cycle |

## Requirements (AND Platform Reqs)

| Document | AND Reqs | Summary |
|----------|----------|---------|
| [SUB-PR](../specs/requirements/SUB-PR.md) | 7 | Patient record forms, offline sync, camera integration |
| [SUB-CW](../specs/requirements/SUB-CW.md) | 3 | Encounter management on mobile |
| [SUB-MM](../specs/requirements/SUB-MM.md) | 2 | Medication management on mobile |
| [SUB-RA](../specs/requirements/SUB-RA.md) | 5 | Mobile dashboards and report views |
| [SYS-REQ](../specs/requirements/SYS-REQ.md) | — | SYS-09: Android app system requirement |

## Features & Implementation

| Document | Summary |
|----------|---------|
| [Initial Project Scaffolds](../features/initial-project-scaffolds.md) | 46-file Android scaffold with stub implementations and passing tests |

## Configuration

| Document | Summary |
|----------|---------|
| [Dependencies](../config/dependencies.md) | Kotlin/Gradle library versions and rationale |
| [Project Setup](../config/project-setup.md) | Android clone, build, run, and test commands |
| [Feature Flags](../config/feature-flags.md) | Kotlin implementation examples for feature flags |

## Design

| Document | Summary |
|----------|---------|
| [Banani Developer Tutorial](../experiments/03-Banani-Developer-Tutorial.md) | Prompts for designing PMS Android screens |
| [Banani Getting Started](../experiments/03-Banani-Getting-Started.md) | Mobile-specific design-to-code pipeline |
