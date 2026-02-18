# Platform: Web Frontend

**Tech Stack:** Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS 3

## Architecture

| Document | Summary |
|----------|---------|
| [ADR-0004: Frontend Tech Stack](../architecture/0004-frontend-tech-stack.md) | Tech stack selection: Next.js 15, React 19, TypeScript, Tailwind CSS 3 |
| [ADR-0002: Multi-Repo Structure](../architecture/0002-multi-repo-structure.md) | Frontend as independent repo with own release cycle |

## Requirements (WEB Platform Reqs)

| Document | WEB Reqs | Summary |
|----------|----------|---------|
| [SUB-PR](../specs/requirements/SUB-PR.md) | 4 | Patient record forms, search, list views |
| [SUB-CW](../specs/requirements/SUB-CW.md) | 3 | Encounter management UI |
| [SUB-MM](../specs/requirements/SUB-MM.md) | 2 | Medication management UI |
| [SUB-RA](../specs/requirements/SUB-RA.md) | 5 | Dashboards, charts, audit log viewer, CSV export |
| [SYS-REQ](../specs/requirements/SYS-REQ.md) | — | SYS-08: Web UI system requirement |

## Features & Implementation

| Document | Summary |
|----------|---------|
| [Initial Project Scaffolds](../features/initial-project-scaffolds.md) | 39-file frontend scaffold with stub implementations |

## Configuration

| Document | Summary |
|----------|---------|
| [Dependencies](../config/dependencies.md) | Node.js library versions and rationale |
| [Project Setup](../config/project-setup.md) | Frontend clone, install, run, and test commands |
| [Feature Flags](../config/feature-flags.md) | TypeScript implementation examples for feature flags |

## Tool Evaluations & Tutorials

### Tambo (Conversational AI Sidebar)
| Document | Summary |
|----------|---------|
| [Tambo PMS Integration PRD](../Experiments/00-PRD-Tambo-PMS-Integration.md) | Conversational analytics sidebar with 6 generative UI components |
| [Tambo Developer Tutorial](../Experiments/00-Tambo-Developer-Onboarding-Tutorial.md) | Building Tambo components and tools |
| [Tambo Setup Guide](../Experiments/00-Tambo-PMS-Developer-Setup-Guide.md) | Self-hosting Tambo backend, creating PMS components |

### Storybook (Component Development & Testing)
| Document | Summary |
|----------|---------|
| [Storybook Developer Tutorial](../Experiments/01-Storybook-Developer-Tutorial.md) | Writing stories for all PMS UI components |
| [Storybook Getting Started](../Experiments/01-Storybook-Getting-Started.md) | Installing Storybook 8 in Next.js 15 / React 19 |

### v0 (AI Code Generation)
| Document | Summary |
|----------|---------|
| [v0 Developer Tutorial](../Experiments/02-v0-Developer-Tutorial.md) | Prompts for generating PMS UI pages |
| [v0 Getting Started](../Experiments/02-v0-Getting-Started.md) | Using Vercel v0 with the PMS frontend |

### Banani (AI Design)
| Document | Summary |
|----------|---------|
| [Banani Developer Tutorial](../Experiments/03-Banani-Developer-Tutorial.md) | Prompts for designing PMS web screens |
| [Banani Getting Started](../Experiments/03-Banani-Getting-Started.md) | Text-to-UI generation, Figma export |

### POC Evaluation
| Document | Summary |
|----------|---------|
| [POC Gap Analysis](../Experiments/04-POC-Gap-Analysis.md) | kind-clinical-data React SPA vs. system requirements |
