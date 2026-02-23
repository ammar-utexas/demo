# Subsystem Requirements: Authentication & User Management (SUB-AU)

**Document ID:** PMS-SUB-AU-001
**Version:** 1.0
**Date:** 2026-02-18
**Parent:** [System Requirements](SYS-REQ.md)

---

## Scope

The Authentication & User Management subsystem implements closed-registration authentication (OAuth 2.0 and email/password), JWT session management, admin-controlled user provisioning, and the four-role RBAC model. It is the security foundation for all other subsystems. User management is an administrative activity performed via the web frontend; Android receives login and profile capabilities only.

## Requirements

| Req ID | Parent | Description | Verification | Status |
| --- | --- | --- | --- | --- |
| SUB-AU-0001 | SYS-REQ-0014 | Authenticate users via OAuth 2.0 (Google, Microsoft, GitHub) using Authorization Code flow with PKCE; reject unregistered or inactive users with 403 | Test | Not Started |
| SUB-AU-0002 | SYS-REQ-0014 | Authenticate users via email/password with bcrypt hashing (cost 12) and password complexity validation (12+ chars, mixed case, digit, special character); support password reset via email token | Test | Not Started |
| SUB-AU-0003 | SYS-REQ-0001 | Issue JWT access tokens (configurable expiry, default 30 min) with claims (sub, email, name, roles, iat, exp) and opaque server-side refresh tokens (7-day lifetime) | Test | Not Started |
| SUB-AU-0004 | SYS-REQ-0001 | Lock account after 5 consecutive failed email/password attempts for 30 minutes; locked accounts rejected across all authentication methods | Test | Not Started |
| SUB-AU-0005 | SYS-REQ-0015 | Seed a default admin account on first deployment from environment variables (ADMIN_SEED_EMAIL, ADMIN_SEED_NAME, ADMIN_SEED_PASSWORD); operation is idempotent | Test | Not Started |
| SUB-AU-0006 | SYS-REQ-0015 | Provide admin-only user CRUD: create (with email, name, roles), update, deactivate (revoke all sessions), reactivate, and resend invite | Test | Not Started |
| SUB-AU-0007 | SYS-REQ-0015 | Implement invite-based onboarding: generate one-time invite token (72-hour expiry), send invite email, accept invite and set password to activate account | Test | Not Started |
| SUB-AU-0008 | SYS-REQ-0005 | Implement four-role model (admin, clinician, sales, lab-staff) with multi-role assignment; permissions evaluated as the union of all assigned roles | Test | Not Started |
| SUB-AU-0009 | SYS-REQ-0005 | Enforce role-permission matrix per API endpoint; unauthorized access rejected with 403 and logged to audit trail | Test | Not Started |
| SUB-AU-0010 | SYS-REQ-0005 | Prevent last-admin lockout: admin role cannot be removed from the sole remaining admin user | Test | Not Started |
| SUB-AU-0011 | SYS-REQ-0003 | Audit log all authentication events (login, logout, failed attempts, lockout, OAuth link) and user management operations (create, update, deactivate, reactivate, role change, invite send) | Test | Not Started |

## Design Decisions

1. **No Android user management** — User management is an admin activity, not a mobile clinical workflow. Android provides login and current-user profile only. Can be added later via governance procedure 2.1.
2. **OAuth as authentication only** — OAuth providers verify identity but do not create users. The user must pre-exist in the PMS database with a matching email.
3. **Union-based permissions** — When a user has multiple roles, permissions are the union (logical OR) across all roles. More roles = more access.
4. **Bcrypt cost factor 12** — Industry standard for password hashing. Balances security with login latency.
5. **Provider-agnostic OAuth** — All three providers follow the same Authorization Code + PKCE flow behind a common interface. Adding a new provider requires only configuration.
6. **Refresh token serialization** — Web uses a single-Promise lock to prevent thundering herd on concurrent refresh attempts (follows RC-WEB-01). Android uses Kotlin Mutex (follows PC-AND-02).

---

## Platform Decomposition

### Backend (BE) — 14 requirements

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
| --- | --- | --- | --- | --- | --- |
| SUB-AU-0001-BE | SUB-AU-0001 | OAuth endpoints: `GET /auth/oauth/{provider}/authorize` (redirect to provider), `GET /auth/oauth/{provider}/callback` (exchange code for token, lookup user by email, create `user_oauth_accounts` record on first login, issue JWT). Provider configuration via environment variables. | `routers/auth.py`, `services/auth_service.py`, `services/oauth_service.py` | TST-AU-0001-BE | Not Started |
| SUB-AU-0002-BE | SUB-AU-0002 | Email/password login endpoint: `POST /auth/login` (validate credentials, issue JWT). Password reset: `POST /auth/password/reset-request` (generate reset token, send email), `POST /auth/password/reset` (validate token, update password hash). | `routers/auth.py`, `services/auth_service.py` | TST-AU-0002-BE | Not Started |
| SUB-AU-0003-BE | SUB-AU-0003 | JWT issuance with claims (sub, email, name, roles, iat, exp). Refresh token storage in database. `POST /auth/logout` revokes refresh token. Token refresh endpoint reissues access token from valid refresh token. | `services/auth_service.py`, `services/token_service.py`, `routers/auth.py` | TST-AU-0003-BE | Not Started |
| SUB-AU-0004-BE | SUB-AU-0004 | Track `failed_login_attempts` and `locked_until` on user record. Increment on failed email/password attempt, reset on success. Check lockout before authenticating via any method. | `services/auth_service.py`, `models/user.py` | TST-AU-0004-BE | Not Started |
| SUB-AU-0005-BE | SUB-AU-0005 | Database migration seeds admin account from `ADMIN_SEED_EMAIL`, `ADMIN_SEED_NAME`, `ADMIN_SEED_PASSWORD`. Skip insert if email already exists (idempotent). Hash password with bcrypt. Assign `admin` role. | `migrations/`, `models/user.py` | TST-AU-0005-BE | Not Started |
| SUB-AU-0006-BE | SUB-AU-0006 | User management REST endpoints: `POST /users` (create + send invite), `GET /users` (paginated list), `GET /users/{id}`, `PUT /users/{id}` (update name/email), `PATCH /users/{id}/status` (activate/deactivate), `POST /users/{id}/resend-invite`. All endpoints require `admin` role. `GET /users/me` requires any authenticated user. Deactivation revokes all active refresh tokens. | `routers/users.py`, `services/user_service.py`, `models/user.py` | TST-AU-0006-BE | Not Started |
| SUB-AU-0007-BE | SUB-AU-0007 | Invite token generation (cryptographically random, unique), expiry tracking (`invite_expires_at`). `POST /auth/invite/accept` validates token, sets password hash, transitions status to `active`. Expired tokens rejected with 410. | `services/user_service.py`, `services/auth_service.py`, `routers/auth.py` | TST-AU-0007-BE | Not Started |
| SUB-AU-0008-BE | SUB-AU-0008 | Role seeding via migration: `admin`, `clinician`, `sales`, `lab-staff`. `user_roles` join table with `user_id`, `role_id`, `assigned_at`, `assigned_by`. `PUT /users/{id}/roles` replaces user's roles (admin-only). Every user must retain at least one role. | `models/role.py`, `models/user_role.py`, `routers/users.py`, `services/user_service.py` | TST-AU-0008-BE | Not Started |
| SUB-AU-0009-BE | SUB-AU-0009 | `require_role` middleware reads JWT `roles` claim, checks against endpoint's allowed roles, rejects with 403 if no match. Role-permission matrix defined per the [Authentication feature §4.3](../../features/authentication.md). | `middleware/auth.py` | TST-AU-0009-BE | Not Started |
| SUB-AU-0010-BE | SUB-AU-0010 | Before removing `admin` role from a user, query count of remaining admin users. If count would drop to zero, reject with 409 and descriptive error message. | `services/user_service.py` | TST-AU-0010-BE | Not Started |
| SUB-AU-0011-BE | SUB-AU-0011 | Audit log auth events using standardized actions: AUTH_LOGIN, AUTH_LOGIN_FAILED, AUTH_LOGOUT, AUTH_LOCKOUT, AUTH_OAUTH_LINK, AUTH_PASSWORD_RESET. User management actions: USER_CREATE, USER_UPDATE, USER_DEACTIVATE, USER_REACTIVATE, USER_ROLE_CHANGE, USER_INVITE_SEND. Resource type: `user`. | `services/audit_service.py`, `routers/auth.py`, `routers/users.py` | TST-AU-0011-BE | Not Started |
| SUB-AU-0012-BE | SUB-AU-0001 | `user_oauth_accounts` table: store provider identity (`provider`, `provider_user_id`, `provider_email`) linked to user. Unique constraint on (`provider`, `provider_user_id`). | `models/user_oauth_account.py` | TST-AU-0012-BE | Not Started |
| SUB-AU-0013-BE | SUB-AU-0002 | Password validation service: enforce minimum 12 characters, at least one uppercase, one lowercase, one digit, one special character. Reject non-compliant passwords with 422 and specific violation messages. | `services/auth_service.py` | TST-AU-0013-BE | Not Started |
| SUB-AU-0014-BE | SUB-AU-0006 | Email service integration: send invite email with tokenized link, send password reset email with tokenized link. Email service abstracted behind interface for testability (mock in dev/test). | `services/email_service.py` | TST-AU-0014-BE | Not Started |

### Web Frontend (WEB) — 9 requirements

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
| --- | --- | --- | --- | --- | --- |
| SUB-AU-0001-WEB | SUB-AU-0001 | Login page with OAuth provider buttons (Google, Microsoft, GitHub). Clicking a button redirects to `GET /auth/oauth/{provider}/authorize`. Handle callback redirect and store returned JWT. | `app/login/`, `lib/auth.ts` | TST-AU-0001-WEB | Not Started |
| SUB-AU-0002-WEB | SUB-AU-0002 | Email/password login form on login page. Password reset request form (`/forgot-password`) and password reset form (`/reset-password?token=...`). Display validation errors from backend. | `app/login/`, `app/forgot-password/`, `app/reset-password/` | TST-AU-0002-WEB | Not Started |
| SUB-AU-0003-WEB | SUB-AU-0003 | JWT token storage (httpOnly cookie or secure storage), auth guard with parameterized `requireRole` (follows PC-WEB-01). Token refresh with single-Promise lock to prevent thundering herd (RC-WEB-01). Logout clears tokens and redirects to login. | `lib/auth.ts`, `middleware.ts` | TST-AU-0003-WEB | Not Started |
| SUB-AU-0006-WEB | SUB-AU-0006 | User management admin pages: paginated user list, create user form (email, name, role selection), user detail/edit form, deactivate/reactivate toggle, resend invite button. All pages guarded by `requireRole(['admin'])`. | `app/admin/users/` | TST-AU-0006-WEB | Not Started |
| SUB-AU-0007-WEB | SUB-AU-0007 | Invite acceptance page (`/invite/accept?token=...`): validate token, display set-password form with complexity requirements, submit to activate account. Show error for expired/invalid tokens. | `app/invite/` | TST-AU-0007-WEB | Not Started |
| SUB-AU-0008-WEB | SUB-AU-0008 | Multi-role selection in user create/edit forms (checkbox group for admin, clinician, sales, lab-staff). Display assigned roles in user list and detail views. At least one role must be selected (client-side validation). | `app/admin/users/` | TST-AU-0008-WEB | Not Started |
| SUB-AU-0004-WEB | SUB-AU-0004 | Display account lockout message on login form when backend returns lockout error. Show remaining lockout duration if provided. | `app/login/` | TST-AU-0004-WEB | Not Started |
| SUB-AU-0009-WEB | SUB-AU-0009 | Navigation and route visibility based on user's roles from JWT claims. Hide menu items and routes the user has no role to access. Redirect unauthorized access attempts to a 403 page. | `components/navigation/`, `middleware.ts` | TST-AU-0009-WEB | Not Started |
| SUB-AU-0015-WEB | SUB-AU-0006 | Current user profile page (`/profile`): display user name, email, and assigned roles from `GET /users/me`. Available to all authenticated users. | `app/profile/` | TST-AU-0015-WEB | Not Started |

### Android (AND) — 6 requirements

| Platform Req ID | Parent | Description | Module(s) | Test Case(s) | Status |
| --- | --- | --- | --- | --- | --- |
| SUB-AU-0001-AND | SUB-AU-0001 | Login screen with OAuth provider buttons. OAuth flow via Chrome Custom Tabs or Android AppAuth library. Handle redirect URI callback, exchange code via backend, store returned JWT. | `ui/login/LoginScreen.kt`, `data/auth/OAuthManager.kt` | TST-AU-0001-AND | Not Started |
| SUB-AU-0002-AND | SUB-AU-0002 | Email/password login form on login screen. Password reset request screen. Display validation errors from backend. | `ui/login/LoginScreen.kt`, `ui/auth/ForgotPasswordScreen.kt` | TST-AU-0002-AND | Not Started |
| SUB-AU-0003-AND | SUB-AU-0003 | JWT token storage in encrypted DataStore. Auth interceptor injects bearer token on all API calls. Token refresh synchronized via Kotlin `Mutex` — first caller refreshes, subsequent callers wait and reuse new token (PC-AND-02). Logout clears tokens and navigates to login. | `data/auth/TokenManager.kt`, `data/api/AuthInterceptor.kt` | TST-AU-0003-AND | Not Started |
| SUB-AU-0004-AND | SUB-AU-0004 | Display account lockout message on login screen when backend returns lockout error. Show remaining lockout duration if provided. | `ui/login/LoginScreen.kt` | TST-AU-0004-AND | Not Started |
| SUB-AU-0007-AND | SUB-AU-0007 | Handle invite deep link (`pms://invite/accept?token=...`): open set-password screen, validate token via backend, submit password to activate account. Show error for expired/invalid tokens. | `ui/auth/InviteAcceptScreen.kt` | TST-AU-0007-AND | Not Started |
| SUB-AU-0015-AND | SUB-AU-0006 | Current user profile screen: display user name, email, and assigned roles from `GET /users/me`. Available to all authenticated users. | `ui/profile/ProfileScreen.kt` | TST-AU-0015-AND | Not Started |
