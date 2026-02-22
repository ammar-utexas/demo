# ADR-0004: Frontend Tech Stack — Next.js with Tailwind CSS

**Date:** 2026-02-15
**Status:** Accepted

## Context

The PMS web frontend needs to provide a responsive interface for clinical staff to manage patients, encounters, medications, and reports. It must integrate with the FastAPI backend via REST.

## Options Considered

1. **Next.js (App Router) + Tailwind CSS** — React meta-framework with utility-first CSS.
   - Pros: Server components, file-based routing, great DX, built-in optimizations.
   - Cons: React-specific, SSR adds complexity for pure SPA use cases.

2. **Vite + React + CSS Modules** — Lightweight SPA setup.
   - Pros: Fast builds, simple.
   - Cons: No SSR, no file-based routing, more manual setup.

3. **Angular + Material** — Enterprise framework.
   - Pros: Opinionated, built-in state management.
   - Cons: Steeper learning curve, heavier bundle, less flexible.

## Decision

Use **Next.js 15 (App Router) with TypeScript and Tailwind CSS**.

## Key Dependencies

| Library | Purpose |
|---|---|
| Next.js 15 | React framework with App Router |
| React 19 | UI library |
| TypeScript | Type safety |
| Tailwind CSS 3 | Utility-first styling |
| clsx + tailwind-merge | Conditional class composition |
| Vitest + Testing Library | Unit testing |

## Architecture

```
src/
├── app/          # Next.js App Router (file-based routing)
├── components/
│   ├── ui/       # Reusable primitives (Button, Card, Input, Badge)
│   └── layout/   # App shell (Sidebar, Header)
├── lib/          # API client, auth utilities, helpers
└── types/        # TypeScript interfaces matching backend schemas
```

## Backend Integration

- API client in `lib/api.ts` with automatic JWT token attachment
- `next.config.ts` rewrites `/api/*` to the backend URL
- TypeScript types mirror backend Pydantic schemas exactly

## Consequences

- TypeScript types in `src/types/` must stay in sync with backend schemas.
- All pages use the Sidebar + Header layout pattern for consistency.
- The `"use client"` directive is used only where browser APIs are needed.
