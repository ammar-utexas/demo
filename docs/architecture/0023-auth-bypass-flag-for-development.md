# ADR-0023: Authentication Bypass Flag for Development

**Status:** Accepted
**Date:** 2026-02-23
**Deciders:** Development Team

---

## Context

The PMS authentication system ([Authentication & User Management](../features/authentication.md)) requires OAuth 2.0 (Google, Microsoft, GitHub) or email/password credentials for every request. During local development and automated testing, this creates several friction points:

1. **OAuth provider dependency** — Developers need valid OAuth client IDs and network access to provider endpoints, which is unavailable offline or in CI environments without secrets.
2. **Token lifecycle overhead** — JWTs expire, requiring developers to repeatedly log in during iterative frontend or API development.
3. **Test isolation** — Integration and end-to-end tests must either mock the full auth flow or maintain test credentials, adding brittleness.
4. **Onboarding delay** — New contributors must configure OAuth providers and seed admin accounts before they can run the application locally.

The project already uses feature flags for release control ([ADR-0006](0006-release-management-strategy.md), [Feature Flag Registry](../config/feature-flags.md)). We need a mechanism that lets developers bypass authentication in non-production environments without weakening the security posture of QA, Staging, or Production.

## Options Considered

### Option A: Environment Variable Auth Bypass Flag

Introduce a single environment variable (`NEXT_PUBLIC_AUTH_BYPASS_ENABLED`) that, when set to `true`, skips all authentication checks and injects a configurable mock user identity into the session.

- **Pros:** Simple to implement, no additional infrastructure, easy to toggle per developer, works offline, consistent with existing feature flag patterns.
- **Cons:** Risk of accidental enablement in production if environment configuration is mismanaged; frontend flag is visible in client bundle.

### Option B: Mock OAuth Provider (Local Identity Server)

Run a local identity provider (e.g., Keycloak dev mode or a custom mock server) that implements the same OAuth endpoints, allowing the real auth flow to execute against a fake provider.

- **Pros:** Exercises the full auth flow including token exchange; catches integration bugs early; no code path divergence between dev and prod.
- **Cons:** Significant setup overhead (Docker, provider configuration); slower developer feedback loop; every contributor must run the mock server; does not help with quick frontend iteration.

### Option C: Hard-Coded Dev Credentials with Auto-Login

Embed a default dev user/password in the seeded database and have the frontend auto-submit credentials when a dev flag is set.

- **Pros:** Uses the real email/password auth flow; no code path changes in auth middleware.
- **Cons:** Still requires the backend to be running with a seeded database; does not help frontend-only development; risk of credentials leaking into version control; auto-login is fragile if password policy changes.

## Decision

Use **Option A: Environment Variable Auth Bypass Flag**.

When `NEXT_PUBLIC_AUTH_BYPASS_ENABLED=true` is set:

1. **Frontend** — The auth guard in the Next.js middleware and client-side route protection is skipped. A mock user object is injected into the auth context with a configurable role via `NEXT_PUBLIC_AUTH_BYPASS_ROLE` (defaults to `admin`).
2. **Backend** — The FastAPI dependency that validates the JWT `Authorization` header accepts a special header value (`Bearer dev-bypass-token`) and resolves to a configurable mock user. This is only active when the backend's `AUTH_BYPASS_ENABLED=true` environment variable is set.
3. **Guard rails** — The flag defaults to `false` in all environments. The application logs a prominent warning on startup when the bypass is active. CI pipelines for QA, Staging, and Production fail if the flag is detected as enabled.

### Mock User Defaults

| Field | Default Value | Override Variable |
|---|---|---|
| `id` | `00000000-0000-0000-0000-000000000000` | — |
| `email` | `dev@localhost` | `NEXT_PUBLIC_AUTH_BYPASS_EMAIL` |
| `name` | `Dev User` | `NEXT_PUBLIC_AUTH_BYPASS_NAME` |
| `role` | `admin` | `NEXT_PUBLIC_AUTH_BYPASS_ROLE` |
| `status` | `active` | — |

## Rationale

Option A was selected because:

1. **Minimal overhead** — No additional services to run. Developers add one line to `.env.local` and start working immediately.
2. **Alignment with existing patterns** — The project already uses environment-variable-based feature flags ([ADR-0006](0006-release-management-strategy.md)). This follows the same convention rather than introducing new infrastructure.
3. **Frontend-first development** — Enables UI work without a running backend by providing a mock user context, which is critical for rapid iteration with tools like Storybook ([Storybook evaluation](../experiments/01-Storybook-Getting-Started.md)) and v0 ([v0 evaluation](../experiments/02-v0-Getting-Started.md)).
4. **Explicit opt-in** — The flag defaults to `false` everywhere, requiring conscious action to enable. Combined with startup warnings and CI guards, the risk of accidental production enablement is acceptably low.

Option B was rejected because the setup cost disproportionately exceeds the benefit for local development, and it does not address frontend-only workflows. Option C was rejected due to credential management risks and its inability to support frontend-only development.

## Consequences

### Positive

- Developers can start frontend work within minutes of cloning the repository.
- CI test suites can run without OAuth provider secrets, simplifying pipeline configuration.
- New contributors face zero authentication setup during onboarding.
- Mock user role is configurable, enabling developers to test role-based access control paths without multiple accounts.

### Negative

- Code paths diverge between dev (bypass) and production (real auth). Bugs in the actual auth flow will not be caught during bypassed development.
- Developers may defer testing the real auth flow, leading to late-stage integration issues.
- The `NEXT_PUBLIC_` prefix exposes the flag name in the client bundle (though the value is only set in local `.env` files).

### Mitigations

- **Mandatory auth integration tests** — The CI pipeline runs a dedicated test suite with auth bypass disabled and real (test) credentials to validate the actual auth flow.
- **PR checklist item** — Any PR touching auth-related code must include a test run with bypass disabled.
- **`.env.example` documentation** — The bypass flag is documented in `.env.example` with a clear warning that it must never be enabled outside local development.
- **CI guard** — QA, Staging, and Production deployment pipelines assert that `AUTH_BYPASS_ENABLED` is not set to `true`.

## References

- [Authentication & User Management Feature Spec](../features/authentication.md) — Full auth flow, roles, and session management
- [ADR-0006: Release Management Strategy](0006-release-management-strategy.md) — Feature flag conventions and environment pipeline
- [Feature Flag Registry](../config/feature-flags.md) — Naming convention and lifecycle stages
- [Storybook Getting Started](../experiments/01-Storybook-Getting-Started.md) — Component development tool that benefits from auth bypass
- [v0 Getting Started](../experiments/02-v0-Getting-Started.md) — AI code generation tool used for rapid UI prototyping
- [PRD: Tambo PMS Integration](../experiments/00-PRD-Tambo-PMS-Integration.md) — Conversational analytics sidebar requiring authenticated context for development
