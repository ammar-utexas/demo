# Security Scanning Configuration

This document describes the three security scanning tools integrated across all PMS repositories: SonarCloud, CodeRabbit, and Snyk.

## SonarCloud

**Purpose:** Static code analysis, code coverage tracking, and quality gate enforcement.

### Organization & Projects

| Project Key | Repository |
|---|---|
| `utexas-demo_pms-backend` | pms-backend |
| `utexas-demo_pms-frontend` | pms-frontend |
| `utexas-demo_pms-android` | pms-android |
| `utexas-demo_pms-ai` | pms-ai |

**Organization:** `utexas-demo`

### Configuration Files

Each repo contains:
- `sonar-project.properties` — project key, source/test paths, coverage report paths
- `.github/workflows/sonarqube.yml` — CI workflow that runs tests, generates coverage, and invokes SonarCloud

### Coverage Configuration Per Repo

| Repo | Test Command | Coverage Tool | Report Path |
|---|---|---|---|
| pms-backend | `pytest --cov=src/pms --cov-report=xml` | pytest-cov | `coverage.xml` |
| pms-frontend | `npm test -- --coverage --coverage.reporter=lcov` | v8 (via Vitest) | `coverage/lcov.info` |
| pms-android | `./gradlew createDevDebugUnitTestCoverageReport` | JaCoCo (AGP built-in) | `app/build/reports/coverage/test/dev/debug/report.xml` |
| pms-ai | `pytest --cov=services --cov-report=xml` | pytest-cov | `coverage.xml` |

**Android JaCoCo setup:** The `app/build.gradle.kts` has `enableUnitTestCoverage = true` in the `debug` build type, which enables AGP's built-in JaCoCo instrumentation. The CI workflow runs the `createDevDebugUnitTestCoverageReport` Gradle task to generate the XML report. The `sonar-project.properties` file points `sonar.coverage.jacoco.xmlReportPaths` to the AGP output path.

### Quality Gates

A custom **PMS Quality Gate** is configured in SonarCloud and assigned to all three projects. It enforces on new code:
- No critical issues
- No new bugs
- No new vulnerabilities
- Code coverage >= 80%

The quality gate is **enforced** — CI will fail if the gate does not pass. The `continue-on-error` flag has been removed from the workflow.

### Required Secret

| Secret | Where | Source |
|---|---|---|
| `SONAR_TOKEN` | GitHub org or per-repo secrets | SonarCloud > My Account > Security > Generate Token |

### Setup Steps

1. Log in to [sonarcloud.io](https://sonarcloud.io) with your GitHub account
2. Create the organization `utexas-demo` (or import from GitHub)
3. Create 3 projects matching the `sonar.projectKey` values above
4. Disable **Automatic Analysis** in each project (Administration > Analysis Method) — CI-based analysis is used instead
5. Generate a token and add it as `SONAR_TOKEN` in GitHub secrets
6. Push the workflow files — scans will run automatically on the next PR

---

## CodeRabbit

**Purpose:** AI-powered code review on pull requests, configured with HIPAA-aware review instructions.

### Configuration

Each repo contains a `.coderabbit.yaml` file with:
- **Path-specific instructions** referencing requirement IDs (SYS-REQ-0002, SYS-REQ-0003, SYS-REQ-0005)
- **Path filters** to skip generated/vendor files
- **Profile:** `chill` (suggestions, not blocking)

### HIPAA Review Rules

CodeRabbit is instructed to verify:
- **SYS-REQ-0002:** Encryption on PHI fields (models, data layer)
- **SYS-REQ-0003:** Audit logging on patient data access (routers, services)
- **SYS-REQ-0005:** RBAC checks precede data access (routers, UI)

### Setup Steps

1. Install the CodeRabbit GitHub App from [github.com/marketplace/coderabbit](https://github.com/marketplace/coderabbit)
2. Grant access to the `utexas-demo` organization repositories
3. No secrets required — CodeRabbit reads `.coderabbit.yaml` from each repo automatically

---

## Snyk

**Purpose:** Dependency vulnerability scanning, static application security testing (SAST), and container image scanning.

### Scan Types Per Repo

| Repo | Dependencies | SAST (Code) | Container |
|---|---|---|---|
| pms-backend | `snyk/actions/python-3.12` | `snyk/actions/python-3.12` (code test) | `snyk/actions/docker` |
| pms-frontend | `snyk/actions/node` | `snyk/actions/node` (code test) | `snyk/actions/docker` |
| pms-android | `snyk/actions/gradle-jdk17` | `snyk/actions/node` (code test) | N/A |
| pms-ai | `snyk/actions/python-3.12` | `snyk/actions/python-3.12` (code test) | `snyk/actions/docker` |

### Configuration

Each repo contains `.github/workflows/snyk-security.yml` with:
- Separate jobs for each scan type
- `--severity-threshold=medium` to filter low-severity findings
- SARIF output uploaded to GitHub Code Scanning via `github/codeql-action/upload-sarif@v4`
- `continue-on-error: true` on both scan and SARIF upload steps — scans report findings without blocking CI
- SARIF upload uses `continue-on-error` because GitHub Code Scanning requires GitHub Advanced Security, which may not be available on all plans for private repos

### Evidence Storage

- **GitHub Code Scanning:** SARIF results appear in the repo's Security tab > Code scanning alerts
- **Snyk Dashboard:** Full scan history at [app.snyk.io](https://app.snyk.io)
- **Retention:** GitHub Code Scanning retains alerts until dismissed; Snyk retains per plan limits

### Required Secret

| Secret | Where | Source |
|---|---|---|
| `SNYK_TOKEN` | GitHub org or per-repo secrets | Snyk > Account Settings > Auth Token |

### Setup Steps

1. Create a Snyk account at [app.snyk.io](https://app.snyk.io)
2. Copy your auth token from Account Settings
3. Add it as `SNYK_TOKEN` in GitHub secrets (org level recommended)
4. Push the workflow files — scans will run automatically on the next PR

---

## CI Workflow Configuration

### Docker Image Registry

The backend and frontend CI workflows (`.github/workflows/ci.yml`) build and push Docker images to GitHub Container Registry (GHCR). The `IMAGE_NAME` env var must match the GitHub organization:

| Repo | IMAGE_NAME |
|---|---|
| pms-backend | `utexas-demo/pms-backend` |
| pms-frontend | `utexas-demo/pms-frontend` |
| pms-ai | `utexas-demo/pms-ai` |

Images are pushed on `main` branch and version tags. The workflow uses `GITHUB_TOKEN` with `packages: write` permission — no additional secrets needed.

### Frontend Docker Build

The frontend Dockerfile uses a multi-stage build with Next.js standalone output. Two requirements:

1. **`next.config.ts`** must include `output: "standalone"` — this tells Next.js to produce a self-contained `server.js` in `.next/standalone/`
2. **`public/` directory** must exist in the repo (even if empty, with a `.gitkeep`) — the Dockerfile copies it into the runner stage

### Action Version Notes

| Action | Version | Notes |
|---|---|---|
| `sonarsource/sonarqube-scan-action` | `@v6` | Updated from `@v5`; `@v2` had a security vulnerability |
| `sonarsource/sonarqube-quality-gate-action` | `@v1` | Updated from `@master` |
| `github/codeql-action/upload-sarif` | `@v4` | Updated from `@v3`; v3 deprecated December 2026 |

---

## Verification

After merging the configuration files and setting up secrets:

1. **SonarCloud:** Open a PR — the `SonarCloud Analysis` check should appear in PR checks
2. **CodeRabbit:** Open a PR — CodeRabbit should post a review comment automatically
3. **Snyk:** Open a PR — the `Snyk Security Scan` check should appear; findings appear in GitHub Security tab

SonarCloud quality gates are enforced (CI fails on gate failure). Snyk uses `continue-on-error: true` to report findings without blocking CI. CodeRabbit runs in `chill` profile (suggestions only).
