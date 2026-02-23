# Risk Assessment: Authentication & User Management

**Document ID:** PMS-RA-AU-001
**Subsystem:** SUB-AU (Authentication & User Management)
**Feature:** SYS-REQ-0014 (Authentication), SYS-REQ-0015 (User Provisioning), SYS-REQ-0005 (RBAC), SYS-REQ-0016 (Auth Bypass)
**Date:** 2026-02-23
**Author:** AI Agent (reviewed by {REVIEWER})
**Standard:** ISO 14971:2019 — Application of risk management to medical devices
**Related QMS:** ISO 13485:2016 Clause 7.1 (Planning of product realization), Clause 7.3.3 (Design and development inputs)

---

## Scope

This risk assessment covers the Authentication & User Management subsystem (SUB-AU), which is the security foundation for all other PMS subsystems. It encompasses:

- **SUB-AU-0001** — OAuth 2.0 authentication (Google, Microsoft, GitHub) with PKCE
  - SUB-AU-0001-BE, SUB-AU-0001-WEB, SUB-AU-0001-AND
- **SUB-AU-0002** — Email/password authentication with bcrypt and password reset
  - SUB-AU-0002-BE, SUB-AU-0002-WEB, SUB-AU-0002-AND
- **SUB-AU-0003** — JWT access tokens and opaque refresh tokens
  - SUB-AU-0003-BE, SUB-AU-0003-WEB, SUB-AU-0003-AND
- **SUB-AU-0004** — Account lockout (5 attempts, 30 minutes)
  - SUB-AU-0004-BE, SUB-AU-0004-WEB, SUB-AU-0004-AND
- **SUB-AU-0005** — Default admin seed from environment variables
  - SUB-AU-0005-BE
- **SUB-AU-0006** — Admin-only user CRUD with session revocation
  - SUB-AU-0006-BE, SUB-AU-0006-WEB, SUB-AU-0015-WEB, SUB-AU-0015-AND
- **SUB-AU-0007** — Invite-based onboarding (72-hour token expiry)
  - SUB-AU-0007-BE, SUB-AU-0007-WEB, SUB-AU-0007-AND
- **SUB-AU-0008** — Four-role model with union-based permissions
  - SUB-AU-0008-BE, SUB-AU-0008-WEB
- **SUB-AU-0009** — Role-permission matrix enforcement per endpoint
  - SUB-AU-0009-BE, SUB-AU-0009-WEB
- **SUB-AU-0010** — Last-admin lockout prevention
  - SUB-AU-0010-BE
- **SUB-AU-0011** — Audit logging of all auth and user management events
  - SUB-AU-0011-BE
- **SUB-AU-0016** — Environment-variable-controlled auth bypass for dev/CI
  - SUB-AU-0016-BE, SUB-AU-0016-WEB

**Platform requirements also covered:** SUB-AU-0012-BE (OAuth accounts table), SUB-AU-0013-BE (password validation), SUB-AU-0014-BE (email service)

**Architecture references:** ADR-0023 (auth bypass flag)

**Governance cross-references:** DC-AU-01 (audit bypass gap), DC-AU-02 (flag mismatch), PC-BE-02 (shared auth middleware), PC-BE-06 (shared auth — prompts), PC-BE-09 (shared auth — bypass), PC-WEB-01 (shared auth guard), PC-WEB-03 (shared auth — prompts), PC-WEB-04 (shared auth — bypass), PC-AND-02 (shared auth interceptor), RC-WEB-01 (token refresh thundering herd)

---

## Risk Acceptability Matrix

| Probability / Severity | 1 (Negligible) | 2 (Minor) | 3 (Moderate) | 4 (Major) | 5 (Catastrophic) |
|---|---|---|---|---|---|
| **5 (Frequent)** | 5 | 10 | 15 | 20 | 25 |
| **4 (Probable)** | 4 | 8 | 12 | 16 | 20 |
| **3 (Occasional)** | 3 | 6 | 9 | 12 | 15 |
| **2 (Remote)** | 2 | 4 | 6 | 8 | 10 |
| **1 (Improbable)** | 1 | 2 | 3 | 4 | 5 |

Risk levels: **1-4 = Acceptable** (green), **5-9 = ALARP** (yellow), **10-25 = Unacceptable** (red)

---

## Risk Register

### Clinical Safety

| Risk ID | Description | Related Req(s) | Severity | Probability | Risk Level | Mitigation | Residual Risk |
|---|---|---|---|---|---|---|---|
| RISK-AU-001 | **Auth bypass accidentally enabled in production** — SUB-AU-0016 provides environment-variable-controlled auth bypass. If `AUTH_BYPASS_ENABLED=true` reaches production/staging/qa, all authentication is disabled system-wide. Every API endpoint becomes publicly accessible, exposing PHI to unauthenticated callers. Complete HIPAA Security Rule violation (§164.312(d)). | SUB-AU-0016, SUB-AU-0016-BE, SUB-AU-0016-WEB, SYS-REQ-0016 | 5 (Catastrophic) | 2 (Remote) | **10 (Unacceptable)** | (1) SUB-AU-0016-BE returns HTTP 500 with descriptive error if bypass detected and `ENVIRONMENT` is `production`, `staging`, or `qa` (environment guard). (2) CI pipeline guard rejects deployment with bypass enabled. (3) `.env.production` excludes bypass flag by convention. (4) WARN-level startup log when bypass is active (ADR-0023). (5) Non-dismissible yellow banner on frontend when bypass is active (SUB-AU-0016-WEB). | S5 × P1 = **5 (ALARP)** |
| RISK-AU-002 | **JWT signing key compromise** — If the JWT secret is leaked (e.g., committed to source control, exposed in logs, extracted from server), an attacker can forge valid access tokens for any user with any role, bypassing all authentication and authorization controls. | SUB-AU-0003, SUB-AU-0003-BE, SYS-REQ-0001 | 5 (Catastrophic) | 2 (Remote) | **10 (Unacceptable)** | (1) JWT secret stored in environment variables, never committed to source control. (2) 30-minute access token expiry limits exposure window. (3) Server-side opaque refresh tokens enable revocation. (4) Secret rotation procedure: generate new secret, existing tokens expire naturally within 30 min. (5) Audit trail detects anomalous access patterns. | S5 × P1 = **5 (ALARP)** |
| RISK-AU-003 | **Incomplete role-permission matrix leaves endpoints unprotected** — SUB-AU-0009-BE enforces a role-permission matrix per API endpoint. If the matrix is incomplete or a new endpoint is added without a corresponding entry, the endpoint may be accessible without proper authorization. Cross-subsystem impact: all 6 subsystems' endpoints depend on this matrix. | SUB-AU-0009, SUB-AU-0009-BE, SYS-REQ-0005 | 4 (Major) | 2 (Remote) | **8 (ALARP)** | (1) Role-permission matrix defined per Authentication feature §4.3. (2) `require_role` middleware enforces per endpoint — endpoints without guards reject by default. (3) Unauthorized access returns 403 and is logged to audit trail (SUB-AU-0011-BE). (4) Code review process and integration tests validate guard coverage. (5) Consolidated RBAC matrix document maps every endpoint to allowed roles (PC-BE-04, resolved). | S4 × P1 = **4 (Acceptable)** |
| RISK-AU-004 | **Union-based multi-role over-permissioning** — SUB-AU-0008 implements union-based permissions: a user with multiple roles receives the combined permissions of all assigned roles. An admin could inadvertently assign excessive roles, granting a user broader access than intended for their job function. | SUB-AU-0008, SUB-AU-0008-BE, SUB-AU-0008-WEB | 3 (Moderate) | 2 (Remote) | **6 (ALARP)** | (1) Union-based permissions is an intentional design decision (Design Decision #3: "More roles = more access"). (2) Role assignment is admin-only (SUB-AU-0006). (3) At least one role required (SUB-AU-0008-BE). (4) Role changes are audit-logged (SUB-AU-0011-BE: USER_ROLE_CHANGE). (5) Admin UI displays assigned roles clearly (SUB-AU-0008-WEB). | S3 × P1 = **3 (Acceptable)** |
| RISK-AU-005 | **Privilege escalation via user management endpoints** — Non-admin user accesses user CRUD endpoints (POST/GET/PUT/PATCH on `/users`), creating accounts, modifying roles, or deactivating users without authorization. | SUB-AU-0006, SUB-AU-0006-BE, SUB-AU-0009-BE | 4 (Major) | 1 (Improbable) | **4 (Acceptable)** | (1) All user management endpoints require `admin` role (SUB-AU-0006-BE). (2) `require_role` middleware enforces per endpoint (SUB-AU-0009-BE). (3) Unauthorized access returns 403 and is audit-logged. (4) `GET /users/me` is the only endpoint available to non-admin authenticated users. | S4 × P1 = **4 (Acceptable)** |
| RISK-AU-006 | **Invite token interception enables unauthorized account activation** — An attacker intercepts an invite email or deep link containing the one-time token and activates the account before the intended recipient, gaining access under the invited user's identity. | SUB-AU-0007, SUB-AU-0007-BE, SUB-AU-0007-AND | 4 (Major) | 1 (Improbable) | **4 (Acceptable)** | (1) Cryptographically random, unique tokens (SUB-AU-0007-BE). (2) One-time use — invalidated after acceptance. (3) 72-hour expiry. (4) Token sent only to the admin-specified email address. (5) Expired/used tokens rejected with 410. | S4 × P1 = **4 (Acceptable)** |
| RISK-AU-007 | **Email service delivers invite/reset to wrong recipient** — If the admin enters an incorrect email during user creation, the invite token is sent to an unintended person who can then activate the account and access the system. | SUB-AU-0014-BE, SUB-AU-0006-BE, SUB-AU-0007 | 4 (Major) | 1 (Improbable) | **4 (Acceptable)** | (1) Admin manually enters the email during user creation — responsibility lies with the admin. (2) Email uniqueness constraint prevents creating a duplicate user with a different email. (3) Invite acceptance audit-logged (SUB-AU-0011-BE). (4) Admin can deactivate an incorrectly created account and revoke all sessions (SUB-AU-0006-BE). | S4 × P1 = **4 (Acceptable)** |

### Data Integrity

| Risk ID | Description | Related Req(s) | Severity | Probability | Risk Level | Mitigation | Residual Risk |
|---|---|---|---|---|---|---|---|
| RISK-AU-008 | **Credential brute-force / stuffing attack** — Attacker uses automated tools to try many email/password combinations against the login endpoint, attempting to gain access using leaked credentials from other services. | SUB-AU-0002, SUB-AU-0004, SUB-AU-0002-BE, SUB-AU-0004-BE, SUB-AU-0013-BE | 4 (Major) | 2 (Remote) | **8 (ALARP)** | (1) Account lockout after 5 consecutive failed attempts for 30 minutes (SUB-AU-0004). (2) Bcrypt cost factor 12 makes offline brute-force impractical (Design Decision #4). (3) Password complexity: 12+ chars, mixed case, digit, special character (SUB-AU-0013-BE). (4) Lockout applies across all auth methods (SUB-AU-0004). (5) Failed login attempts audit-logged (SUB-AU-0011-BE: AUTH_LOGIN_FAILED). | S4 × P1 = **4 (Acceptable)** |
| RISK-AU-009 | **OAuth PKCE misconfiguration allows authorization code interception** — If PKCE is not correctly implemented (e.g., code verifier not validated, using plain challenge method), an attacker on the same device or network could intercept the authorization code and exchange it for a token. | SUB-AU-0001, SUB-AU-0001-BE, SUB-AU-0001-WEB, SUB-AU-0001-AND | 4 (Major) | 2 (Remote) | **8 (ALARP)** | (1) PKCE (Authorization Code flow with PKCE) is mandatory per SUB-AU-0001. (2) Provider-agnostic OAuth via common interface (Design Decision #5) — single implementation tested across all providers. (3) Standard library implementations (e.g., AppAuth for Android). (4) OAuth providers enforce PKCE server-side. | S4 × P1 = **4 (Acceptable)** |
| RISK-AU-010 | **Refresh token theft enables persistent unauthorized access** — Attacker obtains a refresh token (via XSS, stolen cookie, or compromised device) and uses it to generate new access tokens for up to 7 days, maintaining persistent access. | SUB-AU-0003, SUB-AU-0003-BE, SUB-AU-0003-WEB, SUB-AU-0003-AND | 4 (Major) | 2 (Remote) | **8 (ALARP)** | (1) Server-side opaque refresh tokens — not self-contained JWTs, cannot be forged. (2) Logout revokes refresh token (SUB-AU-0003-BE). (3) Deactivation revokes all refresh tokens (SUB-AU-0006-BE). (4) 7-day expiry limits exposure window. (5) httpOnly cookie storage prevents JavaScript access (SUB-AU-0003-WEB). (6) Encrypted DataStore on Android (SUB-AU-0003-AND). | S4 × P1 = **4 (Acceptable)** |
| RISK-AU-011 | **XSS-based JWT exfiltration from client storage** — Cross-site scripting vulnerability in the frontend allows an attacker to steal the JWT access token from client storage and impersonate the user. Note: CLAUDE.md references localStorage; SUB-AU-0003-WEB specifies "httpOnly cookie or secure storage." | SUB-AU-0003-WEB, SUB-AU-0001-WEB, SUB-AU-0002-WEB | 4 (Major) | 2 (Remote) | **8 (ALARP)** | (1) SUB-AU-0003-WEB specifies httpOnly cookie or secure storage — implementation must prefer httpOnly cookies (not accessible to JavaScript). (2) React's built-in XSS protection (auto-escaping). (3) Content Security Policy headers. (4) Next.js framework protections. (5) Short token expiry (30 min default) limits stolen token utility. | S4 × P1 = **4 (Acceptable)** |
| RISK-AU-012 | **Password reset token prediction enables account takeover** — Attacker guesses or brute-forces a password reset token and resets a user's password without access to their email. | SUB-AU-0002, SUB-AU-0002-BE, SUB-AU-0007-BE | 4 (Major) | 1 (Improbable) | **4 (Acceptable)** | (1) Cryptographically random token generation (SUB-AU-0007-BE). (2) Token sent only to the registered email. (3) Time-limited expiry. (4) One-time use — invalidated after consumption. (5) Password reset audit-logged (SUB-AU-0011-BE: AUTH_PASSWORD_RESET). | S4 × P1 = **4 (Acceptable)** |
| RISK-AU-013 | **Audit log failure silently drops authentication events** — If the audit service fails (database connection loss, write error), authentication events (login, logout, failed attempts, lockout) may not be recorded, creating a HIPAA §164.312(b) compliance gap. | SUB-AU-0011, SUB-AU-0011-BE, SYS-REQ-0003 | 3 (Moderate) | 2 (Remote) | **6 (ALARP)** | (1) Audit logging is synchronous within the database transaction — if the audit write fails, the transaction rolls back. (2) Established pattern from SUB-PR-0005-BE (patient audit logging). (3) Standardized audit event catalog (PC-BE-03, PC-BE-07). (4) Database reliability (PostgreSQL with WAL ensures durability). | S3 × P1 = **3 (Acceptable)** |
| RISK-AU-014 | **Auth bypass audit trail gap in dev/CI environments** — When bypass is active (SUB-AU-0016), no login, logout, failed attempt, or lockout events occur because the authentication flow is completely skipped. SUB-AU-0011 requires audit logging of all auth events. | SUB-AU-0016 vs SUB-AU-0011 | 1 (Negligible) | 4 (Probable) | **4 (Acceptable)** | (1) DC-AU-01 resolved: AUTH_BYPASS_ACTIVE startup event logged (action: `AUTH_BYPASS_ACTIVE`, resource_type: `system`). (2) Dev/CI environments contain no PHI — audit gap has no regulatory impact. (3) Runtime auth events cannot occur when bypass is active (they are inherently scoped to non-bypass operation). | S1 × P4 = **4 (Acceptable)** |
| RISK-AU-015 | **Android invite deep link scheme hijack** — Malicious app registers the same `pms://` URI scheme on the Android device, intercepting invite acceptance deep links and capturing the one-time invite token. | SUB-AU-0007-AND | 3 (Moderate) | 2 (Remote) | **6 (ALARP)** | (1) Invite tokens are one-time use and expire in 72 hours. (2) App Links (HTTPS-based verified links) preferred over custom `pms://` scheme for Android 12+ (domain verification prevents hijacking). (3) Token acceptance requires setting a password — interceptor cannot silently activate. (4) Invite send is audit-logged (SUB-AU-0011-BE). | S3 × P1 = **3 (Acceptable)** |

### Availability

| Risk ID | Description | Related Req(s) | Severity | Probability | Risk Level | Mitigation | Residual Risk |
|---|---|---|---|---|---|---|---|
| RISK-AU-016 | **OAuth provider outage prevents user authentication** — One or more OAuth providers (Google, Microsoft, GitHub) experience an outage, preventing users who rely on OAuth from authenticating. Since PMS uses closed registration (OAuth does not create users), users without email/password credentials cannot fall back to email/password auth unless they have previously set a password. | SUB-AU-0001, SUB-AU-0001-BE, SUB-AU-0001-WEB, SUB-AU-0001-AND | 3 (Moderate) | 3 (Occasional) | **9 (ALARP)** | (1) Dual authentication methods: OAuth + email/password (SUB-AU-0002). (2) Three independent OAuth providers — simultaneous outage of all three is extremely unlikely. (3) Email/password authentication is independent of external services. (4) Invite-based onboarding sets a password during activation (SUB-AU-0007), ensuring all users have email/password as a fallback. | S3 × P1 = **3 (Acceptable)** |
| RISK-AU-017 | **Intentional account lockout denial-of-service** — Attacker repeatedly submits incorrect passwords for a known email address, triggering the 5-attempt lockout (SUB-AU-0004). The targeted user is locked out for 30 minutes across all authentication methods, including OAuth. This attack can be repeated indefinitely. | SUB-AU-0004, SUB-AU-0004-BE | 3 (Moderate) | 3 (Occasional) | **9 (ALARP)** | (1) 30-minute auto-unlock limits each lockout duration. (2) Lockout is time-bounded — no permanent account impact. (3) AUTH_LOCKOUT event audit-logged for detection (SUB-AU-0011-BE). (4) Recommend: CAPTCHA or progressive delay on login endpoint as future enhancement to reduce attack probability. | S3 × P2 = **6 (ALARP)** |
| RISK-AU-018 | **Backend-frontend auth bypass flag mismatch** — Developer configures `AUTH_BYPASS_ENABLED=true` on one side but not the other. Frontend bypass + backend auth → all API calls fail with 401. Frontend auth + backend bypass → frontend sends real JWT but backend ignores it and injects a different mock user identity. Both scenarios produce confusing errors during development. | SUB-AU-0016-BE, SUB-AU-0016-WEB | 2 (Minor) | 3 (Occasional) | **6 (ALARP)** | (1) DC-AU-02 resolved: SUB-AU-0016-WEB detects mismatch at runtime by comparing mock user identity against API response. (2) Configuration error banner: "Backend auth bypass is not enabled — check AUTH_BYPASS_ENABLED." (3) Documentation in `.env.example` specifies that both flags must be set consistently. | S2 × P1 = **2 (Acceptable)** |
| RISK-AU-019 | **Admin seed credentials leaked via environment variables** — The default admin seed (ADMIN_SEED_EMAIL, ADMIN_SEED_NAME, ADMIN_SEED_PASSWORD) is stored in environment variables that may be exposed in CI logs, Docker inspect output, or misconfigured secret managers. An attacker with the seed password gains admin access. | SUB-AU-0005, SUB-AU-0005-BE, SYS-REQ-0015 | 4 (Major) | 2 (Remote) | **8 (ALARP)** | (1) Seed operation is idempotent — runs once, creating the initial admin only if no admin exists. (2) Admin should change password after first login (onboarding procedure). (3) Environment variables not committed to source control (.gitignore). (4) Password hashed with bcrypt cost 12 before storage. (5) Seed password must pass the same complexity validation as user passwords (SUB-AU-0013-BE). | S4 × P1 = **4 (Acceptable)** |

### Concurrency

| Risk ID | Description | Related Req(s) | Severity | Probability | Risk Level | Mitigation | Residual Risk |
|---|---|---|---|---|---|---|---|
| RISK-AU-020 | **Last-admin lockout via concurrent role removal** — Two administrators simultaneously remove the `admin` role from each other. Both requests read "2 admins exist," both pass the SUB-AU-0010-BE check, and both commit — leaving zero administrators. The system becomes unmanageable without direct database intervention. | SUB-AU-0010, SUB-AU-0010-BE | 4 (Major) | 2 (Remote) | **8 (ALARP)** | (1) SUB-AU-0010-BE queries count of remaining admin users before removal; rejects with 409 if count would drop to zero. (2) Recommend: use `SELECT COUNT(*) FROM user_roles WHERE role = 'admin' FOR UPDATE` to serialize concurrent admin role removal, preventing the TOCTOU race. (3) Extremely narrow race window — requires two admins modifying roles at the exact same time. | S4 × P1 = **4 (Acceptable)** |
| RISK-AU-021 | **Token refresh thundering herd** — Multiple concurrent API calls fail with 401 (token expired). Each call independently triggers a token refresh. Multiple refresh requests hit the backend — only the first succeeds; subsequent ones use an invalidated refresh token, causing cascading 401 errors and user session loss. | SUB-AU-0003-WEB, SUB-AU-0003-AND, RC-WEB-01, PC-AND-02 | 3 (Moderate) | 2 (Remote) | **6 (ALARP)** | (1) RC-WEB-01 resolved: single-Promise lock on web — first caller refreshes, subsequent callers await and reuse the new token (Design Decision #6). (2) PC-AND-02 resolved: Kotlin `Mutex` on Android serializes refresh attempts. (3) Both implementations follow the same pattern: first-caller-refreshes, others-wait. | S2 × P1 = **2 (Acceptable)** |
| RISK-AU-022 | **Deactivated user retains access until token expiry** — Admin deactivates a user (SUB-AU-0006-BE), but the user's current access token remains valid for up to 30 minutes. During this window, the deactivated user can continue making authenticated API requests. | SUB-AU-0006-BE, SUB-AU-0003-BE | 3 (Moderate) | 2 (Remote) | **6 (ALARP)** | (1) Deactivation immediately revokes all active refresh tokens (SUB-AU-0006-BE) — no new access tokens can be issued. (2) Access token 30-minute default expiry limits the window. (3) For immediate revocation, backend could implement a short-lived token blacklist (cache-based, keyed by `jti` claim) — recommended as future enhancement for high-security environments. (4) Deactivation audit-logged (SUB-AU-0011-BE: USER_DEACTIVATE). | S3 × P1 = **3 (Acceptable)** |

---

## Summary

| Metric | Count |
|---|---|
| **Total risks identified** | **22** |
| Acceptable (1-4) before mitigation | 5 |
| ALARP (5-9) before mitigation | 15 |
| Unacceptable (10-25) before mitigation | 2 |

### After Mitigation (Residual Risk)

| Residual Level | Count | Risk IDs |
|---|---|---|
| **Acceptable (1-4)** | **19** | RISK-AU-003, 004, 005, 006, 007, 008, 009, 010, 011, 012, 013, 014, 015, 016, 018, 019, 020, 021, 022 |
| **ALARP (5-9)** | **3** | RISK-AU-001 (5), RISK-AU-002 (5), RISK-AU-017 (6) |
| **Unacceptable (10-25)** | **0** | — |
| **Residual unacceptable risks** | **0** | Must be 0 before release |

### Residual ALARP Justification

The 3 residual ALARP risks are accepted under the following rationale:

| Risk ID | Residual | Acceptance Rationale |
|---|---|---|
| RISK-AU-001 | 5 | Auth bypass in production has catastrophic severity that cannot be reduced by design — disabling all authentication is inherently a worst-case scenario. Probability is reduced to Improbable by three independent defense-in-depth layers: (1) backend environment guard returns HTTP 500, (2) CI pipeline guard rejects deployment, (3) `.env.production` excludes the flag. All three must fail simultaneously for production exposure. Residual risk is comparable to other environment-variable-based configuration risks in production systems. |
| RISK-AU-002 | 5 | JWT signing key compromise has catastrophic severity — a forged token bypasses all access controls. Probability is Improbable because the secret is stored in environment variables (never in source control) and is not transmitted over the wire. The 30-minute token expiry limits the exploitation window even if compromise occurs. Secret rotation restores security within 30 minutes. Residual risk is inherent to any JWT-based authentication system. |
| RISK-AU-017 | 6 | Intentional lockout DoS is a known trade-off of account lockout mechanisms (SUB-AU-0004). The lockout protects against brute-force attacks (RISK-AU-008) but creates a DoS vector. Severity is Moderate (30-minute inconvenience, no PHI exposure). Probability is Remote with recommended CAPTCHA/rate limiting. This is a security defense trade-off: removing lockout would increase RISK-AU-008 from Acceptable to ALARP. The current balance prioritizes credential protection over availability. |

---

## Traceability to Governance Mitigations

The following resolved conflicts from [requirements-governance.md](../processes/requirements-governance.md) serve as existing mitigations referenced in this risk assessment:

| Governance ID | Description | Risks Mitigated |
|---|---|---|
| DC-AU-01 | Auth bypass skips audit trail — AUTH_BYPASS_ACTIVE startup event specified | RISK-AU-014 |
| DC-AU-02 | Backend-frontend bypass flag inconsistency — runtime mismatch detection | RISK-AU-018 |
| PC-BE-02 | Shared auth middleware coupling — accepted as designed, TST-AUTH-0001 system test | RISK-AU-003 |
| PC-BE-04 | Role matrix inconsistency — consolidated RBAC matrix | RISK-AU-003, RISK-AU-004 |
| PC-BE-09 | Shared auth middleware bypass — follows PC-BE-02 precedent, integration test added | RISK-AU-001 |
| PC-WEB-01 | Shared auth guard — parameterized `requireRole` with subsystem-specific role lists | RISK-AU-003 |
| PC-WEB-04 | Shared auth module bypass — short-circuit before guard and refresh lock | RISK-AU-001 |
| PC-AND-02 | Shared auth interceptor — Mutex-based token refresh synchronization | RISK-AU-021 |
| RC-WEB-01 | Token refresh thundering herd — single-Promise lock | RISK-AU-021 |

---

## Regulatory Mapping

| Regulatory Requirement | Risk IDs | Compliance Status |
|---|---|---|
| HIPAA §164.312(d) — Person or Entity Authentication | RISK-AU-001, 002, 005, 006, 008, 009, 010, 011 | Mitigated via multi-method auth (OAuth + email/password), PKCE, token management, lockout, and environment guard |
| HIPAA §164.312(a)(1) — Access Controls | RISK-AU-003, 004, 005 | Mitigated via RBAC model (SUB-AU-0008/0009), role-permission matrix enforcement per endpoint |
| HIPAA §164.312(b) — Audit Controls | RISK-AU-013, 014 | Mitigated via comprehensive auth event audit logging (SUB-AU-0011-BE) and AUTH_BYPASS_ACTIVE startup event |
| HIPAA §164.312(a)(2)(iv) — Encryption of ePHI | RISK-AU-010, 011 | Mitigated via httpOnly cookies, encrypted DataStore (Android), bcrypt password hashing |
| HIPAA §164.312(c)(1) — Integrity Controls | RISK-AU-012, 020 | Mitigated via cryptographic tokens, one-time use, last-admin lockout prevention |
| HIPAA §164.308(a)(5)(ii)(D) — Password Management | RISK-AU-008, 012, 017 | Mitigated via password complexity (SUB-AU-0013-BE), lockout (SUB-AU-0004), reset tokens |
| ISO 13485 §7.3.3 — Design Inputs (risk) | All | This document fulfills the risk assessment input requirement |
| ISO 13485 §7.3.4 — Design Outputs | All | Mitigations trace to specific requirements and ADRs |
| ISO 14971 §4.4 — Risk Analysis | All 22 risks | Severity and probability estimated per risk acceptability matrix |
| ISO 14971 §5 — Risk Evaluation | All 22 risks | Evaluated against acceptability criteria (Acceptable/ALARP/Unacceptable) |
| ISO 14971 §6 — Risk Control | 17 risks >= ALARP | Mitigations specified with residual risk re-evaluation |

---

## References

- [SYS-REQ-0014](../../specs/requirements/SYS-REQ.md) — Authentication
- [SYS-REQ-0015](../../specs/requirements/SYS-REQ.md) — User Provisioning
- [SYS-REQ-0005](../../specs/requirements/SYS-REQ.md) — RBAC
- [SYS-REQ-0016](../../specs/requirements/SYS-REQ.md) — Auth Bypass for Development
- [SUB-AU](../../specs/requirements/SUB-AU.md) — Authentication & User Management domain requirements
- [SUB-BE (AU section)](../../specs/requirements/platform/SUB-BE.md) — Backend platform requirements
- [SUB-WEB (AU section)](../../specs/requirements/platform/SUB-WEB.md) — Web frontend platform requirements
- [SUB-AND (AU section)](../../specs/requirements/platform/SUB-AND.md) — Android platform requirements
- [ADR-0023](../../architecture/0023-auth-bypass-flag-for-development.md) — Auth bypass flag for development
- [Requirements Governance](../processes/requirements-governance.md) — Resolved conflicts and race conditions
